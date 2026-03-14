<template>
  <div class="onboarding-root">
    <div class="onboarding-container">
      <div class="onboarding-header">
        <h1 class="onboarding-title">Welcome to Fork!</h1>
        <p class="onboarding-subtitle">Let's set up your profile to get started</p>
      </div>

      <div class="progress-container">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <span class="progress-text">Step {{ currentStep }} of {{ totalSteps }}</span>
      </div>

      <!-- Step 1: Physical Information -->
      <StepPhysicalInformation
        v-if="currentStep === 1"
        :formData="formData"
        @update="updateField"
      />

      <!-- Step 2: Activity Level -->
      <StepActivityLevel v-if="currentStep === 2" :formData="formData" @update="updateField" />

      <!-- Step 3: Calorie Goals -->
      <StepCalorieGoals v-if="currentStep === 3" :formData="formData" @update="updateGoalField" />

      <!-- Step 4: Macro Goals -->
      <StepMacroGoals v-if="currentStep === 4" :formData="formData" @update="updateGoalField" />

      <!-- Navigation buttons -->
      <div class="navigation-buttons">
        <button
          class="nav-button nav-button-secondary"
          @click="previousStep"
          :disabled="currentStep === 1"
        >
          Back
        </button>
        <button class="nav-button nav-button-primary" @click="nextStep" :disabled="!canProceed">
          {{ isLastStep ? 'Complete Setup' : 'Continue' }}
        </button>
      </div>

      <button class="skip-button" @click="skipOnboarding">Skip for now</button>
    </div>

    <!-- Success modal -->
    <div class="modal-overlay" v-if="showSuccessModal">
      <div class="success-modal">
        <div class="success-icon">✓</div>
        <h2>Profile Setup Complete!</h2>
        <p>You're all set to start tracking your nutrition and fitness journey.</p>
        <button class="nav-button nav-button-primary" @click="goToToday">Go to Today</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import type { User, Goals } from '@/types/user'
import { getFormattedDateToday } from '@/helpers/utils'
import StepPhysicalInformation from '@/components/OnboardingSteps/StepPhysicalInformation.vue'
import StepActivityLevel from '@/components/OnboardingSteps/StepActivityLevel.vue'
import StepCalorieGoals from '@/components/OnboardingSteps/StepCalorieGoals.vue'
import StepMacroGoals from '@/components/OnboardingSteps/StepMacroGoals.vue'

const router = useRouter()

const currentStep = ref(1)
const totalSteps = ref(4)
const saving = ref(false)
const showSuccessModal = ref(false)

const formData = ref({
  weight: 0,
  height: 0,
  age: 0,
  gender: '',
  activity_level: '',
  goals: {
    daily_calorie_target: 0,
    daily_calorie_burn_target: 0,
    daily_protein_target: 0,
    daily_carbs_target: 0,
    daily_fat_target: 0,
  } as Goals,
})

const progress = computed(() => {
  return ((currentStep.value - 1) / (totalSteps.value - 1)) * 100
})

const isLastStep = computed(() => currentStep.value === totalSteps.value)

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 1:
      return (
        formData.value.weight > 0 &&
        formData.value.height > 0 &&
        formData.value.age > 0 &&
        formData.value.gender !== ''
      )
    case 2:
      return formData.value.activity_level !== ''
    case 3:
      return formData.value.goals.daily_calorie_target > 0
    case 4:
      return (
        formData.value.goals.daily_protein_target > 0 ||
        formData.value.goals.daily_carbs_target > 0 ||
        formData.value.goals.daily_fat_target > 0
      )
    default:
      return false
  }
})

const updateField = (field: string, value: string | number) => {
  if (field === 'gender') {
    formData.value.gender = value as string
  } else if (field === 'weight') {
    formData.value.weight = value as number
  } else if (field === 'height') {
    formData.value.height = value as number
  } else if (field === 'age') {
    formData.value.age = value as number
  } else if (field === 'activity_level') {
    formData.value.activity_level = value as string
  }
}

const updateGoalField = (field: string, value: number) => {
  formData.value.goals[field as keyof Goals] = value
}

const nextStep = async () => {
  if (currentStep.value < totalSteps.value) {
    currentStep.value++
  } else {
    await saveProfile()
  }
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const saveProfile = async () => {
  try {
    saving.value = true
    const user_local = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user_local || !user_local.user_id) {
      throw new Error('User not found in local storage')
    }

    const user_id = user_local.user_id

    const userData: Partial<User> = {
      weight: formData.value.weight,
      height: formData.value.height,
      age: formData.value.age,
      gender: formData.value.gender,
      activity_level: formData.value.activity_level,
      goals: formData.value.goals,
    }

    await fetchWrapper.patch(
      `/api/v1/user/${user_id}?weight_date_overwrite=${getFormattedDateToday()}`,
      userData,
    )
    showSuccessModal.value = true
  } catch (err) {
    console.error('Error saving profile:', err)
    alert('Failed to save profile. Please try again.')
  } finally {
    saving.value = false
  }
}

const skipOnboarding = () => {
  router.push('/today')
}

const goToToday = () => {
  router.push('/today')
}

// Load existing user data to pre-fill form
onMounted(async () => {
  try {
    const user_local = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user_local || !user_local.user_id) {
      throw new Error('User not found in local storage')
    }

    const user_id = user_local.user_id
    const user = await fetchWrapper.get(`/api/v1/user/${user_id}`)

    if (user) {
      formData.value = {
        weight: user.weight || 0,
        height: user.height || 0,
        age: user.age || 0,
        gender: user.gender || '',
        activity_level: user.activity_level || '',
        goals: {
          daily_calorie_target: user.goals?.daily_calorie_target || 0,
          daily_calorie_burn_target: user.goals?.daily_calorie_burn_target || 0,
          daily_protein_target: user.goals?.daily_protein_target || 0,
          daily_carbs_target: user.goals?.daily_carbs_target || 0,
          daily_fat_target: user.goals?.daily_fat_target || 0,
        },
      }
    }
  } catch (err) {
    console.error('Error loading user data:', err)
  }
})
</script>

<style scoped lang="css">
.onboarding-root {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--color-background-primary);
  padding: 1rem;
}

.onboarding-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 500px;
  background-color: var(--color-background-secondary);
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.onboarding-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.onboarding-title {
  font-size: 1.75rem;
  font-weight: bold;
  color: var(--color-text-primary);
  margin: 0 0 0.5rem 0;
}

.onboarding-subtitle {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background-color: var(--color-background-tertiary);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: var(--color-accent-secondary);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.navigation-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.nav-button {
  flex: 1;
  padding: 0.875rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition:
    background-color 0.2s,
    opacity 0.2s;
}

.nav-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-button-secondary {
  background-color: var(--color-background-tertiary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-accent-secondary);
}

.nav-button-secondary:not(:disabled):hover {
  opacity: 0.8;
}

.nav-button-primary {
  background-color: var(--color-accent-secondary);
  color: var(--color-text-primary);
}

.nav-button-primary:not(:disabled):hover {
  background-color: var(--color-accent-primary);
}

.skip-button {
  margin-top: 1rem;
  padding: 0.75rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  text-decoration: underline;
}

.skip-button:hover {
  color: var(--color-text-primary);
}

/* Success Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.success-modal {
  background-color: var(--color-background-secondary);
  border-radius: 1rem;
  padding: 2rem;
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.success-icon {
  width: 4rem;
  height: 4rem;
  margin: 0 auto 1rem;
  background-color: var(--color-accent-primary);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 2rem;
  color: white;
  font-weight: bold;
}

.success-modal h2 {
  font-size: 1.5rem;
  color: var(--color-text-primary);
  margin: 0 0 0.5rem 0;
}

.success-modal p {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin: 0 0 1.5rem 0;
}

@media (max-width: 480px) {
  .onboarding-root {
    padding: 0.5rem;
  }
  .onboarding-container {
    padding: 1rem;
  }

  .onboarding-title {
    font-size: 1.5rem;
  }

  .navigation-buttons {
    flex-direction: column;
  }
}
</style>
