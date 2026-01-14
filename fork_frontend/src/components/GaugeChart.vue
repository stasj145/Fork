<template>
  <div class="GaugeChart">
    <VueUiSparkgauge :config="config" :dataset="props.dataset" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PropType } from 'vue'
import { VueUiSparkgauge } from 'vue-data-ui'
import type { VueUiSparkgaugeConfig } from 'vue-data-ui'
import 'vue-data-ui/style.css' // If you are using multiple components, place this style import in your main

interface DataRrow {
  value: number
  min: number
  max: number
  prefix?: string
  suffix?: string
  rounding?: number
  colorMin?: string
  colorMax?: string
  colorFont?: string
}

const props = defineProps({
  dataset: {
    type: Object as PropType<DataRrow>,
    required: true,
  },
  showAnimation: {
    type: Boolean,
    default: true,
  },
})

const config = computed<VueUiSparkgaugeConfig>(() => ({
  debug: false,
  loading: false,
  theme: '',
  style: {
    fontFamily: 'inherit',
    background: '#FFFFFF',
    height: 70,
    basePosition: 60,
    animation: {
      show: props.showAnimation,
      speedMs: 30,
    },
    title: {
      show: false,
      fontSize: 12,
      position: 'top',
      textAlign: 'center',
      bold: false,
      color: '#1A1A1Aff',
    },
    dataLabel: {
      fontSize: 12,
      autoColor: false,
      color: props.dataset.colorFont === undefined ? '#000000' : props.dataset.colorFont,
      offsetY: -10,
      bold: true,
      rounding: props.dataset.rounding === undefined ? 0 : props.dataset.rounding,
      prefix: props.dataset.prefix === undefined ? '' : props.dataset.prefix,
      suffix: props.dataset.suffix === undefined ? '' : props.dataset.suffix,
      formatter: null,
    },
    colors: {
      min: props.dataset.colorMin === undefined ? 'rgba(0, 255, 0, 1)' : props.dataset.colorMin,
      max: props.dataset.colorMax === undefined ? 'rgba(255, 0, 0, 1)' : props.dataset.colorMax,
      showGradient: true,
    },
    track: {
      autoColor: true,
      color: '#5f8beeff',
      strokeLinecap: 'round',
    },
    gutter: {
      color: '#e1e5e8ff',
      strokeLinecap: 'round',
    },
  },
}))
</script>

<style scoped lang="css">
.GaugeChart {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}
</style>
