<template>
  <div class="trade-container">
    <div class="grid-layout">
      <div class="col col-2">
        <VirtualAccountCard />
      </div>
      <div class="col col-6 chart-wrapper">
        <StockChartPanel
          :stock="stock"
          :isLiked="isLiked"
          :selectedInterval="selectedInterval"
          @update:selectedInterval="val => selectedInterval = val"
          :ohlcData="ohlcData"
          :toggleLike="toggleLike"
        />
      </div>
      <div class="col col-4">
        <TradePanel
          :key="orderTab + '-' + filteredOrders.length"
          :tab="tab" @update:tab="val => tab = val"
          :showQuickOrder="showQuickOrder" :toggleQuickOrder="() => showQuickOrder = !showQuickOrder"
          :price="price" @update:price="val => price = val"
          :quantity="quantity" @update:quantity="val => quantity = val"
          :submitReservedTrade="submitReservedTrade"
          :pendingOrders="pendingOrders" :deleteReserve="deleteReserve"
          :marketBuy="marketBuy" :marketSell="marketSell"
          :quickQty="quickQty" @update:quickQty="val => quickQty = val"
          :holdingQuantity="holdingQuantity" :averagePrice="averagePrice"
          :orderTab="orderTab" @update:orderTab="val => orderTab = val"
          :filteredOrders="filteredOrders"
          :availableBuyQty="availableBuyQty" :availableSellQty="availableSellQty"
          :stockName="stock?.name"
          :currentPrice="stock?.current_price"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watchEffect, watch } from 'vue'
import { useRoute } from 'vue-router'
import StockChartPanel from '@/components/StockChartPanel.vue'
import TradePanel from '@/components/TradePanel.vue'
import VirtualAccountCard from '@/components/VirtualAccountCard.vue'
import { useUserStore } from '@/stores/user'
import { useAccountStore } from '@/stores/account'
import { useStockChartStore } from '@/stores/stockchart'
import axios from '@/stores/axios.js'
import { useNotificationStore } from '@/stores/notification'
import swal from 'sweetalert'

const route = useRoute()
const code = route.params.code.replace('K', '')

const store = useStockChartStore()
const userStore = useUserStore()
const accountStore = useAccountStore()
const notificationStore = useNotificationStore()

let prevLength = notificationStore.notifications.length

const stock = computed(() => store.currentPriceMap[code])
const myUserId = computed(() => userStore.userInfo?.id)

const selectedInterval = ref('1m')
const ohlcData = ref([])

const tab = ref('buy')
const orderTab = ref('pending')
const showQuickOrder = ref(false)
const price = ref(0)
const quantity = ref(1)
const quickQty = ref(1)
const tradeType = ref('BUY')
const reserveList = ref([])

const filteredOrders = computed(() => reserveList.value.filter(r => orderTab.value === 'pending' ? !r.executed : r.executed))
const pendingOrders = computed(() => reserveList.value.filter(r => !r.executed))

const balance = ref(0)
const holdingQuantity = ref(0)
const averagePrice = ref(0)

const availableBuyQty = computed(() => !stock.value?.current_price || !balance.value ? 0 : Math.floor(balance.value / stock.value.current_price))
const availableSellQty = computed(() => holdingQuantity.value)
const isLiked = ref(false)

watchEffect(() => {
  tradeType.value = tab.value.toUpperCase()
})

const fetchAccountAndHoldings = async () => {
  try {
    const [accountRes, holdingsRes] = await Promise.all([
      axios.get('/api/trade/account/'),
      axios.get('/api/trade/holdings/'),
    ])
    balance.value = accountRes.data.balance
    const match = holdingsRes.data.find(h => h.code === code)
    if (match) {
      holdingQuantity.value = match.quantity
      averagePrice.value = match.average_price
    } else {
      holdingQuantity.value = 0
      averagePrice.value = 0
    }
  } catch (err) {
    console.error('❌ 계좌/보유 종목 조회 실패:', err)
  }
}

const fetchReserveList = async () => {
  try {
    const res = await axios.get(`/api/trade/reserve/${code}/`)
    reserveList.value = [...res.data]
    console.log('✅ 최신 예약 리스트:', res.data)
  } catch (err) {
    console.error('❌ 예약 리스트 불러오기 실패:', err)
  }
}

const submitReservedTrade = async () => {
  try {
    await axios.post('/api/trade/reserve/', {
      code,
      name: stock.value?.name || code,
      trade_type: tradeType.value,
      target_price: price.value,
      quantity: quantity.value,
    })
    swal('✅ 예약 등록 완료', `${stock.value?.name} ${quantity.value}주 예약됨`, 'success')
    fetchReserveList()
  } catch (err) {
    swal('❌ 예약 실패', err.response?.data?.detail || '서버 오류', 'error')
  }
}

const deleteReserve = async (id) => {
  const confirm = await swal({
    title: '예약 취소',
    text: '정말 삭제하시겠습니까?',
    icon: 'warning',
    buttons: true,
    dangerMode: true
  })
  if (!confirm) return

  try {
    await axios.delete(`/api/trade/reserve/${code}/${id}/`)
    swal('✅ 예약 삭제 완료', '', 'success')
    fetchReserveList()
  } catch (err) {
    swal('❌ 삭제 실패', err.response?.data?.detail || '서버 오류', 'error')
  }
}

const marketBuy = async () => {
  if (quickQty.value <= 0) return swal('수량 오류', '수량을 입력해주세요.', 'warning')
  try {
    await axios.post('/api/trade/buy-now/', {
      code,
      name: stock.value?.name || code,
      quantity: quickQty.value,
      price: stock.value?.current_price,
    })
    swal('✅ 매수 완료', `${stock.value?.name} ${quickQty.value}주 매수 완료`, 'success')

    // ✅ 알림 발생
    pushImmediateNotification({
      stockName: stock.value?.name || code,
      price: stock.value?.current_price,
      quantity: quickQty.value,
      tradeType: 'BUY',
      route: { name: 'stock-detail', params: { code } }
    })
    fetchAccountAndHoldings()
    await accountStore.fetchAccount()
  } catch (err) {
    swal('❌ 매수 실패', err.response?.data?.detail || '서버 오류', 'error')
  }
}

const marketSell = async () => {
  if (quickQty.value <= 0) return swal('수량 오류', '수량을 입력해주세요.', 'warning')
  try {
    await axios.post('/api/trade/sell-now/', {
      code,
      name: stock.value?.name || code,
      quantity: quickQty.value,
      price: stock.value?.current_price,
    })
    swal('✅ 매도 완료', `${stock.value?.name} ${quickQty.value}주 매도 완료`, 'success')

    // ✅ 알림 발생
    pushImmediateNotification({
      stockName: stock.value?.name || code,
      price: stock.value?.current_price,
      quantity: quickQty.value,
      tradeType: 'SELL',
      route: { name: 'stock-detail', params: { code } }
    })
    fetchAccountAndHoldings()
    await accountStore.fetchAccount()
  } catch (err) {
    swal('❌ 매도 실패', err.response?.data?.detail || '서버 오류', 'error')
  } 
}

const fetchLikeStatus = async () => {
  try {
    const res = await axios.get(`/api/trade/like/${code}/`)
    isLiked.value = res.data.liked
  } catch (err) {
    console.error('❌ 좋아요 상태 조회 실패:', err)
  }
}

const toggleLike = async () => {
  try {
    const res = await axios.post(`/api/trade/like/${code}/`, {
      name: stock.value?.name || ''
    })
    isLiked.value = res.data.liked
    await accountStore.fetchLikedStocks()
  } catch (err) {
    console.error('❌ 좋아요 토글 실패:', err)
  }
}

// 알람처리 ----------------------
const pushImmediateNotification = ({ stockName, price, quantity, tradeType, route }) => {
  const message = `${stockName} ${price}원에 ${quantity}주 ${tradeType === 'BUY' ? '매수' : '매도'} 체결`

  const notif = {
    message,
    route,
    timestamp: new Date().toISOString()
  }

  notificationStore.addNotification(notif)
  notificationStore.notifications.unshift(notif)

  if (Notification.permission === 'granted') {
    new Notification('💰 GooseBank 알림', {
      body: message,
    })
  }
}
// --------------------------------
onMounted(async () => {
  await fetchLikeStatus()
  await store.preloadOHLC(code)
  store.startOHLCFor(code, selectedInterval.value)
  if (stock.value?.current_price) {
    price.value = stock.value.current_price
  }
  await fetchReserveList()
  await fetchAccountAndHoldings()
})

watchEffect(() => {
  const real = store.ohlcMap[code]?.[selectedInterval.value]
  if (!Array.isArray(real) || real.length === 0) return

  const hasInvalid = real.some(item => {
    return ['time', 'open', 'high', 'low', 'close'].some(key => {
      return item[key] === undefined || item[key] === null || isNaN(item[key])
    })
  })

  if (hasInvalid) {
    console.warn('❌ 유효하지 않은 값 포함됨', real)
  }

  ohlcData.value = real.map(item => ({
    time: Number(item.time),
    open: Number(item.open),
    high: Number(item.high),
    low: Number(item.low),
    close: Number(item.close),
  }))
})

watch(
  () => notificationStore.notifications.length,
  (len) => {
    const latest = notificationStore.notifications[0]

    if (len <= prevLength) {
      prevLength = len
      return
    }
    prevLength = len

    if (latest?.user_id === myUserId.value && latest?.code === code) {
      const message = latest.message || '체결됨'
      swal("📢 체결 완료", message, "info")

      fetchReserveList()
      fetchAccountAndHoldings()
      accountStore.fetchAccount()
      orderTab.value = 'done'
    }
  }
)


</script>

<style scoped>
.trade-container {
  height: 100vh;
  overflow: hidden;
}
.grid-layout {
  display: flex;
  height: 100%;
}
.col {
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
.col-2 {
  flex: 1.9;
  border-right: 1px solid #ddd;
}
.col-6 {
  flex: 6.1;
  border-right: 1px solid #ddd;
}
.col-4 {
  flex: 4;
}
.chart-wrapper {
  display: flex;
  flex-direction: column;
  justify-content: stretch;
}
</style>
