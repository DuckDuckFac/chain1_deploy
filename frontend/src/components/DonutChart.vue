<template>
  <div class="donut-legend-wrap">
    <!-- 도넛 차트 영역 -->
    <div class="chart-area">
      <Doughnut :data="chartData" :options="chartOptions" :width="500" :height="600" />
    </div>
</div>

</template>

<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from 'chart.js'
import ChartDataLabels from 'chartjs-plugin-datalabels'

const centerImagePlugin = {
  id: 'centerImage',
  afterDraw(chart, args, options) {
    const { ctx, chartArea: { left, top, width, height } } = chart
    const image = new Image()
    image.src = options.imageSrc
    image.onload = () => {
      const centerX = left + width / 2
      const centerY = top + height / 2

      const maxSize = options.size || 80
      const aspectRatio = image.width / image.height

      let drawWidth, drawHeight

      if (aspectRatio >= 1) {
        // 가로가 더 길다 → 가로 기준
        drawWidth = maxSize
        drawHeight = maxSize / aspectRatio
      } else {
        // 세로가 더 길다 → 세로 기준
        drawHeight = maxSize
        drawWidth = maxSize * aspectRatio
      }

      const x = centerX - drawWidth / 2
      const y = centerY - drawHeight / 2
      ctx.drawImage(image, x, y, drawWidth, drawHeight)
    }
  }
}



// Chart.js 구성 요소 등록
ChartJS.register(Title, Tooltip, Legend, ArcElement, ChartDataLabels, centerImagePlugin)

// props 정의
const props = defineProps({
  holdings: Array,
  cash: Number,
  colors: Array
})


// ✅ labels 및 safeColors 계산
const labels = [...props.holdings.map(h => h.name), '현금']

const safeColors = props.colors.length >= labels.length
  ? props.colors
  : [...props.colors, ...Array(labels.length - props.colors.length).fill('#cccccc')]

// ✅ 차트 데이터
const chartData = computed(() => ({
  labels,
  datasets: [{
    data: [...props.holdings.map(h => h.evaluation_amount), props.cash],
    backgroundColor: safeColors
  }]
}))

// ✅ 라벨(legend) 항목
const legendItems = computed(() => (
  [...props.holdings.map((h, i) => ({
    label: h.name,
    color: safeColors[i]
  })), {
    label: '현금',
    color: safeColors[props.holdings.length]
  }]
))

// ✅ 차트 옵션
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    datalabels: {
      color: '#000',
      font: {
        weight: 'thin',
        size: 12
      },
      formatter: (value, context) => {
        const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0)
        const percent = (value / total) * 100
        return percent > 5 ? `${percent.toFixed(1)}%` : ''
      }
    },
    centerImage: {
      imageSrc: '/cute.png', 
      
      size: 150
    }
  }
}


</script>

<style scoped>
.donut-legend-wrap {
  display: flex;
  align-items: flex-start;
  gap: 2rem;
  justify-content: flex-start;
  flex-wrap: nowrap;
  max-width: 640px;
  margin: 0 auto;
}

.chart-area {
  flex: 0 0 300px;
  width: 360px;
  height: 360px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.legend-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  white-space: nowrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  display: inline-block;
}

.legend-label {
  font-size: 0.95rem;
  color: #444;
}
</style>
