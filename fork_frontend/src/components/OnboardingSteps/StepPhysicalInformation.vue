<template>
  <div class="step-container">
    <h2 class="step-title">Physical Information</h2>
    <p class="step-description">Tell us about your body metrics</p>

    <div class="form-section">
      <div class="form-group">
        <label for="weight">Weight (kg)</label>
        <div class="input-with-icon">
          <IconWeight class="input-icon"></IconWeight>
          <input
            id="weight"
            :value="formData.weight"
            @input="updateField('weight', ($event.target as HTMLInputElement).value)"
            type="number"
            min="1"
            max="500"
            step="0.1"
            placeholder="e.g., 70"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="height">Height (cm)</label>
        <div class="input-with-icon">
          <IconHeight class="input-icon"></IconHeight>
          <input
            id="height"
            :value="formData.height"
            @input="updateField('height', ($event.target as HTMLInputElement).value)"
            type="number"
            min="1"
            max="400"
            step="1"
            placeholder="e.g., 175"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="age">Age</label>
        <div class="input-with-icon">
          <IconAge class="input-icon"></IconAge>
          <input
            id="age"
            :value="formData.age"
            @input="updateField('age', ($event.target as HTMLInputElement).value)"
            type="number"
            min="1"
            max="200"
            step="1"
            placeholder="e.g., 30"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="gender">Gender</label>
        <div class="input-with-icon">
          <IconGender class="input-icon"></IconGender>
          <select
            id="gender"
            :value="formData.gender"
            @change="updateField('gender', ($event.target as HTMLSelectElement).value)"
          >
            <option value="" disabled>Select your gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import IconWeight from '@/components/icons/IconWeight.vue'
import IconHeight from '@/components/icons/IconHeight.vue'
import IconAge from '@/components/icons/IconAge.vue'
import IconGender from '@/components/icons/IconGender.vue'

interface FormData {
  weight: number
  height: number
  age: number
  gender: string
}

defineProps<{
  formData: FormData
}>()

const emit = defineEmits<{
  update: [field: string, value: string | number]
}>()

const updateField = (field: string, value: string) => {
  emit('update', field, field === 'gender' ? value : parseFloat(value) || 0)
}
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
</style>
