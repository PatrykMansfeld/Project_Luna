<script setup>
import { computed, onMounted, ref } from 'vue'
import { fetchPersonas, resetSession, sendMessage } from './api.js'
import ChatInput from './components/ChatInput.vue'
import ChatWindow from './components/ChatWindow.vue'
import PersonaSelector from './components/PersonaSelector.vue'

// Stałe współdzielone tylko przez główny kontener aplikacji.
const THEME_KEY = 'theme'
const DEFAULT_BOT_NAME = 'Bot'

// Główny stan widoku: aktywna persona, historia rozmowy, status requestu i motyw.
const personas = ref([])
const selectedPersona = ref(null)
const messages = ref([])
const loading = ref(false)
const botName = ref(DEFAULT_BOT_NAME)
const error = ref('')
const dark = ref(getInitialTheme())
const sessionId = `s-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
const activePersona = computed(
  () => personas.value.find((persona) => persona.id === selectedPersona.value) ?? null,
)

// Najpierw synchronizujemy motyw z dokumentem, potem pobieramy persony z API.
setTheme(dark.value)
onMounted(loadPersonas)

// Kolejność źródeł motywu: localStorage, a na końcu preferencja systemowa.
function getInitialTheme() {
  const savedTheme = localStorage.getItem(THEME_KEY)
  if (savedTheme) {
    return savedTheme === 'dark'
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

// Jedno miejsce do przełączania motywu i zapisu ustawienia użytkownika.
function setTheme(value) {
  dark.value = value
  document.documentElement.classList.toggle('dark', value)
  localStorage.setItem(THEME_KEY, value ? 'dark' : 'light')
}

function toggleDark() {
  setTheme(!dark.value)
}

// Aktualizuje zaznaczenie i nazwę aktywnego bota widoczną w UI.
function syncSelectedPersona(id) {
  selectedPersona.value = id
  botName.value = personas.value.find((persona) => persona.id === id)?.name ?? DEFAULT_BOT_NAME
}

// Inicjalizacja aplikacji: pobranie person i wybór pierwszej dostępnej.
async function loadPersonas() {
  try {
    personas.value = await fetchPersonas()
    if (personas.value[0]) {
      syncSelectedPersona(personas.value[0].id)
    }
  } catch {
    error.value = 'Nie udało się połączyć z serwerem.'
  }
}

// Zmiana persony czyści lokalny czat i resetuje kontekst po stronie backendu.
async function selectPersona(id) {
  if (id === selectedPersona.value) {
    return
  }

  syncSelectedPersona(id)
  messages.value = []

  try {
    await resetSession(sessionId)
  } catch {
    // Ignore session reset failures and let the next message recreate context.
  }
}

// Wiadomość trafia najpierw do UI, a potem do API, żeby interfejs reagował od razu.
async function handleSend(text) {
  if (!selectedPersona.value) {
    return
  }

  messages.value.push({ role: 'user', content: text })
  loading.value = true
  error.value = ''

  try {
    const data = await sendMessage(sessionId, text, selectedPersona.value)
    botName.value = data.bot_name || botName.value
    messages.value.push({ role: 'assistant', content: data.reply })
  } catch {
    error.value = 'Błąd — sprawdź czy backend i Ollama działają.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="app-shell">
    <!-- Górny pasek z brandingiem aplikacji i przełącznikiem motywu. -->
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

    <!-- Sekcja aktywnej persony i lista chipów do szybkiego przełączania. -->
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

    <!-- Główne okno rozmowy renderuje historię wiadomości i stan "pisania". -->
    <ChatWindow
      :messages="messages"
      :loading="loading"
      :bot-name="botName"
    />

    <!-- Komunikat błędu trzymamy blisko inputa, żeby był widoczny przy ponownej próbie. -->
    <div v-if="error" class="app-error">{{ error }}</div>

    <!-- Pole jest blokowane podczas requestu albo zanim wybierze się persona. -->
    <ChatInput :disabled="loading || !selectedPersona" @send="handleSend" />
  </div>
</template>

<style scoped>
/* Główna karta aplikacji na tle strony. */
.app-shell {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
  max-width: min(58rem, calc(100vw - 1rem));
  margin: 0 auto;
  overflow: hidden;
  background: var(--surface);
  border: 1px solid var(--shell-border);
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(24px);
  transition: background 0.25s ease, border-color 0.25s ease;
  isolation: isolate;
}

.app-shell::before {
  content: '';
  position: absolute;
  top: -5rem;
  right: -4rem;
  width: 16rem;
  height: 16rem;
  border-radius: 50%;
  background: radial-gradient(circle, var(--glow-b) 0%, transparent 72%);
  filter: blur(8px);
  pointer-events: none;
}

.app-shell > * {
  position: relative;
  z-index: 1;
}

/* Na desktopie karta ma oddech od krawędzi okna i większe zaokrąglenie. */
@media (min-width: 56rem) {
  .app-shell {
    min-height: calc(100dvh - 2.5rem);
    margin: 1.25rem auto;
    border-radius: 1.75rem;
  }
}

/* Header odpowiada wyłącznie za branding i akcję zmiany motywu. */
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.15rem 1.25rem 1rem;
  border-bottom: 1px solid var(--border);
  background: linear-gradient(180deg, var(--surface-strong), transparent);
  transition: background 0.25s ease, border-color 0.25s ease;
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
  border-radius: 1rem;
  background: linear-gradient(135deg, #f8d9a4 0%, #8ab9ff 100%);
  color: #162033;
  font-family: var(--display);
  font-size: 1.35rem;
  font-weight: 700;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.55), 0 12px 28px rgba(30, 52, 86, 0.18);
}

.brand-copy {
  display: grid;
  gap: 0.2rem;
}

.brand-kicker {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--text-soft);
}

.app-title {
  font-family: var(--display);
  font-size: clamp(1.35rem, 2vw, 1.8rem);
  font-weight: 600;
  color: var(--text-h);
  letter-spacing: -0.04em;
  line-height: 1;
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.75rem;
  height: 2.75rem;
  border: 1px solid var(--shell-border);
  border-radius: 0.9rem;
  background: var(--surface-strong);
  color: var(--text);
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.theme-toggle:hover {
  background: var(--accent-bg);
  border-color: var(--accent-border);
  color: var(--accent);
  transform: translateY(-1px);
}

/* Ta sekcja łączy opis aktywnej persony i pasek wyboru. */
.persona-stage {
  display: grid;
  gap: 0.95rem;
  padding: 1rem 1.25rem 1.15rem;
  border-bottom: 1px solid var(--border);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.14), transparent);
}

.persona-copy {
  display: grid;
  gap: 0.35rem;
}

.section-label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.16em;
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
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-h);
  letter-spacing: -0.03em;
}

.persona-blurb {
  max-width: 38rem;
  font-size: 0.95rem;
  color: var(--text-soft);
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.42rem 0.8rem;
  border-radius: 999px;
  border: 1px solid var(--accent-border);
  background: var(--accent-bg);
  color: var(--accent);
  font-size: 0.8rem;
  font-weight: 700;
}

.status-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 0 0.25rem var(--accent-bg);
}

/* Jedno miejsce na komunikaty błędu z backendu lub problemów z połączeniem. */
.app-error {
  margin: 0 1.25rem 0.75rem;
  padding: 0.8rem 1rem;
  border: 1px solid rgba(239, 68, 68, 0.18);
  border-radius: 1rem;
  background: rgba(239, 68, 68, 0.08);
  color: #ef4444;
  font-size: 0.85rem;
  text-align: left;
  box-shadow: var(--shadow-sm);
}

/* Na telefonach redukujemy marginesy, ale nie zmieniamy układu sekcji. */
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
    width: 2.7rem;
    height: 2.7rem;
  }
}
</style>
