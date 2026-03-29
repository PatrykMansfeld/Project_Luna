<script setup>
// Props przyjmowane od rodzica (App.vue)
defineProps({
  personas: { type: Array, required: true },  // Lista person: [{ id, name, blurb }]
  selected: { type: String, default: null },  // ID aktualnie wybranej persony
})
// Event emitowany do rodzica po kliknięciu persony
const emit = defineEmits(['select'])
</script>

<template>
  <!-- Kontener z przyciskami person, scrollowalny horyzontalnie -->
  <div class="persona-bar">
    <!-- Pojedynczy przycisk persony (chip) -->
    <button
      v-for="p in personas"
      :key="p.id"
      class="persona-chip"
      :class="{ active: selected === p.id }"
      @click="emit('select', p.id)"
      :title="p.blurb"
    >
      <span class="chip-avatar">{{ p.name[0] }}</span> <!-- Awatar — pierwsza litera imienia -->
      <span class="chip-name">{{ p.name }}</span>       <!-- Pełne imię persony -->
    </button>
  </div>
</template>

<style scoped>
.persona-bar {
  display: flex;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  border-bottom: 1px solid var(--border);
  background: var(--bg-secondary);
  overflow-x: auto;
  transition: background 0.25s ease;
}

.persona-chip {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.85rem 0.35rem 0.35rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: transparent;
  color: var(--text);
  cursor: pointer;
  font: inherit;
  font-size: 0.82rem;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.persona-chip:hover {
  border-color: var(--accent-border);
  background: var(--accent-bg);
  color: var(--text-h);
}

.persona-chip.active {
  border-color: var(--accent);
  background: var(--accent-bg);
  color: var(--accent);
  font-weight: 600;
}

.chip-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.55rem;
  height: 1.55rem;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  font-weight: 700;
  font-size: 0.7rem;
  flex-shrink: 0;
  transition: background 0.2s;
}

.persona-chip.active .chip-avatar {
  background: var(--accent);
  box-shadow: 0 0 0 2px var(--accent-bg);
}
</style>
