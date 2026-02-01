<!-- eslint-disable vue/no-mutating-props  -->
<template>
  <div class="food-details-info-root" v-if="selectedFood">
    <div class="segmented-control" v-if="isEditingMode">
      <SegmentedControl
        :options="['Advanced', 'Basic']"
        v-model="selectedMaskType"
      ></SegmentedControl>
    </div>
    <div class="food-img-container" v-if="isEditingMode || selectedFood.img_name">
      <div class="food-img-placeholder" v-if="!selectedFood.img_name">
        <IconImagePlaceholder></IconImagePlaceholder>
      </div>
      <img :src="imageSrc" alt="Food Image" v-if="selectedFood.img_name && imageSrc" />
      <div class="food-img-actions" v-if="isEditingMode">
        <input
          class="food-img-input"
          type="file"
          accept="image/jpeg, image/png"
          @change="handleFileChanged"
        />
        <ErrorModal
          v-model="showUpdatingError"
          title="Updating Error"
          message="Unable to update image."
          :details="errorDetails"
        ></ErrorModal>
        <button
          class="food-img-delete"
          :class="{ 'btn-delete-awaiting-confirmation': deleteConfirmed }"
          @click="deleteImage"
        >
          <span v-if="!deleting">Delete image</span>
          <div v-else class="food-img-delete-spinner">
            <Spinner></Spinner>
          </div>
          <ErrorModal
            v-model="showDeletionError"
            title="Deletion Error"
            message="Unable to delete image."
            :details="errorDetails"
          ></ErrorModal>
        </button>
      </div>
    </div>
    <div class="food-info">
      <div class="food-info-item">
        <label>Name</label>
        <input v-model="selectedFood.name" :disabled="!isEditingMode" />
      </div>
      <div class="food-info-item" v-if="maskTypeAdvanced">
        <label>Description</label>
        <textarea v-model="selectedFood.description" v-auto-resize :disabled="!isEditingMode" />
      </div>
      <div class="food-info-item" v-if="maskTypeAdvanced">
        <label>Brand</label>
        <input v-model="selectedFood.brand" :disabled="!isEditingMode" />
      </div>
    </div>
    <div class="food-nutrition">
      <div v-if="isEditingMode && maskTypeAdvanced" class="food-nutrition-editing-fields">
        <div class="food-nutrition-item">
          <label>Calories/100g</label>
          <input type="number" min="0" max="100" v-model.number="caloriesPer100" />
        </div>
        <div class="food-nutrition-item">
          <label>Protein/100g</label>
          <input type="number" min="0" max="100" v-model.number="proteinPer100" />
        </div>
        <div class="food-nutrition-item">
          <label>Carbs/100g</label>
          <input type="number" min="0" max="100" v-model.number="carbsPer100" />
        </div>
        <div class="food-nutrition-item">
          <label>Fat/100g</label>
          <input type="number" min="0" max="100" v-model.number="fatPer100" />
        </div>
      </div>
      <div v-if="isEditingMode && !maskTypeAdvanced" class="food-nutrition-editing-fields">
        <div class="food-nutrition-item">
          <label>Total Calories</label>
          <input type="number" min="0" max="100" v-model.number="caloriesPerServing" />
        </div>
        <div class="food-nutrition-item">
          <label>Total Protein</label>
          <input type="number" min="0" max="100" v-model.number="proteinPerServing" />
        </div>
        <div class="food-nutrition-item">
          <label>Total Carbohydrates</label>
          <input type="number" min="0" max="100" v-model.number="carbsPerServing" />
        </div>
        <div class="food-nutrition-item">
          <label>Total Fat</label>
          <input type="number" min="0" max="100" v-model.number="fatPerServing" />
        </div>
      </div>

      <div v-if="!isEditingMode" class="food-nutrition-display">
        <div class="gauge-chart">
          <GaugeChart
            :show-animation="showChartAnimation"
            :dataset="{
              value: selectedFood.calories_per_100,
              min: 0,
              max: 500,
              rounding: 0,
              suffix: ' Kcal/100g',
              colorMin: '#b3ffb3',
              colorMax: '#ff0000',
            }"
          ></GaugeChart>
        </div>
        <div class="sparkbar-chart">
          <SparkbarChart
            :show-animation="showChartAnimation"
            :dataset="[
              {
                name: 'Fat per 100g',
                value: selectedFood.fat_per_100,
                color: '#97e6ff',
                prefix: '',
                suffix: 'g',
                rounding: 2,
              },

              {
                name: 'Carbs per 100g',
                value: selectedFood.carbs_per_100,
                color: '#7b11fd',
                prefix: '',
                suffix: 'g',
                rounding: 2,
              },
              {
                name: 'Protein per 100g',
                value: selectedFood.protein_per_100,
                color: '#ff4492ff',
                prefix: '',
                suffix: 'g',
                rounding: 2,
              },
            ]"
          />
        </div>
      </div>
    </div>
    <div class="food-properties-info">
      <div class="food-serving-size-info">
        <div class="food-info-item">
          <label v-if="maskTypeAdvanced">Serving size in g</label>
          <label v-else>Amount in g</label>
          <input
            v-model="selectedFood.serving_size"
            type="number"
            min="1"
            max="100"
            :disabled="!isEditingMode"
          />
        </div>
        <div class="food-info-item" v-if="maskTypeAdvanced">
          <label>Serving size unit</label>
          <input v-model="selectedFood.serving_unit" :disabled="!isEditingMode" />
        </div>
      </div>
      <div
        class="food-info-item barcode-container"
        v-if="(selectedFood.barcode || isEditingMode) && maskTypeAdvanced"
      >
        <label>Barcode</label>
        <input v-model="selectedFood.barcode" :disabled="!isEditingMode" />
      </div>
      <div class="toggle-container">
        <div class="toggle-private-container">
          <label class="toggle-private-label">Private</label>
          <ToggleSwitch
            class="toggle-private"
            v-model:state="selectedFood.private"
            :disabled="!isEditingMode"
          ></ToggleSwitch>
        </div>
        <div class="toggle-hidden-container">
          <label class="toggle-hidden-label">Hide from search</label>
          <ToggleSwitch
            class="toggle-hidden"
            v-model:state="selectedFood.hidden"
            :disabled="!isEditingMode"
          ></ToggleSwitch>
        </div>
      </div>
    </div>
    <div
      class="food-ingredients-info"
      v-if="(isEditingMode || selectedFood.ingredients.length > 0) && maskTypeAdvanced"
    >
      <label class="food-ingredients-label">Ingredients</label>
      <div class="ingredients-summary" v-if="selectedFood.ingredients.length > 0">
        <div class="summary-row">
          <span class="summary-label">Total Weight:</span>
          <span class="summary-value">{{ totalWeight }}g</span>
        </div>
        <div class="summary-row">
          <span class="summary-label">Total Calories:</span>
          <span class="summary-value">{{ Math.round(totalCalories) }} Kcal</span>
        </div>
        <div class="summary-row">
          <span class="summary-label">Total Protein:</span>
          <span class="summary-value">{{ totalProteins.toFixed(1) }}g</span>
        </div>
        <div class="summary-row">
          <span class="summary-label">Total Carbs:</span>
          <span class="summary-value">{{ totalCarbs.toFixed(1) }}g</span>
        </div>
        <div class="summary-row">
          <span class="summary-label">Total Fat:</span>
          <span class="summary-value">{{ totalFat.toFixed(1) }}g</span>
        </div>
        <button class="auto-fill-btn" @click="autoFillNutrients" v-if="isEditingMode">
          Auto-fill nutrients
        </button>
      </div>
      <FoodItemSummary
        v-for="ingredient in selectedFood.ingredients"
        :key="ingredient.ingredient_id"
        :ingredient-entry="ingredient"
        :disable-change-overlay="!isEditingMode"
        @remove-ingredient="removeIngredient(ingredient)"
        @entry-edit-requested="handleIngredientEditRequest(ingredient)"
      ></FoodItemSummary>
      <button class="add-food-ingredient-btn" @click="handleAddIngredient" v-if="isEditingMode">
        <IconAdd></IconAdd>
      </button>
    </div>
  </div>
</template>

<!-- eslint-disable vue/no-mutating-props  -->
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import type { Food, Ingredient } from '@/types/food'
import SparkbarChart from '@/components/SparkbarChart.vue'
import GaugeChart from '@/components/GaugeChart.vue'
import ToggleSwitch from '../ToggleSwitch.vue'
import IconAdd from '../icons/IconAdd.vue'
import FoodItemSummary from '../FoodItemSummary.vue'
import SegmentedControl from '../SegmentedControl.vue'
import IconImagePlaceholder from '../icons/IconImagePlaceholder.vue'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import Spinner from '../Spinner.vue'
import ErrorModal from '../ErrorModal.vue'

const deleteConfirmed = ref<boolean>(false)
const deleting = ref<boolean>(false)
const showDeletionError = ref<boolean>(false)
const showUpdatingError = ref<boolean>(false)
const errorDetails = ref<string>('N/A')
const selectedMaskType = ref<string>('Advanced')
const imageSrc = ref<string>('')

const selectedFood = defineModel<Food | null>('selectedFood')

defineProps({
  isEditingMode: {
    type: Boolean,
    default: false,
  },
  showChartAnimation: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['ingredient-edit-requested', 'ingredient-add-requested'])

const vAutoResize = {
  mounted(el: HTMLTextAreaElement) {
    el.style.boxSizing = 'border-box'

    const resize = () => {
      el.style.height = 'auto'
      el.style.height = el.scrollHeight + 2 + 'px'
    }

    el.addEventListener('input', resize)
    resize() // Initial resize
  },
}

const maskTypeAdvanced = computed(() => {
  return selectedMaskType.value == 'Advanced'
})

// Helper function to create nutrient computed properties
function createNutrientComputed(nutrient: 'calories' | 'protein' | 'carbs' | 'fat') {
  const perServingKey = `${nutrient}_per_serving` as keyof Food
  const per100Key = `${nutrient}_per_100` as keyof Food

  return computed({
    get: () => {
      if (!selectedFood.value) return 0
      if (selectedFood.value[perServingKey]) {
        console.log('Exists')
        return selectedFood.value[perServingKey]
      }
      if (selectedFood.value) {
        console.log('recalculating')
        if (
          selectedFood.value.serving_size &&
          selectedFood.value.serving_size > 0 &&
          selectedFood.value[per100Key]
        ) {
          const per100Value = selectedFood.value[per100Key]
          const servingSize = selectedFood.value.serving_size
          if (per100Value !== undefined && servingSize !== undefined) {
            ;(selectedFood.value[perServingKey] as number) =
              (<number>per100Value / 100) * servingSize
            return selectedFood.value[perServingKey]
          }
        }
      }
      return 0
    },
    set: (value) => {
      if (selectedFood.value && value !== undefined) {
        ;(selectedFood.value[perServingKey] as number) = <number>value
        if (selectedFood.value.serving_size && selectedFood.value.serving_size > 0) {
          ;(selectedFood.value[per100Key] as number) =
            (<number>value / selectedFood.value.serving_size) * 100
        }
      }
    },
  })
}

// Helper function to create nutrient computed properties for the reverse direction
function createNutrientComputedReverse(nutrient: 'calories' | 'protein' | 'carbs' | 'fat') {
  const perServingKey = `${nutrient}_per_serving` as keyof Food
  const per100Key = `${nutrient}_per_100` as keyof Food

  return computed({
    get: () => selectedFood.value?.[per100Key],
    set: (value) => {
      if (selectedFood.value && value !== undefined) {
        ;(selectedFood.value[per100Key] as number) = <number>value
        if (selectedFood.value.serving_size && selectedFood.value.serving_size > 0) {
          ;(selectedFood.value[perServingKey] as number) =
            (<number>value / 100) * selectedFood.value.serving_size
        }
      }
    },
  })
}

// Computed properties to automatically calculate missing values
const caloriesPerServing = createNutrientComputed('calories')
const proteinPerServing = createNutrientComputed('protein')
const carbsPerServing = createNutrientComputed('carbs')
const fatPerServing = createNutrientComputed('fat')

// Computed properties to automatically calculate per_serving when per_100 is provided
const caloriesPer100 = createNutrientComputedReverse('calories')
const proteinPer100 = createNutrientComputedReverse('protein')
const carbsPer100 = createNutrientComputedReverse('carbs')
const fatPer100 = createNutrientComputedReverse('fat')

const totalWeight = computed(() => {
  if (!selectedFood.value) return 0
  return selectedFood.value.ingredients.reduce(
    (total, ingredient) => total + ingredient.quantity,
    0,
  )
})

const totalCalories = computed(() => {
  if (!selectedFood.value) return 0
  return selectedFood.value.ingredients.reduce((total, ingredient) => {
    const calories = (ingredient.ingredient.calories_per_100 * ingredient.quantity) / 100
    return total + calories
  }, 0)
})

const totalProteins = computed(() => {
  if (!selectedFood.value) return 0
  return selectedFood.value.ingredients.reduce((total, ingredient) => {
    const proteins = (ingredient.ingredient.protein_per_100 * ingredient.quantity) / 100
    return total + proteins
  }, 0)
})

const totalCarbs = computed(() => {
  if (!selectedFood.value) return 0
  return selectedFood.value.ingredients.reduce((total, ingredient) => {
    const carbs = (ingredient.ingredient.carbs_per_100 * ingredient.quantity) / 100
    return total + carbs
  }, 0)
})

const totalFat = computed(() => {
  if (!selectedFood.value) return 0
  return selectedFood.value.ingredients.reduce((total, ingredient) => {
    const fat = (ingredient.ingredient.fat_per_100 * ingredient.quantity) / 100
    return total + fat
  }, 0)
})

// Function to auto-fill nutrient information based on ingredients
const autoFillNutrients = () => {
  if (!selectedFood.value) return

  selectedFood.value.calories_per_100 =
    Math.round((totalCalories.value / totalWeight.value) * 100) || 0
  selectedFood.value.protein_per_100 =
    Number(((totalProteins.value / totalWeight.value) * 100).toFixed(2)) || 0
  selectedFood.value.carbs_per_100 =
    Number(((totalCarbs.value / totalWeight.value) * 100).toFixed(2)) || 0
  selectedFood.value.fat_per_100 =
    Number(((totalFat.value / totalWeight.value) * 100).toFixed(2)) || 0
}

const removeIngredient = (ingredientToRemove: Ingredient) => {
  if (selectedFood.value) {
    selectedFood.value.ingredients = selectedFood.value?.ingredients.filter(
      (ingredient) => ingredient.ingredient_id != ingredientToRemove.ingredient_id,
    )
  }
}

const handleIngredientEditRequest = (ingredientToEdit: Ingredient) => {
  emit('ingredient-edit-requested', ingredientToEdit)
}

const handleAddIngredient = () => {
  emit('ingredient-add-requested')
}

// Watch for serving size changes to properly recalculate values
watch(
  () => selectedFood.value?.serving_size,
  (newSize, oldSize) => {
    if (newSize !== oldSize && newSize !== undefined && newSize > 0 && selectedFood.value) {
      if (!maskTypeAdvanced.value) {
        if (selectedFood.value.calories_per_serving !== undefined) {
          selectedFood.value.calories_per_100 =
            (selectedFood.value.calories_per_serving / newSize) * 100
        }
        if (selectedFood.value.protein_per_serving !== undefined) {
          selectedFood.value.protein_per_100 =
            (selectedFood.value.protein_per_serving / newSize) * 100
        }
        if (selectedFood.value.carbs_per_serving !== undefined) {
          selectedFood.value.carbs_per_100 = (selectedFood.value.carbs_per_serving / newSize) * 100
        }
        if (selectedFood.value.fat_per_serving !== undefined) {
          selectedFood.value.fat_per_100 = (selectedFood.value.fat_per_serving / newSize) * 100
        }
      }
    }
  },
)

async function deleteImage() {
  if (!deleteConfirmed.value) {
    deleteConfirmed.value = true
    return
  }

  deleting.value = true
  if (!selectedFood.value?.img_name) {
    deleting.value = false
    deleteConfirmed.value = false
    return
  }

  try {
    await fetchWrapper.delete(`/api/v1/food/item/${selectedFood.value.id}/image`)
  } catch (err) {
    if (err instanceof Error) {
      showDeletionError.value = true
      errorDetails.value = err.message || 'N/A'
    }
  } finally {
    deleting.value = false
    deleteConfirmed.value = false
  }
}

async function handleFileChanged($event: Event) {
  const target = $event.target as HTMLInputElement
  if (target && target.files) {
    await updateImage(target.files[0]!)
  }
}

async function updateImage(image: File) {
  if (!image || !selectedFood.value) {
    return
  }

  try {
    const formData = new FormData()
    formData.append('file', image)

    await fetchWrapper.put(`/api/v1/food/item/${selectedFood.value.id}/image`, formData)
  } catch (err) {
    if (err instanceof Error) {
      showUpdatingError.value = true
      errorDetails.value = err.message || 'N/A'
    }
  } finally {
    deleteConfirmed.value = false
  }
}

async function getImage() {
  if (!selectedFood.value || !selectedFood.value.img_name) {
    return
  }

  try {
    const imgResp = await fetchWrapper.get(
      `/api/v1/food/item/${selectedFood.value.id}/image?size=large`,
    )
    const imgBlob = new Blob([imgResp], { type: 'image/jpeg' })
    imageSrc.value = URL.createObjectURL(imgBlob)
  } catch (err) {
    if (err instanceof Error) {
      console.warn('Could not load: ' + err.message)
    }
  }
}

onMounted(async () => {
  getImage()
})
</script>

<style lang="css" scoped>
.food-details-info-root {
  display: flex;
  flex-direction: column;
  justify-content: start;
  align-items: start;
  width: calc(var(--main-content-width) - 1rem);
  max-width: 1200px;
  min-height: calc(var(--main-content-height) - 2rem);
  background-color: var(--color-background-secondary);
  border-radius: 0.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 0.5rem;
  padding-bottom: 5rem; /* padding for bottom buttons*/
}

.segmented-control {
  width: 100%;
  height: 2rem;
  margin-bottom: 0.5rem;
}

.food-img-container {
  width: 100%;
  height: 5rem;
  display: flex;
  flex-direction: row;
  margin-bottom: 0.5rem;
  justify-content: center;
}

.food-img-placeholder,
.food-img {
  height: 5rem;
  width: 5rem;
}

.food-img-placeholder * {
  color: var(--color-text-secondary);
}

.food-img-actions {
  display: flex;
  flex-direction: column;
  height: 100%;
  justify-content: space-evenly;
  padding-left: 0.5rem;
}

.food-img-input {
}

.food-img-delete {
  height: 2rem;
  width: 8rem;
  font-size: 1rem;
  background-color: var(--color-accent-secondary);
  border: 1px solid var(--color-accent-primary);
  border-radius: 0.25rem;
  background-color: #ffa9a9ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.food-img-delete.btn-delete-awaiting-confirmation {
  background-color: rgb(255, 0, 0);
}

.food-img-delete-spinner {
  height: 1.5rem;
  width: 1.5rem;
}

.food-info {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--color-accent-secondary);
  padding: 0.5rem;
  border-radius: 0.5rem;
  width: 100%;
}

.food-info-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 0.5rem;
}
.food-info-item label {
  position: relative;
  bottom: -0.4rem;
  color: var(--color-text-primary);
  font-size: 1rem;
  font-weight: bold;
  margin-left: 0.5rem;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
  background-color: var(--color-background-secondary);
  width: fit-content;
  margin-top: -0.4rem;
}

.food-info-item input,
.food-info-item textarea {
  color: var(--color-text-primary);
  border: 1px solid var(--color-accent-secondary);
  padding: 0.5rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.food-info-item textarea {
  max-height: 10rem;
}

.food-nutrition {
  display: flex;
  flex-direction: column;
  margin-top: 0.5rem;
  border: 1px solid var(--color-accent-secondary);
  padding: 0.5rem;
  border-radius: 0.5rem;
  width: 100%;
}

.food-nutrition-editing-fields {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: auto auto;
  column-gap: 0.5rem;
  width: 100%;
}
.food-nutrition-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 0.5rem;
  width: 100%;
  justify-content: end;
}

.food-nutrition-item label {
  position: relative;
  bottom: -0.4rem;
  color: var(--color-text-primary);
  font-size: 1rem;
  font-weight: bold;
  margin-left: 0.5rem;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
  background-color: var(--color-background-secondary);
  width: fit-content;
  margin-top: -0.4rem;
}

.food-nutrition-item input {
  color: var(--color-text-primary);
  border: 1px solid var(--color-accent-secondary);
  padding: 0.5rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  width: 100%;
  transition: border-color 0.3s;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: var(--color-accent-primary);
}

.food-nutrition-display {
  width: 100%;
  display: grid;
  column-gap: 2.5%;
  grid-template-columns: 30% 65%;
}

.food-nutrition-display .gauge-chart {
  width: 100%;
}

.food-nutrition-display .sparkbar-chart {
  width: 100%;
}

.food-properties-info {
  display: flex;
  flex-direction: column;
  align-items: start;
  width: 100%;
  height: 100%;
  padding: 0.5rem;
  margin-top: 0.5rem;
  border: 1px solid var(--color-accent-secondary);
  border-radius: 0.5rem;
}

.food-serving-size-info {
  display: flex;
  flex-direction: row;
  align-items: start;
  gap: 0.25rem;
  width: 100%;
  height: 100%;
}

.food-serving-size-info .food-info-item {
  width: 100%;
}

.food-serving-size-info .food-info-item:nth-child(2) {
  width: 50%;
}

.barcode-container {
  width: 100%;
}

.toggle-container {
  display: flex;
  width: 100%;
  flex-direction: row;
  justify-content: start;
}

.toggle-private-container,
.toggle-hidden-container {
  width: 50%;
  display: flex;
  flex-direction: row;
  align-items: center;
}

.toggle-private-label,
.toggle-hidden-label {
  color: var(--color-text-primary);
  font-size: 1rem;
  font-weight: bold;
  margin-right: 0.5rem;
  margin-left: 0.5rem;
}

.food-ingredients-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: 100%;
  padding: 0rem 0.5rem 0.5rem 0.5rem;
  margin-top: 0.5rem;
  border: 1px solid var(--color-accent-secondary);
  border-radius: 0.5rem;
  margin-top: 1rem;
  gap: 0.5rem;
}

.food-ingredients-label {
  align-self: start;
  position: relative;
  top: -0.7rem;
  left: -0.5rem;
  margin-bottom: -0.5rem;
  color: var(--color-text-primary);
  font-size: 1rem;
  font-weight: bold;
  margin-left: 0.5rem;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
  background-color: var(--color-background-secondary);
  width: fit-content;
}

.ingredients-summary {
  width: 100%;
  background-color: var(--color-background-tertiary);
  border-radius: 0.5rem;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}

.summary-label {
  font-weight: bold;
  color: var(--color-text-primary);
}

.summary-value {
  color: var(--color-text-primary);
}

.auto-fill-btn {
  width: 100%;
  padding: 0.5rem;
  background-color: var(--color-accent-primary);
  border: 1px solid var(--color-accent-secondary);
  border-radius: 0.5rem;
  color: var(--color-black);
  font-weight: bold;
  margin-top: 0.5rem;
}

.add-food-ingredient-btn {
  width: 2rem;
  height: 2rem;
  background-color: var(--color-accent-secondary);
  border: 1px solid var(--color-accent-primary);
  border-radius: 1rem;
}

@media (max-width: 480px) {
  .food-details-info-root {
    min-height: calc(var(--main-content-height) - 1rem);
    padding-bottom: 4rem;
  }

  .food-nutrition-display {
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }

  .food-nutrition-display .gauge-chart {
    width: 100%;
  }
}
</style>
