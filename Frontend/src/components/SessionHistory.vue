<script setup>
const props = defineProps({
  sessions: { type: Array, default: () => [] },
  activeSessionId: { type: String, default: null },
  personas: { type: Array, default: () => [] },
})

const emit = defineEmits(['load'])

function personaName(personaId) {
  return props.personas.find((p) => p.id === personaId)?.name ?? personaId
}

function timeAgo(iso) {
  const diff = Date.now() - new Date(iso).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return 'przed chwilą'
  if (m < 60) return `${m} min temu`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h} h temu`
  return `${Math.floor(h / 24)} d temu`
}
</script>

<template>
  <div v-if="sessions.length" class="session-history">
    <p class="history-label">Poprzednie rozmowy</p>
    <ul class="session-list">
      <li
        v-for="s in sessions"
        :key="s.id"
        class="session-item"
        :class="{ active: s.id === activeSessionId }"
        @click="emit('load', s)"
      >
        <span class="session-persona">{{ personaName(s.persona_id) }}</span>
        <span class="session-meta">{{ s.message_count }} wiad. · {{ timeAgo(s.updated_at) }}</span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.session-history {
  padding: 0.75rem 1.25rem 0.85rem;
  border-bottom: 2px solid var(--border);
  background: var(--surface);
}

.history-label {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-soft);
  margin-bottom: 0.5rem;
}

.session-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.session-item {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  padding: 0.35rem 0.65rem;
  border: 2px solid var(--border);
  background: var(--surface-2);
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  transition: transform 0.1s, box-shadow 0.1s;
  min-width: 7rem;
}

.session-item:hover {
  transform: translate(-1px, -1px);
  box-shadow: var(--shadow);
}

.session-item.active {
  background: var(--accent);
  color: #000;
}

.session-persona {
  font-size: 0.8rem;
  font-weight: 700;
  color: inherit;
}

.session-item.active .session-persona {
  color: #000;
}

.session-meta {
  font-size: 0.68rem;
  color: var(--text-soft);
}

.session-item.active .session-meta {
  color: rgba(0, 0, 0, 0.6);
}

@media (max-width: 600px) {
  .session-history {
    padding-left: 1rem;
    padding-right: 1rem;
  }
}
</style>
