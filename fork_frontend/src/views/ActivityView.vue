<template>
  <div class="activity-view-root">
    <ErrorModal
      v-model="showLoadingError"
      title="Loading Error"
      message="Unable to load user data"
      :details="errorDetails"
    ></ErrorModal>
    <div v-if="!selectedActivity && user" class="activity-view-content">
      <div class="search-root">
        <div class="search-bar-container">
          <input
            type="text"
            v-model="searchQuery"
            @input="handleSearch"
            @keydown.enter="submitSearch"
            placeholder="Search for activity..."
            class="search-input"
          />
          <button @click="clearSearch" class="search-clear-btn" v-if="searchQuery">&times;</button>
        </div>
        <button @click="submitSearch" class="search-submit-btn"><IconSearch></IconSearch></button>
        <select class="search-type-select" v-model="searchType">
          <option class="search-type-option" value="local">local</option>
          <option class="search-type-option" value="personal">personal</option>
        </select>
      </div>
      <div class="results-root">
        <span class="no-results-text" v-if="!showResults">Search for an activity to start...</span>
        <div class="results-container" v-if="showResults">
          <div v-if="loading" class="results-loading">Searching...</div>
          <div v-else-if="searchResults.length > 0" class="results-list">
            <div
              v-for="activity in searchResults"
              :key="activity.id"
              class="result-item"
              @click="selectActivity(activity)"
            >
              <div class="activity-name">{{ activity.name }}</div>
              <div class="activity-summary-details">
                <span>
                  {{ (activity.calories_burned_kg_h * user.weight).toFixed(1) }}
                  kcal per hour (at {{ user.weight }}kg)</span
                >
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="button-root">
        <button class="btn-add" @click="openAddActivity()">
          <IconAdd></IconAdd>
        </button>
      </div>
    </div>
    <div v-if="selectedActivity && user" class="activity-details-root">
      <ActivityDetails
        v-model:selected-activity="selectedActivity"
        v-model:creationMode="addMode"
        :user="user"
        @activity-deleted="handleActivityDeleted"
        @back-requested="closeActivityDetails"
      ></ActivityDetails>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import type { Activity } from '@/types/activity'
import { createEmptyActivity } from '@/types/activity'
import type { User } from '@/types/user'
import ErrorModal from '@/components/ErrorModal.vue'
import ActivityDetails from '@/components/ActivityDetails/ActivityDetails.vue'

import IconAdd from '@/components/icons/IconAdd.vue'
import IconSearch from '@/components/icons/IconSearch.vue'

const showLoadingError = ref(false)
const errorDetails = ref('')
const user = ref<User | null>(null)
const searchQuery = ref('')
const searchResults = ref<Activity[]>([])
const loading = ref(false)
const showResults = ref(false)
const debounceTimer = ref<number | null>(null)
const selectedActivity = ref<Activity | null>(null)
const addMode = ref(false)
const searchType = ref('local')

interface ActivitySearch {
  query: string
  source: string
  limit: number
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

function closeActivityDetails() {
  selectedActivity.value = null
  addMode.value = false
}

const selectActivity = (activity: Activity) => {
  selectedActivity.value = activity
}

const handleSearch = () => {
  const debounceTimeout = 300

  if (debounceTimer.value) {
    clearTimeout(debounceTimer.value)
  }

  debounceTimer.value = window.setTimeout(() => {
    if (searchQuery.value.trim()) {
      performSearch()
    } else {
      clearResults()
    }
  }, debounceTimeout)
}

const submitSearch = () => {
  // Clear any existing debounce timer
  if (debounceTimer.value) {
    clearTimeout(debounceTimer.value)
    debounceTimer.value = null
  }

  // Perform search immediately
  if (searchQuery.value.trim()) {
    performSearch()
  } else {
    clearResults()
  }
}

const performSearch = async () => {
  if (!searchQuery.value.trim()) return

  loading.value = true
  showResults.value = true

  const query: ActivitySearch = {
    query: searchQuery.value,
    source: searchType.value,
    limit: 20,
  }

  try {
    const results = await fetchWrapper.post(`/api/v1/activity/search`, query)
    searchResults.value = results || []
  } catch (error) {
    console.error('Search error:', error)
    searchResults.value = []
  } finally {
    loading.value = false
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  clearResults()
}

const openAddActivity = () => {
  selectedActivity.value = createEmptyActivity()
  addMode.value = true
}

const clearResults = () => {
  searchResults.value = []
  showResults.value = false
  if (debounceTimer.value) {
    clearTimeout(debounceTimer.value)
    debounceTimer.value = null
  }
}

const handleActivityDeleted = (activityId: string) => {
  closeActivityDetails()
  searchResults.value = searchResults.value.filter((activity) => activity.id !== activityId)
}

onMounted(async () => {
  loadUserData()
})
</script>

<style lang="css" scoped>
.activity-view-root {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: var(--main-content-height);
  width: var(--main-content-width);
  background-color: var(--color-background-primary);
  padding: 1rem;
}

.activity-view-root.ingredientsmode {
  padding: 0;
}

.activity-view-content {
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
  padding-bottom: 4rem; /* padding for bottom buttons*/
}

.search-root {
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: start;
  align-items: center;
}

.search-bar-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  flex: 1;
}

.search-input {
  width: 100%;
  border: 1px solid var(--color-accent-secondary);
  padding: 0.5rem 1.5rem 0.5rem 1rem;
  font-size: 1rem;
  transition:
    border-color 0.3s,
    box-shadow 0.3s;
  border-radius: 0.5rem 0rem 0rem 0.5rem;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-accent-primary);
  box-shadow: 0 0 2px 0 var(--color-accent-primary);
}

.search-clear-btn {
  position: relative;
  right: 1.5rem;
  border: none;
  background: none;
  width: 0;
  height: 100%;
  font-size: 1.5rem;
  color: var(--color-text-secondary);
}

.search-submit-btn {
  width: 2rem;
  height: calc(2.31rem);
  background-color: var(--color-accent-secondary);
  border: 1px solid var(--color-accent-secondary);
  border-radius: 0rem 0.5rem 0.5rem 0rem;
  cursor: pointer;
}

.search-submit-btn:hover {
  background-color: var(--color-accent-primary);
  border-color: var(--color-accent-primary);
}

.search-type-select {
  margin-left: 0.5rem;
  padding: 0.5rem 0rem 0.5rem 0.5rem;
  font-size: 1rem;
  height: 100%;
  background: None;
  border: 1px solid var(--color-accent-secondary);
  border-radius: 0.5rem;
}

.barcode-search-btn {
  margin-left: 0.5rem;
  padding: 0.25rem;
  height: 100%;
  width: 2rem;
  flex-shrink: 0;
  background: None;
  border: 1px solid var(--color-accent-secondary);
  border-radius: 0.5rem;
}

.results-root {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  margin-top: 1rem;
  align-items: center;
}

.results-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: start;
  width: 100%;
}

.results-list {
  display: flex;
  flex-direction: column;
  align-items: start;
  width: 100%;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

.result-item {
  margin-bottom: 0.3rem;
  width: 100%;
  padding: 0.15rem;
  padding-left: 0.5rem;
  border: 0.15rem solid var(--color-accent-secondary);
  border-radius: 0.5rem;
  background-color: var(--color-background-tertiary);
}

.result-item:hover {
  background-color: var(--color-accent-secondary);
}

.activity-name {
  font-size: 1.25rem;
  color: var(--color-text-primary);
  margin-bottom: 0.1rem;
}

.activity-summary-details {
  font-size: 1rem;
  color: var(--color-text-secondary);
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
  background-color: var(--color-accent-secondary);
  border: 1px solid var(--color-accent-secondary);
  border-radius: 1rem;
}

@media (max-width: 480px) {
  .activity-view-root {
    padding: 0.5rem;
  }

  .activity-view-content {
    min-height: calc(var(--main-content-height) - 1rem);
  }

  .button-root {
    bottom: 1rem;
  }
}
</style>
