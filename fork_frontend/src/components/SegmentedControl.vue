<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: string
  options: string[]
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

// Calculate the width and position based on the index of the selected option
const activeIndex = computed(() => props.options.indexOf(props.modelValue))

const sliderStyle = computed(() => ({
  width: `${100 / props.options.length}%`,
  transform: `translateX(${activeIndex.value * 100}%)`,
}))

const selectOption = (option: string) => {
  emit('update:modelValue', option)
}
</script>

<template>
  <div class="segmented-control">
    <!-- The sliding background highlight -->
    <div class="slider" :style="sliderStyle"></div>

    <!-- The actual buttons -->
    <button
      v-for="option in options"
      :key="option"
      type="button"
      class="option-button"
      :class="{ 'is-active': modelValue === option }"
      @click="selectOption(option)"
    >
      {{ option }}
    </button>
  </div>
</template>

<style scoped>
.segmented-control {
  position: relative;
  display: flex;
  align-items: center;
  background-color: var(--color-background-secondary);
  border: 1px solid var(--color-accent-secondary);
  border-radius: 0.5rem;
  padding: 0.25rem;
  user-select: none;
  width: 100%;
}

.slider {
  position: absolute;
  top: 0.25rem;
  bottom: 0.25rem;
  left: 0;
  z-index: 1;
  background-color: var(--color-background-tertiary);
  border-radius: calc(0.25rem - 2px);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.25s ease-out;
}

.option-button {
  position: relative;
  z-index: 2;
  flex: 1;
  background: none;
  border: none;
  padding: 8px 16px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: color 0.2s ease;
  outline: none;
  border-radius: 0.25rem;
}

.option-button.is-active {
  color: var(--color-text-primary);
}

/* Accessible focus states */
.option-button:focus-visible {
  box-shadow: 0 0 0 2px #3b82f6;
}
</style>
