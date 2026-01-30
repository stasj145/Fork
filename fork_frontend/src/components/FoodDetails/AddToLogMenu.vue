<!-- eslint-disable vue/no-mutating-props  -->
<template>
  <div class="add-to-log-menu-root">
    <div class="first-two">
      <input
        v-model="foodEntryInfo.quantity"
        class="add-to-log-input"
        type="number"
        min="0.0"
        max="10000"
        step="10"
        :disabled="adding"
      />
      <select v-model="foodEntryInfo.unit" class="add-to-log-select-unit" :disabled="adding">
        <option value="g">g</option>
        <option value="serving">{{ selectedFood.serving_unit }}</option>
        <option value="calories">Calories</option>
        <option value="fat">Fat</option>
        <option value="carbs">Carbs</option>
        <option value="protein">Protein</option>
      </select>
    </div>
    <div class="last-three">
      <select
        v-model="foodEntryInfo.meal_type"
        class="add-to-log-select-meal-type"
        :disabled="adding"
      >
        <option value="breakfast">Breakfast</option>
        <option value="lunch">Lunch</option>
        <option value="dinner">Dinner</option>
        <option value="snack">Snack</option>
      </select>
      <button class="add-to-log-btn" @click="handleEatButton()" :disabled="adding">
        <IconEat v-if="!adding"></IconEat>
        <Spinner v-else></Spinner>
        <ErrorModal
          v-model="showAddingOrUpdatingError"
          title="Food Entry Error"
          message="Unable to create new food entry or update existing one."
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
import { onMounted, ref } from 'vue'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import { getFormattedDate } from '@/helpers/utils'
import type { Food } from '@/types/food'
import IconCancel from '@/components/icons/IconCancel.vue'
import ErrorModal from '@/components/ErrorModal.vue'
import Spinner from '@/components/Spinner.vue'
import IconEat from '../icons/IconEat.vue'
import type { FoodEntry } from '@/types/foodLog'

const selectedFood = defineModel<Food>('selectedFood', { required: true })
const logEntry = defineModel<FoodEntry | null>('logEntry', { default: null })

const emit = defineEmits(['close-requested', 'log-updated'])

const showAddingOrUpdatingError = ref(false)
const errorDetails = ref('N/A')
const adding = ref(false)

const placeholder_id = 'PLACEHOLDER_ID_ITEM_NOT_IN_LOCAL_DB'

interface FoodEntryInfo {
  quantity: number
  unit: string
  meal_type: string
}

const foodEntryInfo = ref<FoodEntryInfo>({
  quantity: 1.0,
  unit: 'serving',
  meal_type: getDefaultMealType(),
})

function getDefaultMealType(): string {
  const currentHour = new Date().getHours()

  if (currentHour >= 5 && currentHour < 11) {
    return 'breakfast'
  } else if (currentHour >= 11 && currentHour < 16) {
    return 'lunch'
  } else if (currentHour >= 16 && currentHour < 22) {
    return 'dinner'
  } else {
    return 'snack' // 22:00 - 4:59
  }
}
function emitDone() {
  emit('log-updated')
}

async function handleEatButton() {
  addOrUpdateFoodInLog()
}

async function addOrUpdateFoodInLog() {
  adding.value = true
  try {
    if (!selectedFood.value || !selectedFood.value.id) {
      throw Error('No food selected')
    }
    if (selectedFood.value.id == placeholder_id) {
      // create/save food first if it has a placeholder id.
      await saveFood(selectedFood.value)
    }

    const quantity: number = await calculateQuantity()
    if (logEntry.value) {
      //update
      await APIAddOrUpdateFoodEntry(
        quantity,
        foodEntryInfo.value.meal_type,
        null,
        logEntry.value.id,
      )
    } else {
      //create
      await APIAddOrUpdateFoodEntry(quantity, foodEntryInfo.value.meal_type, selectedFood.value.id)
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

async function calculateQuantity() {
  const nutrientOptions = ['calories_per_100', 'fat_per_100', 'carbs_per_100', 'protein_per_100']

  if (foodEntryInfo.value.unit == 'serving') {
    return foodEntryInfo.value.quantity * selectedFood.value.serving_size
  } else if (nutrientOptions.includes(foodEntryInfo.value.unit + '_per_100')) {
    const per_100Value = selectedFood.value[(foodEntryInfo.value.unit + '_per_100') as keyof Food]

    // Check if per_100Value is a valid number
    if (typeof per_100Value !== 'number' || per_100Value === 0) {
      throw new Error(`Invalid value for ${foodEntryInfo.value.unit}_per_100: ${per_100Value}`)
    }

    const multiplier: number = 100 / per_100Value
    return Number((foodEntryInfo.value.quantity * multiplier).toFixed(1))
  } else {
    return foodEntryInfo.value.quantity
  }
}

async function saveFood(updatedFood: Food) {
  try {
    if (updatedFood.barcode?.trim() == '') {
      updatedFood.barcode = null
    }
    const results: Food = await fetchWrapper.post('/api/v1/food/item/', updatedFood)
    selectedFood.value = results
  } catch (err) {
    if (err instanceof Error) {
      showAddingOrUpdatingError.value = true
      errorDetails.value = err.message || 'N/A'
    }
  }
}

async function APIAddOrUpdateFoodEntry(
  quantity: number,
  mealType: string,
  foodId: string | null = null,
  logEntryId: string | null = null,
) {
  if (foodId) {
    //create
    const body = { food_id: foodId, quantity: quantity, meal_type: mealType }
    await fetchWrapper.post(`/api/v1/log/day/${getFormattedDate()}/food`, body)
  } else if (logEntryId) {
    //update
    const body = { meal_type: foodEntryInfo.value.meal_type, quantity: quantity }
    await fetchWrapper.patch(`/api/v1/log/day/${getFormattedDate()}/food/${logEntryId}`, body)
  } else {
    showAddingOrUpdatingError.value = true
    errorDetails.value =
      'APIAddOrUpdateFoodEntry needs either foodId or logEntryId but neither was provided.'
  }
}

function setupLogUpdateMode(logEntry: FoodEntry) {
  foodEntryInfo.value.meal_type = logEntry.meal_type
  if (logEntry.quantity % logEntry.food_item.serving_size === 0) {
    foodEntryInfo.value.unit = 'serving'
    foodEntryInfo.value.quantity = logEntry.quantity / logEntry.food_item.serving_size
  } else {
    foodEntryInfo.value.unit = 'g'
    foodEntryInfo.value.quantity = logEntry.quantity
  }
}

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

.add-to-log-menu-root .first-two,
.add-to-log-menu-root .last-three {
  display: flex;
  flex-direction: row;
  height: 100%;
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

.add-to-log-input {
  color: var(--color-black);
  background-color: var(--color-accent-primary);
  border: none;
  box-shadow: 0 0 1px 1px var(--color-accent-primary);
  padding: 0.5rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.3s;
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

  .add-to-log-menu-root .last-three {
    margin-top: 0.5rem;
  }

  .add-to-log-select-meal-type {
    width: 100%;
    margin-left: 0;
  }

  .add-to-log-input,
  .add-to-log-select-unit {
    width: 50%;
  }

  .add-to-log-btn-cancel,
  .add-to-log-btn {
    width: 4rem;
  }
}
</style>
