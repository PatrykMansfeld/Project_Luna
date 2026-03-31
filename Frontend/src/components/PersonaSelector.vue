<script setup>
defineProps({
  personas: { type: Array, required: true },
  selected: { type: String, default: null },
})
const emit = defineEmits(['select'])
</script>

<template>
  <div class="persona-bar">
    <button
      v-for="p in personas"
      :key="p.id"
      class="persona-chip"
      :class="{ active: selected === p.id }"
      @click="emit('select', p.id)"
      :title="p.blurb"
    >
      <span class="chip-avatar">{{ p.name.charAt(0) }}</span>
      <span class="chip-name">{{ p.name }}</span>
    </button>
  </div>
</template>

<style scoped>
.persona-bar {
  display: flex;
  gap: 0.65rem;
  overflow-x: auto;
  padding-bottom: 0.15rem;
  scrollbar-width: none;
}

.persona-bar::-webkit-scrollbar {
  display: none;
}

.persona-chip {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  min-height: 3.1rem;
  padding: 0.5rem 1rem 0.5rem 0.45rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface-strong);
  color: var(--text);
  cursor: pointer;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease, color 0.2s ease;
}

.persona-chip:hover {
  transform: translateY(-1px);
  border-color: var(--accent-border);
  background: var(--accent-bg);
  color: var(--text-h);
}

.persona-chip.active {
  border-color: var(--accent);
  background: linear-gradient(135deg, var(--accent-bg), transparent 85%), var(--surface-strong);
  color: var(--text-h);
  font-weight: 600;
}

.chip-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%);
  color: #fff;
  font-weight: 700;
  font-size: 0.78rem;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.chip-name {
  letter-spacing: -0.02em;
}

.persona-chip.active .chip-avatar {
  box-shadow: 0 0 0 0.3rem var(--accent-bg);
  transform: scale(1.02);
}
</style>
