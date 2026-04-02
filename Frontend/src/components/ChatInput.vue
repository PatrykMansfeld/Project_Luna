<script setup>
import { ref } from 'vue'

defineProps({
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['send'])

const text = ref('')

function submit() {
  const message = text.value.trim()
  if (!message) {
    return
  }

  emit('send', message)
  text.value = ''
}
</script>

<template>
  <form class="chat-input" @submit.prevent="submit">
    <div class="input-wrap">
      <input
        v-model="text"
        type="text"
        placeholder="Napisz wiadomość…"
        :disabled="disabled"
        autocomplete="off"
        maxlength="8000"
      />
      <button type="submit" :disabled="disabled || !text.trim()" title="Wyślij">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"/>
          // The original line above is replaced with a polygon to create a filled paper plane icon.
          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
        </svg>
      </button>
    </div>
  </form>
</template>

<style scoped>
.chat-input {
  padding: 0.9rem 1.25rem 1.25rem;
  border-top: 1px solid var(--border);
  background: linear-gradient(180deg, transparent, var(--bg-secondary) 28%);
  transition: background 0.25s ease, border-color 0.25s ease;
}

.input-wrap {
  display: flex;
  gap: 0.6rem;
  align-items: center;
  background: var(--input-bg);
  border: 1px solid var(--shell-border);
  border-radius: 0.4rem;
  padding: 0.35rem 0.4rem 0.35rem 1.1rem;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.25s ease, box-shadow 0.2s ease;
}

.input-wrap:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-bg), var(--shadow-sm);
  transform: translateY(-1px);
}

.input-wrap input {
  flex: 1;
  min-height: 2.85rem;
  padding: 0.55rem 0;
  border: none;
  background: transparent;
  color: var(--text-h);
  font: inherit;
  font-size: 0.95rem;
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
  width: 2.85rem;
  height: 2.85rem;
  border: none;
  border-radius: 0.25rem;
  background: var(--brand-gradient);
  color: var(--brand-text);
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
  transition: transform 0.2s ease, filter 0.2s ease, opacity 0.2s ease;
  flex-shrink: 0;
}

.input-wrap button:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.input-wrap button:not(:disabled):hover {
  filter: brightness(1.05);
  transform: translateY(-1px);
}

@media (max-width: 600px) {
  .chat-input {
    padding-left: 1rem;
    padding-right: 1rem;
  }
}
</style>
