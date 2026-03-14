<template>
  <div class="step-container">
    <h2 class="step-title">Calorie Goals</h2>
    <p class="step-description">Set your daily calorie targets</p>

    <div class="info-box" v-if="hasPhysicalData">
      <div class="info-box-header">
        <IconInfo class="info-icon"></IconInfo>
        <span class="info-title">Your Calculated Values</span>
      </div>
      <div class="info-box-content">
        <div class="calculation-item">
          <span class="calculation-label">BMI (Body Mass Index):</span>
          <span class="calculation-value"
            >{{ bmi }} <span class="bmi-category">{{ bmiCategory }}</span></span
          >
        </div>
        <div class="calculation-item">
          <span class="calculation-label">BMR (Basal Metabolic Rate):</span>
          <span class="calculation-value">{{ bmr }} kcal/day</span>
        </div>
        <div class="calculation-item">
          <span class="calculation-label">TDEE (Total Daily Energy Expenditure):</span>
          <span class="calculation-value">{{ tdee }} kcal/day</span>
        </div>
        <div class="calculation-item">
          <span class="calculation-label">Estimated Weekly Weight Change:</span>
          <span class="calculation-value" :class="weightChangeClass">
            {{ weeklyWeightChangeDisplay }}
          </span>
        </div>
        <p class="calculation-hint">
          Your TDEE is the number of calories you burn per day based on your activity level. To lose
          weight, consume fewer calories than your TDEE. To gain weight, consume more. Estimated
          weight change based on 7,700 kcal ≈ 1 kg of body fat.
        </p>
      </div>
    </div>

    <div class="form-section">
      <div class="form-group">
        <label for="daily_calorie_target">Daily Calorie Target</label>
        <div class="input-with-icon">
          <IconCalorie class="input-icon"></IconCalorie>
          <input
            id="daily_calorie_target"
            :value="formData.goals.daily_calorie_target"
            @input="
              updateGoalField('daily_calorie_target', ($event.target as HTMLInputElement).value)
            "
            type="number"
            min="0"
            max="10000"
            step="50"
            placeholder="e.g., 2000"
          />
        </div>
        <div class="input-hint" v-if="tdee > 0">
          Suggested: {{ tdee }} kcal (maintenance) | {{ tdee - 500 }} kcal (weight loss) |
          {{ tdee + 500 }} kcal (weight gain)
        </div>
      </div>

      <div class="form-group">
        <label for="daily_calorie_burn_target">Daily Active Calorie Burn Target</label>
        <div class="input-with-icon">
          <IconActiveCalories class="input-icon"></IconActiveCalories>
          <input
            id="daily_calorie_burn_target"
            :value="formData.goals.daily_calorie_burn_target"
            @input="
              updateGoalField(
                'daily_calorie_burn_target',
                ($event.target as HTMLInputElement).value,
              )
            "
            type="number"
            min="0"
            max="10000"
            step="50"
            placeholder="e.g., 500"
          />
        </div>
        <div class="input-hint">Target calories to burn through exercise daily</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import IconCalorie from '@/components/icons/IconCalorie.vue'
import IconActiveCalories from '@/components/icons/IconActiveCalories.vue'
import IconInfo from '@/components/icons/IconInfo.vue'

interface Goals {
  daily_calorie_target: number
  daily_calorie_burn_target: number
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

// Activity level multipliers for TDEE calculation
const activityMultipliers: Record<string, number> = {
  sedentary: 1.2,
  lightly_active: 1.375,
  moderately_active: 1.55,
  very_active: 1.725,
  super_active: 1.9,
}

const hasPhysicalData = computed(() => {
  return (
    props.formData.weight > 0 &&
    props.formData.height > 0 &&
    props.formData.age > 0 &&
    props.formData.gender !== ''
  )
})

// Calculate BMI (Body Mass Index)
// Formula: weight (kg) / (height (m))^2
const bmi = computed(() => {
  if (!hasPhysicalData.value) return 0
  const heightInMeters = props.formData.height / 100
  return (props.formData.weight / (heightInMeters * heightInMeters)).toFixed(1)
})

const bmiCategory = computed(() => {
  const bmiValue = parseFloat(bmi.value as string)
  if (bmiValue === 0) return ''
  if (bmiValue < 15) return '(Critically Underweight)'
  if (bmiValue < 18.5) return '(Underweight)'
  if (bmiValue < 25) return '(Normal)'
  if (bmiValue < 30) return '(Overweight)'
  if (bmiValue < 35) return '(Class 1 Obesity)'
  if (bmiValue < 40) return '(Class 2 Obesity)'
  return '(Class 3 Obesity)'
})

// Calculate BMR (Basal Metabolic Rate) using Mifflin-St Jeor Equation
// Men: (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) + 5
// Women: (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) - 161
const bmr = computed(() => {
  if (!hasPhysicalData.value) return 0
  let baseBmr = 10 * props.formData.weight + 6.25 * props.formData.height - 5 * props.formData.age
  if (props.formData.gender === 'male') {
    baseBmr += 5
  } else {
    baseBmr -= 161
  }
  return Math.round(baseBmr)
})

// Calculate TDEE (Total Daily Energy Expenditure)
// TDEE = BMR × Activity Level Multiplier
const tdee = computed(() => {
  if (bmr.value === 0 || !props.formData.activity_level) return 0
  const multiplier = activityMultipliers[props.formData.activity_level as string] || 1.2
  return Math.round(bmr.value * multiplier)
})

// Calculate weekly weight change based on calorie deficit/surplus
// 1 kg of body fat ≈ 7700 kcal
const CALORIES_PER_KG_FAT = 7700

const weeklyWeightChange = computed(() => {
  if (tdee.value === 0 || props.formData.goals.daily_calorie_target === 0) return 0
  const totalDailyBurn = tdee.value
  const dailyDeficit = totalDailyBurn - props.formData.goals.daily_calorie_target
  const weeklyDeficit = dailyDeficit * 7
  return weeklyDeficit / CALORIES_PER_KG_FAT
})

const weeklyWeightChangeDisplay = computed(() => {
  const change = weeklyWeightChange.value
  const sign = change > 0 ? '' : '+'
  return `${sign}${(change * -1).toFixed(2)} kg/week`
})

const weightChangeClass = computed(() => {
  const change = weeklyWeightChange.value
  if (change > 0.5) return 'weight-gain'
  if (change < -0.5) return 'weight-loss'
  if (change > 0) return 'weight-gain-slight'
  if (change < 0) return 'weight-loss-slight'
  return ''
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

.bmi-category {
  font-weight: normal;
  color: var(--color-text-secondary);
  margin-left: 0.25rem;
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

/* Weight change color classes */
.weight-loss {
  color: #ef4444 !important;
}

.weight-loss-slight {
  color: #f97316 !important;
}

.weight-gain {
  color: #22c55e !important;
}

.weight-gain-slight {
  color: #84cc16 !important;
}

@media (max-width: 480px) {
  .calculation-item {
    flex-direction: column;
    align-items: start;
    gap: 0.25rem;
  }
}
</style>
