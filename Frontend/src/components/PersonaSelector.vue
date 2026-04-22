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
  gap: 0.6rem;
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
  gap: 0.55rem;
  min-height: 2.85rem;
  padding: 0.45rem 0.9rem 0.45rem 0.4rem;
  border: 2px solid var(--border);
  background: var(--surface);
  color: var(--text);
  cursor: pointer;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  white-space: nowrap;
  box-shadow: var(--shadow-sm);
  transition: transform 0.12s, box-shadow 0.12s;
}

.persona-chip:hover {
  transform: translate(-2px, -2px);
  box-shadow: 4px 4px 0px var(--border);
}

.persona-chip:active {
  transform: translate(0, 0);
  box-shadow: none;
}

.persona-chip.active {
  background: var(--accent);
  color: #000;
}

.chip-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.9rem;
  height: 1.9rem;
  background: #000;
  color: var(--accent);
  font-family: var(--display);
  font-weight: 800;
  font-size: 0.78rem;
  flex-shrink: 0;
}

.chip-name {
  letter-spacing: -0.01em;
}
</style>
