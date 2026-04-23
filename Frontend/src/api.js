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

export async function sendMessage(sessionId, userMessage, personaId, { onToken, onDone }) {
  let response
  try {
    response = await fetch(`${BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        user_message: userMessage,
        persona_id: personaId,
      }),
    })
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

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop()

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      try {
        const data = JSON.parse(line.slice(6))
        if (data.type === 'token') {
          onToken(data.content)
        } else if (data.type === 'done') {
          onDone(data)
        } else if (data.type === 'error') {
          const err = new Error(data.detail)
          err.type = 'server'
          throw err
        }
      } catch (parseErr) {
        if (parseErr.type) throw parseErr
      }
    }
  }
}

export function resetSession(sessionId) {
  return request(`/reset/${encodeURIComponent(sessionId)}`, {
    method: 'POST',
  })
}
