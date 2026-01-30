<template>
  <div class="food-view-root" :class="{ ingredientsmode: isAddIngredientMode }">
    <div v-if="!selectedFood" class="food-view-content">
      <!-- Barcode Scanner Modal -->
      <BarcodeScanner
        v-if="showScanner"
        @barcode-scanned="handleBarcodeScanned"
        @close="showScanner = false"
      />
      <span class="parent-food-note" v-if="parentFood">
        Adding ingredient to: {{ parentFood.name }}</span
      >
      <div class="search-root">
        <div class="search-bar-container">
          <input
            type="text"
            v-model="searchQuery"
            @input="handleSearch"
            @keydown.enter="submitSearch"
            placeholder="Search for food..."
            class="search-input"
          />
          <button @click="clearSearch" class="search-clear-btn" v-if="searchQuery">&times;</button>
        </div>
        <button @click="submitSearch" class="search-submit-btn"><IconSearch></IconSearch></button>
        <select class="search-type-select" v-model="searchType">
          <option class="search-type-option" value="local">local</option>
          <option class="search-type-option" value="personal">personal</option>
          <option class="search-type-option" value="tandoor">tandoor</option>
          <option class="search-type-option" value="openfoodfacts">online</option>
        </select>
        <button class="barcode-search-btn" @click="openBarcodeScanner">
          <IconBarcode></IconBarcode>
        </button>
      </div>
      <div class="results-root">
        <div class="no-results" v-if="!showResults">
          <span class="no-results-text" >Search for a food to start...</span>
          <div class="last-logged-results-container">
            <span class="last-logged-results-container-heading">Recent food</span>
            <div v-if="loadingLastLogged" class="results-loading">Loading recently logged food...</div>
            <div v-else-if="lastLoggedFood.length > 0" class="results-list">
              <div
                v-for="food in lastLoggedFood"
                :key="food.id"
                class="result-item"
                @click="selectFood(food)"
              >
                <div class="food-name">{{ food.name }}</div>
                <div class="food-summary-details">
                  <span>Calories: {{ food.calories_per_100.toFixed(0) }}/100g</span>
                </div>
              </div>
            </div>
            <span v-else>No recent food found</span>
          </div>
        </div>
        <div class="results-container" v-if="showResults">
          <div v-if="loading" class="results-loading">Searching...</div>
          <div v-else-if="searchResults.length > 0" class="results-list">
            <div
              v-for="food in searchResults"
              :key="food.id"
              class="result-item"
              @click="selectFood(food)"
            >
              <div class="food-name">{{ food.name }}</div>
              <div class="food-summary-details">
                <span>Calories: {{ food.calories_per_100.toFixed(0) }}/100g</span>
              </div>
            </div>
          </div>
          <span v-else>Nothing found</span>
        </div>
      </div>
      <div class="button-root">
        <button
          class="btn-ingredient-mode-back"
          v-if="isAddIngredientMode"
          @click="ingredientModeBack"
        >
          <IconBack></IconBack>
        </button>
        <button class="btn-add" @click="openAddFood()">
          <IconAdd></IconAdd>
        </button>
      </div>
    </div>
    <div v-if="selectedFood" class="food-details-root">
      <FoodDetails
        v-model:selectedFood="selectedFood"
        v-model:creationMode="addMode"
        v-model:ingredient-parent="parentFood"
        @food-deleted="handleFoodDeleted"
        @ingredient-added="ingredientModeBack"
        @back-requested="closeFoodDetails"
      ></FoodDetails>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import type { Food } from '@/types/food'
import { createEmptyFood } from '@/types/food'
import FoodDetails from '@/components/FoodDetails/FoodDetails.vue'

import IconBarcode from '@/components/icons/IconBarcode.vue'
import IconAdd from '@/components/icons/IconAdd.vue'
import IconSearch from '@/components/icons/IconSearch.vue'
import IconBack from '@/components/icons/IconBack.vue'
import BarcodeScanner from '@/components/BarcodeScanner.vue'

const searchQuery = ref('')
const searchCode = ref('')
const searchResults = ref<Food[]>([])
const lastLoggedFood = ref<Food[]>([])
const loading = ref(false)
const loadingLastLogged = ref(false)
const showResults = ref(false)
const showResultsLastLogged = ref(false)
const debounceTimer = ref<number | null>(null)
const selectedFood = ref<Food | null>(null)
const addMode = ref(false)
const searchType = ref('local')
const showScanner = ref(false)

const parentFood = defineModel<Food | null>('parentFood', { default: null })

const emits = defineEmits(['close-add-ingredients'])

defineProps({
  isAddIngredientMode: {
    type: Boolean,
    default: false,
  },
})

interface foodSearch {
  query: string | undefined
  code: string | undefined
  source: string
  limit: number
}

function closeFoodDetails() {
  selectedFood.value = null
  addMode.value = false
}

const selectFood = (food: Food) => {
  selectedFood.value = food
}

const handleSearch = () => {
  let debounceTimeout = 300

  if (searchType.value == 'openfoodfacts') {
    // in case of openfoodfacts search, set the debounce timer WAY higher than normal to prevent excessive API requests
    debounceTimeout = 2000
  }
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
  if (!searchQuery.value.trim() && !searchCode.value) return

  loading.value = true
  showResults.value = true

  const query: foodSearch = {
    query: searchQuery.value != '' ? searchQuery.value : undefined,
    code: searchCode.value != '' ? searchCode.value : undefined,
    source: searchType.value,
    limit: 20,
  }

  try {
    const results = await fetchWrapper.post(`/api/v1/food/search`, query)
    searchResults.value = results || []
  } catch (error) {
    console.error('Search error:', error)
    searchResults.value = []
  } finally {
    loading.value = false
    searchCode.value = ''
  }
}

const getLastLoggedFood = async () => {
  loadingLastLogged.value = true
  showResultsLastLogged.value = true

  try {
    const results = await fetchWrapper.get(`/api/v1/food/last_logged?n_items=20`)
    lastLoggedFood.value = results || []
  } catch (error) {
    console.error('Search error:', error)
    lastLoggedFood.value = []
  } finally {
    loadingLastLogged.value = false
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  clearResults()
}

const openAddFood = () => {
  selectedFood.value = createEmptyFood()
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

const handleFoodDeleted = (foodId: string) => {
  closeFoodDetails()
  searchResults.value = searchResults.value.filter((food) => food.id !== foodId)
}

const handleBarcodeScanned = async (barcode: string) => {
  searchQuery.value = ''
  searchCode.value = barcode
  await performSearch()
  if (searchResults.value.length == 1 && searchResults.value[0]) {
    showScanner.value = false
    selectedFood.value = searchResults.value[0]
  }
}

const openBarcodeScanner = () => {
  showScanner.value = true
}

const ingredientModeBack = async () => {
  emits('close-add-ingredients')
}

onMounted(async () => {
  getLastLoggedFood()
})
</script>

<style lang="css" scoped>
.food-view-root {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: var(--main-content-height);
  width: var(--main-content-width);
  background-color: var(--color-background-primary);
  padding: 1rem;
}

.food-view-root.ingredientsmode {
  padding: 0;
}

.food-view-content {
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

.parent-food-note {
  width: 100%;
  padding: 0.25rem;
  margin-bottom: 0.25rem;
  text-align: center;
  border-radius: 0.5rem;
  background-color: var(--color-background-tertiary);
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.no-results{
  display: flex;
  flex-direction: column;
  width: 100%;
  align-items: center;

}

.last-logged-results-container {
  display: flex;
  flex-direction: column;
  align-content: center;
  justify-content: start;
  width: 100%;
  border: 1px solid var(--color-accent-secondary);
  padding: 0.5rem;
  border-radius: 0.5rem;
  margin-top: 1.5rem;
}

.last-logged-results-container-heading {
  color: var(--color-text-heading);
  background-color: var(--color-background-secondary);
  font-weight: bold;
  position: relative;
  bottom: 2rem;
  left: 0.5rem;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
  margin-bottom: -1rem;
  z-index: 10;
  font-size: 2rem;
  width: fit-content;
}

.results-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: start;
  width: 100%;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

.results-list {
  display: flex;
  flex-direction: column;
  align-items: start;
  width: 100%;
  gap: 0.3rem;
}

.result-item {
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

.food-name {
  font-size: 1.25rem;
  color: var(--color-text-primary);
  margin-bottom: 0.1rem;
}

.food-summary-details {
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
  .food-view-root {
    padding: 0.5rem;
  }

  .food-view-content {
    min-height: calc(var(--main-content-height) - 1rem);
  }

  .last-logged-results-container-heading {
    font-size: 1.5rem;
    bottom: 1.6rem;
  }

  .button-root {
    bottom: 1rem;
  }
}
</style>
