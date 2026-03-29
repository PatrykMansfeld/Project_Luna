// Moduł API — funkcje komunikujące się z backendem FastAPI
// Wszystkie requesty idą przez /api, które Vite proxy przekierowuje na port 8000

const BASE = '/api' // Prefix proxy — Vite przepisuje go na http://127.0.0.1:8000

/**
 * Pobiera listę dostępnych person (np. Luna, Zori) z backendu.
 * Zwraca tablicę obiektów: { id, name, blurb }
 */
export async function fetchPersonas() {
  const res = await fetch(`${BASE}/personas`)
  if (!res.ok) throw new Error('Nie udało się pobrać person')
  const data = await res.json()
  return data.personas
}

/**
 * Wysyła wiadomość użytkownika do backendu i zwraca odpowiedź bota.
 * @param {string} sessionId  — identyfikator sesji rozmowy
 * @param {string} userMessage — treść wiadomości użytkownika
 * @param {string} personaId  — id wybranej persony (np. "Luna")
 * @returns {{ session_id, bot_name, reply }} — odpowiedź z backendu
 */
export async function sendMessage(sessionId, userMessage, personaId) {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      user_message: userMessage,
      persona_id: personaId,
    }),
  })
  if (!res.ok) throw new Error('Błąd wysyłania wiadomości')
  return res.json()
}

/**
 * Resetuje sesję rozmowy — czyści historię wiadomości na backendzie.
 * Wywoływane np. przy zmianie persony.
 */
export async function resetSession(sessionId) {
  const res = await fetch(`${BASE}/reset/${encodeURIComponent(sessionId)}`, {
    method: 'POST',
  })
  if (!res.ok) throw new Error('Błąd resetowania sesji')
  return res.json()
}
