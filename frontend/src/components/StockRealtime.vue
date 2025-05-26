<template>
  <div class="stock-section">
    <!-- 🔸 오늘의 주식 카드 -->
    <div class="top-stocks">
      <h2>오늘의 주식</h2>
      <div class="top-stock-cards">
        <div
          v-for="item in topThreeStocks"
          :key="item.code"
          class="top-stock-card"
          @click="goToDetail(item.code)"
        >
          <div class="rank-badge">{{ topThreeStocks.indexOf(item) + 1 }}위</div>
          <div v-if="parseFloat(item.rate) >= 15" class="badge-surge">급등주 🚀</div>
<!-- ✅ Flex 구조로 감싸기 -->
  <div class="card-content">
    <div class="text-info">
      <h3
        class="name-with-code"
        :class="{ 'smaller-name': (item.name || '').length < 6 }"
      >
        {{ item.name }}
      </h3>
      <p class="code-under-name">({{ item.code }})</p>
      <p
        :class="{
          'price-text': true,
          'price-small': (Math.floor(item.current_price).toLocaleString() + '원').length >= 7
        }"
      >
        <strong>현재가 : {{ Math.floor(item.current_price).toLocaleString() }}원</strong>
      </p>
      <p :class="rateClass(item.rate)">등락률 : {{ item.rate }}%</p>
    </div>
    <div class="mini-chart-box">
      <MiniChart
        :code="item.code" 
        :rate="Number(item.rate)"
        :compact="false"
        :width="200"
        :height="150"
      />
    </div>
  </div>

      </div>
    </div>
    </div>

    <!-- 🔹 정렬 버튼 -->
    <div class="sort-buttons">
      <button @click="setSortMode('rate-desc')">등락률 ⬆</button>
      <button @click="setSortMode('rate-asc')">등락률 ⬇</button>
      <button @click="setSortMode('liked')">💛 좋아요 우선</button>
    </div>

    <!-- 🔸 표 형태 전체 종목 -->
    <table class="stock-table">
  <thead>
    <tr>
      <th>💛 순위</th>
      <th>종목명 (코드)</th>
      <th>현재가</th>
      <th>등락률</th>
      <th>미니차트</th>
    </tr>
  </thead>
  <tbody>
    <tr
      v-for="(item, index) in stockList"
      :key="item.code"
      @click="goToDetail(item.code)"
      class="stock-row"
      :class="{ even: index % 2 === 1 }"
    >
      <td>
        <button
          v-if="isLogin"
          class="like-button"
          @click.stop="toggleLike(item)"
        >
          {{ item.liked ? '💛' : '🤍' }}
        </button>
        <span class="rank-number">{{ index + 1 }}위</span>
      </td>
      <td>
        <strong>{{ item.name || '이름 없음' }}</strong><br />
        <span class="stock-code">({{ item.code }})</span>
      </td>
      <td><strong>{{ Math.floor(item.current_price).toLocaleString() }}원</strong></td>
      <td :class="rateClass(item.rate)"><strong>{{ item.rate }}%</strong></td>
      <td>
        <div class="mini-chart-wrapper">
          <MiniChart
            :code="item.code"
            :rate="Number(item.rate)"
            :compact="true"
            :bg-color="index % 2 === 0 ? '#ffffff' : '#f4f6f8'"
          />
        </div>
      </td>
    </tr>
  </tbody>
</table>
  </div>
</template>



<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { io } from 'socket.io-client'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAccountStore } from '@/stores/account'
import axios from '@/stores/axios'
import MiniChart from '@/components/MiniChart.vue'
import socket from '@/stores/socket'
import { useNotificationStore } from '@/stores/notification'


const stockList = ref([])
const likedSet = ref(new Set())
const router = useRouter()
const accountStore = useAccountStore()
const userStore = useUserStore()
const isLogin = computed(() => userStore.isLogin)
const notificationStore = useNotificationStore()
const goToDetail = (code) => {
  router.push({ name: 'stock-detail', params: { code } })
}
const topThreeStocks = computed(() => {
  return [...stockList.value]
    .sort((a, b) => parseFloat(b.rate) - parseFloat(a.rate))
    .slice(0, 3)
})
const rateClass = (rate) => {
  const r = parseFloat(rate)
  if (isNaN(r)) return ''
  if (r > 0) return 'rise'
  if (r < 0) return 'fall'
  return ''
}
// 정렬 로직
const sortMode = ref('rate-desc')  // 기본값: 등락률 내림차순

const setSortMode = (mode) => {
  sortMode.value = mode
  sortStockList()
}

const sortStockList = () => {
  if (sortMode.value === 'rate-desc') {
    stockList.value.sort((a, b) => parseFloat(b.rate) - parseFloat(a.rate))
  } else if (sortMode.value === 'rate-asc') {
    stockList.value.sort((a, b) => parseFloat(a.rate) - parseFloat(b.rate))
  } else if (sortMode.value === 'liked') {
    stockList.value.sort((a, b) => {
      const likeA = a.liked ? 1 : 0
      const likeB = b.liked ? 1 : 0
      return likeB - likeA
    })
  }
}

watch(() => notificationStore.tradeExecutedData, (data) => {
  if (!data) return
  if (data.user_id === userStore.userInfo.id) {
    swal(`${data.name} ${data.quantity}주 ${data.trade_type === 'BUY' ? '매수' : '매도'} 체결됨`, "", "success")
    accountStore.fetchAccount()
    accountStore.fetchLikedStocks()
  }
})

// 🔹 좋아요 토글
const toggleLike = async (item) => {
  try {
    const res = await accountStore.toggleLike(item.code, item.name || '')
    item.liked = res?.liked  // ✅ 서버 응답에 따라 바로 반영
  } catch (err) {
    console.error('❌ 좋아요 토글 실패:', err)
  }
}

onMounted(async () => {
  await accountStore.loadLikedStocks()
  likedSet.value = new Set(accountStore.likedStocks.map(s => s.code))

  socket.on('stock_data', (data) => {
    const idx = stockList.value.findIndex(s => s.code === data.code)
    const liked = likedSet.value.has(data.code)

    if (idx >= 0) {
      stockList.value[idx] = {
        ...stockList.value[idx],
        ...data,
        liked: stockList.value[idx].liked ?? liked,
      }
    } else {
      stockList.value.push({ ...data, liked })
    }

    // 🔁 정렬 실행
    sortStockList()
  })
  })

onUnmounted(() => {
  socket.off('stock_data')
  socket.off('trade_executed')
})
</script>


<style scoped>
.stock-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* 정렬 버튼 */
.sort-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin: 20px 0;
}

.sort-buttons button {
  background-color: #fffefee1;
  color: #62aeff;
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 2px 6px rgba(0, 123, 255, 0.1);
}

.sort-buttons button:hover {
  background-color: #d0e8ff;
}

/* 표 스타일 */
.stock-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
  border-top: 1px solid #ccc;
}
.stock-table th,
.stock-table td {
  border: none; /* 모든 선 제거 */
  border-bottom: 1px solid #ddd; /* 가로선만 */
  padding: 12px;
  text-align: center;
  vertical-align: middle;
}

.stock-row.even {
  background-color: #f4f6f8;
}
.stock-row:hover {
  background-color: #f5f9ff;
  cursor: pointer;
}

.rank-number {
  font-size: 0.8rem;
  color: #555;
  margin-left: 4px;
}


/* 공통 텍스트 스타일 */
.stock-code {
  font-size: 0.8rem;
  color: #888;
}
.like-button {
  background: none;
  border: none;
  font-size: 1.4rem;
  cursor: pointer;
}
.rise {
  color: #f02b2b;
  font-weight: bold;
}
.fall {
  color: #1f93e7;
  font-weight: bold;
}
.stock-row:hover {
  background-color: #f5f9ff;
  cursor: pointer;
}

/* 오늘의 주식 영역 */
.top-stocks {
  margin-bottom: 24px;
}
.top-stocks h2 {
  margin-bottom: 12px;
  font-size: 1.4rem;
  color: #333;
}

/* 카드 영역 */
.top-stock-cards {
  display: flex;
  justify-content: space-between;
  gap: 0;
  position: relative;

}

/* 카드 개별 스타일 */
.top-stock-card {
  flex: 1;
  width: 375px; /* ✅ 카드 가로 고정 */
  height: 230px; /* ✅ 카드 세로 고정 */
  margin: 0 8px;
  padding: 16px;
  background: #fffdf2;
  border: 2px solid #ffd700;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: transform 0.2s ease;
  position: relative;
  box-sizing: border-box;
  text-align: left;
}
.top-stock-card:first-child {
  margin-left: 0;
}
.top-stock-card:last-child {
  margin-right: 0;
}
.top-stock-card:hover {
  transform: scale(1.03);
}

/* 순위 뱃지 */
.rank-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  background: gold;
  color: #000;
  font-weight: bold;
  border-radius: 8px;
  padding: 4px 8px;
  font-size: 0.8rem;
}

/* 급등주 뱃지 */
.badge-surge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #ff6164e5;
  color: white;
  font-size: 0.75rem;
  font-weight: bold;
  padding: 4px 8px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}


/* 카드 내 텍스트 구조 정리 */
.top-stock-card h3 {
  margin-top: 48px; /* 뱃지 공간 확보 */
  font-size: 1.1rem;
  font-weight: bold;
}
.top-stock-card .stock-code {
  font-size: 0.85rem;
  color: #999;
  margin-bottom: 8px;
}
.top-stock-card .price {
  font-size: 0.95rem;
  color: #222;
  margin: 4px 0;
}
.top-stock-card .rate {
  font-size: 0.95rem;
  margin-bottom: 8px;
}
/* 미니차트 */
.mini-chart-wrapper {
  width: 100px;           /* 또는 max-width: 100px; */
  height: 30px;           /* compact 모드 기준 높이 */
  overflow: hidden;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mini-square-chart {
  width: 180px;
  height: 200px;
  margin-top: 12px;
  margin-left: auto;   /* 오른쪽 정렬 */
  margin-right: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}


.text-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.card-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start; /* 텍스트는 위에 고정 */
  position: relative;
}

.mini-chart-box {
  width: 100px;
  height: 50px;
  position: relative;
  bottom: 12px;
  right: 12px;
  margin-top: 50px;
  margin-right: 105px;
}

/* 카드 개별 스타일 */
.top-stock-card {
  flex: 1;
  width: 375px; /* ✅ 카드 가로 고정 */
  height: 230px; /* ✅ 카드 세로 고정 */
  flex: none; /* ✅ flex 비율 비활성화 */
  margin: 0 8px;
  padding: 16px;
  background: #fffdf2;
  border: 2px solid #ffd700;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  border-radius: 5px;
  transition: 0.2s;
}
.smaller-name {
  font-size: 1.6rem !important;
}
.code-under-name {
  font-size: 0.9rem;
  color: #999;
  margin-top: -8px; /* 살짝 붙이기 */
  margin-bottom: 4px;
}
.code-under-price {
  
  margin-top: 13px; 
}

.top-stock-card p {
  margin: 0; /* ✅ p 태그 기본 마진 제거 */
  line-height: 1.4;
}

.price-text {
  font-size: 1rem;
}
.price-small {
  font-size: 0.85rem;
}
</style>
