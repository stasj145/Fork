<template>
  <div class="dot-menu-root">
    <button class="open-menu-btn" @click="toggelMenu">
      <IconDotMenu></IconDotMenu>
    </button>
    <div class="menu" v-if="showMenu" ref="menuRef">
      <button
        class="menu-btn btn-delete"
        :class="{ 'btn-delete-awaiting-confirmation': deleteConfirmed }"
        @click="removeAllEntries"
      >
        <span v-if="!deleting">Remove all</span>
        <div class="btn-spinner">
          <Spinner v-if="deleting"></Spinner>
        </div>
        <ErrorModal
          v-model="showDeletionError"
          title="Deletion Error"
          message="Unable to delete entry."
          :details="errorDetails"
        ></ErrorModal>
      </button>
      <button class="menu-btn" @click="copyYesterday">
        <span v-if="!updating">Copy from yesterday</span>
        <div class="btn-spinner">
          <Spinner v-if="updating"></Spinner>
        </div>
        <ErrorModal
          v-model="showUpdatingError"
          title="Updating Error"
          message="Unable to update entries."
          :details="errorDetails"
        ></ErrorModal>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import IconDotMenu from './icons/IconDotMenu.vue'
import type { FoodEntry, FoodLog } from '@/types/foodLog'
import type { ActivityLog, ActivityEntry } from '@/types/activityLog'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import { getFormattedDate } from '@/helpers/utils'
import ErrorModal from './ErrorModal.vue'
import Spinner from './Spinner.vue'

const showMenu = ref<boolean>(false)
const showDeletionError = ref<boolean>(false)
const showUpdatingError = ref<boolean>(false)
const errorDetails = ref<string>('')
const deleteConfirmed = ref<boolean>(false)
const deleting = ref<boolean>(false)
const updating = ref<boolean>(false)
const menuRef = ref<HTMLElement | null>(null)

const logEntries = defineModel<FoodEntry[] | ActivityEntry[]>('logEntries', { required: true })
const entriesToAdd = ref<object[]>([])

const props = defineProps({
  date: {
    type: String,
    default: getFormattedDate(),
  },
  mealType: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['refresh', 'addEntries'])

function toggelMenu() {
  showMenu.value = !showMenu.value
}

function handleClickOutside(event: MouseEvent) {
  if (menuRef.value && !menuRef.value.contains(event.target as Node)) {
    showMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})

async function removeAllEntries() {
  if (!deleteConfirmed.value) {
    deleteConfirmed.value = true
    return
  }

  if (logEntries.value.length == 0) {
    deleteConfirmed.value = false
    return
  }

  if ((<FoodEntry>logEntries.value[0]).food_item) {
    removeAllFoodItems()
  } else if ((<ActivityEntry>logEntries.value[0]).activity) {
    removeAllActivityItems()
  }
}

async function removeAllFoodItems() {
  if (logEntries.value.length == 0) {
    showMenu.value = false
    return
  }

  if (!(<FoodEntry>logEntries.value[0]).food_item) {
    return
  }

  deleting.value = true
  for (const logEntry of logEntries.value) {
    if ((<FoodEntry>logEntry).id) {
      try {
        await fetchWrapper.delete(`/api/v1/log/day/${props.date}/food/${(<FoodEntry>logEntry).id}`)
      } catch (err) {
        if (err instanceof Error) {
          showDeletionError.value = true
          errorDetails.value = err.message || 'N/A'
          break
        }
      }
    }
  }
  if (!showDeletionError.value) {
    deleting.value = false
    deleteConfirmed.value = false
    emit('refresh')
    showMenu.value = false
  }
}

async function removeAllActivityItems() {
  if (logEntries.value.length == 0) {
    showMenu.value = false
    return
  }

  if (!(<ActivityEntry>logEntries.value[0]).activity) {
    return
  }

  deleting.value = true
  for (const logEntry of logEntries.value) {
    if ((<ActivityEntry>logEntry).id) {
      try {
        await fetchWrapper.delete(
          `/api/v1/log/day/${props.date}/activity/${(<ActivityEntry>logEntry).id}`,
        )
      } catch (err) {
        if (err instanceof Error) {
          showDeletionError.value = true
          errorDetails.value = err.message || 'N/A'
          break
        }
      }
    }
  }
  if (!showDeletionError.value) {
    deleting.value = false
    deleteConfirmed.value = false
    emit('refresh')
    showMenu.value = false
  }
}

async function copyYesterday() {
  const mealTypes: string[] = ['breakfast', 'lunch', 'dinner', 'snack']

  if (props.mealType == 'activity') {
    updating.value = true
    const oldActivityLog: ActivityLog = await getYesterdayActivityLogData()
    for (const entry of oldActivityLog.activity_entries) {
      const body = {
        activity_id: entry.activity.id,
        duration: entry.duration,
        calories_burned: entry.calories_burned,
      }
      const newEntry: ActivityEntry = await fetchWrapper.post(
        `/api/v1/log/day/${props.date}/activity`,
        body,
      )
      entriesToAdd.value.push(newEntry)
    }
    emit('addEntries', entriesToAdd.value)
    entriesToAdd.value = []
    updating.value = false
    return
  }

  if (!mealTypes.includes(props.mealType)) {
    return
  }

  updating.value = true
  const oldFoodLog: FoodLog = await getYesterdayFoodLogData()
  for (const entry of oldFoodLog.food_entries) {
    if (entry.meal_type == props.mealType) {
      const body = {
        food_id: entry.food_item.id,
        quantity: entry.quantity,
        meal_type: props.mealType,
      }
      const newEntry: FoodEntry = await fetchWrapper.post(
        `/api/v1/log/day/${getFormattedDate()}/food`,
        body,
      )

      entriesToAdd.value.push(newEntry)
    }
  }
  emit('addEntries', entriesToAdd.value)
  updating.value = false
  entriesToAdd.value = []
}

const getYesterdayFoodLogData = async () => {
  const dateToGet: string = getFormattedDate(-1, props.date)
  try {
    const foodResult = await fetchWrapper.get(`/api/v1/log/day/${dateToGet}/food`)
    return foodResult
  } catch (err) {
    console.error('Error loading log data:', err)
    if (err instanceof Error) {
      showUpdatingError.value = true
      errorDetails.value = err.message || err.toString() || 'Unknown error'
    }
  }
}

const getYesterdayActivityLogData = async () => {
  const dateToGet: string = getFormattedDate(-1, props.date)
  try {
    const activityResult = await fetchWrapper.get(`/api/v1/log/day/${dateToGet}/activity`)
    return activityResult
  } catch (err) {
    console.error('Error loading log data:', err)
    if (err instanceof Error) {
      showUpdatingError.value = true
      errorDetails.value = err.message || err.toString() || 'Unknown error'
    }
  }
}
</script>

<style lang="css" scoped>
.open-menu-btn {
  height: 100%;
  width: 100%;
  background: none;
  border: none;
  cursor: pointer;
}

.menu {
  position: absolute;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  width: 12rem;
  background-color: var(--color-accent-primary);
  box-shadow: 0 0 5px 0px var(--color-accent-primary);
  border-radius: 0.5rem;
  padding: 0.5rem;
  z-index: 1000;
}

.menu-btn {
  width: 100%;
  height: 2rem;
  background-color: var(--color-accent-secondary);
  border: none;
  border-radius: 0.25rem;
  box-shadow: 0 0 5px 0px var(--color-accent-secondary);
  padding: 0.5rem;
  display: flex;
  align-content: center;
  justify-content: center;
}

.menu-btn span {
  color: var(--color-text-primary);
  width: 100%;
  font-weight: bold;
  font-size: 0.9rem;
  line-height: 0.9rem;
  flex-shrink: 0;
  align-self: center;
}

.btn-delete {
  background-color: #ffa9a9ff;
}

.btn-delete.btn-delete-awaiting-confirmation {
  background-color: rgb(255, 0, 0);
}

.btn-spinner {
  height: 1.7rem;
  width: 1.7rem;
}
</style>
