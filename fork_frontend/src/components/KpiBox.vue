<template>
  <div class="kpi-box-root">
    <span class="kpi-title">{{ title }}</span>
    <span class="kpi-value">{{ value }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps({
  title: {
    type: String,
    required: true,
  },
  value: {
    type: String,
    required: true,
  },
})
</script>

<style lang="css" scoped>
.kpi-box-root {
  height: 100%;
  width: 100%;
  background-color: inherit;
  border: none;
  border-radius: 0.5rem;
  box-shadow: 0 0px 5px rgba(0, 0, 0, 0.3);

  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.5rem;
  justify-content: center;
  align-items: center;
}

.kpi-title {
  font-size: 1rem;
  color: var(--color-text-secondary);
}
.kpi-value {
  font-size: 1.5rem;
  color: var(--color-text-primary);
  font-weight: bold;
}
</style>
