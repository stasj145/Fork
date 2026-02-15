<!-- eslint-disable vue/no-mutating-props  -->
<template>
  <div class="add-ingredient-menu-root" v-if="selectedFood">
    <input
      v-model="ingredientQuantity"
      class="add-to-ingredients-input"
      type="number"
      min="0.0"
      max="10000"
      step="10"
    />
    <select v-model="ingredientQuantityUnit" class="add-to-ingredients-select-unit">
      <option value="g">g</option>
      <option value="serving">{{ selectedFood.serving_unit }}</option>
    </select>
    <button class="add-to-ingredients-btn" @click="handleaddIngredientButton()">
      <IconAdd v-if="!updating"></IconAdd>
      <Spinner v-else></Spinner>

      <ErrorModal
        v-model="showUpdatingError"
        title="Ingredient Entry Error"
        message="Unable to update ingredients."
        :details="errorDetails"
      ></ErrorModal>
    </button>
    <button class="add-to-ingredients-btn-cancel" @click="emit('close-requested')">
      <IconCancel></IconCancel>
    </button>
  </div>
</template>

<!-- eslint-disable vue/no-mutating-props  -->
<script setup lang="ts">
import { ref } from 'vue'
import type { Food, Ingredient } from '@/types/food'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import IconCancel from '@/components/icons/IconCancel.vue'
import IconAdd from '../icons/IconAdd.vue'
import ErrorModal from '../ErrorModal.vue'
import Spinner from '../Spinner.vue'

const selectedFood = defineModel<Food | null>('selectedFood')
const ingredientParent = defineModel<Food | null>('ingredientParent', { default: null })
const ingredient = defineModel<Ingredient | null>('ingredient', { default: null })

const emit = defineEmits(['done', 'close-requested'])

const placeholder_id = 'PLACEHOLDER_ID_ITEM_NOT_IN_LOCAL_DB'
const showUpdatingError = ref(false)
const errorDetails = ref('N/A')
const updating = ref(false)
const ingredientQuantityUnit = ref('g')
const ingredientQuantity = ref(ingredient.value ? ingredient.value.quantity : 1.0)

async function saveFood(updatedFood: Food) {
  try {
    if (updatedFood.barcode?.trim() == '') {
      updatedFood.barcode = null
    }
    const results: Food = await fetchWrapper.post('/api/v1/food/item/', updatedFood)
    selectedFood.value = results

    if (updatedFood.external_image_url) {
      const externalImg = await fetch(updatedFood.external_image_url)

      const imageBlob = await externalImg.blob()
      const file = new File([imageBlob], 'external.jpg', { type: imageBlob.type })

      const formData = new FormData()
      formData.append('file', file)

      await fetchWrapper.put(`/api/v1/food/item/${selectedFood.value.id}/image`, formData)
    }
  } catch (err) {
    if (err instanceof Error) {
      showUpdatingError.value = true
      errorDetails.value = err.message || 'N/A'
    }
    updating.value = false
  }
}

async function handleaddIngredientButton() {
  if (ingredient.value) {
    ingredient.value.quantity =
      ingredientQuantityUnit.value == 'serving'
        ? ingredientQuantity.value * ingredient.value.ingredient.serving_size
        : ingredientQuantity.value
    emit('done')
    return
  }
  if (ingredientParent.value && selectedFood.value && selectedFood.value.id) {
    updating.value = true
    if (selectedFood.value.id == placeholder_id) {
      // create food first if it has a placeholder id.
      await saveFood(selectedFood.value)
    }

    let quantity: number = 0.0
    if (ingredientQuantityUnit.value == 'serving') {
      quantity = ingredientQuantity.value * selectedFood.value.serving_size
    } else {
      quantity = ingredientQuantity.value
    }

    ingredientParent.value.ingredients.push({
      parent_id: null,
      ingredient_id: selectedFood.value.id,
      quantity: quantity,
      ingredient: selectedFood.value,
    })

    updating.value = false
    emit('done')
  }
}
</script>

<style lang="css" scoped>
.add-ingredient-menu-root {
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

.add-to-ingredients-btn-cancel,
.add-to-ingredients-btn {
  height: 100%;
  width: 3rem;
  margin-left: 0.5rem;
  padding: 0.5rem;
  background-color: var(--color-accent-primary);
  border: none;
  box-shadow: 0 0 1px 1px var(--color-accent-primary);
  border-radius: 1rem;
}
.add-to-ingredients-select-unit {
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

.add-to-ingredients-input {
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
  .add-ingredient-menu-root {
    position: fixed;
    bottom: 0;
    right: 0;
    width: 100vw;
    height: 4rem;
    border-radius: 0;
    border-top-left-radius: 1rem;
    border-top-right-radius: 1rem;

    display: flex;
    flex-direction: row;
  }

  .add-to-log-menu-root .last-three {
    margin-top: 0.5rem;
  }

  .add-to-log-select-meal-type {
    width: 100%;
    margin-left: 0;
  }

  .add-to-ingredients-input,
  .add-to-ingredients-select-unit {
    width: 50%;
  }

  .add-to-ingredients-btn-cancel,
  .add-to-ingredients-btn {
    width: 4rem;
  }
}
</style>
