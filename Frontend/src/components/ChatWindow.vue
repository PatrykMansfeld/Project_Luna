<script setup>
import { ref, nextTick, watch } from 'vue'

const props = defineProps({
  messages: { type: Array, required: true },   // Tablica wiadomości: [{ role, content }]
  loading: { type: Boolean, default: false },  // Czy bot aktualnie "pisze"
  botName: { type: String, default: 'Bot' },   // Nazwa bota do wyświetlenia
})

// Referencja do kontenera DOM — potrzebna do auto-scrolla
const container = ref(null)

// Przewija okno czatu na sam dół (po renderze nowej wiadomości)
function scrollToBottom() {
  nextTick(() => {
    if (container.value) {
      container.value.scrollTop = container.value.scrollHeight
    }
  })
}

// Watchery — scrolluj gdy zmieni się liczba wiadomości lub stan ładowania
watch(() => props.messages.length, scrollToBottom)
watch(() => props.loading, scrollToBottom)
</script>

<template>
  <!-- Kontener czatu — scrollowalny w pionie, zajmuje resztę dostępnej wysokości -->
  <div class="chat-window" ref="container">

    <!-- Stan pusty — widoczny gdy nie ma jeszcze żadnych wiadomości -->
    <div v-if="messages.length === 0 && !loading" class="chat-empty">
      <div class="empty-icon">💬</div>
      <p class="empty-title">Hej! Jestem <strong>{{ botName }}</strong></p>
      <p class="empty-hint">Napisz coś, żeby zacząć rozmowę</p>
    </div>

    <!-- Pętla po wiadomościach — każda jako wiersz z bąbelkiem -->
    <div
      v-for="(msg, i) in messages"
      :key="i"
      class="msg-row"
      :class="msg.role"
    >
      <!-- Awatar bota (kółko z pierwszą literą imienia) — tylko dla wiadomości bota -->
      <div class="msg-avatar" v-if="msg.role === 'assistant'">
        {{ botName[0] }}
      </div>
      <!-- Bąbelek z treścią wiadomości -->
      <div class="msg-bubble" :class="msg.role">
        <div class="msg-text">{{ msg.content }}</div>
      </div>
    </div>

    <!-- Animacja "pisze..." — widoczna gdy loading === true -->
    <div v-if="loading" class="msg-row assistant">
      <div class="msg-avatar">{{ botName[0] }}</div>
      <div class="msg-bubble assistant">
        <div class="typing">
          <span></span><span></span><span></span> <!-- Trzy pulsujące kropki -->
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-window {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: var(--bg);
  transition: background 0.25s ease;
}

/* empty state */
.chat-empty {
  margin: auto;
  text-align: center;
  padding: 2rem;
}
.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
}
.empty-title {
  font-size: 1.1rem;
  color: var(--text-h);
  margin-bottom: 0.3rem;
}
.empty-hint {
  font-size: 0.85rem;
  color: var(--text);
  opacity: 0.65;
}

/* message rows */
.msg-row {
  display: flex;
  align-items: flex-end;
  gap: 0.5rem;
  max-width: 80%;
  animation: fadeUp 0.2s ease;
}

.msg-row.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.msg-row.assistant {
  align-self: flex-start;
}

.msg-avatar {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  font-weight: 700;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-bottom: 0.15rem;
}

/* bubbles */
.msg-bubble {
  padding: 0.6rem 0.95rem;
  border-radius: var(--radius);
  line-height: 1.55;
  word-break: break-word;
  box-shadow: var(--shadow-sm);
  transition: background 0.25s ease, color 0.25s ease;
}

.msg-bubble.user {
  background: var(--bubble-user);
  color: var(--bubble-user-text);
  border-bottom-right-radius: 0.25rem;
}

.msg-bubble.assistant {
  background: var(--bubble-bot);
  color: var(--bubble-bot-text);
  border-bottom-left-radius: 0.25rem;
}

.msg-text {
  font-size: 0.92rem;
  white-space: pre-wrap;
}

/* typing animation */
.typing {
  display: flex;
  gap: 0.28rem;
  padding: 0.3rem 0.15rem;
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

@media (max-width: 600px) {
  .msg-row {
    max-width: 90%;
  }
}
</style>

@keyframes blink {
  0%, 80%, 100% { opacity: 0.4; transform: scale(1); }
  40% { opacity: 1; transform: scale(1.15); }
}
</style>
