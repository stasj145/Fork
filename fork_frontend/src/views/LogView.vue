<template>
  <div class="log-view-root">
    <div class="profile-loading-spinner" v-if="loading">
      <Spinner></Spinner>
    </div>
    <div class="log-view-content-root" v-if="!loading && user">
      <div class="info-container weight">
        <span class="info-container-heading weight">Weight</span>
        <div class="segmented-control">
          <SegmentedControl
            class="segmented-control weight"
            :options="Object.keys(dateRangeChartSelectorLookup)"
            v-model="dateRangeChartSelector"
          ></SegmentedControl>
        </div>
        <div class="kpis weight">
          <div class="weight-kpis-first-row">
            <div class="weight-kpi">
              <KpiBox
                :title="'Starting weight'"
                :value="startingWeight.toFixed(1) + ' kg'"
              ></KpiBox>
            </div>
            <div class="weight-kpi">
              <KpiBox :title="'Current weight'" :value="user.weight.toFixed(1) + ' kg'"></KpiBox>
            </div>
          </div>
          <div class="weight-kpis-second-row">
            <div class="weight-kpi">
              <KpiBox
                :title="'Weight change %'"
                :value="((user.weight / startingWeight) * 100 - 100).toFixed(1) + '%'"
              ></KpiBox>
            </div>
            <div class="weight-kpi">
              <KpiBox
                :title="'Weight change kg'"
                :value="(user.weight - startingWeight).toFixed(1) + ' kg'"
              ></KpiBox>
            </div>
          </div>
          <div class="weight-kpis-third-row">
            <div class="weight-kpi">
              <KpiBox
                :title="'Avg change/day '"
                :value="
                  ((user.weight - startingWeight) / weightXAxisLabels.length).toFixed(1) + ' kg'
                "
              ></KpiBox>
            </div>
            <div class="weight-kpi">
              <KpiBox
                :title="'Avg change/week'"
                :value="
                  (((user.weight - startingWeight) / weightXAxisLabels.length) * 7).toFixed(1) +
                  ' kg'
                "
              ></KpiBox>
            </div>
          </div>
        </div>
        <div class="weight-chart">
          <XYChart
            :dataset="weightDataset"
            :x-axis-values="weightXAxisLabels"
            :y-min="weightYMin"
            :y-lable="'Weight in kg'"
            :minimal-labels="dateRangeChartSelector != '30d' && dateRangeChartSelector != '14d'"
          ></XYChart>
        </div>
      </div>
      <div class="info-container calories">
        <span class="info-container-heading calories">Calories</span>
        <div class="segmented-control">
          <SegmentedControl
            class="segmented-control calories"
            :options="Object.keys(dateRangeChartSelectorLookup)"
            v-model="dateRangeChartSelector"
          ></SegmentedControl>
        </div>
        <div class="kpis calories">
          <div class="calories-kpis-first-row"></div>

          <div class="calories-kpis-second-row"></div>

          <div class="calories-kpis-third-row"></div>
        </div>
        <div class="calorie-chart" v-if="foodLogXAxisLabels.length > 0">
          <XYChart
            :dataset="calorieDataset"
            :x-axis-values="foodLogXAxisLabels"
            :y-min="calorieYMin"
            :y-lable="'Kcal'"
            :minimal-labels="dateRangeChartSelector != '30d' && dateRangeChartSelector != '14d'"
          ></XYChart>
        </div>
      </div>
    </div>
    <ErrorModal
      v-model="showLoadingError"
      title="Loading Error"
      message="Unable to load data"
      :details="errorDetails"
    ></ErrorModal>
  </div>
</template>

<script setup lang="ts">
import ErrorModal from '@/components/ErrorModal.vue'
import KpiBox from '@/components/KpiBox.vue'
import SegmentedControl from '@/components/SegmentedControl.vue'
import Spinner from '@/components/Spinner.vue'
import XYChart from '@/components/XYChart.vue'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import { type FoodLog } from '@/types/foodLog'
import type { User, WeightHistory } from '@/types/user'
import { computed, onMounted, ref, watch } from 'vue'
import { type VueUiXyDatasetItem } from 'vue-data-ui'

let weightHistory: LocalWeightHistory[] = []
let foodLogHistory: LocalFoodLogHistory[] = []

const user = ref<User | null>(null)
const loading = ref<boolean>(true)
const showLoadingError = ref(false)
const errorDetails = ref('')
const calorieDataset = ref<VueUiXyDatasetItem[]>([])
const foodLogXAxisLabels = ref<string[]>([])
const dateRangeChartSelector = ref<string>('30d')
const dateRangeChartSelectorLookup: { [id: string]: number } = {
  '14d': -14,
  '30d': -30,
  '90d': -90,
  '365d': -365,
  full: 0,
}
const calorieYMin = ref<number>(0)

const weightYMin = ref<number>(0)
const startingWeight = ref<number>(0)

const weightDataset = computed(() => {
  if (!user.value || !user.value.weight_history) {
    return []
  }
  const seriesData = weightHistory
    .map((x) => x.weight)
    .reverse()
    .slice(dateRangeChartSelectorLookup[dateRangeChartSelector.value], weightHistory.length)

  // eslint-disable-next-line
  weightYMin.value = Math.floor((Math.round(Math.min(...(<number[]>seriesData))) + 1) / 10) * 10

  for (const weight of seriesData) {
    if (weight) {
      // eslint-disable-next-line
      startingWeight.value = weight
      break
    }
  }

  return <VueUiXyDatasetItem[]>[
    {
      name: 'Weight',
      series: seriesData,
      color: '#ffcd44',
      type: 'line',
      shape: 'circle',
      useArea: false,
      useProgression: false,
      dataLabels: true,
      smooth: true,
      dashed: false,
      useTag: 'none',
    },
  ]
})

const weightXAxisLabels = computed(() => {
  const xAxisData = user.value
    ? weightHistory
        .map((x) => x.created_at)
        .reverse()
        .slice(dateRangeChartSelectorLookup[dateRangeChartSelector.value], weightHistory.length)
    : []

  return xAxisData
})

watch(dateRangeChartSelector, async () => {
  await loadLogData()
})

const getCalorieDataset = () => {
  if (!user.value) {
    return []
  }
  const seriesData = foodLogHistory.map((x) => x.calories).reverse()

  return <VueUiXyDatasetItem[]>[
    {
      name: 'Calories',
      series: seriesData,
      color: '#baff79ff',
      type: 'line',
      shape: 'circle',
      useArea: false,
      useProgression: false,
      dataLabels: true,
      smooth: true,
      dashed: false,
      useTag: 'none',
    },
  ]
}

const getFoodLogXAxisLabels = () => {
  const xAxisData = foodLogHistory ? foodLogHistory.map((x) => x.date).reverse() : []

  return xAxisData
}

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
      weightHistory = fillGaps(user.value.weight_history)
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

const loadLogData = async () => {
  try {
    const foodLogList = await fetchWrapper.get(
      `/api/v1/log/last/food?n_logs=${<number>dateRangeChartSelectorLookup[dateRangeChartSelector.value] * -1}`,
    )
    if (foodLogList) {
      foodLogHistory = await prepFoodLogsData(foodLogList)
    }

    calorieDataset.value = getCalorieDataset()
    foodLogXAxisLabels.value = getFoodLogXAxisLabels()
  } catch (err) {
    console.error('Error loading users log data:', err)
    if (err instanceof Error) {
      showLoadingError.value = true
      errorDetails.value = err.message || err.toString() || 'Unknown error'
    }
  }
}

interface LocalWeightHistory {
  id?: string
  weight: number | null
  created_at: string
}

function formatDate(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function fillGaps(weights: WeightHistory[]): LocalWeightHistory[] {
  if (!weights[0]) {
    return []
  }

  const result: LocalWeightHistory[] = [weights[0]]

  for (let i = 1; i < weights.length; i++) {
    const prev = result[result.length - 1]!
    const curr = weights[i]!

    const prevDate = new Date(prev.created_at)
    const currDate = new Date(curr.created_at)

    const daysDiff = (prevDate.getTime() - currDate.getTime()) / (24 * 60 * 60 * 1000)

    if (daysDiff > 1) {
      const currentDate = new Date(prevDate)
      currentDate.setDate(prevDate.getDate() - 1)

      while (currentDate > currDate) {
        result.push({
          created_at: formatDate(currentDate),
          id: undefined,
          weight: null,
        })

        currentDate.setDate(currentDate.getDate() - 1)
      }
    }

    result.push(<LocalWeightHistory>curr)
  }

  return result
}

interface LocalFoodLogHistory {
  id?: string
  date: string

  calories: number | null
  protein: number | null
  fat: number | null
  carbs: number | null

  goalCalories: number | null
  goalProtein: number | null
  goalFat: number | null
  goalCarbs: number | null
}

async function prepFoodLogsData(foodLogs: FoodLog[]): Promise<LocalFoodLogHistory[]> {
  if (!foodLogs[0]) {
    return []
  }

  const result: LocalFoodLogHistory[] = [await createLocalFoodLogHistoryFromFoodLog(foodLogs[0])]

  for (let i = 1; i < foodLogs.length; i++) {
    const prev = result[result.length - 1]!
    const curr = foodLogs[i]!

    const prevDate = new Date(prev.date)
    const currDate = new Date(curr.date)

    const daysDiff = (prevDate.getTime() - currDate.getTime()) / (24 * 60 * 60 * 1000)

    if (daysDiff > 1) {
      const currentDate = new Date(prevDate)
      currentDate.setDate(prevDate.getDate() - 1)

      while (currentDate > currDate) {
        result.push(<LocalFoodLogHistory>{
          id: undefined,
          date: formatDate(currentDate),
          calories: null,
          protein: null,
          fat: null,
          carbs: null,
          goalCalories: null,
          goalProtein: null,
          goalCarbs: null,
          goalFat: null,
        })

        currentDate.setDate(currentDate.getDate() - 1)
      }
    }

    result.push(await createLocalFoodLogHistoryFromFoodLog(curr))
  }

  return result
}

async function createLocalFoodLogHistoryFromFoodLog(
  foodLog: FoodLog,
): Promise<LocalFoodLogHistory> {
  let totalCalories: number = 0
  let totalProtein: number = 0
  let totalFat: number = 0
  let totalCarbs: number = 0

  for (const entry of foodLog.food_entries) {
    totalCalories += (entry.food_item.calories_per_100 / 100) * entry.quantity
    totalProtein += (entry.food_item.protein_per_100 / 100) * entry.quantity
    totalFat += (entry.food_item.fat_per_100 / 100) * entry.quantity
    totalCarbs += (entry.food_item.fat_per_100 / 100) * entry.quantity
  }

  return <LocalFoodLogHistory>{
    id: foodLog.id,
    date: foodLog.date,
    calories: totalCalories,
    protein: totalProtein,
    fat: totalFat,
    carbs: totalCarbs,
    goalCalories: foodLog.goals.daily_calorie_target,
    goalProtein: foodLog.goals.daily_protein_target,
    goalCarbs: foodLog.goals.daily_carbs_target,
    goalFat: foodLog.goals.daily_fat_target,
  }
}

onMounted(async () => {
  loadUserData()
  loadLogData()
})
</script>

<style scoped>
.log-view-root {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: var(--main-content-height);
  width: var(--main-content-width);
  background-color: var(--color-background-primary);
  padding: 1rem;
}

.profile-loading-spinner {
  width: 5rem;
  height: 5rem;
}

.log-view-content-root {
  display: flex;
  flex-direction: column;
  justify-content: start;
  align-items: center;
  gap: 0.5rem;
  width: calc(var(--main-content-width) - 1rem);
  max-width: 1200px;
  min-height: calc(var(--main-content-height) - 2rem);
  background-color: var(--color-background-secondary);
  border-radius: 0.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 0.5rem;
}

.info-container {
  width: 100%;
  height: fit-content;
  border: 1px solid var(--color-accent-secondary);
  padding: 0.5rem;
  border-radius: 0.5rem;
  margin-top: 1.5rem;
}
.info-container-heading {
  color: var(--color-text-heading);
  background-color: var(--color-background-secondary);
  font-weight: bold;
  position: relative;
  bottom: 2rem;
  left: 0.5rem;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
  z-index: 10;
  font-size: 2rem;
}

.segmented-control {
  width: 100%;
  margin-top: -1rem;
}

.kpis {
  margin-top: 1rem;
  margin-bottom: 1rem;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
}

.weight-kpis-first-row,
.weight-kpis-second-row,
.weight-kpis-third-row {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
}

.weight-kpi {
  height: 5rem;
  width: 100%;
}

.weight-chart {
  width: 100%;
}

@media (max-width: 480px) {
  .log-view-root {
    padding: 0.5rem;
  }

  .log-view-content-root {
    min-height: calc(var(--main-content-height) - 1rem);
  }

  .info-container {
    margin-top: 0.5rem;
  }

  .info-container-heading {
    font-size: 1.5rem;
    bottom: 1.4rem;
  }

  .kpis {
    flex-direction: column;
  }

  .weight-kpi {
    height: 3.5rem;
  }
}
</style>
