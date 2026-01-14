<template>
  <div class="today-view-root">
    <div class="profile-loading-spinner" v-if="loading">
      <Spinner></Spinner>
      <ErrorModal
        v-model="showLoadingError"
        title="Loading Error"
        message="Unable to load log data."
        :details="errorDetails"
      ></ErrorModal>
    </div>
    <div class="today-view-content" v-if="!loading && foodLog && !entryEditMode">
      <div class="charts-root">
        <div class="chart-calories-left">
          <GaugeChart
            :dataset="{
              value: foodLog.goals.daily_calorie_target - totalCalories + totalBurnedCalories,
              min: 0,
              max: foodLog.goals.daily_calorie_target + totalBurnedCalories,
              rounding: 0,
              suffix: ' Kcal left',
              colorMin: '#fdff74ff',
              colorMax: '#b3ffb3',
            }"
            :show-animation="!disableChartAnimation"
          ></GaugeChart>
        </div>
        <SparkbarChart
          class="summary-chart"
          :dataset="summaryDataset"
          :show-animation="!disableChartAnimation"
        />
      </div>
      <div class="food-information food-information-breakfast">
        <div class="food-info-heading">
          <label>Breakfast </label>
          <div class="food-info-heading-dot-menu">
            <TodayDotMenu
              v-model:log-entries="breakfastEntries"
              :date="props.date"
              @refresh="refreshFoodEntries"
              :meal-type="'breakfast'"
              @addEntries="addFoodEntries"
            ></TodayDotMenu>
          </div>
        </div>
        <MealTypeSummary
          :meal-entries="breakfastEntries"
          v-if="breakfastEntries.length > 1"
        ></MealTypeSummary>
        <FoodItemSummary
          v-for="foodEntry in breakfastEntries"
          :key="foodEntry.id"
          :food-entry="foodEntry"
          @food-entry-deleted="handleFoodEntryDeleted(foodEntry)"
          @entry-edit-requested="handleEntryEditRequest(foodEntry)"
        ></FoodItemSummary>
        <span class="nothing-logged-text" v-if="breakfastEntries.length == 0">Nothing logged</span>
      </div>
      <div class="food-information food-information-lunch">
        <div class="food-info-heading">
          <label>Lunch </label>
          <div class="food-info-heading-dot-menu">
            <TodayDotMenu
              v-model:log-entries="lunchEntries"
              :date="props.date"
              @refresh="refreshFoodEntries"
              :meal-type="'lunch'"
              @addEntries="addFoodEntries"
            ></TodayDotMenu>
          </div>
        </div>
        <MealTypeSummary
          :meal-entries="lunchEntries"
          v-if="lunchEntries.length > 1"
        ></MealTypeSummary>
        <FoodItemSummary
          v-for="foodEntry in lunchEntries"
          :key="foodEntry.id"
          :food-entry="foodEntry"
          @food-entry-deleted="handleFoodEntryDeleted(foodEntry)"
          @entry-edit-requested="handleEntryEditRequest(foodEntry)"
        ></FoodItemSummary>
        <span class="nothing-logged-text" v-if="lunchEntries.length == 0">Nothing logged</span>
      </div>
      <div class="food-information food-information-dinner">
        <div class="food-info-heading">
          <label>Dinner </label>
          <div class="food-info-heading-dot-menu">
            <TodayDotMenu
              v-model:log-entries="dinnerEntries"
              :date="props.date"
              @refresh="refreshFoodEntries"
              :meal-type="'dinner'"
              @addEntries="addFoodEntries"
            ></TodayDotMenu>
          </div>
        </div>
        <MealTypeSummary
          :meal-entries="dinnerEntries"
          v-if="dinnerEntries.length > 1"
        ></MealTypeSummary>
        <FoodItemSummary
          v-for="foodEntry in dinnerEntries"
          :key="foodEntry.id"
          :food-entry="foodEntry"
          @food-entry-deleted="handleFoodEntryDeleted(foodEntry)"
          @entry-edit-requested="handleEntryEditRequest(foodEntry)"
        ></FoodItemSummary>
        <span class="nothing-logged-text" v-if="dinnerEntries.length == 0">Nothing logged</span>
      </div>
      <div class="food-information food-information-snack">
        <div class="food-info-heading">
          <label>Snack </label>
          <div class="food-info-heading-dot-menu">
            <TodayDotMenu
              v-model:log-entries="snackEntries"
              :date="props.date"
              @refresh="refreshFoodEntries"
              :meal-type="'snack'"
              @addEntries="addFoodEntries"
            ></TodayDotMenu>
          </div>
        </div>
        <MealTypeSummary
          :meal-entries="snackEntries"
          v-if="snackEntries.length > 1"
        ></MealTypeSummary>
        <FoodItemSummary
          v-for="foodEntry in snackEntries"
          :key="foodEntry.id"
          :food-entry="foodEntry"
          @food-entry-deleted="handleFoodEntryDeleted(foodEntry)"
          @entry-edit-requested="handleEntryEditRequest(foodEntry)"
        ></FoodItemSummary>
        <span class="nothing-logged-text" v-if="snackEntries.length == 0">Nothing logged</span>
      </div>
      <div class="activity-information">
        <div class="food-info-heading">
          <label>Activities </label>
          <div class="food-info-heading-dot-menu">
            <TodayDotMenu
              v-model:log-entries="activityEntries"
              :date="props.date"
              @refresh="refreshActivityEntries"
              @add-entries="addActivityEntries"
              :meal-type="'activity'"
            ></TodayDotMenu>
          </div>
        </div>
        <ActivityItemSummary
          v-for="activityEntry in activityEntries"
          :key="activityEntry.id"
          :activity-entry="activityEntry"
          @activity-entry-deleted="handleActivityEntryDeleted"
          @entry-edit-requested="handleActivityEntryEditRequest"
        ></ActivityItemSummary>
        <span class="nothing-logged-text" v-if="activityEntries.length == 0">Nothing logged</span>
      </div>
    </div>
    <div v-if="entryEditMode && entryToEdit" class="food-details-root">
      <FoodDetails
        v-model:selectedFood="entryToEdit.food_item"
        v-model:log-entry="entryToEdit"
        @entry-updated="loadLogData(props.date)"
        @back-requested="toggleEditEntryMode"
      ></FoodDetails>
    </div>
    <div v-if="entryEditMode && activityEntryToEdit && user" class="activity-details-root">
      <ActivityDetails
        v-model:selected-activity="activityEntryToEdit.activity"
        v-model:log-entry="activityEntryToEdit"
        :user="user"
        @entry-updated="loadLogData(props.date)"
        @back-requested="toggleEditEntryMode"
      ></ActivityDetails>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import { getFormattedDate } from '@/helpers/utils'
import type { FoodEntry, FoodLog } from '@/types/foodLog'
import type { ActivityLog, ActivityEntry } from '@/types/activityLog'
import type { User } from '@/types/user'

import Spinner from '@/components/Spinner.vue'
import ErrorModal from '@/components/ErrorModal.vue'
import GaugeChart from '@/components/GaugeChart.vue'
import SparkbarChart from '@/components/SparkbarChart.vue'
import FoodItemSummary from '@/components/FoodItemSummary.vue'
import ActivityItemSummary from '@/components/ActivityItemSummary.vue'
import FoodDetails from '@/components/FoodDetails/FoodDetails.vue'
import ActivityDetails from '@/components/ActivityDetails/ActivityDetails.vue'
import MealTypeSummary from '@/components/MealTypeSummary.vue'
import TodayDotMenu from '@/components/TodayDotMenu.vue'

const foodLog = ref<FoodLog | null>(null)
const activityLog = ref<ActivityLog | null>(null)
const user = ref<User | null>(null)
const loading = ref(false)
const showLoadingError = ref(false)
const errorDetails = ref('')
const entryEditMode = ref(false)
const entryToEdit = ref<FoodEntry | null>(null)
const activityEntryToEdit = ref<ActivityEntry | null>(null)
const disableChartAnimation = ref(false)

const props = defineProps({
  date: {
    type: String,
    default: getFormattedDate(),
  },
})

function refreshFoodEntries() {
  if (!foodLog.value) {
    return
  }
  disableChartAnimation.value = true
  loadLogData(props.date)
}

function refreshActivityEntries() {
  if (!activityLog.value) {
    return
  }
  loadLogData(props.date)
}

const loadUserData = async () => {
  try {
    const user_local = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user_local || !user_local.user_id) {
      throw new Error('User not found in local storage')
    }
    const user_id = user_local.user_id
    user.value = await fetchWrapper.get(`/api/v1/user/${user_id}`)
  } catch (err) {
    console.error('Error loading user data:', err)
    if (err instanceof Error) {
      showLoadingError.value = true
      errorDetails.value = err.message || err.toString() || 'Unknown error'
    }
  }
}

const loadLogData = async (dateToLoad: string) => {
  loading.value = true
  try {
    // Fetch food log
    const foodResult = await fetchWrapper.get(`/api/v1/log/day/${dateToLoad}/food`)
    foodLog.value = foodResult

    // Fetch activity log
    const activityResult = await fetchWrapper.get(`/api/v1/log/day/${dateToLoad}/activity`)
    activityLog.value = activityResult
  } catch (err) {
    console.error('Error loading log data:', err)
    if (err instanceof Error) {
      showLoadingError.value = true
      errorDetails.value = err.message || err.toString() || 'Unknown error'
    }
  } finally {
    loading.value = false
    entryEditMode.value = false
  }
}

const totalCalories = computed(() => {
  if (!foodLog.value) return 0
  return foodLog.value.food_entries.reduce((total, entry) => {
    const calories = (entry.food_item.calories_per_100 * entry.quantity) / 100
    return total + calories
  }, 0)
})

const totalProtein = computed(() => {
  if (!foodLog.value) return 0
  return foodLog.value.food_entries.reduce((total, entry) => {
    const protein = (entry.food_item.protein_per_100 * entry.quantity) / 100
    return total + protein
  }, 0)
})

const totalCarbs = computed(() => {
  if (!foodLog.value) return 0
  return foodLog.value.food_entries.reduce((total, entry) => {
    const carbs = (entry.food_item.carbs_per_100 * entry.quantity) / 100
    return total + carbs
  }, 0)
})

const totalFat = computed(() => {
  if (!foodLog.value) return 0
  return foodLog.value.food_entries.reduce((total, entry) => {
    const fat = (entry.food_item.fat_per_100 * entry.quantity) / 100
    return total + fat
  }, 0)
})

const totalBurnedCalories = computed(() => {
  if (!activityLog.value) return 0
  return activityLog.value.activity_entries.reduce((total, entry) => {
    return total + entry.calories_burned
  }, 0)
})

// Computed properties for filtering food entries by meal type
const breakfastEntries = computed(() => {
  if (!foodLog.value) return []
  return foodLog.value.food_entries.filter((entry) => entry.meal_type === 'breakfast')
})

const lunchEntries = computed(() => {
  if (!foodLog.value) return []
  return foodLog.value.food_entries.filter((entry) => entry.meal_type === 'lunch')
})

const dinnerEntries = computed(() => {
  if (!foodLog.value) return []
  return foodLog.value.food_entries.filter((entry) => entry.meal_type === 'dinner')
})

const snackEntries = computed(() => {
  if (!foodLog.value) return []
  return foodLog.value.food_entries.filter((entry) => entry.meal_type === 'snack')
})

// Computed properties for activity entries
const activityEntries = computed(() => {
  if (!activityLog.value) return []
  return activityLog.value.activity_entries
})

const summaryDataset = computed(() => {
  if (!foodLog.value) {
    return []
  }
  const dataset = [
    {
      name: 'Calorie intake',
      value: totalCalories.value,
      target: Math.max(foodLog.value?.goals.daily_calorie_target, totalCalories.value),
      color: '#baff79ff',
      prefix: '',
      suffix: ' Kcal / ' + foodLog.value?.goals.daily_calorie_target + ' Kcal',
      rounding: 0,
    },
    {
      name: 'Fat intake',
      value: totalFat.value,
      target: Math.max(foodLog.value?.goals.daily_fat_target, totalFat.value),
      color: '#97e6ff',
      prefix: '',
      suffix: ' g / ' + foodLog.value?.goals.daily_fat_target + ' g',
      rounding: 1,
    },
    {
      name: 'Carbs intake',
      value: totalCarbs.value,
      target: Math.max(foodLog.value?.goals.daily_carbs_target, totalCarbs.value),
      color: '#7b11fd',
      prefix: '',
      suffix: ' g / ' + foodLog.value?.goals.daily_carbs_target + ' g',
      rounding: 1,
    },
    {
      name: 'Protein intake',
      value: totalProtein.value,
      target: Math.max(foodLog.value?.goals.daily_protein_target, totalProtein.value),
      color: '#ff4492ff',
      prefix: '',
      suffix: ' g / ' + foodLog.value?.goals.daily_protein_target + ' g',
      rounding: 1,
    },
  ]

  if (activityLog.value && activityLog.value.goals.daily_calorie_burn_target > 0) {
    dataset.splice(1, 0, {
      name: 'Calories burned',
      value: totalBurnedCalories.value,
      target: Math.max(
        activityLog.value.goals.daily_calorie_burn_target,
        totalBurnedCalories.value,
      ),
      color: '#5affc3ff',
      prefix: '',
      suffix: ' Kcal / ' + activityLog.value.goals.daily_calorie_burn_target + ' Kcal',
      rounding: 0,
    })
  }

  return dataset
})

const handleFoodEntryDeleted = (foodEntry: FoodEntry) => {
  if (!foodLog.value) {
    return
  }

  disableChartAnimation.value = true

  foodLog.value.food_entries = foodLog.value.food_entries.filter(
    (entry) => entry.id !== foodEntry.id,
  )
}

const toggleEditEntryMode = () => {
  entryEditMode.value = !entryEditMode.value
}
const handleEntryEditRequest = (foodEntry: FoodEntry) => {
  toggleEditEntryMode()
  entryToEdit.value = foodEntry
}

const handleActivityEntryDeleted = (activityEntryId: string) => {
  if (!activityLog.value) {
    return
  }

  disableChartAnimation.value = true

  activityLog.value.activity_entries = activityLog.value.activity_entries.filter(
    (entry) => entry.id !== activityEntryId,
  )
}

const handleActivityEntryEditRequest = (activityEntry: ActivityEntry) => {
  toggleEditEntryMode()
  activityEntryToEdit.value = activityEntry
}

async function addFoodEntries(entries: FoodEntry[]) {
  disableChartAnimation.value = true
  foodLog.value?.food_entries.push(...entries)
}

async function addActivityEntries(entries: ActivityEntry[]) {
  disableChartAnimation.value = true
  activityLog.value?.activity_entries.concat(entries)
}

onMounted(async () => {
  await loadUserData()
  loadLogData(props.date)
})
</script>

<style lang="css" scoped>
.today-view-root {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: var(--main-content-height);
  width: var(--main-content-width);
  background-color: var(--color-background-primary);
  padding: 1rem;
}

.today-view-content {
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
  gap: 1rem;
}

.charts-root {
  display: flex;
  flex-direction: row;
  width: 100%;
  align-items: center;
}

.chart-calories-left {
  width: 70%;
}
.summary-chart {
  margin-right: 0.5rem;
}

.food-information {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  border: 1px solid var(--color-accent-secondary);
  border-radius: 0.5rem;
  width: 100%;
  height: 100%;
  min-height: 4rem;
  padding: 0.5rem;
}

.food-info-heading {
  display: flex;
  flex-direction: row;
  align-self: start;
  position: relative;
  top: -1.5rem;
  background-color: var(--color-background-secondary);
  margin-left: 0.5rem;
  font-weight: bold;
  color: var(--color-text-primary);
  margin-bottom: -1.75rem;
  padding-left: 0.5rem;
  padding-right: 0.1rem;
}

.food-info-heading label {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--color-text-primary);
}

.food-info-heading-dot-menu {
  position: relative;
  top: 0.4rem;
  width: 1rem;
  cursor: pointer;
}

.nothing-logged-text {
  color: var(--color-text-secondary);
}

.activity-information {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  border: 1px solid var(--color-accent-secondary);
  border-radius: 0.5rem;
  width: 100%;
  height: 100%;
  min-height: 4rem;
  padding: 0.5rem;
}

@media (max-width: 480px) {
  .today-view-root {
    padding: 0.5rem;
  }

  .today-view-content {
    min-height: calc(var(--main-content-height) - 1rem);
  }

  .charts-root {
    flex-direction: column;
    margin-bottom: 1rem;
  }

  .summary-chart {
    margin-right: 0;
  }
}
</style>
