<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="modal-overlay" @click="closeModal">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h2 class="modal-title">Weight History</h2>
            <button class="close-button" @click="closeModal" aria-label="Close modal">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path
                  fill-rule="evenodd"
                  d="M5.47 5.47a.75.75 0 011.06 0L12 10.94l5.47-5.47a.75.75 0 111.06 1.06L13.06 12l5.47 5.47a.75.75 0 11-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 01-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 010-1.06z"
                  clip-rule="evenodd"
                />
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <div class="weight-history-controls">
              <button class="btn-add-weight" @click="addNewWeightEntry">
                <IconAdd class="icon-add" />
                <span>Add Weight Entry</span>
              </button>
            </div>

            <div class="weight-history-list">
              <div
                v-for="(entry, index) in weightHistory"
                :key="entry.id"
                class="weight-history-item"
              >
                <div class="weight-history-item-content">
                  <div class="weight-history-date">
                    <input v-model="entry.created_at" type="date" class="date-input" />
                  </div>
                  <div class="weight-history-weight">
                    <input
                      v-model.number="entry.weight"
                      type="number"
                      min="0"
                      max="500"
                      step="0.1"
                      class="weight-input"
                    />
                    kg
                  </div>
                  <div class="weight-history-actions">
                    <button
                      class="btn-delete-weight"
                      @click="deleteWeightEntry(index)"
                      :disabled="weightHistory.length <= 1"
                    >
                      <IconDelete class="icon-delete" />
                    </button>
                  </div>
                </div>
              </div>

              <div v-if="weightHistory.length === 0" class="no-entries">
                No weight entries found
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" @click="closeModal">Cancel</button>
            <button class="btn-primary" @click="saveChanges">Save Changes</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import IconAdd from '@/components/icons/IconAdd.vue'
import IconDelete from '@/components/icons/IconDelete.vue'
import type { WeightHistory } from '@/types/user'
import { getFormattedDateToday } from '@/helpers/utils'

const props = defineProps<{
  modelValue: boolean
  initialWeightHistory: WeightHistory[]
}>()

const emit = defineEmits(['update:modelValue', 'save'])

const weightHistory = ref(props.initialWeightHistory.slice())

const closeModal = () => {
  emit('update:modelValue', false)
}

const addNewWeightEntry = () => {
  const newEntry: WeightHistory = {
    weight: 0,
    created_at: getFormattedDateToday(),
  }
  weightHistory.value.unshift(newEntry)
}

const deleteWeightEntry = (index: number) => {
  if (weightHistory.value.length <= 1) return
  weightHistory.value.splice(index, 1)
}

const saveChanges = () => {
  emit('save', weightHistory.value)
  closeModal()
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  padding: 1rem;
}

.modal-container {
  background: var(--color-background-secondary);
  border-radius: 0.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease-out;
  border: 1px solid var(--color-accent-secondary);
}

.modal-header {
  padding: 1rem;
  border-bottom: 1px solid var(--color-accent-secondary);
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
  flex: 1;
}

.close-button {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s;
  width: 32px;
  height: 32px;
  color: var(--color-text-secondary);
}

.close-button:hover {
  background-color: var(--color-background-tertiary);
}

.close-button svg {
  width: 20px;
  height: 20px;
}

.modal-body {
  padding: 1rem;
}

.weight-history-controls {
  margin-bottom: 1rem;
}

.btn-add-weight {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: var(--color-accent-primary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-accent-secondary);
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
  width: 100%;
  justify-content: center;
}

.btn-add-weight:hover {
  background-color: var(--color-accent-secondary);
}

.icon-add {
  width: 20px;
  height: 20px;
}

.weight-history-list {
  max-height: 300px;
  overflow-y: auto;
}

.weight-history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem;
  border: 1px solid var(--color-accent-secondary);
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  background-color: var(--color-background-tertiary);
  flex-wrap: wrap;
}

.weight-history-item-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 2.25rem;
  gap: 1rem;
}

.weight-history-date {
  font-weight: 500;
  color: var(--color-text-primary);
  flex: 1;
  min-width: 120px;
  height: 100%;
}

.weight-history-weight {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex: 1;
  justify-content: flex-end;
  height: 100%;
}

.weight-input {
  height: 100%;
  padding: 0.25rem;
  border: 1px solid var(--color-accent-secondary);
  border-radius: 0.5rem;
  text-align: right;
  color: var(--color-text-primary);
  background-color: var(--color-background-secondary);
  font-size: 1rem;
}

.date-input {
  padding: 0.5rem;
  border: 1px solid var(--color-accent-secondary);
  border-radius: 0.5rem;
  color: var(--color-text-primary);
  background-color: var(--color-background-secondary);
  font-size: 1rem;
  width: 150px;
}

.weight-history-actions {
  display: flex;
  align-items: center;
}

.btn-delete-weight {
  background: none;
  border: 1px solid var(--color-accent-secondary);
  cursor: pointer;
  color: #ef4444;
  padding: 0.5rem;
  border-radius: 0.25rem;
  transition: all 0.2s;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  height: 2.5rem;
  width: 2.5rem;
}

.btn-delete-weight:hover {
  background-color: #fee2e2;
  border-color: #ef4444;
}

.btn-delete-weight:disabled {
  color: #9ca3af;
  cursor: not-allowed;
  border-color: #d1d5db;
  font-style: italic;
}

.modal-footer {
  padding: 1rem;
  border-top: 1px solid var(--color-accent-secondary);
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  padding: 0.625rem 1.25rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid var(--color-accent-secondary);
}

.btn-primary {
  background-color: var(--color-accent-primary);
  color: var(--color-text-primary);
}

.btn-primary:hover {
  background-color: var(--color-accent-secondary);
}

.btn-secondary {
  background-color: var(--color-background-secondary);
  color: var(--color-text-primary);
}

.btn-secondary:hover {
  background-color: var(--color-background-tertiary);
}

/* Animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container {
  animation: slideUp 0.3s ease-out;
}

.modal-leave-active .modal-container {
  animation: slideDown 0.3s ease-in;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes slideDown {
  from {
    transform: translateY(0);
    opacity: 1;
  }
  to {
    transform: translateY(20px);
    opacity: 0;
  }
}

@media (max-width: 480px) {
  .modal-container {
    margin: 0rem;
  }
  .modal-body {
    padding: 0.5rem;
  }

  .modal-footer {
    flex-direction: column-reverse;
  }

  .weight-history-item {
    padding: 0.25rem;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>
