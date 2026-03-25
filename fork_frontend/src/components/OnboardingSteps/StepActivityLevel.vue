<template>
  <div class="step-container">
    <h2 class="step-title">Activity Level</h2>
    <p class="step-description">How active are you on a daily basis?</p>

    <div class="form-section">
      <div class="form-group">
        <label for="activity_level">Activity Level</label>
        <div class="input-with-icon">
          <IconActivityLevel class="input-icon"></IconActivityLevel>
          <select
            id="activity_level"
            :value="formData.activity_level"
            @change="updateField('activity_level', ($event.target as HTMLSelectElement).value)"
          >
            <option value="" disabled>Select your activity level</option>
            <option value="sedentary">Sedentary</option>
            <option value="lightly_active">Lightly Active</option>
            <option value="moderately_active">Moderately Active</option>
            <option value="very_active">Very Active</option>
            <option value="super_active">Super Active</option>
          </select>
        </div>
      </div>

      <div class="activity-description">
        <details class="activity-details">
          <summary>What do these levels mean?</summary>
          <div class="activity-details-content">
            <p><strong>Sedentary (1.2):</strong> Little or no exercise, desk job</p>
            <p><strong>Lightly Active (1.375):</strong> Light exercise/sports 1-3 days/week</p>
            <p><strong>Moderately Active (1.55):</strong> Moderate exercise/sports 3-5 days/week</p>
            <p><strong>Very Active (1.725):</strong> Hard exercise/sports 6-7 days/week</p>
            <p>
              <strong>Super Active (1.9):</strong> Very hard exercise, physical job, or training
              twice a day
            </p>
          </div>
        </details>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import IconActivityLevel from '@/components/icons/IconActivityLevel.vue'
import type { UserUpdateRequest } from '@/types/api/user.types'

defineProps<{
  formData: UserUpdateRequest
}>()

const emit = defineEmits<{
  update: [field: keyof UserUpdateRequest, value: any]
}>()

const updateField = (field: keyof UserUpdateRequest, value: string) => {
  emit('update', field, value)
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

.activity-description {
  margin-top: 0.5rem;
}

.activity-details {
  background-color: var(--color-background-tertiary);
  border-radius: 0.5rem;
  padding: 0.75rem;
}

.activity-details summary {
  cursor: pointer;
  font-weight: 600;
  color: var(--color-text-primary);
  font-size: 0.875rem;
}

.activity-details-content {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-accent-secondary);
}

.activity-details-content p {
  margin: 0.5rem 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}
</style>
