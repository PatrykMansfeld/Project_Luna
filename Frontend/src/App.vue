<script setup>
import { ref, onMounted } from 'vue'
import PersonaSelector from './components/PersonaSelector.vue' // Pasek wyboru persony
import ChatWindow from './components/ChatWindow.vue'           // Okno z wiadomościami
import ChatInput from './components/ChatInput.vue'             // Pole do wpisywania wiadomości
import { fetchPersonas, sendMessage, resetSession } from './api.js' // Funkcje API

// --- Stan reaktywny aplikacji ---
const personas = ref([])          // Lista person pobranych z backendu
const selectedPersona = ref(null) // ID aktualnie wybranej persony
const messages = ref([])          // Tablica wiadomości: { role: 'user'|'assistant', content: '...' }
const loading = ref(false)        // Flaga — czy czekamy na odpowiedź bota
const botName = ref('Bot')        // Wyświetlana nazwa bota (np. "Luna")
const error = ref('')             // Komunikat błędu (pusty = brak błędu)

// Sprawdza localStorage, a jeśli brak — ustawienia systemowe
const dark = ref(
  localStorage.getItem('theme') === 'dark' ||
  (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)
)

// Dodaje/usuwa klasę "dark" z <html> i zapisuje wybór w localStorage
function applyTheme() {
  document.documentElement.classList.toggle('dark', dark.value)
  localStorage.setItem('theme', dark.value ? 'dark' : 'light')
}
applyTheme() // Ustaw motyw od razu przy załadowaniu

// Przełącza motyw jasny ↔ ciemny
function toggleDark() {
  dark.value = !dark.value
  applyTheme()
}

// --- Sesja ---
// Unikalny identyfikator sesji — generowany raz przy załadowaniu strony
const sessionId = `s-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`

// --- Inicjalizacja — pobierz persony z backendu po zamontowaniu komponentu ---
onMounted(async () => {
  try {
    personas.value = await fetchPersonas()
    if (personas.value.length) {
      selectedPersona.value = personas.value[0].id  // Domyślnie wybierz pierwszą personę
      botName.value = personas.value[0].name
    }
  } catch (e) {
    error.value = 'Nie udało się połączyć z serwerem.'
  }
})

// Zmiana persony — czyści historię czatu i resetuje sesję na backendzie
async function selectPersona(id) {
  if (id === selectedPersona.value) return // Już wybrana — nic nie rób
  selectedPersona.value = id
  const p = personas.value.find((x) => x.id === id)
  botName.value = p?.name ?? 'Bot'
  messages.value = [] // Czyści widoczne wiadomości
  try {
    await resetSession(sessionId) // Czyści historię na backendzie
  } catch {
    // ignore — jeśli reset się nie uda, nic złego się nie stanie
  }
}

// Wysyłanie wiadomości — dodaje do czatu, wysyła do backendu, dodaje odpowiedź
async function handleSend(text) {
  messages.value.push({ role: 'user', content: text }) // Dodaj wiadomość usera do czatu
  loading.value = true  // Pokaż animację "pisze..."
  error.value = ''      // Wyczyść poprzedni błąd

  try {
    const data = await sendMessage(sessionId, text, selectedPersona.value)
    botName.value = data.bot_name
    messages.value.push({ role: 'assistant', content: data.reply }) // Dodaj odpowiedź bota
  } catch {
    error.value = 'Błąd — sprawdź czy backend i Ollama działają.'
  } finally {
    loading.value = false // Wyłącz animację ładowania
  }
}
</script>

<template>
  <!-- Główny kontener aplikacji — flex column na pełną wysokość ekranu -->
  <div class="app-shell">

    <!-- HEADER — logo, tytuł i przycisk zmiany motywu -->
    <header class="app-header">
      <div class="header-left"></div> <!-- Pusty div dla wyrównania flexem (3 kolumny) -->
      <div class="header-center">
        <span class="app-logo">🌙</span>
        <h1 class="app-title">Project Luna</h1>
      </div>
      <div class="header-right">
        <!-- Przycisk przełączania dark/light mode -->
        <button class="theme-toggle" @click="toggleDark" :title="dark ? 'Tryb jasny' : 'Tryb ciemny'">
          <svg v-if="dark" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
          </svg>
          <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        </button>
      </div>
    </header>

    <!-- PASEK PERSON — przyciski do wyboru osobowości bota -->
    <PersonaSelector
      :personas="personas"
      :selected="selectedPersona"
      @select="selectPersona"
    />

    <!-- OKNO CZATU — lista wiadomości + animacja "pisze..." -->
    <ChatWindow
      :messages="messages"
      :loading="loading"
      :bot-name="botName"
    />

    <!-- KOMUNIKAT BŁĘDU — widoczny tylko gdy error nie jest pusty -->
    <div v-if="error" class="app-error">{{ error }}</div>

    <!-- POLE WEJŚCIOWE — formularz z inputem i przyciskiem wyślij -->
    <ChatInput :disabled="loading" @send="handleSend" />
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  max-width: 50rem;
  margin: 0 auto;
  background: var(--bg);
  transition: background 0.25s ease;
}

@media (min-width: 50rem) {
  .app-shell {
    border-left: 1px solid var(--border);
    border-right: 1px solid var(--border);
  }
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 1rem;
  border-bottom: 1px solid var(--border);
  background: var(--bg-secondary);
  transition: background 0.25s ease;
}

.header-left,
.header-right {
  width: 2.5rem;
  flex-shrink: 0;
}

.header-center {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  justify-content: center;
}

.app-logo {
  font-size: 1.2rem;
  line-height: 1;
}

.app-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-h);
  letter-spacing: -0.3px;
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.2rem;
  height: 2.2rem;
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  background: transparent;
  color: var(--text);
  cursor: pointer;
  transition: all 0.2s;
}
.theme-toggle:hover {
  background: var(--accent-bg);
  border-color: var(--accent-border);
  color: var(--accent);
}

.app-error {
  padding: 0.5rem 1rem;
  margin: 0 1rem;
  font-size: 0.8rem;
  color: #ef4444;
  background: rgba(239, 68, 68, 0.08);
  border-radius: 0.5rem;
  text-align: center;
}
</style>
