const BASE = '/api'

async function request(path, options) {
  const response = await fetch(`${BASE}${path}`, options)
  if (!response.ok) {
    throw new Error(`Request failed: ${path}`)
  }

  return response.json()
}

export async function fetchPersonas() {
  const data = await request('/personas')
  return data.personas
}

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

export function resetSession(sessionId) {
  return request(`/reset/${encodeURIComponent(sessionId)}`, {
    method: 'POST',
  })
}
