const BASE = '/api'

async function request(path, options) {
  let response
  try {
    response = await fetch(`${BASE}${path}`, options)
  } catch {
    const err = new Error('Brak połączenia z serwerem.')
    err.type = 'network'
    throw err
  }
  if (!response.ok) {
    const err = new Error(`HTTP ${response.status}`)
    err.type = response.status >= 500 ? 'server' : 'client'
    err.status = response.status
    throw err
  }
  return response.json()
}

export async function fetchPersonas() {
  const data = await request('/personas')
  return data.personas
}

export async function fetchSessions() {
  const data = await request('/sessions')
  return data.sessions
}

export async function fetchSessionMessages(sessionId) {
  return request(`/sessions/${encodeURIComponent(sessionId)}/messages`)
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
