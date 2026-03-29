<script setup>
import { ref } from 'vue'

// Props od rodzica — blokuje input gdy bot generuje odpowiedź
defineProps({
  disabled: { type: Boolean, default: false },
})
// Event emitowany do rodzica z treścią wiadomości
const emit = defineEmits(['send'])

// Treść wpisana w input (reaktywna, powiązana przez v-model)
const text = ref('')

// Obsługa wysłania — walidacja, emit eventu, czyszczenie pola
function submit() {
  const msg = text.value.trim()
  if (!msg) return        // Nie wysyłaj pustych wiadomości
  emit('send', msg)       // Przekaż tekst do App.vue
  text.value = ''         // Wyczyść pole po wysłaniu
}
</script>

<template>
  <!-- Formularz — submit.prevent zapobiega przeładowaniu strony -->
  <form class="chat-input" @submit.prevent="submit">
    <!-- Wrapper łączący input i przycisk w jedną „kapsułę" -->
    <div class="input-wrap">
      <input
        v-model="text"
        type="text"
        placeholder="Napisz wiadomość…"
        :disabled="disabled"
        autocomplete="off"
        maxlength="8000"
      />
      <!-- Przycisk wyślij — nieaktywny gdy pole puste lub trwa ładowanie -->
      <button type="submit" :disabled="disabled || !text.trim()" title="Wyślij">
        <!-- Ikona „wyślij" (SVG papierowy samolot) -->
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"/>
          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
        </svg>
      </button>
    </div>
  </form>
</template>

<style scoped>
.chat-input {
  padding: 0.6rem 1rem 0.75rem;
  border-top: 1px solid var(--border);
  background: var(--bg-secondary);
  transition: background 0.25s ease;
}

.input-wrap {
  display: flex;
  gap: 0.45rem;
  align-items: center;
  background: var(--input-bg);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 0.25rem 0.3rem 0.25rem 1rem;
  transition: border-color 0.2s, background 0.25s, box-shadow 0.2s;
}

.input-wrap:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-bg);
}

.input-wrap input {
  flex: 1;
  padding: 0.5rem 0;
  border: none;
  background: transparent;
  color: var(--text-h);
  font: inherit;
  font-size: 0.92rem;
  outline: none;
}

.input-wrap input::placeholder {
  color: var(--text);
  opacity: 0.5;
}

.input-wrap button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.2rem;
  height: 2.2rem;
  border: none;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  cursor: pointer;
  transition: background 0.2s, opacity 0.2s;
  flex-shrink: 0;
}

.input-wrap button:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.input-wrap button:not(:disabled):hover {
  background: var(--accent-hover);
}
</style>
