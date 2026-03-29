// Package main — punkt startowy Go API gateway.
// Gateway przyjmuje requesty od frontendu (Vue) i przekazuje je
// do backendu Pythonowego (FastAPI), który komunikuje się z Ollamą.
//
// Architektura:  Vue (:5173) → Go API (:3000) → FastAPI (:8000) → Ollama
//
// Zmienne środowiskowe:
//
//	BACKEND_URL — adres backendu FastAPI (domyślnie http://127.0.0.1:8000)
//	API_ADDR    — adres nasłuchu Go API  (domyślnie :3000)
package main

import (
	"log"
	"net/http"
	"os"

	"project-luna/api/handler"
	"project-luna/api/middleware"
)

func main() {
	// Odczytaj konfigurację ze zmiennych środowiskowych (lub użyj domyślnych)
	backendURL := envOrDefault("BACKEND_URL", "http://127.0.0.1:8000")
	listenAddr := envOrDefault("API_ADDR", ":3000")

	// Nowy multiplexer — router HTTP ze standardowej biblioteki Go 1.22+
	mux := http.NewServeMux()

	// Proxy — instancja odpowiedzialna za przekazywanie requestów do FastAPI
	proxy := handler.NewProxy(backendURL)

	// --- Rejestracja endpointów (mapują 1:1 do FastAPI) ---

	// GET /ollama   — sprawdza status połączenia z Ollamą (model, URL)
	mux.HandleFunc("GET /ollama", proxy.Forward)

	// GET /personas — zwraca listę dostępnych person (Luna, Zori, ...)
	mux.HandleFunc("GET /personas", proxy.Forward)

	// POST /chat    — wysyła wiadomość użytkownika i zwraca odpowiedź bota
	mux.HandleFunc("POST /chat", proxy.Forward)

	// POST /reset/{sessionID} — resetuje historię rozmowy danej sesji
	mux.HandleFunc("POST /reset/{sessionID}", proxy.ForwardReset)

	// GET /health   — health check samego Go API (nie trafia do backendu)
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(`{"status":"ok","service":"go-api-gateway"}`))
	})

	// Owijamy router middleware'ami:
	// 1. Logger  — loguje każdy request (metoda, ścieżka, status, czas)
	// 2. CORS    — dodaje nagłówki pozwalające na cross-origin requesty z frontu
	wrapped := middleware.CORS(middleware.Logger(mux))

	// Uruchom serwer HTTP
	log.Printf("Go API gateway listening on %s — proxying to %s", listenAddr, backendURL)
	if err := http.ListenAndServe(listenAddr, wrapped); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}

// envOrDefault zwraca wartość zmiennej środowiskowej lub fallback,
// jeśli zmienna nie istnieje lub jest pusta.
func envOrDefault(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
