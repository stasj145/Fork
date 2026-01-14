<template>
  <div class="meal-summary">
    <div class="summary-row">
      <div class="summary-item">
        <span class="summary-label">Weight</span>
        <span class="summary-value">{{ formattedWeight.toFixed(0) }} g</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">Calories</span>
        <span class="summary-value">{{ totalCalories.toFixed(0) }} kcal</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">Protein</span>
        <span class="summary-value">{{ totalProtein.toFixed(1) }} g</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">Carbs</span>
        <span class="summary-value">{{ totalCarbs.toFixed(1) }} g</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">Fat</span>
        <span class="summary-value">{{ totalFat.toFixed(1) }} g</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { FoodEntry } from '@/types/foodLog'

const props = defineProps<{
  mealEntries: FoodEntry[]
}>()

const formattedWeight = computed(() => {
  if (!props.mealEntries || props.mealEntries.length === 0) {
    return 0
  }

  const totalWeight = props.mealEntries.reduce((total, entry) => {
    return total + entry.quantity
  }, 0)

  return totalWeight
})

const totalCalories = computed(() => {
  if (!props.mealEntries || props.mealEntries.length === 0) {
    return 0
  }

  return props.mealEntries.reduce((total, entry) => {
    const calories = (entry.food_item.calories_per_100 * entry.quantity) / 100
    return total + calories
  }, 0)
})

const totalProtein = computed(() => {
  if (!props.mealEntries || props.mealEntries.length === 0) {
    return 0
  }

  return props.mealEntries.reduce((total, entry) => {
    const protein = (entry.food_item.protein_per_100 * entry.quantity) / 100
    return total + protein
  }, 0)
})

const totalCarbs = computed(() => {
  if (!props.mealEntries || props.mealEntries.length === 0) {
    return 0
  }

  return props.mealEntries.reduce((total, entry) => {
    const carbs = (entry.food_item.carbs_per_100 * entry.quantity) / 100
    return total + carbs
  }, 0)
})

const totalFat = computed(() => {
  if (!props.mealEntries || props.mealEntries.length === 0) {
    return 0
  }

  return props.mealEntries.reduce((total, entry) => {
    const fat = (entry.food_item.fat_per_100 * entry.quantity) / 100
    return total + fat
  }, 0)
})
</script>

<style lang="css" scoped>
.meal-summary {
  display: flex;
  flex-direction: column;
  width: 100%;
  background-color: var(--color-background-tertiary);
  border-radius: 0.5rem;
  padding: 0.5rem;
}

.summary-row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
}

.summary-label {
  font-size: 0.7rem;
  color: var(--color-text-secondary);
  text-align: center;
}

.summary-value {
  font-weight: bold;
  color: var(--color-text-primary);
  text-align: center;
}

@media (max-width: 480px) {
  .summary-label {
    font-size: 0.7rem;
    width: 60px;
  }

  .summary-value {
    font-size: 0.8rem;
  }
}
</style>
