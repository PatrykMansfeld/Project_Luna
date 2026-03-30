const BASE = '/api'

// Wspólny helper dla requestów do backendu, żeby nie powielać fetch i obsługi błędów.
async function request(path, options) {
  const response = await fetch(`${BASE}${path}`, options)
  if (!response.ok) {
    throw new Error(`Request failed: ${path}`)
  }

  return response.json()
}

// Persony zasilają pasek wyboru i sekcję aktywnej persony w App.vue.
export async function fetchPersonas() {
  const data = await request('/personas')
  return data.personas
}

// Główne wywołanie czatu; backend zwraca reply i ewentualnie nazwę aktywnego bota.
export function sendMessage(sessionId, userMessage, personaId) {
  return request('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      user_message: userMessage,
      persona_id: personaId,
    }),
  })
}

// Reset sesji czyści kontekst rozmowy przy zmianie persony.
export function resetSession(sessionId) {
  return request(`/reset/${encodeURIComponent(sessionId)}`, {
    method: 'POST',
  })
}
