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
          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
        </svg>
      </button>
    </div>
  </form>
</template>

<style scoped>
.chat-input {
  padding: 0.9rem 1.25rem 1.25rem;
  border-top: 2px solid var(--border);
  background: var(--surface-2);
}

.input-wrap {
  display: flex;
  gap: 0.6rem;
  align-items: center;
  background: var(--surface);
  border: 2px solid var(--border);
  padding: 0.3rem 0.35rem 0.3rem 1rem;
  box-shadow: var(--shadow-sm);
  transition: transform 0.12s, box-shadow 0.12s;
}

.input-wrap:focus-within {
  box-shadow: var(--shadow);
  transform: translate(-1px, -1px);
}

.input-wrap input {
  flex: 1;
  min-height: 2.7rem;
  padding: 0.5rem 0;
  border: none;
  background: transparent;
  color: var(--text-h);
  font: inherit;
  font-size: 0.95rem;
  outline: none;
}

.input-wrap input::placeholder {
  color: var(--text-soft);
}

.input-wrap button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.7rem;
  height: 2.7rem;
  border: 2px solid var(--border);
  background: var(--accent);
  color: #000;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  transition: transform 0.12s, box-shadow 0.12s, opacity 0.15s;
  flex-shrink: 0;
}

.input-wrap button:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.input-wrap button:not(:disabled):hover {
  transform: translate(-2px, -2px);
  box-shadow: 4px 4px 0px var(--border);
}

.input-wrap button:not(:disabled):active {
  transform: translate(0, 0);
  box-shadow: none;
}

@media (max-width: 600px) {
  .chat-input {
    padding-left: 1rem;
    padding-right: 1rem;
  }
}
</style>
