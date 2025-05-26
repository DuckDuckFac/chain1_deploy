<template>
    <div
    ref="chartContainer"
    class="mini-chart"
    :style="`width: ${props.width}px; height: ${props.height}px;`"
  ></div>
</template>


<script setup>
import { onMounted, ref } from 'vue'
import { createChart } from 'lightweight-charts'

const props = defineProps({
  code: String,
  rate: Number,
  compact: Boolean,
  width: { type: Number, default: 100 },
  height: { type: Number, default: 30 },
})

const chartContainer = ref(null)
const chartRef = ref(null)
const color = props.rate >= 0 ? '#d32f2f' : '#1976d2'
onMounted(async () => {
  try {
    const res = await fetch(`http://localhost:8000/api/ohlc/${props.code}/1m/`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)

    const data = await res.json()

    chartRef.value = createChart(chartContainer.value, {
      width: props.width,
      height: props.height,
      layout: { backgroundColor: 'rgba(0, 0, 0, 0)',  textColor: '#333' },
      grid: { vertLines: { visible: false }, horzLines: { visible: false } },
      priceScale: { visible: false },
      timeScale: { visible: false },
      crosshair: { vertLine: { visible: false }, horzLine: { visible: false } },
    })

      const upColor = '#FF4C4C'
      const downColor = '#1E90FF'
      const color = props.rate >= 0 ? upColor : downColor

      const series = chartRef.value.addAreaSeries({
        lineColor: color,
        topColor: color + '88',
        bottomColor: color + '00',
        lineWidth: 2,
        lastValueVisible: false,
        priceLineVisible: false,
      })

    const lineData = data.slice(-15).map(d => ({
      time: Math.floor(new Date(d.timestamp).getTime() / 1000),
      value: d.close,
    }))

    series.setData(lineData)
  } catch (err) {
    console.error('❌ MiniChart fetch 실패:', err)
  }
})

window.addEventListener('resize', () => {
  if (chartRef.value && chartContainer.value) {
    chartRef.value.resize(props.width, props.height)
  }
})
</script>


<style scoped>
.mini-chart {
  width: unset;
  height: unset;
}
</style>