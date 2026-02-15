<template>
  <div class="profile-root">
    <div class="profile-loading-spinner" v-if="loading">
      <Spinner></Spinner>
    </div>
    <div class="user-information-root" v-if="!loading && user">
      <WeightHistoryModal
        v-if="showWeightHistoryModal"
        v-model="showWeightHistoryModal"
        :initial-weight-history="user.weight_history"
        @save="saveWeightHistory"
      ></WeightHistoryModal>
      <div class="user-base-info">
        <div class="user-info-item-with-icon">
          <IconName class="icon"></IconName>
          <div class="user-info-item">
            <label>Name</label>
            <input v-model="user.username" :disabled="!isEditing" />
          </div>
        </div>
        <div class="user-info-item-with-icon">
          <IconEmail class="icon"></IconEmail>
          <div class="user-info-item">
            <label>E-Mail address</label>
            <input v-model="user.email" type="email" :disabled="!isEditing" />
          </div>
        </div>
      </div>
      <div class="user-goal-info">
        <div class="user-info-item-with-icon">
          <IconCalorie class="icon"></IconCalorie>
          <div class="user-info-item">
            <label>Daily calorie target</label>
            <input
              v-model="user.goals.daily_calorie_target"
              type="number"
              min="0"
              max="10000"
              step="50"
              :disabled="!isEditing"
            />
          </div>
        </div>
        <div class="user-info-item-with-icon">
          <IconActiveCalories class="icon"></IconActiveCalories>
          <div class="user-info-item">
            <label>Daily active calorie burn target</label>
            <input
              v-model="user.goals.daily_calorie_burn_target"
              type="number"
              min="0"
              max="10000"
              step="50"
              :disabled="!isEditing"
            />
          </div>
        </div>

        <div class="user-info-item-with-icon">
          <IconProtein class="icon"></IconProtein>
          <div class="user-info-item">
            <label>Daily protein target</label>
            <input
              v-model="user.goals.daily_protein_target"
              type="number"
              min="0"
              max="1000"
              step="10"
              :disabled="!isEditing"
            />
          </div>
        </div>
        <div class="user-info-item-with-icon">
          <IconCarbs class="icon"></IconCarbs>
          <div class="user-info-item">
            <label>Daily carbohydrates target</label>
            <input
              v-model="user.goals.daily_carbs_target"
              type="number"
              min="0"
              max="1000"
              step="10"
              :disabled="!isEditing"
            />
          </div>
        </div>
        <div class="user-info-item-with-icon">
          <IconFat class="icon"></IconFat>
          <div class="user-info-item">
            <label>Daily fat target</label>
            <input
              v-model="user.goals.daily_fat_target"
              type="number"
              min="0"
              max="1000"
              step="10"
              :disabled="!isEditing"
            />
          </div>
        </div>
      </div>
      <div class="user-physical-info">
        <div class="user-info-item-with-icon">
          <IconWeight class="icon"></IconWeight>
          <div class="user-info-item">
            <label>Weight in kg</label>
            <input
              v-model="user.weight"
              type="number"
              min="0"
              max="500"
              step="1"
              :disabled="!isEditing"
            />
          </div>
          <button v-if="isEditing" class="btn-edit-history" @click="openWeightHistoryModal">
            Edit History
          </button>
        </div>
        <div class="user-info-item-with-icon">
          <IconHeight class="icon"></IconHeight>
          <div class="user-info-item">
            <label>Height in cm</label>
            <input
              v-model="user.height"
              type="number"
              min="0"
              max="400"
              step="1"
              :disabled="!isEditing"
            />
          </div>
        </div>
        <div class="user-info-item-with-icon">
          <IconAge class="icon"></IconAge>
          <div class="user-info-item">
            <label>Age</label>
            <input
              v-model="user.age"
              type="number"
              min="0"
              max="200"
              step="1"
              :disabled="!isEditing"
            />
          </div>
        </div>
        <div class="user-info-item-with-icon">
          <IconGender class="icon"></IconGender>
          <div class="user-info-item">
            <label>Gender</label>
            <select v-model="user.gender" class="user-info-item-select" :disabled="!isEditing">
              <option class="search-type-option" value="male">Male</option>
              <option class="search-type-option" value="female">Female</option>
            </select>
          </div>
        </div>
        <div class="user-info-item-with-icon">
          <IconActivityLevel class="icon"></IconActivityLevel>
          <div class="user-info-item">
            <label>Activity level</label>
            <select
              v-model="user.activity_level"
              class="user-info-item-select"
              :disabled="!isEditing"
            >
              <option class="search-type-option" value="sedentary">Sedentary</option>
              <option class="search-type-option" value="lightly_active">Lightly active</option>
              <option class="search-type-option" value="moderately_active">
                Moderately active
              </option>
              <option class="search-type-option" value="very_active">Very active</option>
              <option class="search-type-option" value="super_active">Super active</option>
            </select>
            <details class="activity-level-details">
              <summary>Which activity level should i choose?</summary>
              The activity level is used as a multiplier for the BMR (Basal Metabolic Rate) to
              estimate daily base calorie burn calculate:
              <ul>
                - Sedentary (1.2): Little or no exercise, desk job.
              </ul>
              <ul>
                - Lightly Active (1.375): Light exercise/sports 1-3 days/week.
              </ul>
              <ul>
                - Moderately Active (1.55): Moderate exercise/sports 3-5 days/week.
              </ul>
              <ul>
                - Very Active (1.725): Hard exercise/sports 6-7 days/week.
              </ul>
              <ul>
                - Super Active (1.9): Very hard exercise, physical job, or training twice a day.
              </ul>
            </details>
          </div>
        </div>
      </div>
      <div class="change-password-container">
        <div class="user-info-item-with-icon">
          <IconPassword class="icon"></IconPassword>
          <div class="user-info-item">
            <label>New password</label>
            <input v-model="newPassword" type="password" :disabled="!isEditing" />
          </div>
        </div>
        <div class="user-info-item-with-icon">
          <IconPassword class="icon"></IconPassword>
          <div class="user-info-item">
            <label>Confirm new password</label>
            <input v-model="newPasswordConfirmation" type="password" :disabled="!isEditing" />
          </div>
        </div>
      </div>
      <div class="logout-btn-container">
        <button class="btn-logout" @click="logout()" :disabled="saving">
          <div class="btn-logout-content">
            <IconLogout></IconLogout>
            <span class="btn-logout-text">Logout</span>
          </div>
        </button>
      </div>
    </div>
    <ErrorModal
      v-model="showLoadingError"
      title="Loading Error"
      message="Unable to load user data"
      :details="errorDetails"
    ></ErrorModal>
    <div class="button-root">
      <button class="btn-save" @click="saveUser()" v-if="isEditing" :disabled="saving">
        <IconSave v-if="!saving"></IconSave>
        <Spinner v-else></Spinner>
        <ErrorModal
          v-model="showSavingError"
          title="Save Error"
          message="Unable to save user info."
          :details="errorDetails"
        ></ErrorModal>
      </button>
      <button class="btn-edit" @click="toggleEditing()" v-if="!isEditing" :disabled="saving">
        <IconEdit></IconEdit>
      </button>
      <button class="btn-cancel" @click="toggleEditing()" v-else :disabled="saving">
        <IconCancel></IconCancel>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import { useAuthStore } from '@/stores/auth'
import type { User } from '@/types/user'
import type { WeightHistory } from '@/types/user'
import ErrorModal from '@/components/ErrorModal.vue'
import Spinner from '@/components/Spinner.vue'
import WeightHistoryModal from '@/components/WeightHistoryModal.vue'

// Icon imports
import IconName from '@/components/icons/IconName.vue'
import IconEmail from '@/components/icons/IconEmail.vue'
import IconCalorie from '@/components/icons/IconCalorie.vue'
import IconProtein from '@/components/icons/IconProtein.vue'
import IconCarbs from '@/components/icons/IconCarbs.vue'
import IconFat from '@/components/icons/IconFat.vue'
import IconWeight from '@/components/icons/IconWeight.vue'
import IconHeight from '@/components/icons/IconHeight.vue'
import IconAge from '@/components/icons/IconAge.vue'
import IconGender from '@/components/icons/IconGender.vue'
import IconActivityLevel from '@/components/icons/IconActivityLevel.vue'
import IconActiveCalories from '@/components/icons/IconActiveCalories.vue'
import IconEdit from '@/components/icons/IconEdit.vue'
import IconSave from '@/components/icons/IconSave.vue'
import IconCancel from '@/components/icons/IconCancel.vue'
import IconPassword from '@/components/icons/IconPassword.vue'
import IconLogout from '@/components/icons/IconLogout.vue'
import { getFormattedDateToday } from '@/helpers/utils'

const router = useRouter()

const user = ref<User | null>(null)
const showLoadingError = ref(false)
const showSavingError = ref(false)
const errorDetails = ref('')
const saving = ref(false)
const loading = ref(true)
const isEditing = ref(false)
const newPassword = ref<string | null>(null)
const newPasswordConfirmation = ref<string | null>(null)
const showWeightHistoryModal = ref(false)

const loadUserData = async () => {
  try {
    const user_local = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user_local || !user_local.user_id) {
      throw new Error('User not found in local storage')
    }
    loading.value = true
    const user_id = user_local.user_id

    user.value = await fetchWrapper.get(`/api/v1/user/${user_id}`)
    if (user.value?.weight_history[0]) {
      user.value.weight = user.value?.weight_history[0]?.weight
    }
  } catch (err) {
    console.error('Error loading user data:', err)
    if (err instanceof Error) {
      showLoadingError.value = true
      errorDetails.value = err.message || err.toString() || 'Unknown error'
    }
  } finally {
    loading.value = false
  }
}

const saveUser = async () => {
  try {
    if (!user.value) {
      throw new Error('User not found in local storage')
    }
    saving.value = true
    const user_id = user.value.id

    if (newPassword.value && newPassword.value == newPasswordConfirmation.value) {
      user.value.password = newPassword.value
    }
    user.value = await fetchWrapper.patch(
      `/api/v1/user/${user_id}?weight_date_overwrite=${getFormattedDateToday()}`,
      user.value,
    )
    if (user.value?.weight_history[0]) {
      user.value.weight = user.value.weight_history[0].weight
    }
  } catch (err) {
    console.error('Error updating user data:', err)
    if (err instanceof Error) {
      showSavingError.value = true
      errorDetails.value = err.message || err.toString() || 'Unknown error'
    }
  } finally {
    newPassword.value = null
    newPasswordConfirmation.value = null
    saving.value = false
    isEditing.value = false
  }
}

function toggleEditing() {
  isEditing.value = !isEditing.value
}

const logout = async () => {
  const authStore = useAuthStore()

  authStore.logout()
  router.push('/')
}

onMounted(async () => {
  loadUserData()
})

const openWeightHistoryModal = () => {
  if (user.value) {
    showWeightHistoryModal.value = true
  }
}

const saveWeightHistory = async (updatedHistory: WeightHistory[]) => {
  if (!user.value || !user.value.weight_history) {
    return
  }

  try {
    user.value.weight_history = await fetchWrapper.put(
      `/api/v1/user/${user.value.id}/weight-history`,
      updatedHistory,
    )
    if (user.value?.weight_history[0]) {
      user.value.weight = user.value.weight_history[0]?.weight
    }
  } catch (err) {
    console.error('Error updating weight history:', err)
    if (err instanceof Error) {
      showSavingError.value = true
      errorDetails.value = err.message || err.toString() || 'Unknown error'
    }
  }
}
</script>

<style scoped lang="css">
.profile-root {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: var(--main-content-height);
  width: var(--main-content-width);
  background-color: var(--color-background-primary);
  padding: 1rem;
}

.user-information-root {
  display: flex;
  flex-direction: column;
  justify-content: start;
  align-items: center;
  width: calc(var(--main-content-width) - 1rem);
  max-width: 1200px;
  min-height: calc(var(--main-content-height) - 2rem);
  background-color: var(--color-background-secondary);
  border-radius: 0.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 0.5rem;
}

.profile-loading-spinner {
  width: 5rem;
  height: 5rem;
}

.user-base-info,
.user-goal-info,
.user-physical-info,
.change-password-container {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--color-accent-secondary);
  padding: 0.5rem;
  border-radius: 0.5rem;
  width: 100%;
  height: 100%;
}

.user-goal-info,
.user-physical-info,
.change-password-container {
  margin-top: 0.5rem;
}

.user-info-item-with-icon {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.user-info-item-with-icon .icon {
  align-self: start;
  flex-shrink: 0;
  height: 2rem;
  width: 2rem;
  margin-top: 0.75rem;
  margin-right: 0.25rem;
}

.btn-edit-history {
  height: 100%;
  width: 4rem;
  margin-left: 0.5rem;
  padding: 0.25rem;
  background-color: var(--color-accent-secondary);
  border: 1px solid var(--color-accent-secondary);
  border-radius: 1rem;
}

.user-info-item {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  margin-bottom: 0.5rem;
  justify-content: end;
}
.user-info-item label {
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
  z-index: 100;
}
.user-info-item input,
.user-info-item .user-info-item-select {
  color: var(--color-text-primary);
  border: 1px solid var(--color-accent-secondary);
  padding: 0.5rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.3s;
  background-color: var(--color-background-secondary);
}
.user-info-item .user-info-item-select:disabled {
  color: var(--color-text-primary);
}

input:focus {
  outline: none;
  border-color: var(--color-accent-primary);
}

.activity-level-details {
  margin-top: 0.25rem;
  margin-left: 0.25rem;
}
.button-root {
  position: fixed;
  right: max(1.5rem, calc((100vw - 1200px) / 2 + 1rem));
  bottom: 2rem;
  height: 3rem;
}

.button-root button {
  height: 100%;
  width: 3rem;
  margin-left: 0.5rem;
  padding: 0.5rem;
  background-color: var(--color-accent-secondary);
  border: 1px solid var(--color-accent-secondary);
  border-radius: 1rem;
}

.logout-btn-container {
  height: 3rem;
  align-self: start;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}
.btn-logout {
  width: 100%;
  height: 100%;
  padding: 0.5rem;

  background-color: rgb(255, 109, 109);
  border: 1px solid var(--color-accent-secondary);

  border-radius: 1rem;
}

.btn-logout-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  height: 100%;
  width: 5rem;
}

.btn-logout-text {
  margin-left: 0.25rem;
  padding-right: 0.25rem;
  font-weight: bold;
}

@media (max-width: 480px) {
  .profile-root {
    padding: 0.5rem;
  }

  .user-information-root {
    min-height: calc(var(--main-content-height) - 1rem);
  }

  .button-root {
    bottom: 1rem;
  }

  .logout-btn-container {
    margin-bottom: 0rem;
  }
}
</style>
