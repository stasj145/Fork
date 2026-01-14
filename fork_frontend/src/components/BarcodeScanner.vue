<template>
  <div class="scanner-overlay">
    <div class="scanner-container">
      <div class="scanner-header">
        <h2>Scan Barcode</h2>
        <button @click="closeScanner" class="close-btn">&times;</button>
      </div>

      <div class="scanner-content">
        <div v-if="scanning" class="scanner-viewfinder">
          <StreamBarcodeReader
            @decode="onDecode"
            @loaded="onLoaded"
            @error="onError"
            class="scanner-video"
          />
          <div class="viewfinder-overlay">
            <div class="viewfinder-frame"></div>
            <p class="scanner-instructions">Point your camera at a barcode</p>
          </div>
        </div>

        <div v-else-if="success" class="scanner-result success">
          <div class="result-icon">✓</div>
          <p>Barcode scanned successfully!</p>
          <p class="barcode-text">{{ decodedText }}</p>
        </div>

        <div v-else-if="error" class="scanner-result error">
          <div class="result-icon">⚠</div>
          <p>{{ error }}</p>
          <button @click="retryScan" class="retry-btn">Try Again</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { StreamBarcodeReader } from '@teckel/vue-barcode-reader'

const decodedText = ref('')
const scanning = ref(true)
const error = ref<string | null>(null)
const success = ref(false)

const emit = defineEmits<{
  (e: 'barcode-scanned', barcode: string): void
  (e: 'close'): void
}>()

const onDecode = (result: string) => {
  decodedText.value = result
  success.value = true
  scanning.value = false
  error.value = null

  // Emit the barcode to the parent component
  emit('barcode-scanned', result)

  // Close the scanner after a short delay
  setTimeout(() => {
    emit('close')
  }, 1500)
}

const onLoaded = () => {
  console.log('Barcode scanner loaded')
}

const onError = (err: unknown) => {
  console.error('Barcode scanner error:', err)
  error.value = 'Failed to access camera. Please ensure you have granted camera permissions.'
  scanning.value = false
}

const retryScan = () => {
  decodedText.value = ''
  error.value = null
  success.value = false
  scanning.value = true
}

const closeScanner = () => {
  emit('close')
}
</script>

<style scoped>
.scanner-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.scanner-container {
  background-color: var(--color-background-secondary);
  border-radius: 0.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.scanner-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: var(--color-accent-secondary);
  color: white;
}

.scanner-header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scanner-content {
  padding: 1rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.scanner-viewfinder {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: 0.25rem;
}

.scanner-video {
  width: 100%;
  height: 100%;
}

.viewfinder-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.viewfinder-frame {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60%;
  height: 60%;
  border: 2px solid var(--color-accent-primary);
  box-shadow: 0 0 0 1000px rgba(0, 0, 0, 0.5);
}

.scanner-instructions {
  position: absolute;
  bottom: 1rem;
  left: 0;
  width: 100%;
  text-align: center;
  color: white;
  margin: 0;
  padding: 0.5rem;
  background-color: rgba(0, 0, 0, 0.5);
}

.scanner-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  height: 300px;
  padding: 1rem;
}

.result-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.success .result-icon {
  color: #4caf50;
}

.error .result-icon {
  color: #f44336;
}

.barcode-text {
  font-family: monospace;
  font-size: 1.2rem;
  word-break: break-all;
  background-color: var(--color-background-tertiary);
  padding: 0.5rem;
  border-radius: 0.25rem;
  margin-top: 1rem;
}

.retry-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: var(--color-accent-primary);
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
}

.retry-btn:hover {
  background-color: var(--color-accent-secondary);
}
</style>
