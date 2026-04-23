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
type Proxy struct {
	backendURL string
	client     *http.Client
}

// NewProxy tworzy nową instancję proxy wskazującą na podany adres backendu.
func NewProxy(backendURL string) *Proxy {
	return &Proxy{
		backendURL: strings.TrimRight(backendURL, "/"),
		client: &http.Client{
			Timeout: 120 * time.Second,
		},
	}
}

// Forward przekazuje request 1:1 do backendu Pythonowego.
func (p *Proxy) Forward(w http.ResponseWriter, r *http.Request) {
	p.proxyTo(w, r, r.URL.Path)
}

// ForwardReset obsługuje endpoint /reset/{sessionID}.
func (p *Proxy) ForwardReset(w http.ResponseWriter, r *http.Request) {
	sessionID := r.PathValue("sessionID")
	if sessionID == "" {
		http.Error(w, `{"detail":"missing session_id"}`, http.StatusBadRequest)
		return
	}
	p.proxyTo(w, r, "/reset/"+sessionID)
}

func (p *Proxy) proxyTo(w http.ResponseWriter, r *http.Request, path string) {
	targetURL := p.backendURL + path

	proxyReq, err := http.NewRequestWithContext(r.Context(), r.Method, targetURL, r.Body)
	if err != nil {
		log.Printf("proxy: error creating request: %v", err)
		http.Error(w, `{"detail":"internal proxy error"}`, http.StatusInternalServerError)
		return
	}

	for key, values := range r.Header {
		for _, v := range values {
			proxyReq.Header.Add(key, v)
		}
	}
	proxyReq.Header.Set("X-Forwarded-For", r.RemoteAddr)

	resp, err := p.client.Do(proxyReq)
	if err != nil {
		log.Printf("proxy: backend error: %v", err)
		http.Error(w, `{"detail":"backend unavailable"}`, http.StatusBadGateway)
		return
	}
	defer resp.Body.Close()

	for key, values := range resp.Header {
		for _, v := range values {
			w.Header().Add(key, v)
		}
	}
	w.WriteHeader(resp.StatusCode)

	// Flush after each chunk so SSE / streaming responses reach the client immediately.
	flusher, canFlush := w.(http.Flusher)
	buf := make([]byte, 4096)
	for {
		n, readErr := resp.Body.Read(buf)
		if n > 0 {
			w.Write(buf[:n]) //nolint:errcheck
			if canFlush {
				flusher.Flush()
			}
		}
		if readErr == io.EOF {
			break
		}
		if readErr != nil {
			log.Printf("proxy: stream read error: %v", readErr)
			break
		}
	}
}
