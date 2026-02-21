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
                :title="'Avg consumed/day'"
                :value="dataListAverages.caloriesListAvg.toFixed(1) + ' Kcal'"
              ></KpiBox>
            </div>
            <div class="kpi calorie">
              <KpiBox
                :title="'Avg Δ to goal'"
                :value="
                  (dataListAverages.caloriesListAvg - dataListAverages.caloriesGoalListAvg).toFixed(
                    1,
                  ) + ' Kcal'
                "
              ></KpiBox>
            </div>
          </div>
          <div class="calories-kpis-second-row" v-if="user.goals.daily_calorie_burn_target > 0">
            <div class="kpi burned">
              <KpiBox
                :title="'Avg burned/day'"
                :value="dataListAverages.burnedListAvg.toFixed(1) + ' Kcal'"
              ></KpiBox>
            </div>
            <div class="kpi burned">
              <KpiBox
                :title="'Avg Δ to goal'"
                :value="
                  (dataListAverages.burnedListAvg - dataListAverages.burnedGoalListAvg).toFixed(1) +
                  ' Kcal'
                "
              ></KpiBox>
            </div>
          </div>
        </div>
        <div class="calorie-chart" v-if="shouldRenderChart">
          <XYChart
            :dataset="calorieDataset"
            :x-axis-values="foodLogXAxisLabels"
            :y-min="calorieYMin"
            :y-lable="'Kcal'"
            :show-ledgend="true"
            :minimal-labels="dateRangeChartSelector != '30d' && dateRangeChartSelector != '14d'"
            :xAxisRotation="
              dateRangeChartSelector != '30d' && dateRangeChartSelector != '14d' ? -0.1 : 0
            "
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
                :value="dataListAverages.fatListAvg.toFixed(1) + ' g'"
              ></KpiBox>
            </div>
            <div class="kpi macros fat">
              <KpiBox
                :title="'Avg Δ to goal'"
                :value="
                  (dataListAverages.fatListAvg - dataListAverages.fatGoalListAvg).toFixed(1) + ' g'
                "
              ></KpiBox>
            </div>
          </div>

          <div class="macronutrients-kpis-second-row">
            <div class="kpi macros carbs">
              <KpiBox
                :title="'Avg carbs/day'"
                :value="dataListAverages.carbsListAvg.toFixed(1) + ' g'"
              ></KpiBox>
            </div>
            <div class="kpi macros carbs">
              <KpiBox
                :title="'Avg Δ to goal'"
                :value="
                  (dataListAverages.carbsListAvg - dataListAverages.carbsGoalListAvg).toFixed(1) +
                  ' g'
                "
              ></KpiBox>
            </div>
          </div>

          <div class="macronutrients-kpis-third-row">
            <div class="kpi macros protein">
              <KpiBox
                :title="'Avg protein/day'"
                :value="dataListAverages.proteinListAvg.toFixed(1) + ' g'"
              ></KpiBox>
            </div>
            <div class="kpi macros protein">
              <KpiBox
                :title="'Avg Δ to goal'"
                :value="
                  (dataListAverages.proteinListAvg - dataListAverages.proteinGoalListAvg).toFixed(
                    1,
                  ) + ' g'
                "
              ></KpiBox>
            </div>
          </div>
        </div>
        <div class="macronutrients-chart" v-if="shouldRenderChart">
          <XYChart
            :dataset="macronutrientsDataset"
            :x-axis-values="foodLogXAxisLabels"
            :y-min="macronutrientsYMin"
            :y-lable="'g'"
            :show-ledgend="true"
            :minimal-labels="dateRangeChartSelector != '30d' && dateRangeChartSelector != '14d'"
            :xAxisRotation="
              dateRangeChartSelector != '30d' && dateRangeChartSelector != '14d' ? -0.1 : 0
            "
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
import type { ActivityLog } from '@/types/activityLog'
import { type FoodLog } from '@/types/foodLog'
import type { User, WeightHistory } from '@/types/user'
import { computed, onMounted, ref, shallowRef, watch } from 'vue'
import { type VueUiXyDatasetItem } from 'vue-data-ui'

const shouldRenderChart = ref(true)

let weightHistory: LocalWeightHistory[] = []
let foodLogHistory: LocalFoodLogHistory[] = []
let activityLogHistory: LocalActivityLogHistory[] = []

const user = ref<User | null>(null)
const loading = ref<boolean>(true)
const showLoadingError = ref(false)
const errorDetails = ref('')
const calorieDataset = ref<VueUiXyDatasetItem[]>([])
const macronutrientsDataset = shallowRef<VueUiXyDatasetItem[]>([])
const foodLogXAxisLabels = shallowRef<string[]>([])
const dateRangeChartSelector = shallowRef<string>('30d')

const dataLists = shallowRef<DataLists>(getEmptyDataListsObject())
const dataListAverages = shallowRef<DataListAverages>(getEmpytDataListAveragesObject())

interface DataLists {
  caloriesList: (number | null)[]
  caloriesGoalList: (number | null)[]
  fatList: (number | null)[]
  fatGoalList: (number | null)[]
  carbsList: (number | null)[]
  carbsGoalList: (number | null)[]
  proteinList: (number | null)[]
  proteinGoalList: (number | null)[]
  burnedList: (number | null)[]
  burnedGoalList: (number | null)[]
}

interface DataListAverages {
  caloriesListAvg: number
  caloriesGoalListAvg: number
  fatListAvg: number
  fatGoalListAvg: number
  carbsListAvg: number
  carbsGoalListAvg: number
  proteinListAvg: number
  proteinGoalListAvg: number
  burnedListAvg: number
  burnedGoalListAvg: number
}

function getEmpytDataListAveragesObject() {
  return <DataListAverages>{
    caloriesListAvg: 0,
    caloriesGoalListAvg: 0,
    fatListAvg: 0,
    fatGoalListAvg: 0,
    carbsListAvg: 0,
    carbsGoalListAvg: 0,
    proteinListAvg: 0,
    proteinGoalListAvg: 0,
    burnedListAvg: 0,
    burnedGoalListAvg: 0,
  }
}

function getEmptyDataListsObject() {
  return <DataLists>{
    caloriesList: [],
    caloriesGoalList: [],
    fatList: [],
    fatGoalList: [],
    carbsList: [],
    carbsGoalList: [],
    proteinList: [],
    proteinGoalList: [],
    burnedList: [],
    burnedGoalList: [],
  }
}

// TODO: compress all arrays at once instead of individually.
function compressArray(array: (number | null)[], maxLength: number): (number | null)[] {
  if (array.length <= maxLength) return array

  const chunkSize = Math.ceil(array.length / maxLength) || 1
  const compressedArray: (number | null)[] = []

  for (let i = 0; i < array.length; i += chunkSize) {
    const end = Math.min(i + chunkSize, array.length)
    const chunk = array.slice(i, end)

    // Skip if chunk is empty
    if (chunk.length === 0) continue

    let sum = 0
    let count = 0

    for (const value of chunk) {
      if (value !== null && value > 0) {
        sum += value
        count++
      }
    }

    const avg = count > 0 ? sum / count : null

    // Add the average to the compressed array
    compressedArray.push(<number | null>avg)
  }

  return compressedArray
}

function compressLabels(array: string[], maxLength: number): string[] {
  if (array.length <= maxLength) return array

  const chunkSize = Math.ceil(array.length / maxLength) || 1
  const compressedArray: string[] = []

  for (let i = 0; i < array.length; i += chunkSize) {
    const end = Math.min(i + chunkSize, array.length)

    const chunk = array.slice(i, end)

    // Skip if chunk is empty
    if (chunk.length === 0) continue

    const compressionString = chunk[0] + '\n- ' + chunk[chunk.length - 1]
    compressedArray.push(compressionString)
  }

  return compressedArray
}

// Modify the updateListsAndAverages function
async function updateListsAndAverages() {
  const slicedFoodLogHistory = foodLogHistory.slice(
    dateRangeChartSelectorLookup[dateRangeChartSelector.value],
    foodLogHistory.length,
  )
  const slicedActivityLogHistory = activityLogHistory.slice(
    dateRangeChartSelectorLookup[dateRangeChartSelector.value],
    activityLogHistory.length,
  )
  const length = slicedFoodLogHistory.length
  // Pre-allocate arrays
  const caloriesList = []
  const caloriesGoalList = []
  const fatList = []
  const fatGoalList = []
  const carbsList = []
  const carbsGoalList = []
  const proteinList = []
  const proteinGoalList = []
  const burnedList = []
  const burnedGoalList = []
  const xAxisLabels = []

  let caloriesSum = 0
  let caloriesGoalSum = 0
  let fatSum = 0
  let fatGoalSum = 0
  let carbsSum = 0
  let carbsGoalSum = 0
  let proteinSum = 0
  let proteinGoalSum = 0
  let burnedSum = 0
  let burnedGoalSum = 0
  let nonEmptyEntries = 0
  let encounteredNonNullEntry = false
  for (let index = 0; index < length; index++) {
    const foodLog = slicedFoodLogHistory[index]!
    const activityLog = slicedActivityLogHistory[index]!
    if (foodLog.id) {
      encounteredNonNullEntry = true
    }
    if (!encounteredNonNullEntry) {
      continue
    }
    xAxisLabels.push(foodLog.date)
    caloriesList.push(foodLog.calories)
    caloriesGoalList.push(foodLog.goalCalories)
    fatList.push(foodLog.fat)
    fatGoalList.push(foodLog.goalFat)
    carbsList.push(foodLog.carbs)
    carbsGoalList.push(foodLog.goalCarbs)
    proteinList.push(foodLog.protein)
    proteinGoalList.push(foodLog.goalProtein)
    burnedList.push(activityLog.burned)
    burnedGoalList.push(activityLog.goalBurned)
    if (foodLog.id) {
      caloriesSum += <number>foodLog.calories
      caloriesGoalSum += <number>foodLog.goalCalories
      fatSum += <number>foodLog.fat
      fatGoalSum += <number>foodLog.goalFat
      carbsSum += <number>foodLog.carbs
      carbsGoalSum += <number>foodLog.goalCarbs
      proteinSum += <number>foodLog.protein
      proteinGoalSum += <number>foodLog.goalProtein
      burnedSum += <number>activityLog.burned
      burnedGoalSum += <number>activityLog.goalBurned
      nonEmptyEntries++
    }
  }
  // Compute averages
  const avgCalories = nonEmptyEntries > 0 ? caloriesSum / nonEmptyEntries : 0
  const avgCaloriesGoal = nonEmptyEntries > 0 ? caloriesGoalSum / nonEmptyEntries : 0
  const avgFat = nonEmptyEntries > 0 ? fatSum / nonEmptyEntries : 0
  const avgFatGoal = nonEmptyEntries > 0 ? fatGoalSum / nonEmptyEntries : 0
  const avgCarbs = nonEmptyEntries > 0 ? carbsSum / nonEmptyEntries : 0
  const avgCarbsGoal = nonEmptyEntries > 0 ? carbsGoalSum / nonEmptyEntries : 0
  const avgProtein = nonEmptyEntries > 0 ? proteinSum / nonEmptyEntries : 0
  const avgProteinGoal = nonEmptyEntries > 0 ? proteinGoalSum / nonEmptyEntries : 0
  const avgBurned = nonEmptyEntries > 0 ? burnedSum / nonEmptyEntries : 0
  const avgBurnedGoal = nonEmptyEntries > 0 ? burnedGoalSum / nonEmptyEntries : 0

  // Compress arrays if needed
  const maxLength = 100

  const compressedCaloriesList = compressArray(caloriesList, maxLength)
  const compressedCaloriesGoalList = compressArray(caloriesGoalList, maxLength)
  const compressedFatList = compressArray(fatList, maxLength)
  const compressedFatGoalList = compressArray(fatGoalList, maxLength)
  const compressedCarbsList = compressArray(carbsList, maxLength)
  const compressedCarbsGoalList = compressArray(carbsGoalList, maxLength)
  const compressedProteinList = compressArray(proteinList, maxLength)
  const compressedProteinGoalList = compressArray(proteinGoalList, maxLength)
  const compressedBurnedList = compressArray(burnedList, maxLength)
  const compressedBurnedGoalList = compressArray(burnedGoalList, maxLength)

  // Compress the x-axis labels as well
  // const compressedXAxisLabels = compressArray(xAxisLabels as unknown as (number | null)[], maxLength);

  dataLists.value = {
    caloriesList: compressedCaloriesList,
    caloriesGoalList: compressedCaloriesGoalList,
    fatList: compressedFatList,
    fatGoalList: compressedFatGoalList,
    carbsList: compressedCarbsList,
    carbsGoalList: compressedCarbsGoalList,
    proteinList: compressedProteinList,
    proteinGoalList: compressedProteinGoalList,
    burnedList: compressedBurnedList,
    burnedGoalList: compressedBurnedGoalList,
  }
  dataListAverages.value = {
    caloriesListAvg: avgCalories,
    caloriesGoalListAvg: avgCaloriesGoal,
    fatListAvg: avgFat,
    fatGoalListAvg: avgFatGoal,
    carbsListAvg: avgCarbs,
    carbsGoalListAvg: avgCarbsGoal,
    proteinListAvg: avgProtein,
    proteinGoalListAvg: avgProteinGoal,
    burnedListAvg: avgBurned,
    burnedGoalListAvg: avgBurnedGoal,
  }
  // Convert x-axis labels back to string type
  foodLogXAxisLabels.value = compressLabels(xAxisLabels, maxLength)
}

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

interface LocalActivityLogHistory {
  id?: string
  date: string

  burned: number | null
  goalBurned: number | null
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

interface LocalWeightHistory {
  id?: string
  weight: number | null
  created_at: string
}

const weightDataset = computed(() => {
  if (!user.value || !user.value.weight_history) {
    return []
  }
  const seriesData = weightHistory
    .map((x) => x.weight)
    .slice(dateRangeChartSelectorLookup[dateRangeChartSelector.value], weightHistory.length)

  // eslint-disable-next-line
  weightYMin.value =
    Math.floor(Math.round(Math.min(...(<number[]>seriesData).filter((value) => value)) - 1) / 5) * 5

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

  const retDataset = <VueUiXyDatasetItem[]>[
    {
      name: 'Calories consumed',
      series: dataLists.value.caloriesList,
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
      name: 'Consumed goal',
      series: dataLists.value.caloriesGoalList,
      color: '#caff99',
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

  if (user.value.goals.daily_calorie_burn_target > 0) {
    retDataset.push(
      {
        name: 'Calories burned',
        series: dataLists.value.burnedList,
        color: '#5affc3ff',
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
        name: 'Burned goal',
        series: dataLists.value.burnedGoalList,
        color: '#99ffda',
        type: 'line',
        shape: 'triangle',
        useArea: false,
        useProgression: false,
        dataLabels: false,
        smooth: true,
        dashed: true,
        useTag: 'none',
      },
    )
  }

  return retDataset
}
const getMacronutrientsDataset = () => {
  if (!user.value) {
    return []
  }

  return <VueUiXyDatasetItem[]>[
    {
      name: 'Fat',
      series: dataLists.value.fatList,
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
      series: dataLists.value.fatGoalList,
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
      series: dataLists.value.carbsList,
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
      series: dataLists.value.carbsGoalList,
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
      series: dataLists.value.proteinList,
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
      series: dataLists.value.proteinGoalList,
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
      weightHistory.reverse()
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
      foodLogHistory.reverse()
    }

    const activityLogList = await fetchWrapper.get(
      `/api/v1/log/last/activity?n_logs=${<number>dateRangeChartSelectorLookup[dateRangeChartSelector.value] * -1}`,
    )
    if (activityLogList) {
      activityLogHistory = await prepActivityLogsData(activityLogList)
      activityLogHistory.reverse()
    }

    await updateListsAndAverages()
    calorieDataset.value = getCalorieDataset()
    macronutrientsDataset.value = getMacronutrientsDataset()
  } catch (err) {
    console.error('Error loading users log data:', err)
    if (err instanceof Error) {
      showLoadingError.value = true
      errorDetails.value = err.message || err.toString() || 'Unknown error'
    }
  }
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

    if (
      dateRangeChartSelector.value != 'full' &&
      daysDiff > <number>dateRangeChartSelectorLookup[dateRangeChartSelector.value] * -1 + 1
    ) {
      continue
    }

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

    if (
      dateRangeChartSelector.value != 'full' &&
      daysDiff > <number>dateRangeChartSelectorLookup[dateRangeChartSelector.value] * -1 + 1
    ) {
      continue
    }

    if (daysDiff > 1) {
      const currentDate = new Date(prevDate)
      currentDate.setDate(prevDate.getDate() - 1)

      while (currentDate > currDate) {
        result.push(<LocalFoodLogHistory>{
          id: undefined,
          date: formatDate(currentDate),
          calories: null,
          burned: null,
          protein: null,
          fat: null,
          carbs: null,
          goalCalories: null,
          goalBurned: null,
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

async function prepActivityLogsData(
  activityLogs: ActivityLog[],
): Promise<LocalActivityLogHistory[]> {
  if (!activityLogs[0]) {
    return []
  }

  const result: LocalActivityLogHistory[] = [
    await createLocalActivityLogHistoryFromActivityLog(activityLogs[0]),
  ]

  for (let i = 1; i < activityLogs.length; i++) {
    const prev = result[result.length - 1]!
    const curr = activityLogs[i]!

    const prevDate = new Date(prev.date)
    const currDate = new Date(curr.date)

    const daysDiff = (prevDate.getTime() - currDate.getTime()) / (24 * 60 * 60 * 1000)

    if (
      dateRangeChartSelector.value != 'full' &&
      daysDiff > <number>dateRangeChartSelectorLookup[dateRangeChartSelector.value] * -1 + 1
    ) {
      continue
    }

    if (daysDiff > 1) {
      const currentDate = new Date(prevDate)
      currentDate.setDate(prevDate.getDate() - 1)

      while (currentDate > currDate) {
        result.push(<LocalActivityLogHistory>{
          id: undefined,
          date: formatDate(currentDate),
          burned: null,
          goalBurned: null,
        })

        currentDate.setDate(currentDate.getDate() - 1)
      }
    }

    result.push(await createLocalActivityLogHistoryFromActivityLog(curr))
  }

  return result
}

async function createLocalActivityLogHistoryFromActivityLog(
  activityLog: ActivityLog,
): Promise<LocalActivityLogHistory> {
  let totalBurned: number = 0

  for (const entry of activityLog.activity_entries) {
    totalBurned += entry.calories_burned
  }

  return <LocalActivityLogHistory>{
    id: activityLog.id,
    date: activityLog.date,
    burned: totalBurned,
    goalBurned: activityLog.goals.daily_calorie_burn_target,
  }
}

onMounted(async () => {
  await loadUserData()
  await loadLogData()
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
.calories-kpis-second-row,
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
.kpi.burned div {
  background-color: #5affc3ff;
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
