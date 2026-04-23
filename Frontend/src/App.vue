<script setup>
import { computed, onMounted, ref } from 'vue'
import { fetchPersonas, fetchSessions, fetchSessionMessages, resetSession, sendMessage } from './api.js'
import ChatInput from './components/ChatInput.vue'
import ChatWindow from './components/ChatWindow.vue'
import PersonaSelector from './components/PersonaSelector.vue'
import SessionHistory from './components/SessionHistory.vue'

const THEME_KEY = 'theme'
const SESSION_KEY = 'sessionId'
const DEFAULT_BOT_NAME = 'Bot'

const personas = ref([])
const selectedPersona = ref(null)
const messages = ref([])
const loading = ref(false)
const botName = ref(DEFAULT_BOT_NAME)
const error = ref('')
const dark = ref(getInitialTheme())
const sessions = ref([])
const sessionId = ref(getOrCreateSessionId())

const activePersona = computed(
  () => personas.value.find((persona) => persona.id === selectedPersona.value) ?? null,
)

setTheme(dark.value)
onMounted(async () => {
  await loadPersonas()
  await loadSessions()
})

function getOrCreateSessionId() {
  const stored = localStorage.getItem(SESSION_KEY)
  if (stored) return stored
  const id = `s-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
  localStorage.setItem(SESSION_KEY, id)
  return id
}

function getInitialTheme() {
  const saved = localStorage.getItem(THEME_KEY)
  if (saved) return saved === 'dark'
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

function setTheme(value) {
  dark.value = value
  document.documentElement.classList.toggle('dark', value)
  localStorage.setItem(THEME_KEY, value ? 'dark' : 'light')
}

function toggleDark() {
  setTheme(!dark.value)
}

function syncSelectedPersona(id) {
  selectedPersona.value = id
  botName.value = personas.value.find((persona) => persona.id === id)?.name ?? DEFAULT_BOT_NAME
}

function errorMessage(err) {
  if (err.type === 'network') return 'Brak połączenia z serwerem.'
  if (err.type === 'server') return 'Błąd serwera — sprawdź czy Ollama działa.'
  return 'Coś poszło nie tak. Spróbuj ponownie.'
}

async function loadPersonas() {
  try {
    personas.value = await fetchPersonas()
    const storedPersona = sessions.value.find((s) => s.id === sessionId.value)?.persona_id
    const firstPersona = personas.value[0]?.id
    syncSelectedPersona(storedPersona ?? firstPersona ?? null)
  } catch (err) {
    error.value = errorMessage(err)
  }
}

async function loadSessions() {
  try {
    sessions.value = await fetchSessions()
  } catch {
    // session history is non-critical — silently ignore
  }
}

async function selectPersona(id) {
  if (id === selectedPersona.value) return

  syncSelectedPersona(id)
  messages.value = []

  try {
    await resetSession(sessionId.value)
  } catch {
    // Ignore session reset failures and let the next message recreate context.
  }
}

async function restoreSession(session) {
  try {
    const data = await fetchSessionMessages(session.id)
    sessionId.value = session.id
    localStorage.setItem(SESSION_KEY, session.id)
    messages.value = data.messages
    syncSelectedPersona(session.persona_id)
  } catch (err) {
    error.value = errorMessage(err)
  }
}

async function handleSend(text) {
  if (!selectedPersona.value) return

  messages.value.push({ role: 'user', content: text })
  loading.value = true
  error.value = ''

  try {
    const data = await sendMessage(sessionId.value, text, selectedPersona.value)
    botName.value = data.bot_name || botName.value
    messages.value.push({ role: 'assistant', content: data.reply })
    await loadSessions()
  } catch (err) {
    error.value = errorMessage(err)
    messages.value.pop()
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <div class="brand-block">
        <div class="brand-mark">L</div>
        <div class="brand-copy">
          <p class="brand-kicker">Moonlit conversational studio</p>
          <h1 class="app-title">Project Luna</h1>
        </div>
      </div>

      <button
        class="theme-toggle"
        :aria-label="dark ? 'Włącz jasny motyw' : 'Włącz ciemny motyw'"
        :title="dark ? 'Tryb jasny' : 'Tryb ciemny'"
        @click="toggleDark"
      >
          <svg v-if="dark" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
          </svg>
          <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
      </button>
    </header>

    <section class="persona-stage">
      <div class="persona-copy">
        <p class="section-label">Aktywna persona</p>
        <div class="persona-heading">
          <h2 class="persona-name">{{ activePersona?.name || 'Łączenie z biblioteką person' }}</h2>
          <span class="status-pill">
            <span class="status-dot"></span>
            {{ activePersona ? 'Gotowa do rozmowy' : 'Ładowanie' }}
          </span>
        </div>
        <p class="persona-blurb">
          {{ activePersona?.blurb || 'Wybierz styl rozmowy i rozpocznij konwersację w kilku kliknięciach.' }}
        </p>
      </div>

      <PersonaSelector
        :personas="personas"
        :selected="selectedPersona"
        @select="selectPersona"
      />
    </section>

    <SessionHistory
      :sessions="sessions"
      :active-session-id="sessionId"
      :personas="personas"
      @load="restoreSession"
    />

    <ChatWindow
      :messages="messages"
      :loading="loading"
      :bot-name="botName"
    />

    <div v-if="error" class="app-error">{{ error }}</div>

    <ChatInput :disabled="loading || !selectedPersona" @send="handleSend" />
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
  max-width: min(58rem, calc(100vw - 2rem));
  margin: 0 auto;
  background: var(--surface);
  border: 2px solid var(--border);
  box-shadow: var(--shadow-lg);
}

@media (min-width: 56rem) {
  .app-shell {
    min-height: calc(100dvh - 2.5rem);
    margin: 1.25rem auto;
  }
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-bottom: 2px solid var(--border);
  background: var(--header-bg);
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 0.9rem;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  background: #000;
  color: var(--accent);
  font-family: var(--display);
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  border: 2px solid #000;
  box-shadow: var(--shadow-sm);
}

.brand-copy {
  display: grid;
  gap: 0.1rem;
}

.brand-kicker {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--header-text-soft);
}

.app-title {
  font-family: var(--display);
  font-size: clamp(1.2rem, 2vw, 1.5rem);
  font-weight: 800;
  color: var(--header-text);
  letter-spacing: -0.03em;
  line-height: 1;
  text-transform: uppercase;
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.75rem;
  height: 2.75rem;
  border: 2px solid #000;
  background: #000;
  color: var(--accent);
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  transition: transform 0.12s, box-shadow 0.12s;
}

.theme-toggle:hover {
  transform: translate(-2px, -2px);
  box-shadow: 4px 4px 0px #000;
}

.theme-toggle:active {
  transform: translate(0, 0);
  box-shadow: none;
}

.persona-stage {
  display: grid;
  gap: 0.85rem;
  padding: 1rem 1.25rem 1.15rem;
  border-bottom: 2px solid var(--border);
  background: var(--surface-2);
}

.persona-copy {
  display: grid;
  gap: 0.3rem;
}

.section-label {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-soft);
}

.persona-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.persona-name {
  font-family: var(--display);
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--text-h);
  letter-spacing: -0.02em;
}

.persona-blurb {
  max-width: 38rem;
  font-size: 0.92rem;
  color: var(--text-soft);
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.7rem;
  border: 2px solid var(--border);
  background: var(--accent);
  color: #000;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  box-shadow: var(--shadow-sm);
}

.status-dot {
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 50%;
  background: #000;
}

.app-error {
  margin: 0 1.25rem 0.75rem;
  padding: 0.75rem 1rem;
  border: 2px solid #cc0000;
  background: rgba(204, 0, 0, 0.07);
  color: #cc0000;
  font-size: 0.85rem;
  font-weight: 600;
  box-shadow: var(--shadow-sm);
}

@media (max-width: 640px) {
  .app-shell {
    max-width: 100vw;
    border-left: none;
    border-right: none;
  }

  .app-header,
  .persona-stage {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .brand-mark {
    width: 2.5rem;
    height: 2.5rem;
  }
}
</style>
