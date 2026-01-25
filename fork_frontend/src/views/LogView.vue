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
            <div class="kpi weight">
              <KpiBox
                :title="'Starting weight'"
                :value="startingWeight.toFixed(1) + ' kg'"
              ></KpiBox>
            </div>
            <div class="kpi weight">
              <KpiBox :title="'Current weight'" :value="user.weight.toFixed(1) + ' kg'"></KpiBox>
            </div>
          </div>
          <div class="weight-kpis-second-row">
            <div class="kpi weight">
              <KpiBox
                :title="'Weight change %'"
                :value="((user.weight / startingWeight) * 100 - 100).toFixed(1) + '%'"
              ></KpiBox>
            </div>
            <div class="kpi weight">
              <KpiBox
                :title="'Weight change kg'"
                :value="(user.weight - startingWeight).toFixed(1) + ' kg'"
              ></KpiBox>
            </div>
          </div>
          <div class="weight-kpis-third-row">
            <div class="kpi weight">
              <KpiBox
                :title="'Avg change/day '"
                :value="
                  ((user.weight - startingWeight) / weightXAxisLabels.length).toFixed(1) + ' kg'
                "
              ></KpiBox>
            </div>
            <div class="kpi weight">
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
        <div class="segmented-control calories">
          <SegmentedControl
            :options="Object.keys(dateRangeChartSelectorLookup)"
            v-model="dateRangeChartSelector"
          ></SegmentedControl>
        </div>
        <div class="kpis calories">
          <div class="calories-kpis-first-row">
            <div class="kpi calorie">
              <KpiBox
                :title="'Avg/day'"
                :value="
                  getAverageExcludingZeros(foodLogHistory.map((log) => log.calories)).toFixed(1) +
                  ' Kcal'
                "
              ></KpiBox>
            </div>
            <div class="kpi calorie">
              <KpiBox
                :title="'Avg distance to goal'"
                :value="
                  (
                    getAverageExcludingZeros(foodLogHistory.map((log) => log.calories)) -
                    getAverageExcludingZeros(foodLogHistory.map((log) => log.goalCalories))
                  ).toFixed(1) + ' Kcal'
                "
              ></KpiBox>
            </div>
          </div>
        </div>
        <div class="calorie-chart">
          <XYChart
            :dataset="calorieDataset"
            :x-axis-values="foodLogXAxisLabels"
            :y-min="calorieYMin"
            :y-lable="'Kcal'"
            :minimal-labels="dateRangeChartSelector != '30d' && dateRangeChartSelector != '14d'"
          ></XYChart>
        </div>
      </div>
      <div class="info-container macronutrients">
        <span class="info-container-heading macronutrients">Macronutrients</span>
        <div class="segmented-control macronutrients">
          <SegmentedControl
            :options="Object.keys(dateRangeChartSelectorLookup)"
            v-model="dateRangeChartSelector"
          ></SegmentedControl>
        </div>
        <div class="kpis macronutrients">
          <div class="macronutrients-kpis-first-row">
            <div class="kpi macros fat">
              <KpiBox
                :title="'Avg fat/day'"
                :value="
                  getAverageExcludingZeros(foodLogHistory.map((log) => log.fat)).toFixed(1) + ' g'
                "
              ></KpiBox>
            </div>
            <div class="kpi macros fat">
              <KpiBox
                :title="'Avg distance to goal'"
                :value="
                  (
                    getAverageExcludingZeros(foodLogHistory.map((log) => log.fat)) -
                    getAverageExcludingZeros(foodLogHistory.map((log) => log.goalFat))
                  ).toFixed(1) + ' g'
                "
              ></KpiBox>
            </div>
          </div>

          <div class="macronutrients-kpis-second-row">
            <div class="kpi macros carbs">
              <KpiBox
                :title="'Avg carbs/day'"
                :value="
                  getAverageExcludingZeros(foodLogHistory.map((log) => log.carbs)).toFixed(1) + ' g'
                "
              ></KpiBox>
            </div>
            <div class="kpi macros carbs">
              <KpiBox
                :title="'Avg distance to goal'"
                :value="
                  (
                    getAverageExcludingZeros(foodLogHistory.map((log) => log.carbs)) -
                    getAverageExcludingZeros(foodLogHistory.map((log) => log.goalCarbs))
                  ).toFixed(1) + ' g'
                "
              ></KpiBox>
            </div>
          </div>

          <div class="macronutrients-kpis-third-row">
            <div class="kpi macros protein">
              <KpiBox
                :title="'Avg protein/day'"
                :value="
                  getAverageExcludingZeros(foodLogHistory.map((log) => log.protein)).toFixed(1) +
                  ' g'
                "
              ></KpiBox>
            </div>
            <div class="kpi macros protein">
              <KpiBox
                :title="'Avg distance to goal'"
                :value="
                  (
                    getAverageExcludingZeros(foodLogHistory.map((log) => log.protein)) -
                    getAverageExcludingZeros(foodLogHistory.map((log) => log.goalProtein))
                  ).toFixed(1) + ' g'
                "
              ></KpiBox>
            </div>
          </div>
        </div>
        <div class="macronutrients-chart" v-if="foodLogXAxisLabels.length > 0">
          <XYChart
            :dataset="macronutrientsDataset"
            :x-axis-values="foodLogXAxisLabels"
            :y-min="macronutrientsYMin"
            :y-lable="'g'"
            :show-ledgend="true"
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
const macronutrientsDataset = ref<VueUiXyDatasetItem[]>([])
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
const macronutrientsYMin = ref<number>(0)

const weightYMin = ref<number>(0)
const startingWeight = ref<number>(0)

function getAverageExcludingZeros(items: (number | null)[]): number {
  const nonZeroItems = items.filter((item) => item !== 0 && item !== null)
  return nonZeroItems.length > 0
    ? <number>nonZeroItems.reduce((sum, item) => <number>sum + <number>item, 0) /
        nonZeroItems.length
    : 0 // Return 0 if there are no valid items
}

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
  const calorieData = foodLogHistory.map((x) => x.calories).reverse()
  const goalData = foodLogHistory.map((x) => x.goalCalories).reverse()

  return <VueUiXyDatasetItem[]>[
    {
      name: 'Calories',
      series: calorieData,
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
    {
      name: 'Goal',
      series: goalData,
      color: '#7a7a7a',
      type: 'line',
      shape: 'triangle',
      useArea: false,
      useProgression: false,
      dataLabels: false,
      smooth: true,
      dashed: true,
      useTag: 'none',
    },
  ]
}
const getMacronutrientsDataset = () => {
  if (!user.value) {
    return []
  }
  const proteinData = foodLogHistory.map((x) => x.protein).reverse()
  const fatData = foodLogHistory.map((x) => x.fat).reverse()
  const carbsData = foodLogHistory.map((x) => x.carbs).reverse()
  const proteinGoalData = foodLogHistory.map((x) => x.goalProtein).reverse()
  const fatGoalData = foodLogHistory.map((x) => x.goalFat).reverse()
  const carbsGoalData = foodLogHistory.map((x) => x.goalCarbs).reverse()

  return <VueUiXyDatasetItem[]>[
    {
      name: 'Fat',
      series: fatData,
      color: '#97e6ff',
      type: 'line',
      shape: 'circle',
      useArea: false,
      useProgression: false,
      dataLabels: true,
      smooth: true,
      dashed: false,
      useTag: 'none',
    },
    {
      name: 'Fat goal',
      series: fatGoalData,
      color: '#ccf3ff',
      type: 'line',
      shape: 'triangle',
      useArea: false,
      useProgression: false,
      dataLabels: false,
      smooth: true,
      dashed: true,
      useTag: 'none',
    },
    {
      name: 'Carbohydrates',
      series: carbsData,
      color: '#7b11fd',
      type: 'line',
      shape: 'circle',
      useArea: false,
      useProgression: false,
      dataLabels: true,
      smooth: true,
      dashed: false,
      useTag: 'none',
    },
    {
      name: 'Carbohydrates goal',
      series: carbsGoalData,
      color: '#e3cdfe',
      type: 'line',
      shape: 'triangle',
      useArea: false,
      useProgression: false,
      dataLabels: false,
      smooth: true,
      dashed: true,
      useTag: 'none',
    },
    {
      name: 'Protein',
      series: proteinData,
      color: '#ff4492ff',
      type: 'line',
      shape: 'circle',
      useArea: false,
      useProgression: false,
      dataLabels: true,
      smooth: true,
      dashed: false,
      useTag: 'none',
    },
    {
      name: 'Protein goal',
      series: proteinGoalData,
      color: '#ffcce1',
      type: 'line',
      shape: 'triangle',
      useArea: false,
      useProgression: false,
      dataLabels: false,
      smooth: true,
      dashed: true,
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
    macronutrientsDataset.value = getMacronutrientsDataset()
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
    totalCarbs += (entry.food_item.carbs_per_100 / 100) * entry.quantity
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
.weight-kpis-third-row,
.calories-kpis-first-row,
.macronutrients-kpis-first-row,
.macronutrients-kpis-second-row,
.macronutrients-kpis-third-row {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
}

.kpi {
  height: 5rem;
  width: 100%;
}

.kpi div {
  background-color: var(--color-background-tertiary);
}

.kpi.calorie div {
  background-color: #d6ffb0;
}
.kpi.fat div {
  background-color: #97e6ff;
}
.kpi.carbs div {
  background-color: #dbbdff;
}
.kpi.protein div {
  background-color: #ff93c0;
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

  .kpi {
    height: 3.5rem;
  }
}
</style>
