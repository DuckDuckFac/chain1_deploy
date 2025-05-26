<template>
  <div class="account-card">
    <div class="nickname-line">
      <h2 class="nickname">{{ userInfo?.nickname || '사용자' }}</h2>
      <p class="duckbot">님의 계좌</p>
    </div>
        <div class="simple-links">
          <span @click="goToAssets">내 자산</span> |
          <span @click="goToTrades">거래 내역</span>
        </div> 
    <div v-if="isLogin">
      <div v-if="account">
        <div class="balance-block-vertical">
            <p class="label">총 잔고</p>
          <div class="balance-box">
            <p class="value blue">{{ Math.floor(account.balance).toLocaleString() }}<span class="unit">원</span></p>
          </div>
            <p class="label">총 수익</p>
          <div class="profit-box">
            <p class="value orange">{{ Math.floor(account.profit).toLocaleString() }}<span class="unit">원</span></p>
          </div>
        </div>

        <div v-if="likedStocks.length" class="liked-section">
          <h3 class="sub-title">💗 관심 종목</h3>
          <ul class="liked-list">
            <li v-for="stock in likedStocks" :key="stock.code" class="liked-item">
              <a class="stock-link" @click="goToStock(stock.codex)">
                {{ stock.name }} <span class="stock-code">({{ stock.code }})</span>
              </a>
            </li>
          </ul>
        </div>
        <p v-else class="no-liked">💗 표시한 종목이 없습니다.</p>
      </div>
      <p v-else class="loading">⏳ 데이터를 불러오는 중...</p>
    </div>

    <div v-else class="login-required">
      <p>🔐 로그인이 필요한 기능입니다</p>
      <button @click="goToLogin" class="login-button">로그인하러 가기</button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAccountStore } from '@/stores/account'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const accountStore = useAccountStore()

const account = computed(() => accountStore.account)
const likedStocks = computed(() => accountStore.likedStocks)

const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo)
const isLogin = computed(() => userStore.isLogin)

const goToStock = (code) => router.push({ name: 'stock-detail', params: { code } })
const goToAssets = () => router.push({ name: 'my-assets' })
const goToTrades = () => router.push({ name: 'my-trades' })
const goToLogin = () => router.push({ name: 'login', query: { next: route.fullPath } })

onMounted(async () => {
  await accountStore.fetchAccount()
  await accountStore.fetchLikedStocks()
})
</script>

<style scoped>
.account-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  max-width: 340px;
  width: 100%;
  margin: 0 auto;
  font-family: 'Pretendard', sans-serif;
  border: 1px solid #e6ecf1;
}

.section-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #222;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.balance-block-vertical {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.balance-box, .profit-box {
  background: #f9fbff;
  border: 1px solid #d9e7ff;
  border-radius: 12px;
  padding: 0px 8px;
  text-align: center;
  font-size: 0.95rem;
}

.label {
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 4px;
  padding-left: 4px;
}

.value {
  font-size: 1.2rem;
  font-weight: 800;
}

.blue {
  color: #5ca9fc;
}

.orange {
  color: #fcb769;
}

.unit {
  font-size: 0.85rem;
  margin-left: 2px;
  font-weight: 500;
}

.action-buttons {
  display: none;
}

.simple-links {
  display: flex;
  justify-content: center;
  gap: 12px;
  font-size: 0.95rem;
  color: #666;
  margin: 4px 0 16px;
}

.simple-links span {
  cursor: pointer;
}

.simple-links span:hover {
  color: #007bff;
}

.liked-section {
  margin-top: 24px;
}

.sub-title {
  font-size: 1rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 12px;
}

.liked-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.liked-item {
  margin-bottom: 6px;
}

.stock-link {
  color: #007bff;
  font-size: 0.95rem;
  cursor: pointer;
  transition: color 0.2s ease;
  text-decoration: none;
}

.stock-link:hover {
  color: #0056b3;
}

.stock-code {
  color: #999;
  font-size: 0.85rem;
}

.no-liked,
.loading,
.login-required p {
  font-size: 0.9rem;
  color: #999;
  margin-top: 16px;
  text-align: center;
}

.login-button {
  display: block;
  margin: 16px auto 0;
  background: #e0f0ff;
  color: #007bff;
  font-weight: 600;
  padding: 10px 20px;
  font-size: 0.95rem;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.15);
  transition: background 0.3s ease, box-shadow 0.3s ease;
}

.login-button:hover {
  background: #d4eaff;
}
.nickname-line {
  justify-content: center;
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.nickname {
  font-size: 1.2rem;
  color: #007bff;
  font-weight: 700;
}

.duckbot {
   font-size: 1rem;
  color: #949494;
  font-weight: 700;
  font-size: 1rem;
}
</style>