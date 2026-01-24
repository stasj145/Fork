<template>
  <div class="log-view-root">
    <div class="log-view-content-root" v-if="!loading">
      <div class="weight-info-container">
        <span class="weight-heading">Weight (last 30 entries)</span>
        <div class="weight-chart">
          <XYChart :dataset="weightDataset" :x-axis-values="weightXAxisLabels"></XYChart>
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
import XYChart from '@/components/XYChart.vue'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import type { User } from '@/types/user'
import { computed, onMounted, ref } from 'vue'
import { type VueUiXyDatasetItem } from 'vue-data-ui'

const user = ref<User | null>(null)
const loading = ref<boolean>(true)
const showLoadingError = ref(false)
const errorDetails = ref('')

const weightDataset = computed(() => {
  const seriesData = user.value
    ? user.value.weight_history
        .map((x) => x.weight)
        .reverse()
        .slice(-30, user.value.weight_history.length)
    : []
  return <VueUiXyDatasetItem[]>[
    {
      name: 'Weight',
      series: seriesData,
      color: '#ffcd44',
      type: 'line',
      shape: 'circle',
      useArea: false,
      useProgression: true,
      dataLabels: true,
      smooth: true,
      dashed: false,
      useTag: 'none',
    },
  ]
})

const weightXAxisLabels = computed(() => {
  const xAxisData = user.value
    ? user.value.weight_history
        .map((x) => x.created_at)
        .reverse()
        .slice(-30, user.value.weight_history.length)
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
}
</style>
