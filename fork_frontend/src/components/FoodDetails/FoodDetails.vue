<!-- eslint-disable vue/no-mutating-props  -->
<template>
  <div class="food-details-root" v-if="selectedFood && !isAddIngredientsMode">
    <span class="parent-food-note" v-if="ingredientParent">
      Adding ingredient to: {{ ingredientParent.name }}</span
    >
    <FoodDetailsInfo
      v-model:selected-food="selectedFood"
      :is-editing-mode="isEditingMode"
      @ingredient-add-requested="handleAddIngredient"
      @ingredient-edit-requested="handleIngredientEditRequest"
    ></FoodDetailsInfo>
    <ActionButons
      v-if="!isAddToLogMode"
      v-model:selected-food="selectedFood"
      v-model:creation-mode="creationMode"
      :add-mode="ingredientParent != null"
      :editing-mode="isEditingMode"
      @food-deleted="handleFoodDeleted"
      @back-requested="goBack"
      @add-or-eat-requested="handleAddOrEatBtn"
      @toggle-editing="toggleEditing"
    ></ActionButons>
    <AddToLogMenu
      v-if="isAddToLogMode && !ingredientParent"
      v-model:selected-food="selectedFood"
      v-model:log-entry="logEntry"
      @close-requested="isAddToLogMode = false"
      @log-updated="addToLogMenuClose"
    ></AddToLogMenu>
    <AddToIngredientsMenu
      v-if="showAddIngredientsMenu && selectedFood"
      v-model:selected-food="selectedFood"
      v-model:ingredient-parent="ingredientParent"
      @close-requested="showAddIngredientsMenu = false"
      @done="ingredientGoBack"
    ></AddToIngredientsMenu>
    <AddToIngredientsMenu
      v-if="showEditIngredientsMenu && ingredientToEdit && selectedFood"
      v-model:selected-food="selectedFood"
      v-model:ingredient-parent="ingredientParent"
      v-model:ingredient="ingredientToEdit"
      @close-requested="showEditIngredientsMenu = false"
      @done="showEditIngredientsMenu = false"
    ></AddToIngredientsMenu>
  </div>
  <div class="ingredients-food-view-root" v-if="isAddIngredientsMode">
    <FoodView
      :is-add-ingredient-mode="true"
      v-model:parent-food="selectedFood"
      @close-add-ingredients="isAddIngredientsMode = false"
    ></FoodView>
  </div>
</template>

<!-- eslint-disable vue/no-mutating-props  -->
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { Food, Ingredient } from '@/types/food'
import FoodDetailsInfo from './FoodDetailsInfo.vue'
import ActionButons from './ActionButons.vue'
import AddToLogMenu from './AddToLogMenu.vue'
import AddToIngredientsMenu from './AddToIngredientsMenu.vue'
import FoodView from '@/views/FoodView.vue'
import type { FoodEntry } from '@/types/foodLog'

const creationMode = defineModel<boolean>('creationMode', { default: false })
const selectedFood = defineModel<Food | null>('selectedFood')
const ingredientParent = defineModel<Food | null>('ingredientParent', { default: null })
const logEntry = defineModel<FoodEntry | null>('logEntry', { default: null })
const ingredientToEdit = defineModel<Ingredient | null>('ingredientToEdit', { default: null })
const placeholder_id = 'PLACEHOLDER_ID_ITEM_NOT_IN_LOCAL_DB'

const emit = defineEmits(['food-deleted', 'entry-updated', 'ingredient-added', 'back-requested'])

const isAddToLogMode = ref(false)
const isAddIngredientsMode = ref(false)
const showAddIngredientsMenu = ref(false)
const showEditIngredientsMenu = ref(false)
const isEditingMode = ref(false)

function handleFoodDeleted() {
  emit('food-deleted', selectedFood.value?.id)
}

function goBack() {
  emit('back-requested')
}

function ingredientGoBack() {
  emit('ingredient-added')
}

function toggleEditing() {
  isEditingMode.value = !isEditingMode.value
}

function addToLogMenuClose() {
  if (logEntry.value) {
    emit('entry-updated')
  }
  goBack()
}

function handleAddOrEatBtn() {
  if (ingredientParent.value) {
    showAddIngredientsMenu.value = !showAddIngredientsMenu.value
  } else {
    isAddToLogMode.value = !isAddToLogMode.value
  }
}

async function handleAddIngredient() {
  isAddIngredientsMode.value = true
}

const handleIngredientEditRequest = (ingredientToEdit_local: Ingredient) => {
  showEditIngredientsMenu.value = true
  ingredientToEdit.value = ingredientToEdit_local
}

function setupIngredientEditMode() {
  selectedFood.value = ingredientToEdit.value?.ingredient
  showEditIngredientsMenu.value = true
}

onMounted(async () => {
  if (selectedFood.value?.id == placeholder_id) {
    creationMode.value = true
  }
  if (creationMode.value == true) {
    isEditingMode.value = true
  }
  if (ingredientToEdit.value) {
    setupIngredientEditMode()
  }
  if (logEntry.value) {
    isAddToLogMode.value = true
  }
})
</script>

<style lang="css" scoped>
.food-details-root {
  display: flex;
  flex-direction: column;
  justify-content: start;
  align-items: start;
  width: 100%;
  height: 100%;
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

@media (max-width: 480px) {
}
</style>
