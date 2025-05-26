<script setup>
import { ref, watch, toRaw, onMounted } from 'vue'
import { createChart } from 'lightweight-charts'

const props = defineProps({
  ohlcData: Array,
  currentPrice: Number
})

const chartContainer = ref(null)
let chart = null
let candlestickSeries = null
let priceLine = null
let isChartReady = false

function initChart() {
  if (!chartContainer.value || chart) return

  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: 400,
    layout: {
      background: { color: '#fff' },
      textColor: '#222',
    },
    grid: {
      vertLines: { color: '#eee' },
      horzLines: { color: '#eee' },
    },
    timeScale: {
      timeVisible: true,
      secondsVisible: false,
    },
    crossHair: {
      mode: 0,
    },
  })

  candlestickSeries = chart.addCandlestickSeries({
    upColor: '#FF4C4C',
    downColor: '#1E90FF',
    borderVisible: false,
    wickUpColor: '#FF4C4C',
    wickDownColor: '#1E90FF',
  })

  isChartReady = true
  console.log('📈 차트 초기화 완료')
}

onMounted(() => {
  initChart()

  // 💡 이 안에서만 watch 실행
  watch(() => props.ohlcData, (newData) => {
    if (!isChartReady || !candlestickSeries) {
      console.warn('⛔ 차트 아직 준비되지 않음')
      return
    }

    const rawData = toRaw(newData)
    console.log('✅ ohlcData 변경 감지:', rawData)

    if (!rawData || rawData.length === 0) return

    const formatted = rawData.map(item => ({
      time: Number(item.time),
      open: Number(item.open),
      high: Number(item.high),
      low: Number(item.low),
      close: Number(item.close),
    }))

    candlestickSeries.setData(formatted)
    chart.timeScale().scrollToRealTime()
  }, { immediate: true })

  watch(() => props.currentPrice, (price) => {
    if (!candlestickSeries || !price) return

    if (priceLine) {
      candlestickSeries.removePriceLine(priceLine)
    }

    priceLine = candlestickSeries.createPriceLine({
      price,
      color: 'red',
      lineWidth: 1,
      lineStyle: 2,
      axisLabelVisible: true,
      title: '현재가',
    })
  })
})
</script>

<template>
  <div ref="chartContainer" class="chart-container" />
</template>

<style scoped>
.chart-container {
  width: 100%;
  max-width: 800px;
  height: 400px;
  margin: 0 auto;
}
</style>
