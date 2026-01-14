<!-- eslint-disable vue/no-mutating-props  -->
<template>
  <div class="activity-details-root" v-if="selectedActivity">
    <ActivityDetailsInfo
      v-model:selected-activity="selectedActivity"
      :is-editing-mode="isEditingMode"
      :user="user"
    ></ActivityDetailsInfo>
    <ActionButons
      v-if="!isAddToLogMode"
      v-model:selected-activity="selectedActivity"
      v-model:creation-mode="creationMode"
      :editing-mode="isEditingMode"
      @activity-deleted="handleActivityDeleted"
      @back-requested="goBack"
      @add-requested="handleAddBtn"
      @toggle-editing="toggleEditing"
    ></ActionButons>
    <AddActivityToLogMenu
      v-if="isAddToLogMode"
      v-model:selected-activity="selectedActivity"
      v-model:log-entry="logEntry"
      :user="user"
      @close-requested="isAddToLogMode = false"
      @log-updated="addToLogMenuClose"
    ></AddActivityToLogMenu>
  </div>
</template>

<!-- eslint-disable vue/no-mutating-props  -->
<script setup lang="ts">
import { onMounted, ref, type PropType } from 'vue'
import type { Activity } from '@/types/activity.ts'
import ActivityDetailsInfo from './ActivityDetailsInfo.vue'
import ActionButons from './ActionButons.vue'
import AddActivityToLogMenu from './AddActivityToLogMenu.vue'
import type { ActivityEntry } from '@/types/activityLog'
import type { User } from '@/types/user'

const creationMode = defineModel<boolean>('creationMode', { default: false })
const selectedActivity = defineModel<Activity | null>('selectedActivity')
const logEntry = defineModel<ActivityEntry | null>('logEntry', { default: null })

defineProps({
  user: {
    type: Object as PropType<User>,
    required: true,
  },
})

const emit = defineEmits(['activity-deleted', 'entry-updated', 'back-requested'])

const isAddToLogMode = ref(false)
const isEditingMode = ref(false)

function handleActivityDeleted() {
  emit('activity-deleted', selectedActivity.value?.id)
}

function goBack() {
  emit('back-requested')
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

function handleAddBtn() {
  isAddToLogMode.value = !isAddToLogMode.value
}

onMounted(async () => {
  if (creationMode.value == true) {
    isEditingMode.value = true
  }
  if (logEntry.value) {
    isAddToLogMode.value = true
  }
})
</script>

<style lang="css" scoped>
.activity-details-root {
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
