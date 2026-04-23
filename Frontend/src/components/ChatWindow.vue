<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { marked } from 'marked'

marked.setOptions({ breaks: true, gfm: true })

const props = defineProps({
  messages: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  botName: { type: String, default: 'Bot' },
})

const container = ref(null)
const botInitial = computed(() => props.botName.charAt(0).toUpperCase() || 'B')
const lastContent = computed(() => props.messages[props.messages.length - 1]?.content ?? '')

function renderMarkdown(content) {
  return marked.parse(content)
}

function scrollToBottom() {
  nextTick(() => {
    if (container.value) {
      container.value.scrollTop = container.value.scrollHeight
    }
  })
}

watch([() => props.messages.length, () => props.loading, lastContent], scrollToBottom)
</script>

<template>
  <div class="chat-window" ref="container">
    <div v-if="messages.length === 0 && !loading" class="chat-empty">
      <div class="empty-orb">{{ botInitial }}</div>
      <p class="empty-label">Kanał gotowy</p>
      <p class="empty-title">Porozmawiaj z <strong>{{ botName }}</strong></p>
      <p class="empty-hint">Wybierz personę powyżej i wyślij pierwszą wiadomość, żeby uruchomić konwersację.</p>
    </div>

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
        <div v-if="msg.role === 'assistant' && msg.streaming && !msg.content" class="typing">
          <span></span><span></span><span></span>
        </div>
        <div
          v-else-if="msg.role === 'assistant'"
          class="msg-text md"
          v-html="renderMarkdown(msg.content)"
        ></div>
        <div v-else class="msg-text">{{ msg.content }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-window {
  flex: 1;
  overflow-y: auto;
  padding: 1.4rem 1.25rem 1.6rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  background: var(--surface);
}

.chat-empty {
  margin: auto;
  text-align: center;
  width: min(100%, 26rem);
  padding: 2rem 1.5rem;
  border: 2px solid var(--border);
  background: var(--surface-2);
  box-shadow: var(--shadow);
}

.empty-orb {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 4rem;
  height: 4rem;
  margin-bottom: 1rem;
  background: var(--accent);
  color: #000;
  font-family: var(--display);
  font-size: 1.7rem;
  font-weight: 800;
  border: 2px solid var(--border);
  box-shadow: var(--shadow-sm);
}

.empty-label {
  margin-bottom: 0.4rem;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-soft);
}

.empty-title {
  font-family: var(--display);
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--text-h);
  letter-spacing: -0.02em;
  margin-bottom: 0.5rem;
}

.empty-hint {
  font-size: 0.9rem;
  color: var(--text-soft);
}

.msg-row {
  display: flex;
  align-items: flex-end;
  gap: 0.6rem;
  max-width: min(84%, 38rem);
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
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--border);
  background: var(--accent);
  color: #000;
  font-family: var(--display);
  font-weight: 800;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-bottom: 0.1rem;
  box-shadow: var(--shadow-sm);
}

.msg-bubble {
  padding: 0.75rem 1rem;
  border: 2px solid var(--border);
  line-height: 1.65;
  word-break: break-word;
  box-shadow: var(--shadow-sm);
}

.msg-bubble.user {
  background: var(--accent-2);
  color: #fff;
}

.msg-bubble.assistant {
  background: var(--surface);
  color: var(--text);
}

.msg-text {
  font-size: 0.95rem;
  white-space: pre-wrap;
}

/* Markdown rendered content */
.msg-text.md {
  white-space: normal;
}

.msg-text.md :deep(p) { margin: 0 0 0.5em; }
.msg-text.md :deep(p:last-child) { margin-bottom: 0; }
.msg-text.md :deep(ul),
.msg-text.md :deep(ol) { margin: 0.4em 0; padding-left: 1.4em; }
.msg-text.md :deep(li) { margin-bottom: 0.2em; }
.msg-text.md :deep(code) {
  font-family: monospace;
  font-size: 0.88em;
  background: var(--surface-2);
  border: 1px solid var(--border);
  padding: 0.1em 0.35em;
}
.msg-text.md :deep(pre) {
  margin: 0.6em 0;
  padding: 0.75em 1em;
  background: var(--surface-2);
  border: 2px solid var(--border);
  overflow-x: auto;
}
.msg-text.md :deep(pre code) {
  background: none;
  border: none;
  padding: 0;
  font-size: 0.85em;
}
.msg-text.md :deep(strong) { font-weight: 700; }
.msg-text.md :deep(em) { font-style: italic; }
.msg-text.md :deep(blockquote) {
  border-left: 3px solid var(--border);
  margin: 0.5em 0;
  padding-left: 0.75em;
  color: var(--text-soft);
}

.typing {
  display: flex;
  gap: 0.3rem;
  padding: 0.3rem 0.2rem;
}

.typing span {
  width: 0.4rem;
  height: 0.4rem;
  border-radius: 50%;
  background: var(--text);
  opacity: 0.4;
  animation: pulse 1.2s infinite;
}
.typing span:nth-child(2) { animation-delay: 0.15s; }
.typing span:nth-child(3) { animation-delay: 0.3s; }

@keyframes pulse {
  0%, 80%, 100% { opacity: 0.4; transform: scale(1); }
  40% { opacity: 1; transform: scale(1.2); }
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}

@media (max-width: 600px) {
  .msg-row { max-width: 92%; }
  .chat-window { padding-left: 1rem; padding-right: 1rem; }
}
</style>
