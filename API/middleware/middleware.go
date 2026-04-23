// Package middleware zawiera middleware'y HTTP dla Go API gateway.
//
// Middleware'y owijają handler i wykonują logikę przed/po obsłudze requestu:
//   - CORS   — pozwala frontendowi na cross-origin requesty (np. z localhost:5173)
//   - Logger — loguje każdy request z metodą, ścieżką, statusem i czasem odpowiedzi
//
// Kolejność owijania ma znaczenie — request przechodzi przez nie od zewnątrz:
//
//	CORS → Logger → Handler (router)
package middleware

import (
	"log"
	"net/http"
	"time"
)

// CORS dodaje nagłówki Cross-Origin Resource Sharing do każdej odpowiedzi.
// Pozwala frontendowi (Vue na innym porcie) komunikować się z Go API.
//
// Dla preflight requestów (OPTIONS) — zwraca 204 No Content bez przekazywania
// do dalszych handlerów, bo przeglądarka potrzebuje tylko nagłówków.
//
// UWAGA: Allow-Origin "*" jest OK na dev, ale w produkcji warto zawęzić
// do konkretnego originu (np. "https://twoja-domena.pl").
func CORS(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Nagłówki CORS — przeglądarka sprawdza je przed wysłaniem requestu
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		// Preflight request — przeglądarka pyta "czy mogę wysłać POST z JSON?"
		// Odpowiadamy samymi nagłówkami, bez body
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}

		// Nie preflight — przekaż do następnego handlera
		next.ServeHTTP(w, r)
	})
}

// Logger loguje każdy przychodzący request z informacjami:
//   - Metoda HTTP (GET, POST, ...)
//   - Ścieżka URL (/chat, /personas, ...)
//   - Kod statusu odpowiedzi (200, 400, 502, ...)
//   - Czas obsługi requestu (np. 150ms)
//
// Przykład loga: POST /chat → 200 (1250ms)
func Logger(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()

		// Owijamy ResponseWriter żeby przechwycić status code
		// (standardowy ResponseWriter nie udostępnia go po zapisie)
		wrapped := &statusWriter{ResponseWriter: w, status: http.StatusOK}

		// Obsłuż request
		next.ServeHTTP(wrapped, r)

		// Zaloguj po zakończeniu obsługi
		log.Printf("%s %s → %d (%s)", r.Method, r.URL.Path, wrapped.status, time.Since(start).Round(time.Millisecond))
	})
}

// statusWriter opakowuje http.ResponseWriter i przechwytuje kod statusu.
// Standardowy ResponseWriter nie daje dostępu do statusu po wywołaniu
// WriteHeader(), więc musimy go zapamiętać sami do logowania.
type statusWriter struct {
	http.ResponseWriter
	status int // domyślnie 200 (ustawiane w Logger)
}

// WriteHeader przechwytuje kod statusu i przekazuje go dalej.
func (sw *statusWriter) WriteHeader(code int) {
	sw.status = code
	sw.ResponseWriter.WriteHeader(code)
}

// Flush przekazuje wywołanie Flush do opakowanego ResponseWriter (wymagane dla SSE / streamingu).
func (sw *statusWriter) Flush() {
	if f, ok := sw.ResponseWriter.(http.Flusher); ok {
		f.Flush()
	}
}
