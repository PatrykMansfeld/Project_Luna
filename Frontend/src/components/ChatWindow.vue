<script setup>
import { computed, nextTick, ref, watch } from 'vue'

// Komponent dostaje cały stan czatu z App.vue; lokalnie pilnuje tylko auto-scrolla.
const props = defineProps({
  messages: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  botName: { type: String, default: 'Bot' },
})

const container = ref(null)
// Awatar bota składamy z pierwszej litery, żeby nie duplikować logiki w template.
const botInitial = computed(() => props.botName.charAt(0).toUpperCase() || 'B')

// Po dopisaniu wiadomości albo zmianie loadingu przewijamy okno na dół.
function scrollToBottom() {
  nextTick(() => {
    const element = container.value
    if (element) {
      element.scrollTop = element.scrollHeight
    }
  })
}

watch([() => props.messages.length, () => props.loading], scrollToBottom)
</script>

<template>
  <!-- Przewijalny obszar rozmowy: pusty stan, wiadomości i wskaźnik pisania. -->
  <div class="chat-window" ref="container">
    <div v-if="messages.length === 0 && !loading" class="chat-empty">
      <div class="empty-orb">{{ botInitial }}</div>
      <p class="empty-label">Kanał gotowy</p>
      <p class="empty-title">Porozmawiaj z <strong>{{ botName }}</strong></p>
      <p class="empty-hint">Wybierz personę powyżej i wyślij pierwszą wiadomość, żeby uruchomić konwersację.</p>
    </div>

    <!-- Wspólny układ wiadomości; rola steruje pozycją i wariantem bąbelka. -->
    <div
      v-for="(msg, i) in messages"
      :key="i"
      class="msg-row"
      :class="msg.role"
    >
      <div class="msg-avatar" v-if="msg.role === 'assistant'">
        {{ botInitial }}
      </div>
      <div class="msg-bubble" :class="msg.role">
        <div class="msg-text">{{ msg.content }}</div>
      </div>
    </div>

    <!-- Osobny blok, więc animację pisania można podmienić bez ruszania listy wiadomości. -->
    <div v-if="loading" class="msg-row assistant">
      <div class="msg-avatar">{{ botInitial }}</div>
      <div class="msg-bubble assistant">
        <div class="typing">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-window {
  position: relative;
  flex: 1;
  overflow-y: auto;
  padding: 1.4rem 1.25rem 1.6rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  background: linear-gradient(180deg, transparent, rgba(255, 255, 255, 0.05));
  transition: background 0.25s ease;
}

/* Środkowa, przewijalna część layoutu z historią rozmowy. */
.chat-empty {
  margin: auto;
  text-align: center;
  width: min(100%, 28rem);
  padding: 2.25rem 1.5rem;
  border: 1px solid var(--shell-border);
  border-radius: 1.75rem;
  background: var(--surface-strong);
  box-shadow: var(--shadow-sm);
}

.empty-orb {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 4.25rem;
  height: 4.25rem;
  margin-bottom: 1rem;
  border-radius: 1.4rem;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%);
  color: #fff;
  font-family: var(--display);
  font-size: 1.7rem;
  font-weight: 700;
  box-shadow: 0 18px 40px rgba(18, 41, 74, 0.18);
}

.empty-label {
  margin-bottom: 0.45rem;
  font-size: 0.73rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--text-soft);
}

.empty-title {
  font-size: 1.35rem;
  color: var(--text-h);
  letter-spacing: -0.03em;
  margin-bottom: 0.45rem;
}

.empty-hint {
  font-size: 0.92rem;
  color: var(--text-soft);
}

.msg-row {
  display: flex;
  align-items: flex-end;
  gap: 0.65rem;
  max-width: min(82%, 38rem);
  animation: fadeUp 0.28s cubic-bezier(0.16, 1, 0.3, 1);
}

.msg-row.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.msg-row.assistant {
  align-self: flex-start;
}

.msg-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  border: 1px solid var(--shell-border);
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%);
  color: #fff;
  font-weight: 700;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-bottom: 0.15rem;
  box-shadow: var(--shadow-sm);
}

.msg-bubble {
  padding: 0.8rem 1rem;
  border: 1px solid transparent;
  border-radius: 1.3rem;
  line-height: 1.6;
  word-break: break-word;
  box-shadow: var(--shadow-sm);
  transition: background 0.25s ease, color 0.25s ease, border-color 0.25s ease;
}

.msg-bubble.user {
  background: var(--bubble-user);
  color: var(--bubble-user-text);
  border-bottom-right-radius: 0.4rem;
}

.msg-bubble.assistant {
  background: var(--bubble-bot);
  color: var(--bubble-bot-text);
  border-color: var(--border);
  backdrop-filter: blur(14px);
  border-bottom-left-radius: 0.4rem;
}

.msg-text {
  font-size: 0.95rem;
  white-space: pre-wrap;
}

.typing {
  display: flex;
  gap: 0.3rem;
  padding: 0.35rem 0.2rem;
}

.typing span {
  width: 0.42rem;
  height: 0.42rem;
  border-radius: 50%;
  background: var(--accent);
  opacity: 0.35;
  animation: pulse 1.2s infinite;
}
.typing span:nth-child(2) { animation-delay: 0.15s; }
.typing span:nth-child(3) { animation-delay: 0.3s; }

@keyframes pulse {
  0%, 80%, 100% { opacity: 0.35; transform: scale(1); }
  40% { opacity: 1; transform: scale(1.2); }
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Mobilnie pozwalamy wiadomościom zająć trochę więcej szerokości. */
@media (max-width: 600px) {
  .msg-row {
    max-width: 92%;
  }

  .chat-window {
    padding-left: 1rem;
    padding-right: 1rem;
  }
}
</style>
