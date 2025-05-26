<template>
  <div style="height: 300px;"> <!-- 그래프 높이 조정 -->
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const props = defineProps({
  intrRate: Number,
  intrRate2: Number,
})

const chartData = {
  labels: ['금리'],
  datasets: [
    {
      label: '기본 금리(%)',
      data: [props.intrRate],
      backgroundColor: 'rgba(205, 206, 210, 0.8)',
    },
    {
      label: '최고 금리(%)',
      data: [props.intrRate2],
      backgroundColor: 'rgba(0, 123, 255, 0.8)',
    },
  ],
}

const chartOptions = {
  responsive: true,
  indexAxis: 'y', 
  maintainAspectRatio: false,
  animation: {
    duration: 1000,
    easing: 'easeOutQuart',
  },
  plugins: {
    legend: {
      display: true,
      position: 'top',
      labels: {
        font: {
          size: 14,
        },
        color: '#000',
      },
    },
    title: {
      display: true,
      text: '금리 비교 그래프',
      font: {
        size: 25,
      },
      color: '#000',
    },
  },
  scales: {
    x: {
      ticks: {
        color: '#000',
        font: {
          size: 15,
        },
      },
      grid: {
        color: '#eee',
      },
    },
    y: {
      beginAtZero: true,
      max: Math.max(props.intrRate, props.intrRate2) + 1,
      ticks: {
        display: false, 
        color: '#000',
        font: {
          size: 13,
        },
      },
      grid: {
        color: '#eee',
      },
    },
  },
}
</script>
