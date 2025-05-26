<template>
 <div class="chart-container">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title, Tooltip, Legend,
  LineElement, PointElement, LinearScale, CategoryScale
} from 'chart.js'

import { ref, watch } from 'vue'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, LinearScale, CategoryScale)

const props = defineProps({
  priceHistory: Array
})

const chartData = ref({
  labels: [],
  datasets: [{
    label: '현재가 추이',
    data: [],
    borderColor: 'blue',
    backgroundColor: 'lightblue',
    fill: false,
    tension: 0.3
  }]
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: false
    }
  }
}

watch(() => props.priceHistory, (newVal) => {
  const copied = [...newVal]
  chartData.value = {
    labels: copied.map((_, idx) => idx + 1),
    datasets: [{
      label: '현재가 추이',
      data: copied,
      borderColor: 'blue',
      backgroundColor: 'lightblue',
      fill: false,
      tension: 0.3
    }]
  }
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  max-width: 600px;     
  height: 300px;         
  margin: 0 auto;
}
</style>