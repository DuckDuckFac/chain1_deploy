<template>
  <div class="trade-card">
    <!-- 간편 주문 버튼 & 탭 -->
    <div class="trade-header">
      <div class="tabs" v-if="!showQuickOrder">
        <button :class="{ active: localTab === 'buy' }" @click="localTab = 'buy'">구매</button>
        <button :class="{ active: localTab === 'sell' }" @click="localTab = 'sell'">판매</button>
        <button :class="{ active: localTab === 'reserve' }" @click="localTab = 'reserve'">대기</button>
      </div>
      <button class="quick-toggle" @click="toggleQuickOrder">
        {{ showQuickOrder ? '닫기' : '간편 주문' }}
      </button>
    </div>

    <!-- ✅ 간편 주문 -->
    <div v-if="showQuickOrder" class="quick-order-section">
      <h3>간편 주문</h3>
      <label>주문 수량:</label>
      <input type="number" v-model="localQuickQty" min="1" />
      <div class="quick-buttons">
        <button class="buy-btn" @click="confirmMarketBuy">시장가 구매</button>
        <button class="sell-btn" @click="confirmMarketSell">시장가 판매</button>
      </div>
    </div>

    <!-- ✅ 주문 패널 -->
    <div v-else>
      <!-- 구매 -->
      <div v-if="localTab === 'buy'" class="order-box">
        <h3>구매</h3>
        <p class="available">구매 가능 수량: {{ availableBuyQty }} 주</p>
        <input type="number" v-model="localPrice" placeholder="구매 가격" />
        <input type="number" v-model="localQuantity" placeholder="수량" />
        <button class="submit-btn" @click="confirmReservedTrade">예약 구매 등록</button>
      </div>

      <!-- 판매 -->
      <div v-if="localTab === 'sell'" class="order-box">
        <h3>판매</h3>
        <p class="available">판매 가능 수량: {{ availableSellQty }} 주</p>
        <input type="number" v-model="localPrice" placeholder="판매 가격" />
        <input type="number" v-model="localQuantity" placeholder="수량" />
        <button class="submit-btn" @click="confirmReservedTrade">예약 판매 등록</button>
      </div>

      <!-- 예약 -->
      <div v-if="localTab === 'reserve'" class="order-box">
        <h3>📋 예약 주문 내역</h3>
        <table v-if="pendingOrders.length">
          <thead>
            <tr>
              <th>종류</th>
              <th>목표가</th>
              <th>수량</th>
              <th>상태</th>
              <th>삭제</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in pendingOrders" :key="r.id">
              <td>{{ r.trade_type }}</td>
              <td>{{ r.target_price }}원</td>
              <td>{{ r.quantity }}</td>
              <td>{{ r.executed ? '완료' : '예약 중' }}</td>
              <td><button v-if="!r.executed" @click="deleteReserve(r.id)">❌</button></td>
            </tr>
          </tbody>
        </table>
        <p v-else>등록된 예약 주문이 없습니다.</p>
      </div>
    </div>

    <!-- ✅ 보유정보 -->
    <div class="holding-info">
      <h4>보유중</h4>
      <div v-if="holdingQuantity > 0">
        <p>보유 수량: {{ holdingQuantity }}주</p>
        <p>평단가: {{ averagePrice.toLocaleString() }}원</p>
      </div>
      <p v-else>이 종목을 보유하고 있지 않습니다.</p>
    </div>

    <!-- ✅ 주문 내역 -->
    <div class="order-history">
      <h4>📜 주문 내역</h4>
      <div class="order-tabs">
        <button @click="localOrderTab = 'pending'" :class="{ active: localOrderTab === 'pending' }">대기</button>
        <button @click="localOrderTab = 'done'" :class="{ active: localOrderTab === 'done' }">완료</button>
      </div>
      <ul v-if="filteredOrders.length">
        <li v-for="order in filteredOrders" :key="order.id">
          {{ order.trade_type }} - {{ order.quantity }}주 @ {{ order.target_price }}원
        </li>
      </ul>
      <p v-else>{{ localOrderTab === 'pending' ? '대기 중인' : '완료된' }} 주문이 없습니다.</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import swal from 'sweetalert'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const isLogin = computed(() => userStore.isLogin)

const emit = defineEmits([
  'update:quickQty',
  'update:price',
  'update:quantity',
  'update:orderTab',
  'update:tab'
])

const props = defineProps([
  'tab', 'showQuickOrder', 'toggleQuickOrder',
  'price', 'quantity', 'submitReservedTrade',
  'pendingOrders', 'deleteReserve',
  'marketBuy', 'marketSell', 'quickQty',
  'holdingQuantity', 'averagePrice',
  'orderTab', 'filteredOrders',
  'availableBuyQty', 'availableSellQty', 'stockName', 'currentPrice'
])

const localQuickQty = computed({
  get: () => props.quickQty,
  set: val => emit('update:quickQty', val)
})

const localPrice = computed({
  get: () => props.price,
  set: val => emit('update:price', val)
})

const localQuantity = computed({
  get: () => props.quantity,
  set: val => emit('update:quantity', val)
})

const localOrderTab = computed({
  get: () => props.orderTab,
  set: val => emit('update:orderTab', val)
})

const localTab = computed({
  get: () => props.tab,
  set: val => emit('update:tab', val)
})

const confirmMarketBuy = async () => {
  const total = localQuickQty.value * (props?.currentPrice || 0)
  const confirmed = await swal({
    title: `${props.stockName} ${localQuickQty.value}주 매수`,
    text: `총 ${total.toLocaleString()}원에 시장가로 매수하시겠습니까?`,
    icon: 'info',
    buttons: ['취소', '확인'],
  })
  if (confirmed) props.marketBuy()
}

const confirmMarketSell = async () => {
  const total = localQuickQty.value * (props?.currentPrice || 0)
  const confirmed = await swal({
    title: `${props.stockName} ${localQuickQty.value}주 매도`,
    text: `총 ${total.toLocaleString()}원에 시장가로 매도하시겠습니까?`,
    icon: 'info',
    buttons: ['취소', '확인'],
  })
  if (confirmed) props.marketSell()
}

const confirmReservedTrade = async () => {
  const total = localPrice.value * localQuantity.value
  const type = localTab.value === 'buy' ? '구매' : '판매'
  const confirmed = await swal({
    title: `${props.stockName} ${localQuantity.value}주 예약 ${type}`,
    text: `총 ${total.toLocaleString()}원에 예약 ${type}하시겠습니까?`,
    icon: 'info',
    buttons: ['취소', '확인'],
  })
  if (confirmed) props.submitReservedTrade()
}
</script>

<style scoped>
.trade-card {
  background: #fff;
  padding: 20px;
  border-radius: 20px;
  border: 1px solid #dbe4ed;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  font-family: 'Pretendard', sans-serif;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 헤더 */
.trade-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tabs button {
  padding: 6px 14px;
  border-radius: 12px;
  background: none;
  border: 1px solid #ccc;
  margin-right: 6px;
  cursor: pointer;
  font-weight: 500;
}

.tabs button.active {
  background: #eaf4ff;
  color: #007bff;
  font-weight: bold;
  border-color: #007bff;
}

.quick-toggle {
  background: #f0f8ff;
  color: #007bff;
  border: none;
  padding: 6px 12px;
  border-radius: 12px;
  cursor: pointer;
}

/* 주문 박스 */
.order-box input {
  width: 100%;
  padding: 8px;
  margin-top: 4px;
  margin-bottom: 12px;
  border-radius: 8px;
  border: 1px solid #ccc;
}

.submit-btn {
  width: 100%;
  padding: 10px;
  background: #007bff;
  color: #fff;
  font-weight: bold;
  border-radius: 10px;
  border: none;
  cursor: pointer;
}

.available {
  font-size: 0.9rem;
  margin: 8px 0;
}

/* 간편 주문 */
.quick-order-section input {
  width: 100%;
  padding: 8px;
  margin: 8px 0;
  border: 1px solid #ccc;
  border-radius: 8px;
}

.quick-buttons {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.buy-btn {
  flex: 1;
  background: #e0f7e9;
  color: #2e7d32;
  border: none;
  border-radius: 10px;
  padding: 8px;
  font-weight: bold;
  cursor: pointer;
}

.sell-btn {
  flex: 1;
  background: #ffebee;
  color: #c62828;
  border: none;
  border-radius: 10px;
  padding: 8px;
  font-weight: bold;
  cursor: pointer;
}

/* 보유 */
.holding-info {
  padding: 12px;
  border-top: 1px solid #eee;
  font-size: 0.9rem;
}

/* 주문 내역 */
.order-history {
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.order-tabs {
  display: flex;
  gap: 10px;
  margin: 10px 0;
}

.order-tabs button {
  flex: 1;
  padding: 6px;
  border-radius: 10px;
  border: 1px solid #ccc;
  background: #fafafa;
  cursor: pointer;
}

.order-tabs button.active {
  background: #e0f0ff;
  border-color: #007bff;
  color: #007bff;
  font-weight: bold;
}

.order-history ul {
  list-style: none;
  padding-left: 0;
}

/* 예약 주문 테이블 스타일 */
.order-box table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  font-size: 0.9rem;
}

.order-box th,
.order-box td {
  padding: 10px;
  text-align: center;
  border-bottom: 1px solid #eee;
}

.order-box th {
  background: #f9fbff;
  font-weight: 600;
  color: #333;
}

.order-box tr:hover {
  background: #f4f9ff;
}

.order-box button {
  background: none;
  border: 1px solid #333;
  cursor: pointer;
  font-size: 1rem;
  color: #d33;
}

.order-box button:hover {
  color: #f00;
}

.order-history li {
  padding: 8px 12px;
  border-bottom: 1px solid #eee;
  font-size: 0.95rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-history li:last-child {
  border-bottom: none;
}

.buy-label {
  color: #d32f2f;
  font-weight: bold;
}

.sell-label {
  color: #1976d2;
  font-weight: bold;
}
</style>
