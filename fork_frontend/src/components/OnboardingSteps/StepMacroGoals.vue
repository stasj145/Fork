<template>
  <div class="step-container">
    <h2 class="step-title">Macronutrient Goals</h2>
    <p class="step-description">Set your daily macro targets (in grams)</p>

    <!-- Macro Suggestions Info Box -->
    <div class="info-box" v-if="hasPhysicalData && formData.goals.daily_calorie_target > 0">
      <div class="info-box-header">
        <IconInfo class="info-icon"></IconInfo>
        <span class="info-title">Suggested Macro Targets</span>
      </div>
      <div class="info-box-content">
        <div class="calculation-item">
          <span class="calculation-label">Protein:</span>
          <span class="calculation-value">{{ suggestedProtein }} g/day</span>
        </div>
        <div class="calculation-item">
          <span class="calculation-label">Fat:</span>
          <span class="calculation-value">{{ suggestedFat }} g/day</span>
        </div>
        <div class="calculation-item">
          <span class="calculation-label">Carbohydrates:</span>
          <span class="calculation-value">{{ suggestedCarbs }} g/day</span>
        </div>
        <p class="calculation-hint">
          Based on {{ weightBasedProtein }} g protein per kg body weight, 25% calories from fat, and
          remaining calories from carbs. Protein: 4 kcal/g, Carbs: 4 kcal/g, Fat: 9 kcal/g.
        </p>
      </div>
    </div>

    <div class="form-section">
      <div class="form-group">
        <label for="daily_protein_target">Daily Protein Target</label>
        <div class="input-with-icon">
          <IconProtein class="input-icon"></IconProtein>
          <input
            id="daily_protein_target"
            :value="formData.goals.daily_protein_target"
            @input="
              updateGoalField('daily_protein_target', ($event.target as HTMLInputElement).value)
            "
            type="number"
            min="0"
            max="1000"
            step="10"
            placeholder="e.g., 150"
          />
        </div>
        <div class="input-hint" v-if="hasPhysicalData">
          Suggested: {{ suggestedProtein }} g ({{ proteinPercentage }}% of calories)
        </div>
      </div>

      <div class="form-group">
        <label for="daily_carbs_target">Daily Carbohydrates Target</label>
        <div class="input-with-icon">
          <IconCarbs class="input-icon"></IconCarbs>
          <input
            id="daily_carbs_target"
            :value="formData.goals.daily_carbs_target"
            @input="
              updateGoalField('daily_carbs_target', ($event.target as HTMLInputElement).value)
            "
            type="number"
            min="0"
            max="1000"
            step="10"
            placeholder="e.g., 200"
          />
        </div>
        <div class="input-hint" v-if="hasPhysicalData && formData.goals.daily_calorie_target > 0">
          Suggested: {{ suggestedCarbs }} g ({{ carbsPercentage }}% of calories)
        </div>
      </div>

      <div class="form-group">
        <label for="daily_fat_target">Daily Fat Target</label>
        <div class="input-with-icon">
          <IconFat class="input-icon"></IconFat>
          <input
            id="daily_fat_target"
            :value="formData.goals.daily_fat_target"
            @input="updateGoalField('daily_fat_target', ($event.target as HTMLInputElement).value)"
            type="number"
            min="0"
            max="1000"
            step="10"
            placeholder="e.g., 70"
          />
        </div>
        <div class="input-hint" v-if="hasPhysicalData && formData.goals.daily_calorie_target > 0">
          Suggested: {{ suggestedFat }} g ({{ fatPercentage }}% of calories)
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import IconProtein from '@/components/icons/IconProtein.vue'
import IconCarbs from '@/components/icons/IconCarbs.vue'
import IconFat from '@/components/icons/IconFat.vue'
import IconInfo from '@/components/icons/IconInfo.vue'

interface Goals {
  daily_calorie_target: number
  daily_calorie_burn_target: number
  daily_protein_target: number
  daily_carbs_target: number
  daily_fat_target: number
}

interface FormData {
  weight: number
  height: number
  age: number
  gender: string
  activity_level: string
  goals: Goals
}

const props = defineProps<{
  formData: FormData
}>()

const emit = defineEmits<{
  update: [field: string, value: number]
}>()

const updateGoalField = (field: string, value: string) => {
  emit('update', field, parseFloat(value) || 0)
}

const hasPhysicalData = computed(() => {
  return (
    props.formData.weight > 0 &&
    props.formData.height > 0 &&
    props.formData.age > 0 &&
    props.formData.gender !== ''
  )
})

// Macro suggestions based on user data
// Protein: 1.5g per kg body weight
// Fat: 25% of total calories
// Carbs: remaining calories

const weightBasedProtein = 1.5 // g per kg body weight

const suggestedProtein = computed(() => {
  if (!hasPhysicalData.value) return 0
  return Math.round(props.formData.weight * weightBasedProtein)
})

const proteinCalories = computed(() => {
  return suggestedProtein.value * 4 // 4 kcal per gram of protein
})

const proteinPercentage = computed(() => {
  if (props.formData.goals.daily_calorie_target === 0) return 0
  return Math.round((proteinCalories.value / props.formData.goals.daily_calorie_target) * 100)
})

const suggestedFat = computed(() => {
  if (props.formData.goals.daily_calorie_target === 0) return 0
  const fatCalories = props.formData.goals.daily_calorie_target * 0.25 // 25% from fat
  return Math.round(fatCalories / 9) // 9 kcal per gram of fat
})

const fatPercentage = computed(() => {
  return 25
})

const suggestedCarbs = computed(() => {
  if (props.formData.goals.daily_calorie_target === 0) return 0
  const proteinCals = proteinCalories.value
  const fatCals = suggestedFat.value * 9
  const remainingCals = props.formData.goals.daily_calorie_target - proteinCals - fatCals
  return Math.round(remainingCals / 4) // 4 kcal per gram of carbs
})

const carbsPercentage = computed(() => {
  if (props.formData.goals.daily_calorie_target === 0) return 0
  const carbsCals = suggestedCarbs.value * 4
  return Math.round((carbsCals / props.formData.goals.daily_calorie_target) * 100)
})
</script>

<style scoped lang="css">
.step-container {
  flex: 1;
  margin-bottom: 1.5rem;
}

.step-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--color-text-primary);
  margin: 0 0 0.5rem 0;
}

.step-description {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0 0 1.5rem 0;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 0.75rem;
  width: 1.25rem;
  height: 1.25rem;
  color: var(--color-text-secondary);
  pointer-events: none;
}

.input-with-icon input,
.input-with-icon select {
  width: 100%;
  padding: 0.75rem 0.75rem 0.75rem 2.75rem;
  font-size: 1rem;
  color: var(--color-text-primary);
  background-color: var(--color-background-tertiary);
  border: 1px solid var(--color-accent-secondary);
  border-radius: 0.5rem;
  transition: border-color 0.2s;
}

.input-with-icon input:focus,
.input-with-icon select:focus {
  outline: none;
  border-color: var(--color-accent-primary);
}

.input-with-icon select {
  cursor: pointer;
}

/* Info Box for calculations */
.info-box {
  background-color: var(--color-background-tertiary);
  border: 1px solid var(--color-accent-secondary);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.info-box-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.info-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--color-accent-primary);
}

.info-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.info-box-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.calculation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-accent-secondary);
}

.calculation-item:last-child {
  border-bottom: none;
}

.calculation-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.calculation-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.calculation-hint {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px dashed var(--color-accent-secondary);
}

/* Input hint text */
.input-hint {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin-top: 0.25rem;
}
</style>
