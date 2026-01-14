<!-- eslint-disable vue/no-mutating-props  -->
<template>
  <div class="activity-item-summary">
    <div class="summary" @click="toggelChangeOverlay()">
      <div class="activity-item-name">{{ activity_name }}</div>
      <div class="activity-item-details">
        <span class="duration">{{ formattedDuration }}</span>
        <div class="nutrition-info">
          <span class="calories">{{ calories }} kcal</span>
        </div>
      </div>
    </div>
    <div class="change-overlay" v-if="showChangeOverlay">
      <button class="btn-back" @click="toggelChangeOverlay()" :disabled="deleting">
        <IconBack></IconBack>
      </button>
      <button class="btn-edit" @click="editActivityEntry()" :disabled="deleting">
        <IconEdit></IconEdit>
      </button>
      <button
        class="btn-delete"
        :class="{ 'btn-delete-awaiting-confirmation': deleteConfirmed }"
        @click="deleteActivityEntry()"
        :disabled="deleting"
      >
        <IconDelete v-if="!deleting"></IconDelete>
        <Spinner v-else></Spinner>
        <ErrorModal
          v-model="showDeletionError"
          title="Deletion Error"
          message="Unable to delete activity entry."
          :details="errorDetails"
        ></ErrorModal>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, type PropType } from 'vue'
import type { ActivityEntry } from '@/types/activityLog'
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
  activityEntry: {
    type: Object as PropType<ActivityEntry>,
    required: true,
  },
})

const emit = defineEmits(['activity-entry-deleted', 'entry-edit-requested'])

const formattedDuration = computed(() => {
  const duration = props.activityEntry.duration
  // Convert hours to minutes if duration is less than 1 hour
  if (duration < 1) {
    const minutes = Math.round(duration * 60)
    return `${minutes} minutes`
  } else {
    // Display hours with one decimal place
    return `${duration.toFixed(1)} hours`
  }
})

const calories = computed(() => {
  return Math.round(props.activityEntry.calories_burned)
})

const activity_name = computed(() => {
  return props.activityEntry.activity.name
})

function editActivityEntry() {
  showChangeOverlay.value = false
  emit('entry-edit-requested', props.activityEntry)
}

function toggelChangeOverlay() {
  showChangeOverlay.value = !showChangeOverlay.value
  deleteConfirmed.value = false
}

async function deleteActivityEntry() {
  if (!deleteConfirmed.value) {
    deleteConfirmed.value = true
    return
  }

  deleting.value = true
  try {
    await fetchWrapper.delete(
      `/api/v1/log/day/${getFormattedDate()}/activity/${props.activityEntry.id}`,
    )
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
    // Emit event to notify parent component that activity was deleted
    emit('activity-entry-deleted', props.activityEntry.id)
  }
}
</script>

<style lang="css" scoped>
.activity-item-summary {
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

.activity-item-name {
  font-weight: bold;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-bottom: 0.2rem;
}

.activity-item-details {
  display: flex;
  flex-direction: row;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.nutrition-info {
  display: flex;
  flex-direction: row;
}
.nutrition-info span {
  margin-left: 1rem;
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
  .activity-item-details {
    justify-content: space-between;
  }

  .nutrition-info {
    justify-content: space-between;
  }
  .nutrition-info span {
    margin-right: 0;
  }
}
</style>
