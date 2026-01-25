<template>
  <div class="log-view-root">
    <div class="log-view-content-root" v-if="!loading && user">
      <div class="weight-info-container">
        <span class="weight-heading">Weight</span>
        <SegmentedControl
          class="weight-segmented-control"
          :options="Object.keys(weightChartSelectorLookup)"
          v-model="weightChartSelector"
        ></SegmentedControl>
        <div class="weight-kpis">
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
            :minimal-labels="weightChartSelector != '30d' && weightChartSelector != '14d'"
          ></XYChart>
        </div>
      </div>
    </div>
    <ErrorModal
      v-model="showLoadingError"
      title="Loading Error"
      message="Unable to load user data"
      :details="errorDetails"
    ></ErrorModal>
  </div>
</template>

<script setup lang="ts">
import ErrorModal from '@/components/ErrorModal.vue'
import KpiBox from '@/components/KpiBox.vue'
import SegmentedControl from '@/components/SegmentedControl.vue'
import XYChart from '@/components/XYChart.vue'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import type { User, WeightHistory } from '@/types/user'
import { computed, onMounted, ref } from 'vue'
import { type VueUiXyDatasetItem } from 'vue-data-ui'

let weightHistory: LocalWeightHistory[] = []

const user = ref<User | null>(null)
const loading = ref<boolean>(true)
const showLoadingError = ref(false)
const errorDetails = ref('')
const weightChartSelector = ref<string>('30d')
const weightChartSelectorLookup: { [id: string]: number } = {
  '14d': -14,
  '30d': -30,
  '90d': -90,
  '365d': -365,
  full: 0,
}

const weightYMin = ref<number>(0)
const startingWeight = ref<number>(0)

const weightDataset = computed(() => {
  if (!user.value || !user.value.weight_history) {
    return []
  }
  const seriesData = weightHistory
    .map((x) => x.weight)
    .reverse()
    .slice(weightChartSelectorLookup[weightChartSelector.value], weightHistory.length)

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
        .slice(weightChartSelectorLookup[weightChartSelector.value], weightHistory.length)
    : []

  return xAxisData
})

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

onMounted(async () => {
  loadUserData()
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

.log-view-content-root {
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

.weight-info-container {
  width: 100%;
  height: fit-content;
  border: 1px solid var(--color-accent-secondary);
  padding: 0.5rem;
  border-radius: 0.5rem;
  margin-top: 1.5rem;
}
.weight-heading {
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

.weight-kpis {
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

  .weight-info-container {
    margin-top: 0.5rem;
  }

  .weight-heading {
    font-size: 1rem;
    bottom: 1.25rem;
  }

  .weight-kpis {
    flex-direction: column;
  }

  .weight-kpi {
    height: 3.5rem;
  }

  .weight-segmented-control div button {
    font-size: 0.1rem;
  }
}
</style>
