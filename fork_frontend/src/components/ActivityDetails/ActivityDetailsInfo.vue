<!-- eslint-disable vue/no-mutating-props  -->
<template>
  <div class="activity-details-info-root" v-if="selectedActivity">
    <div class="activity-info">
      <div class="activity-info-item">
        <label>Name</label>
        <input v-model="selectedActivity.name" :disabled="!isEditingMode" />
      </div>
      <div class="activity-info-item">
        <label>Calories per hour and kg</label>
        <input type="number" min="0" max="100" v-model="selectedActivity.calories_burned_kg_h" />
      </div>
      <div class="activity-info-item">
        <label>Calories/h at current weight ({{ user.weight_history[0]? user.weight_history[0].weight.toFixed(1) : 80 }}kg)</label>
        <span>{{ caloriesPerHourAtUserWeight }} </span>
      </div>
    </div>
  </div>
</template>

<!-- eslint-disable vue/no-mutating-props  -->
<script setup lang="ts">
import { computed, type PropType } from 'vue'
import type { Activity } from '@/types/activity'
import type { User } from '@/types/user'

const selectedActivity = defineModel<Activity | null>('selectedActivity')

const props = defineProps({
  isEditingMode: {
    type: Boolean,
    default: false,
  },
  user: {
    type: Object as PropType<User>,
    required: true,
  },
})

const caloriesPerHourAtUserWeight = computed(() => {
  if (!selectedActivity.value || !props.user.weight_history[0]) return 0
  return (selectedActivity.value.calories_burned_kg_h * props.user.weight_history[0].weight).toFixed(1)
})
</script>

<style lang="css" scoped>
.activity-details-info-root {
  display: flex;
  flex-direction: column;
  justify-content: start;
  align-items: start;
  width: calc(var(--main-content-width) - 1rem);
  max-width: 1200px;
  min-height: calc(var(--main-content-height) - 2rem);
  background-color: var(--color-background-secondary);
  border-radius: 0.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 0.5rem;
  padding-bottom: 5rem; /* padding for bottom buttons*/
}

.activity-info {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--color-accent-secondary);
  padding: 0.5rem;
  border-radius: 0.5rem;
  width: 100%;
}

.activity-info-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 0.5rem;
}
.activity-info-item label {
  position: relative;
  bottom: -0.4rem;
  color: var(--color-text-primary);
  font-size: 1rem;
  font-weight: bold;
  margin-left: 0.5rem;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
  background-color: var(--color-background-secondary);
  width: fit-content;
  margin-top: -0.4rem;
}

.activity-info-item input,
.activity-info-item span {
  color: var(--color-text-primary);
  border: 1px solid var(--color-accent-secondary);
  padding: 0.5rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.3s;
}

@media (max-width: 480px) {
  .activity-details-info-root {
    min-height: calc(var(--main-content-height) - 1rem);
    padding-bottom: 4rem;
  }
}
</style>
