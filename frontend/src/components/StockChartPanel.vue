<template>
  <div class="stock-chart-panel">
    <!-- 종목명 + 코드 + 하트 -->
    <div class="stock-header">
      <div class="name-code">
        <h2 class="stock-name">{{ stock?.name }}</h2>
        <span class="stock-code">({{ stock?.code }})</span>
      </div>
      <button @click="toggleLike" class="like-button">
        {{ isLiked ? '💛' : '🤍' }}
      </button>
    </div>

    <!-- 현재가 + 봉 주기 선택 -->
    <div class="price-and-interval">
      <p class="price-line">현재가: {{ stock?.current_price ?? '-' }}원</p>
      <div class="custom-select-group">
        <label for="interval">봉 주기</label>
        <select v-model="interval" id="interval">
          <option value="1m">1분</option>
          <option value="3m">3분</option>
          <option value="5m">5분</option>
          <option value="10m">10분</option>
          <option value="15m">15분</option>
          <option value="30m">30분</option>
          <option value="60m">60분</option>
        </select>
      </div>
    </div>

    <!-- 등락률 -->
    <p :class="rateClass(stock?.rate)">등락률: {{ stock?.rate ?? '-' }}%</p>

    <!-- 차트 -->
    <div class="chart-box">
    <CandlestickChart
      v-if="chartData.length > 0"
      :ohlcData="chartData"
      :currentPrice="Number(store.currentPriceMap[stockCode]?.current_price || 0)"
    />

    </div>
  </div>
</template>


<script setup>
import { computed } from 'vue'
import CandlestickChart from '@/components/CandlestickChart.vue'
import { useStockChartStore } from '@/stores/stockchart'

const props = defineProps([
  'stock',
  'isLiked',
  'selectedInterval',
  'ohlcData',
  'toggleLike'
])
const emit = defineEmits(['update:selectedInterval'])
const store = useStockChartStore()
const interval = computed({
  get: () => props.selectedInterval,
  set: (val) => emit('update:selectedInterval', val)
})
const stockCode = computed(() => props.stock?.code || '')
const rateClass = (rate) => {
  const r = parseFloat(rate)
  if (isNaN(r)) return ''
  if (r > 0) return 'rise'
  if (r < 0) return 'fall'
  return ''
}

const chartData = computed(() => {
  return store.ohlcMap[stockCode.value]?.[interval.value] || []
})
</script>

<style scoped>
.stock-chart-panel {
  background: #f9fbff;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
  box-sizing: border-box;
}

/* 상단 종목명 + 하트 한 줄 */
.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.name-code {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.stock-name {
  font-size: 1.6rem;
  font-weight: 700;
  margin: 0;
}

.stock-code {
  font-size: 0.95rem;
  color: #888;
}

.like-button {
  font-size: 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
}

/* 현재가/등락률 */
.stock-info {
  text-align: left;
}

.price-line {
  margin-top: 0.25rem;
  font-size: 1rem;
  font-weight: 500;
}

.rise {
  color: #e53935;
  font-weight: 600;
}
.fall {
  color: #1e88e5;
  font-weight: 600;
}

/* 봉 선택 셀렉터 */
.interval-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

/* 차트 */
.chart-box {
  flex: 1;
  width: 100%;
  margin-top: 1rem;
}
.chart-box canvas {
  width: 100% !important;
}

.price-and-interval {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: -8px;
}

/* 기존에서 가져온 선택 박스 스타일 */
.custom-select-group {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #888;
}

.custom-select-group select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background: url("data:image/svg+xml;charset=UTF-8,%3Csvg width='10' height='6' viewBox='0 0 10 6' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%23bbb' stroke-width='1.5' fill='none' fill-rule='evenodd'/%3E%3C/svg%3E") no-repeat right 8px center;
  background-color: transparent;
  border: 1px solid #e6ecf1;
  padding: 4px 28px 4px 8px;
  font-size: 0.85rem;
  color: #333;
  cursor: pointer;
}

.custom-select-group select option {
  color: #555;
  background: white;
  border: 1px solid #e6ecf1;
}
</style>
