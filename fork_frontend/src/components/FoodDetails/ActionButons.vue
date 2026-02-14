<!-- eslint-disable vue/no-mutating-props  -->
<template>
  <div class="button-root" v-if="selectedFood">
    <button class="btn-back" @click="goBack()" :disabled="saving || deleting">
      <IconBack></IconBack>
    </button>
    <button
      class="btn-delete"
      :class="{ 'btn-delete-awaiting-confirmation': deleteConfirmed }"
      @click="deleteFood(selectedFood)"
      v-if="isEditing && !creationMode"
      :disabled="saving || deleting"
    >
      <IconDelete v-if="!deleting"></IconDelete>
      <Spinner v-else></Spinner>
      <ErrorModal
        v-model="showDeletionError"
        title="Deletion Error"
        message="Unable to delete food item. Most likely you are trying to delete a food item that is still being referenced in a food log."
        :details="errorDetails"
      ></ErrorModal>
    </button>
    <button
      class="btn-save"
      @click="saveFood(selectedFood)"
      v-if="isEditing"
      :disabled="saving || deleting"
    >
      <IconSave v-if="!saving"></IconSave>
      <Spinner v-else></Spinner>
      <ErrorModal
        v-model="showSavingError"
        title="Save Error"
        message="Unable to save"
        :details="errorDetails"
      ></ErrorModal>
    </button>
    <button
      class="btn-edit"
      @click="toggleEditing()"
      v-if="!isEditing"
      :disabled="saving || deleting"
    >
      <IconEdit></IconEdit>
    </button>
    <button class="btn-cancel" @click="toggleEditing()" v-else :disabled="saving || deleting">
      <IconCancel></IconCancel>
    </button>
    <button
      class="btn-eat"
      @click="emitAddOrEatMode()"
      v-if="!isEditing"
      :disabled="saving || deleting"
    >
      <div class="btn-eat-content-container">
        <IconEat v-if="!addMode"></IconEat>
        <IconAdd v-else></IconAdd>
        <label v-if="!addMode">Eat</label>
        <label v-else>add</label>
      </div>
    </button>
  </div>
</template>

<!-- eslint-disable vue/no-mutating-props  -->
<script setup lang="ts">
import { ref } from 'vue'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import type { Food } from '@/types/food'
import IconEdit from '@/components/icons/IconEdit.vue'
import IconBack from '@/components/icons/IconBack.vue'
import IconCancel from '@/components/icons/IconCancel.vue'
import IconSave from '../icons/IconSave.vue'
import ErrorModal from '@/components/ErrorModal.vue'
import Spinner from '@/components/Spinner.vue'
import IconEat from '../icons/IconEat.vue'
import IconDelete from '../icons/IconDelete.vue'
import IconAdd from '../icons/IconAdd.vue'

const emit = defineEmits([
  'food-deleted',
  'back-requested',
  'add-or-eat-requested',
  'toggle-editing',
])

const selectedFood = defineModel<Food>('selectedFood', { required: true })
const creationMode = defineModel<boolean>('creationMode', { default: false })

const props = defineProps({
  addMode: {
    type: Boolean,
    default: false,
  },
  editingMode: {
    type: Boolean,
    default: false,
  },
})

const showSavingError = ref(false)
const showDeletionError = ref(false)
const errorDetails = ref('N/A')
const saving = ref(false)
const deleting = ref(false)
const deleteConfirmed = ref(false)
const isEditing = ref(creationMode.value || props.editingMode ? true : false)

const placeholder_id = 'PLACEHOLDER_ID_ITEM_NOT_IN_LOCAL_DB'

function toggleEditing() {
  isEditing.value = !isEditing.value
  deleteConfirmed.value = false
  emit('toggle-editing')
}

function goBack() {
  emit('back-requested')
}

function emitAddOrEatMode() {
  emit('add-or-eat-requested')
}

async function saveFood(updatedFood: Food) {
  deleteConfirmed.value = false
  saving.value = true

  try {
    let finalFood: Food

    if (updatedFood.barcode?.trim() == '') {
      updatedFood.barcode = null
    }

    if (creationMode.value || selectedFood.value.id == placeholder_id) {
      console.log('Creating new food...')
      const results: Food = await fetchWrapper.post('/api/v1/food/item/', updatedFood)

      // Clone to prevent background reactivity from overwriting it
      finalFood = { ...results, img_src: updatedFood.img_src }

      creationMode.value = false
    } else {
      const results: Food = await fetchWrapper.patch(
        `/api/v1/food/item/${updatedFood.id}`,
        updatedFood,
      )
      finalFood = { ...results, img_src: updatedFood.img_src }
    }

    selectedFood.value = finalFood

    if (updatedFood.external_image_url) {
      const response = await fetchWrapper.put(`/api/v1/food/item/${finalFood.id}/image_from_url`, {
        url: updatedFood.external_image_url,
      })
      finalFood.img_name = response['name']
      selectedFood.value.img_name = response['name']
    }
  } catch (err) {
    if (err instanceof Error) {
      showSavingError.value = true
      errorDetails.value = err.message || 'N/A'
    }
  } finally {
    saving.value = false
    getImage()
  }

  if (!showSavingError.value) {
    toggleEditing()
  }
}
async function getImage() {
  if (!selectedFood.value || !selectedFood.value.img_name) {
    return
  }

  try {
    const imgResp = await fetchWrapper.get(
      `/api/v1/food/item/${selectedFood.value.id}/image?size=large`,
      undefined, // no body
      true, // Prevent Cache Read
    )
    const imgBlob = new Blob([imgResp], { type: 'image/jpeg' })
    selectedFood.value.img_src = URL.createObjectURL(imgBlob)
  } catch (err) {
    if (err instanceof Error) {
      console.warn('Could not load: ' + err.message)
    }
  }
}

async function deleteFood(foodToDelete: Food) {
  if (!deleteConfirmed.value) {
    deleteConfirmed.value = true
    return
  }
  deleting.value = true
  try {
    await fetchWrapper.delete(`/api/v1/food/item/${foodToDelete.id}`)
  } catch (err) {
    if (err instanceof Error) {
      showDeletionError.value = true
      errorDetails.value = err.message || 'N/A'
    }
  } finally {
    deleting.value = false
  }
  if (!showDeletionError.value) {
    isEditing.value = false
    emit('food-deleted', foodToDelete.id)
  }
  deleteConfirmed.value = false
}
</script>

<style lang="css" scoped>
.button-root {
  position: fixed;
  right: max(1.5rem, calc((100vw - 1200px) / 2 + 1rem));
  bottom: 2rem;
  height: 3rem;
  z-index: 1000;
}

.button-root button {
  height: 100%;
  width: 3rem;
  margin-left: 0.5rem;
  padding: 0.5rem;
  background-color: var(--color-accent-secondary);
  border: 1px solid var(--color-accent-primary);
  border-radius: 1rem;
}

.button-root button.btn-eat {
  width: fit-content;
}

.button-root button.btn-delete {
  background-color: #ffa9a9ff;
}

.button-root button.btn-delete.btn-delete-awaiting-confirmation {
  background-color: rgb(255, 0, 0);
}

.btn-eat-content-container {
  display: flex;
  flex-direction: row;
  height: 100%;
}
.btn-eat-content-container label {
  color: var(--color-black);
  font-size: 1rem;
  font-weight: bold;
  margin-right: 0.5rem;
  margin-left: 0.5rem;
  align-self: center;
}

@media (max-width: 480px) {
  .button-root {
    bottom: 1rem;
  }
}
</style>
