<template>
  <div class="SparkbarChart">
    <VueUiSparkbar :config="config" :dataset="transformedDataset" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PropType } from 'vue'
import { VueUiSparkbar } from 'vue-data-ui'
import type { VueUiSparkbarConfig } from 'vue-data-ui'
import 'vue-data-ui/style.css'

interface DataRrow {
  name: string
  value: number
  target?: number
  color: string
  prefix: string
  suffix: string
  rounding: number
}

const props = defineProps({
  dataset: {
    type: Array as PropType<DataRrow[]>,
    required: true,
  },
  showAnimation: {
    type: Boolean,
    default: true,
  },
})

const MIN_DISPLAY_VALUE = 2

const transformedDataset = computed(() => {
  return props.dataset.map((item) => {
    const originalValue = item.value

    return {
      ...item,
      // Use minimum display value for the bar if value is too low
      value: item.value > 0 ? Math.max(item.value, MIN_DISPLAY_VALUE) : 0,
      // Add formatter to display the original value in labels
      formatter: () => {
        const rounded =
          item.rounding !== undefined ? originalValue.toFixed(item.rounding) : originalValue
        return `${item.prefix || ''}${rounded}${item.suffix || ''}`
      },
    }
  })
})

const config = computed<VueUiSparkbarConfig>(() => ({
  debug: false,
  loading: false,
  events: {
    datapointEnter: null,
    datapointLeave: null,
    datapointClick: null,
  },
  theme: undefined,
  customPalette: [],
  style: {
    fontFamily: 'inherit',
    backgroundColor: '#ffffffff',
    animation: {
      show: props.showAnimation,
      animationFrames: 30,
    },
    layout: {
      independant: true,
      percentage: false,
      target: 100,
      showTargetValue: false,
      targetValueText: '',
    },
    gutter: {
      backgroundColor: '#e1e5e8ff',
      opacity: 100,
    },
    bar: {
      gradient: {
        show: true,
        intensity: 40,
        underlayerColor: '#FFFFFF',
      },
    },
    labels: {
      fontSize: 16,
      name: {
        position: 'top-left',
        width: '100%',
        color: '#1A1A1Aff',
        bold: true,
      },
      value: {
        show: true,
        bold: true,
      },
    },
    title: {
      text: '',
      color: '#1A1A1Aff',
      fontSize: 20,
      bold: true,
      textAlign: 'left',
      margin: '0 0 6px 0',
      subtitle: {
        color: '#CCCCCCff',
        text: '',
        fontSize: 16,
        bold: false,
      },
    },
    gap: 4,
  },
}))
</script>

<style scoped lang="css">
.SparkbarChart {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}
</style>
