<template>
  <div class="my-assets">
    <div class="asset-summary-box" v-if="summary">
      <div class="summary-top">
        <div class="summary-block">
          <p class="label">보유 KRW</p>
          <p class="value">{{ Math.floor(summary.balance).toLocaleString() }}</p>
        </div>
        <div class="vertical-divider"></div>
        <div class="summary-block">
          <p class="label">총 보유자산</p>
          <p class="value">{{ Math.floor(summary.total_asset).toLocaleString() }}</p>
        </div>
      </div>

      <div class="summary-middle">
        <div class="summary-item">
          <span class="item-label">총 매수</span>
          <span class="item-value">{{ Math.floor(totalPurchase).toLocaleString() }}</span>
        </div>
        <div class="summary-item">
          <span class="item-label">총 평가금액</span>
          <span class="item-value">{{ Math.floor(totalEvaluation).toLocaleString() }}</span>
        </div>
        <div class="summary-item">
          <span class="item-label">총 평가</span>
          <span class="item-value">{{ Math.floor(summary.total_evaluation).toLocaleString() }}</span>
        </div>
        <div class="summary-item">
          <span class="item-label">주문가능</span>
          <span class="item-value">0</span>
        </div>
        <div class="summary-item">
          <span class="item-label">평가손익</span>
          <span class="item-value" :class="totalProfit >= 0 ? 'positive' : 'negative'">
            {{ Math.floor(totalProfit).toLocaleString() }}
          </span>
        </div>
        <div class="summary-item">
          <span class="item-label">수익률</span>
          <span class="item-value" :class="totalRate >= 0 ? 'positive' : 'negative'">
            {{ totalRate.toFixed(2) }}%
          </span>
        </div>
        <div class="summary-item">
          <span class="item-label"> </span>
        </div>
      </div>
    </div>

    <div class="portfolio-section">
      <h3>보유 자산 포트폴리오</h3>
      <div class="donut-legend-wrap">
        <div class="chart-area">
        <DonutChart
          v-if="summary && summary.holdings"
          :holdings="summary.holdings"
          :cash="summary.balance"
          :colors="colorList"
        />
        </div>
        <div class="legend-area">
          <div
            v-for="(item, index) in (summary?.holdings?.length
              ? [{ name: '현금', evaluation_amount: summary.balance }].concat(summary.holdings)
              : [])"
                :key="index"
                class="legend-item"
              >
                <span
                  class="legend-color"
                  :style="{ backgroundColor: colorList[index] }"
                ></span>
                <span class="legend-label">
              {{ item.name }} —
              {{ ((item.evaluation_amount / totalAmount) * 100).toFixed(1) }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <table v-if="summary" class="asset-table">
      <thead>
        <tr>
          <th>종류명</th>
          <th>보유수량</th>
          <th>평균단가</th>
          <th>현재가</th>
          <th>평가금액</th>
          <th>수익률</th>

        </tr>
      </thead>
      <tbody>
        <tr v-for="item in summary.holdings" :key="item.code">
          <td>
            <RouterLink :to="{ name: 'stock-detail', params: { code: item.code } }">
              {{ item.name }}
            </RouterLink>
          </td>
          <td>{{ item.quantity }}</td>
          <td>{{ parseInt(item.average_price).toLocaleString() }}원</td>
          <td>{{ parseInt(item.current_price).toLocaleString() }}원</td>
          <td>{{ parseInt(item.evaluation_amount).toLocaleString() }}원</td>

          <td :class="item.rate > 0 ? 'positive' : item.rate < 0 ? 'negative' : ''">
            {{ item.rate }}%
          </td>

        </tr>
      </tbody>
    </table>

    <p v-if="summary?.holdings?.length === 0" class="no-holdings-message">
   보유 중인 주식이 없습니다.
</p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import axios from '@/stores/axios'
import socket from '@/stores/socket'
import DonutChart from '@/components/DonutChart.vue'

const summary = ref(null)

const totalPurchase = computed(() =>
  summary.value?.holdings?.length
    ? summary.value.holdings.reduce((acc, h) => acc + h.average_price * h.quantity, 0)
    : 0
)


const totalEvaluation = computed(() =>
  summary.value?.holdings?.length
    ? summary.value.holdings.reduce((acc, h) => acc + h.current_price * h.quantity, 0)
    : 0
)
const totalProfit = computed(() =>
  totalEvaluation.value - totalPurchase.value
)

const totalRate = computed(() =>
  totalPurchase.value
    ? (totalProfit.value / totalPurchase.value) * 100
    : 0
)
const totalAmount = computed(() => {
  return summary.value
    ? summary.value.holdings.reduce((acc, h) => acc + h.evaluation_amount, 0) + summary.value.balance
    : 0
})
const colorList = [
  '#AED581', '#81D4FA', '#F8BBD0', '#FFCC80', '#CE93D8',
  '#A5D6A7', '#EF9A9A', '#80DEEA', '#B39DDB', '#FFAB91',
  '#90A4AE', '#F0F4C3', '#BCAAA4', '#80CBC4', '#FFE082',
  '#E0E0E0' // 현금 색
]

onMounted(async () => {
  try {
    const res = await axios.get('/api/trade/summary/')
    summary.value = res.data
  } catch (err) {
    console.error('❌ 요약 불러오기 실패:', err)
    alert('보유 자사 정보를 불러오는 데 실패했습니다.')
  }

  socket.on('stock_data', (data) => {
    if (!summary.value?.holdings) return

    const target = summary.value.holdings.find(h => h.code === data.code)
    if (target) {
      const currentPrice = Number(data.current_price)
      target.current_price = currentPrice
      target.evaluation_amount = target.quantity * currentPrice
      target.rate = target.average_price > 0
        ? Math.round(((currentPrice - target.average_price) / target.average_price) * 10000) / 100
        : 0

      summary.value.holdings = [...summary.value.holdings]
      summary.value.total_evaluation = summary.value.holdings.reduce((acc, h) => acc + h.evaluation_amount, 0)
      summary.value.total_asset = summary.value.balance + summary.value.total_evaluation
      summary.value.profit = summary.value.total_asset - totalPurchase.value
    }
  })
})

onUnmounted(() => {
  socket.off('stock_data')
})
</script>

<style scoped>
.my-assets {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  background: #fff;
}

.asset-summary-box {
  background: #f9fbff;
  border: 1px solid #e1e1e1;
  border-radius: 12px;
  padding: 1rem 1.5rem;
  margin-bottom: 2rem;
}

.summary-top {
  display: flex;
  justify-content: space-evenly;
  margin-bottom: 1rem;
}

.summary-block {
  text-align: center;
}

.label {
  font-size: 0.9rem;
  color: #999;
}

.value {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
}

.summary-middle {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 1rem;
  font-size: 0.95rem;
}

.summary-item {
  flex: 1 1 40%;
  display: flex;
  justify-content: space-between;
  border-bottom: 1px dashed #ddd;
  padding-bottom: 0.3rem;
}

.item-label {
  color: #666;
}

.item-value {
  font-weight: 600;
}

.positive {
  color: red;
}

.negative {
  color: #007bff;
}

.portfolio-section {
  margin-bottom: 2rem;
  justify-content: flex-end;
}

.donut-legend-wrap {
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  gap: 2rem;
  width: 100%;
  padding-right: 2rem;
  padding-left: 3rem;
  position: relative;        /* 기준점 설정 */
}

/* ✅ chart 아래쪽으로 밀기 (예: 30px) */
.chart-area {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 30px;         /* ⬅ 아래로 밀기 */
}

/* ✅ legend 오른쪽으로 밀기 (예: 30px) */
.legend-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  white-space: nowrap;
  padding-left: 70px;        /* ⬅ 오른쪽으로 밀기 */
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

.asset-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  margin-top: 1.5rem;
}

.asset-table th,
.asset-table td {
  padding: 0.75rem;
  text-align: center;
  border-bottom: 1px solid #eee;
}

.asset-table th {
  background-color: #f8f8f8;
  color: #999;
  font-weight: 600;
}

.asset-table tr:nth-child(even) {
  background-color: #fafafa;
}

a {
  color: #007bff;
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}

.vertical-divider {
  width: 1px;
  height: 6rem;
  background-color: rgb(228, 228, 228);
  margin: 0 1.5rem;
}

.no-holdings-message {
  background-color: #f5f8ff;
  color: #007bff;
  border: 1px solid #cce5ff;
  border-radius: 8px;
  padding: 16px 20px;
  text-align: center;
  font-size: 1rem;
  font-weight: 500;
  margin-top: 24px;
  box-shadow: 0 2px 6px rgba(0, 123, 255, 0.08);
}
</style>
