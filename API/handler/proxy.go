// Package handler zawiera logikę proxy przekazującą requesty
// z Go API gateway do backendu Pythonowego (FastAPI).
//
// Proxy nie modyfikuje body requestów — działa jako transparentny
// pośrednik, kopiując nagłówki, body i status code.
package handler

import (
	"io"
	"log"
	"net/http"
	"strings"
	"time"
)

// Proxy przekierowuje requesty z frontendu do Python backendu (FastAPI).
// Przechowuje bazowy URL backendu oraz klienta HTTP z odpowiednim timeoutem.
type Proxy struct {
	backendURL string       // np. "http://127.0.0.1:8000"
	client     *http.Client // klient HTTP z timeoutem 120s (Ollama bywa wolna)
}

// NewProxy tworzy nową instancję proxy wskazującą na podany adres backendu.
// Trailing slash jest usuwany, żeby uniknąć podwójnych slashy w URL-ach.
func NewProxy(backendURL string) *Proxy {
	return &Proxy{
		backendURL: strings.TrimRight(backendURL, "/"),
		client: &http.Client{
			Timeout: 120 * time.Second, // Wysoki timeout — generowanie odpowiedzi przez Ollamę może trwać długo
		},
	}
}

// Forward przekazuje request 1:1 do backendu Pythonowego.
// Ścieżka URL jest zachowana bez zmian (np. /chat → backend/chat).
func (p *Proxy) Forward(w http.ResponseWriter, r *http.Request) {
	p.proxyTo(w, r, r.URL.Path)
}

// ForwardReset obsługuje endpoint /reset/{sessionID}.
// Wyciąga sessionID z parametru ścieżki (Go 1.22 path values)
// i odtwarza oryginalną ścieżkę /reset/<id> dla backendu.
func (p *Proxy) ForwardReset(w http.ResponseWriter, r *http.Request) {
	sessionID := r.PathValue("sessionID")
	if sessionID == "" {
		http.Error(w, `{"detail":"missing session_id"}`, http.StatusBadRequest)
		return
	}
	p.proxyTo(w, r, "/reset/"+sessionID)
}

// proxyTo — główna metoda proxy. Tworzy nowy request do backendu,
// kopiuje nagłówki i body z oryginalnego requestu, wykonuje go,
// a następnie przekazuje odpowiedź (nagłówki + body + status) z powrotem do klienta.
func (p *Proxy) proxyTo(w http.ResponseWriter, r *http.Request, path string) {
	// Składamy pełny URL do backendu: np. http://127.0.0.1:8000/chat
	targetURL := p.backendURL + path

	// Tworzymy nowy request z kontekstem oryginalnego (pozwala na anulowanie)
	proxyReq, err := http.NewRequestWithContext(r.Context(), r.Method, targetURL, r.Body)
	if err != nil {
		log.Printf("proxy: error creating request: %v", err)
		http.Error(w, `{"detail":"internal proxy error"}`, http.StatusInternalServerError)
		return
	}

	// Kopiuj wszystkie nagłówki z oryginalnego requestu (Content-Type, Authorization, itp.)
	for key, values := range r.Header {
		for _, v := range values {
			proxyReq.Header.Add(key, v)
		}
	}
	// Dodaj nagłówek X-Forwarded-For z adresem IP klienta
	proxyReq.Header.Set("X-Forwarded-For", r.RemoteAddr)

	// Wykonaj request do backendu
	resp, err := p.client.Do(proxyReq)
	if err != nil {
		log.Printf("proxy: backend error: %v", err)
		http.Error(w, `{"detail":"backend unavailable"}`, http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()

	// Przekaż nagłówki odpowiedzi z backendu do klienta
	for key, values := range resp.Header {
		for _, v := range values {
			w.Header().Add(key, v)
		}
	}

	// Przekaż status code i body odpowiedzi
	w.WriteHeader(resp.StatusCode)
	io.Copy(w, resp.Body)
}
