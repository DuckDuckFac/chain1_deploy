<template>
  <div class="container">
    <h2 class="section-title">📋 내 거래 내역</h2>

    <!-- 🔍 필터 UI -->
    <div class="filter-box">
      <div class="filter-item">
        <label>거래 구분</label>
        <select v-model="selectedType">
          <option value="all">전체</option>
          <option value="buy">매수</option>
          <option value="sell">매도</option>
        </select>
      </div>
      <div class="filter-item">
        <label>시작일</label>
        <input type="date" v-model="startDate" />
      </div>
      <div class="filter-item">
        <label>종료일</label>
        <input type="date" v-model="endDate" />
      </div>
      <div class="filter-item">
        <label>종목명</label>
        <input v-model="keyword" placeholder="예: 삼성전자" />
      </div>
    </div>

    <!-- 📈 수익 요약 -->
    <div class="summary-box">
      <p><strong>💰 매수 총액:</strong> {{ totalBuyAmount.toLocaleString() }}원</p>
      <p><strong>💵 매도 총액:</strong> {{ totalSellAmount.toLocaleString() }}원</p>
    </div>

    <!-- 📋 거래 테이블 -->
    <table v-if="pagedTrades.length" class="trade-table">
      <thead>
        <tr>
          <th>날짜</th>
          <th>종목명</th>
          <th>구분</th>
          <th>수량</th>
          <th>단가</th>
          <th>총액</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="t in pagedTrades" :key="t.id">
          <td>{{ formatDate(t.trade_time) }}</td>
          <td>{{ t.name }}</td>
          <td :class="t.trade_type === 'buy' ? 'buy' : 'sell'">
            {{ t.trade_type === 'buy' ? '매수' : '매도' }}
          </td>
          <td>{{ t.quantity }}</td>
          <td>{{ Math.floor(t.price).toLocaleString() }}원</td>
          <td>{{ Math.floor(t.price * t.quantity).toLocaleString() }}원</td>
        </tr>
      </tbody>
    </table>
    <p v-else class="empty-message">📭 거래 내역이 없습니다.</p>

    <!-- 페이지네이션 -->
    <div v-if="filteredTrades.length > pageSize" class="pagination">
      <button :disabled="currentPage === 1" @click="currentPage--">이전</button>
      <span>{{ currentPage }} / {{ Math.ceil(filteredTrades.length / pageSize) }}</span>
      <button :disabled="currentPage === Math.ceil(filteredTrades.length / pageSize)" @click="currentPage++">다음</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from '@/stores/axios.js'

const allTrades = ref([])
const currentPage = ref(1)
const pageSize = 10

const selectedType = ref('all')
const keyword = ref('')
const startDate = ref('')
const endDate = ref('')

const filteredTrades = computed(() => {
  return allTrades.value.filter(t => {
    const tradeDate = new Date(t.trade_time)
    const matchType = selectedType.value === 'all' || t.trade_type === selectedType.value
    const matchKeyword = !keyword.value || t.name.includes(keyword.value)
    const matchStart = !startDate.value || tradeDate >= new Date(startDate.value)
    const matchEnd = !endDate.value || tradeDate <= new Date(endDate.value + 'T23:59:59')
    return matchType && matchKeyword && matchStart && matchEnd
  })
})

const pagedTrades = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredTrades.value.slice(start, start + pageSize)
})

const totalBuyAmount = computed(() =>
  filteredTrades.value.filter(t => t.trade_type === 'buy')
    .reduce((sum, t) => sum + t.price * t.quantity, 0)
)
const totalSellAmount = computed(() =>
  filteredTrades.value.filter(t => t.trade_type === 'sell')
    .reduce((sum, t) => sum + t.price * t.quantity, 0)
)

const fetchAllTrades = async () => {
  try {
    const res = await axios.get(`/api/trade/trades/?limit=9999`)
    allTrades.value = res.data.results
  } catch (err) {
    console.error('❌ 거래 내역 불러오기 실패:', err)
    alert('거래 내역을 불러오지 못했습니다.')
  }
}

watch([selectedType, keyword, startDate, endDate], () => {
  currentPage.value = 1
})

onMounted(() => {
  fetchAllTrades()
})

const formatDate = (dt) => new Date(dt).toLocaleString()

onMounted(() => {
  const today = new Date().toISOString().split('T')[0]
  startDate.value = today
  endDate.value = today
  fetchAllTrades()
})
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}
.section-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #222;
  margin-bottom: 1rem;
}
.filter-box {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin: 20px 0;
}

.filter-item {
  display: flex;
  flex-direction: column;
  font-size: 0.9rem;
  color: #333;
}

.filter-item label {
  margin-bottom: 6px;
  font-weight: 600;
  color: #666;
}

.filter-item input,
.filter-item select {
  padding: 8px 12px;
  font-size: 0.95rem;
  border: none;
  border-radius: 8px;
  background-color: #f7f9fb;
  box-shadow: inset 0 0 0 1px #dce3eb;
  transition: box-shadow 0.2s ease;
}

.filter-item input:focus,
.filter-item select:focus {
  outline: none;
  box-shadow: 0 0 0 2px #007bff44;
}
.filter-item input[type="date"] {
  font-family: 'Pretendard', sans-serif;
  font-size: 0.95rem;
  color: #333;
}
.summary-box {
  background: #f9fbff;
  border: 1px solid #dbe9ff;
  padding: 1rem;
  border-radius: 12px;
  font-size: 0.95rem;
  color: #333;
  margin-bottom: 1rem;
}
.trade-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  font-size: 0.95rem;
}
.trade-table th,
.trade-table td {
  padding: 10px 12px;
  text-align: center;
  border-bottom: 1px solid #eee;
}
.trade-table th {
  background-color: #f1f1f1;
  color: #999;
  font-weight: 600;
}
.buy {
  color: #d33;
  font-weight: 600;
}
.sell {
  color: #007bff;
  font-weight: 600;
}
.empty-message {
  text-align: center;
  color: #888;
  margin-top: 2rem;
}
.pagination {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 1.5rem;
}
.pagination button {
  background: #007bff;
  color: white;
  padding: 6px 14px;
  font-size: 0.9rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.pagination button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
