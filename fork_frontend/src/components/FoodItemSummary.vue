<!-- eslint-disable vue/no-mutating-props  -->
<template>
  <div class="food-item-summary">
    <div class="summary" @click="toggelChangeOverlay()">
      <div class="food-item-name">{{ food_name }}</div>
      <div class="food-item-details">
        <span class="quantity">{{ formattedQuantity }}</span>
        <div class="nutrition-info">
          <span class="calories">{{ calories }} kcal</span>
          <span class="proteins">{{ proteins }} g proteins</span>
          <span class="carbs">{{ carbohydrates }} g carbs</span>
          <span class="fat">{{ fat }} g fat</span>
        </div>
      </div>
    </div>
    <div class="change-overlay" v-if="showChangeOverlay">
      <button class="btn-back" @click="toggelChangeOverlay()" :disabled="deleting">
        <IconBack></IconBack>
      </button>
      <button class="btn-edit" @click="editFoodEntry()" :disabled="deleting">
        <IconEdit></IconEdit>
      </button>
      <button
        class="btn-delete"
        :class="{ 'btn-delete-awaiting-confirmation': deleteConfirmed }"
        @click="deleteFoodEntry()"
        :disabled="deleting"
      >
        <IconDelete v-if="!deleting"></IconDelete>
        <Spinner v-else></Spinner>
        <ErrorModal
          v-model="showDeletionError"
          title="Deletion Error"
          message="Unable to delete food entry."
          :details="errorDetails"
        ></ErrorModal>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, type PropType } from 'vue'
import type { FoodEntry } from '@/types/foodLog'
import type { Ingredient } from '@/types/food'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import { getFormattedDate } from '@/helpers/utils'
import IconBack from './icons/IconBack.vue'
import IconEdit from './icons/IconEdit.vue'
import IconDelete from './icons/IconDelete.vue'
import Spinner from './Spinner.vue'
import ErrorModal from './ErrorModal.vue'

const showChangeOverlay = ref(false)
const showDeletionError = ref(false)
const errorDetails = ref('N/A')
const deleting = ref(false)
const deleteConfirmed = ref(false)

const props = defineProps({
  foodEntry: {
    type: Object as PropType<FoodEntry>,
    required: false,
  },
  ingredientEntry: {
    type: Object as PropType<Ingredient>,
    required: false,
  },
  disableChangeOverlay: {
    type: Boolean,
    required: false,
    default: false,
  },
})

const emit = defineEmits(['food-entry-deleted', 'entry-edit-requested', 'remove-ingredient'])

const formattedQuantity = computed(() => {
  let serving_unit: string = 'servings'
  let quantity: number = 0.0
  if (props.foodEntry) {
    serving_unit = props.foodEntry.food_item.serving_unit
    quantity = props.foodEntry.quantity
  } else if (props.ingredientEntry) {
    serving_unit = props.ingredientEntry.ingredient.serving_unit
    quantity = props.ingredientEntry.quantity
  }
  if (servings.value > 0) {
    if (servings.value % 1 === 0) {
      return `${servings.value.toFixed(0)} ${serving_unit}(s) - ${quantity.toFixed(1)}g`
    } else {
      return `${servings.value.toFixed(1)} ${serving_unit}(s) - ${quantity.toFixed(1)}g`
    }
  }
  return `${quantity} g`
})

const calories = computed(() => {
  let calories_per_100: number = 0.0
  let quantity: number = 0.0
  if (props.foodEntry) {
    calories_per_100 = props.foodEntry.food_item.calories_per_100
    quantity = props.foodEntry.quantity
  } else if (props.ingredientEntry) {
    calories_per_100 = props.ingredientEntry.ingredient.calories_per_100
    quantity = props.ingredientEntry.quantity
  }

  return Math.round((calories_per_100 * quantity) / 100)
})
const proteins = computed(() => {
  let protein_per_100: number = 0.0
  let quantity: number = 0.0
  if (props.foodEntry) {
    protein_per_100 = props.foodEntry.food_item.protein_per_100
    quantity = props.foodEntry.quantity
  } else if (props.ingredientEntry) {
    protein_per_100 = props.ingredientEntry.ingredient.protein_per_100
    quantity = props.ingredientEntry.quantity
  }

  return ((protein_per_100 * quantity) / 100).toFixed(1)
})
const carbohydrates = computed(() => {
  let carbs_per_100: number = 0.0
  let quantity: number = 0.0
  if (props.foodEntry) {
    carbs_per_100 = props.foodEntry.food_item.carbs_per_100
    quantity = props.foodEntry.quantity
  } else if (props.ingredientEntry) {
    carbs_per_100 = props.ingredientEntry.ingredient.carbs_per_100
    quantity = props.ingredientEntry.quantity
  }

  return ((carbs_per_100 * quantity) / 100).toFixed(1)
})
const fat = computed(() => {
  let fat_per_100: number = 0.0
  let quantity: number = 0.0
  if (props.foodEntry) {
    fat_per_100 = props.foodEntry.food_item.fat_per_100
    quantity = props.foodEntry.quantity
  } else if (props.ingredientEntry) {
    fat_per_100 = props.ingredientEntry.ingredient.fat_per_100
    quantity = props.ingredientEntry.quantity
  }

  return ((fat_per_100 * quantity) / 100).toFixed(1)
})

const servings = computed(() => {
  let serving_size: number = 0.0
  let quantity: number = 0.0
  if (props.foodEntry) {
    serving_size = props.foodEntry.food_item.serving_size
    quantity = props.foodEntry.quantity
  } else if (props.ingredientEntry) {
    serving_size = props.ingredientEntry.ingredient.serving_size
    quantity = props.ingredientEntry.quantity
  }

  return quantity / serving_size
})

const food_name = computed(() => {
  let name: string = ''
  if (props.foodEntry) {
    name = props.foodEntry.food_item.name
  } else if (props.ingredientEntry) {
    name = props.ingredientEntry.ingredient.name
  }

  return name
})

function editFoodEntry() {
  showChangeOverlay.value = false
  if (props.foodEntry) {
    emit('entry-edit-requested', props.foodEntry.id)
  } else {
    emit('entry-edit-requested', props.ingredientEntry)
  }
}

function toggelChangeOverlay() {
  if (props.disableChangeOverlay) {
    return
  }
  showChangeOverlay.value = !showChangeOverlay.value
  deleteConfirmed.value = false
}

async function deleteFoodEntry() {
  if (!deleteConfirmed.value) {
    deleteConfirmed.value = true
    return
  }
  if (props.ingredientEntry) {
    showChangeOverlay.value = false
    emit('remove-ingredient')
    return
  }

  if (props.foodEntry) {
    deleting.value = true
    try {
      await fetchWrapper.delete(`/api/v1/log/day/${getFormattedDate()}/food/${props.foodEntry.id}`)
    } catch (err) {
      if (err instanceof Error) {
        showDeletionError.value = true
        errorDetails.value = err.message || 'N/A'
      }
    } finally {
      deleting.value = false
      deleteConfirmed.value = false
    }

    if (!showDeletionError.value) {
      showChangeOverlay.value = false
      // Emit event to notify parent component that food was deleted
      emit('food-entry-deleted', props.foodEntry.id)
    }
  }
}
</script>

<style lang="css" scoped>
.food-item-summary {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 4rem;
  background-color: var(--color-background-tertiary);
  border-radius: 0.5rem;
  padding: 0.5rem;
  justify-content: center;
  position: relative;
}

.food-item-name {
  font-weight: bold;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-bottom: 0.2rem;
}

.food-item-details {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.nutrition-info {
  display: flex;
  flex-direction: row;
}
.nutrition-info span {
  margin-right: 1rem;
}

.change-overlay {
  display: flex;
  flex-direction: row;
  height: 100%;
  width: 100%;
  position: absolute;
  top: 0;
  left: 0;
  background-color: rgba(255, 242, 205, 0.8);
  border-radius: 0.5rem;
  justify-content: center;
  z-index: 1;
  box-sizing: border-box;
  padding: 0.5rem;
  gap: 0.5rem;
}

.btn-delete,
.btn-back,
.btn-edit {
  width: 100%;
  max-width: 5rem;
  padding: 0.5rem;
  background-color: var(--color-accent-secondary);
  border: 1px solid var(--color-accent-secondary);
  border-radius: 1rem;
  z-index: 2;
}

.btn-delete svg,
.btn-back svg,
.btn-edit svg {
  height: 100%;
}

.btn-delete {
  background-color: #ffa9a9ff;
}

.btn-delete.btn-delete-awaiting-confirmation {
  background-color: rgb(255, 0, 0);
}

@media (max-width: 480px) {
  .food-item-details {
    flex-direction: column;
  }

  .nutrition-info {
    justify-content: space-between;
  }
  .nutrition-info span {
    margin-right: 0;
  }
}
</style>
