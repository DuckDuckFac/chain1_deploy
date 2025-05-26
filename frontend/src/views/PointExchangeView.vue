<template>
  <div class="exchange-container">
    <h2>🏦 포인트 교환소</h2>
    <p>현재 보유 포인트: <strong>{{ profile?.usable_points || 0 }}</strong> pt</p>
    <p>💰 잔고: <strong>{{ account?.balance?.toLocaleString() || 0 }}</strong> 원</p>

    <div class="form-box">
      <label for="points">교환할 포인트:</label>
      <input type="number" id="points" v-model.number="pointsToExchange" min="1" />

      <p>→ 예상 지급 금액: <strong>{{ formattedAmount }}원</strong></p>

      <button @click="exchangePoints" :disabled="!canExchange">💱 교환하기</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from '@/stores/axios'
import { useUserStore } from '@/stores/user'
import { useAccountStore } from '@/stores/account' 
import swal from 'sweetalert'

// 잔고
const accountStore = useAccountStore()
const account = computed(() => accountStore.account)

const userStore = useUserStore()
const profile = computed(() => userStore.userProfile)

const pointsToExchange = ref(0)
const rate = 10000  // 1포인트 = 10000원

const formattedAmount = computed(() =>
  (pointsToExchange.value * rate).toLocaleString()
)

const canExchange = computed(() =>
  pointsToExchange.value > 0 &&
  pointsToExchange.value <= (profile.value?.usable_points || 0)
)

const exchangePoints = async () => {
  try {
    const res = await axios.post('http://127.0.0.1:8000/api/trade/exchange/', {
      points: pointsToExchange.value
    })
    alert(res.data.message)
    await accountStore.fetchAccount()
    await userStore.getProfile()
    pointsToExchange.value = 0

  } catch (err) {
    console.error('교환 실패:', err)
    alert('교환 중 오류가 발생했습니다.')  
  }
}

onMounted(async () => {
  await userStore.getProfile()
  await accountStore.fetchAccount()
})
</script>

<style scoped>
.exchange-container {
  max-width: 500px;
  margin: 2rem auto;
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: 10px;
  background: #fafafa;
}

.form-box {
  margin-top: 1.5rem;
}

input {
  padding: 0.5rem;
  margin-top: 0.3rem;
  width: 100%;
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
}

button {
  padding: 0.6rem 1rem;
  background-color: #42b983;
  color: white;
  font-weight: bold;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
