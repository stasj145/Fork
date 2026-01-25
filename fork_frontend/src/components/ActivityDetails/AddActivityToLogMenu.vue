<!-- eslint-disable vue/no-mutating-props  -->
<template>
  <div class="add-to-log-menu-root">
    <div class="first-row">
      <input
        v-model="activityEntryInfo.duration"
        class="duration-input"
        type="number"
        min="0.0"
        max="10000"
        step="1"
        :disabled="adding"
      />
      <select v-model="activityEntryInfo.unit" class="add-to-log-select-unit" :disabled="adding">
        <option value="minutes">Minutes</option>
        <option value="hours">Hours</option>
      </select>
    </div>
    <div class="second-row">
      <input
        v-model="displayCaloriesBurned"
        class="calories-input"
        type="number"
        min="0.0"
        max="10000"
        step="1"
        :disabled="adding"
      />
      <span>Kcal</span>
      <button class="add-to-log-btn" @click="handleAddButton()" :disabled="adding">
        <IconAdd v-if="!adding"></IconAdd>
        <Spinner v-else></Spinner>
        <ErrorModal
          v-model="showAddingOrUpdatingError"
          title="Activity Entry Error"
          message="Unable to create new Activity entry or update existing one."
          :details="errorDetails"
        ></ErrorModal>
      </button>
      <button class="add-to-log-btn-cancel" @click="emit('close-requested')" :disabled="adding">
        <IconCancel></IconCancel>
      </button>
    </div>
  </div>
</template>

<!-- eslint-disable vue/no-mutating-props  -->
<script setup lang="ts">
import { computed, onMounted, ref, watch, type PropType } from 'vue'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import { getFormattedDate } from '@/helpers/utils'
import IconCancel from '@/components/icons/IconCancel.vue'
import ErrorModal from '@/components/ErrorModal.vue'
import Spinner from '@/components/Spinner.vue'
import IconAdd from '../icons/IconAdd.vue'
import type { ActivityEntry } from '@/types/activityLog'
import type { Activity } from '@/types/activity'
import type { User } from '@/types/user'

const selectedActivity = defineModel<Activity>('selectedActivity', { required: true })
const logEntry = defineModel<ActivityEntry | null>('logEntry', { default: null })

const emit = defineEmits(['close-requested', 'log-updated'])

const showAddingOrUpdatingError = ref(false)
const errorDetails = ref('N/A')
const adding = ref(false)

const props = defineProps({
  user: {
    type: Object as PropType<User>,
    required: true,
  },
})

interface ActivityEntryInfo {
  duration: number
  unit: string
}

const activityEntryInfo = ref<ActivityEntryInfo>({
  duration: 0.0,
  unit: 'minutes',
})

const manualCaloriesBurned = ref<number | null>(null)

const calculatecDuration = () => {
  if (activityEntryInfo.value.unit == 'minutes') {
    return parseFloat((activityEntryInfo.value.duration / 60).toFixed(3))
  }
  return activityEntryInfo.value.duration
}

const calculateCaloriesBurned = computed(() => {
  if (!props.user.weight_history[0]) {
    return 0
  }

  let calories: number = 0
  const duration: number = calculatecDuration()

  calories = selectedActivity.value.calories_burned_kg_h * props.user.weight_history[0]?.weight * duration

  return parseFloat(calories.toFixed(1))
})

const displayCaloriesBurned = computed({
  get: () => {
    return manualCaloriesBurned.value !== null
      ? manualCaloriesBurned.value
      : calculateCaloriesBurned.value
  },
  set: (value) => {
    manualCaloriesBurned.value = value
  },
})

function emitDone() {
  emit('log-updated')
}

async function handleAddButton() {
  addOrUpdateActivityInLog()
}

async function addOrUpdateActivityInLog() {
  adding.value = true
  try {
    if (!selectedActivity.value) {
      throw Error('No food selected')
    }
    if (!selectedActivity.value.id) {
      // create/save activity first if it has no id.
      await saveActivity(selectedActivity.value)
    }

    const duration: number = calculatecDuration()
    const caloriesBurned: number = displayCaloriesBurned.value
    if (logEntry.value) {
      //update
      await APIAddOrUpdateActivityEntry(duration, caloriesBurned, null, logEntry.value.id)
    } else {
      //create
      await APIAddOrUpdateActivityEntry(duration, caloriesBurned, selectedActivity.value.id)
    }
  } catch (err) {
    if (err instanceof Error) {
      showAddingOrUpdatingError.value = true
      errorDetails.value = err.message || 'N/A'
    }
  } finally {
    adding.value = false
  }
  if (!showAddingOrUpdatingError.value) {
    emitDone()
  }
}

async function saveActivity(updatedActivity: Activity) {
  try {
    const results: Activity = await fetchWrapper.post('/api/v1/activity/', updatedActivity)
    selectedActivity.value = results
  } catch (err) {
    if (err instanceof Error) {
      showAddingOrUpdatingError.value = true
      errorDetails.value = err.message || 'N/A'
    }
  }
}

async function APIAddOrUpdateActivityEntry(
  duration: number,
  caloriesBurned: number,
  activityId: string | null = null,
  logEntryId: string | null = null,
) {
  if (activityId) {
    //create
    const body = { activity_id: activityId, duration: duration, calories_burned: caloriesBurned }
    await fetchWrapper.post(`/api/v1/log/day/${getFormattedDate()}/activity`, body)
  } else if (logEntryId) {
    //update
    const body = { duration: duration, calories_burned: caloriesBurned }
    await fetchWrapper.patch(`/api/v1/log/day/${getFormattedDate()}/activity/${logEntryId}`, body)
  } else {
    showAddingOrUpdatingError.value = true
    errorDetails.value =
      'APIAddOrUpdateFoodEntry needs either activityId or logEntryId but neither was provided.'
  }
}

function setupLogUpdateMode(logEntry: ActivityEntry) {
  if (logEntry.duration % 1 === 0) {
    activityEntryInfo.value.unit = 'hours'
    activityEntryInfo.value.duration = logEntry.duration
  } else {
    activityEntryInfo.value.unit = 'minutes'
    activityEntryInfo.value.duration = logEntry.duration * 60
  }
}

watch([() => activityEntryInfo.value.duration], () => {
  // Reset manual calories when duration changes
  manualCaloriesBurned.value = null
})

onMounted(async () => {
  if (logEntry.value) {
    setupLogUpdateMode(logEntry.value)
  }
})
</script>

<style lang="css" scoped>
.add-to-log-menu-root {
  position: fixed;
  right: max(1rem, calc((100vw - 1200px) / 2) + 0.5rem);
  bottom: 1.5rem;
  height: 4rem;
  /* width: min(calc(1200px - 1rem), calc(100vw - 2rem)); */
  width: fit-content;
  background-color: var(--color-accent-secondary);
  border-radius: 1rem;

  display: flex;
  flex-direction: row;
  padding: 0.5rem;
  z-index: 1000;
}

.add-to-log-menu-root .first-row,
.add-to-log-menu-root .second-row {
  display: flex;
  flex-direction: row;
  height: 100%;
}

.add-to-log-menu-root .second-row {
  margin-left: 0.5rem;
}

.add-to-log-btn-cancel,
.add-to-log-btn {
  height: 100%;
  width: 3rem;
  margin-left: 0.5rem;
  padding: 0.5rem;
  background-color: var(--color-accent-primary);
  border: none;
  box-shadow: 0 0 1px 1px var(--color-accent-primary);
  border-radius: 1rem;
}

.add-to-log-select-meal-type,
.add-to-log-select-unit {
  color: var(--color-black);
  margin-left: 0.5rem;
  border: 1px solid var(--color-accent-primary);
  box-shadow: 0 0 1px 1px var(--color-accent-primary);
  padding: 0.5rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.3s;
  background-color: var(--color-accent-primary);
}

.duration-input,
.calories-input {
  color: var(--color-black);
  background-color: var(--color-accent-primary);
  border: none;
  box-shadow: 0 0 1px 1px var(--color-accent-primary);
  padding: 0.5rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.second-row span {
  margin-left: 0.25rem;
  align-self: center;
  line-height: 2rem;
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--color-black);
}

@media (max-width: 480px) {
  .add-to-log-menu-root {
    position: fixed;
    bottom: 0;
    right: 0;
    width: 100vw;
    height: 8rem;
    border-radius: 0;
    border-top-left-radius: 1rem;
    border-top-right-radius: 1rem;

    display: flex;
    flex-direction: column;
  }

  .add-to-log-menu-root .second-row {
    margin-top: 0.5rem;
  }

  .add-to-log-select-meal-type {
    width: 100%;
    margin-left: 0;
  }

  .duration-input,
  .add-to-log-select-unit {
    width: 50%;
  }
  .calories-input {
    width: 49%;
    flex-shrink: 0;
  }
  span {
    width: 100%;
  }

  .add-to-log-btn-cancel,
  .add-to-log-btn {
    width: 3rem;
    flex-shrink: 0;
  }
  .add-to-log-menu-root .second-row {
    margin-left: 0;
  }
}
</style>
