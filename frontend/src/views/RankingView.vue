<template>
  <div class="ranking-board">
    <!-- ✅ 메인 타이틀 -->
    <h2 class="ranking-title">🏆 투자 랭킹</h2>

    <!-- 🔥 1~3등 카드 -->
    <div class="top-3-wrap">
      <!-- 2등 -->
      <div v-if="top3[1]" class="top-card rank-2">
        <div class="rank-badge">2위</div>
        <img :src="top3[1].profile_image || defaultImg" class="top-profile" alt="프로필" />
        <RouterLink
          :to="{ name: 'user-profile', params: { nickname: top3[1].nickname } }"
          class="top-nickname-link"
        >
          {{ top3[1].nickname || top3[1].username }}
        </RouterLink>
        <div class="top-profit" :style="{ color: (top3[1].return_rate ?? 0) >= 0 ? 'red' : 'blue' }">
          {{ (top3[1].return_rate ?? 0) >= 0 ? '🔺' : '🔻' }}
          {{ Math.abs(top3[1].return_rate ?? 0).toFixed(2) }}%
        </div>
      </div>

      <!-- 1등 -->
      <div v-if="top3[0]" class="top-card rank-1">
        <div class="rank-badge">1위</div>
        <img :src="top3[0].profile_image || defaultImg" class="top-profile" alt="프로필" />
        <RouterLink
          :to="{ name: 'user-profile', params: { nickname: top3[0].nickname } }"
          class="top-nickname-link"
        >
          {{ top3[0].nickname || top3[0].username }}
        </RouterLink>
        <div class="top-profit" :style="{ color: (top3[0].return_rate ?? 0) >= 0 ? 'red' : 'blue' }">
          {{ (top3[0].return_rate ?? 0) >= 0 ? '🔺' : '🔻' }}
          {{ Math.abs(top3[0].return_rate ?? 0).toFixed(2) }}%
        </div>
      </div>

      <!-- 3등 -->
      <div v-if="top3[2]" class="top-card rank-3">
        <div class="rank-badge">3위</div>
        <img :src="top3[2].profile_image || defaultImg" class="top-profile" alt="프로필" />
        <RouterLink
          :to="{ name: 'user-profile', params: { nickname: top3[2].nickname } }"
          class="top-nickname-link"
        >
          {{ top3[2].nickname || top3[2].username }}
        </RouterLink>
        <div class="top-profit" :style="{ color: (top3[2].return_rate ?? 0) >= 0 ? 'red' : 'blue' }">
          {{ (top3[2].return_rate ?? 0) >= 0 ? '🔺' : '🔻' }}
          {{ Math.abs(top3[2].return_rate ?? 0).toFixed(2) }}%
        </div>
      </div>
    </div>

    <!-- 🧾 4등 이하 리스트 -->
    <ul class="ranking-list">
      <li v-for="(user, idx) in others" :key="user.username">
        <span class="rank-num">{{ idx + 4 }}</span>
        <img :src="user.profile_image || defaultImg" class="mini-profile" alt="프로필" />
        <RouterLink
          :to="{ name: 'user-profile', params: { nickname: user.nickname } }"
          class="nickname-link"
        >
          {{ user.nickname || user.username }}
        </RouterLink>
        <span class="amount" :style="{ color: (user.return_rate ?? 0) >= 0 ? 'red' : 'blue' }">
          {{ (user.return_rate ?? 0) >= 0 ? '🔺' : '🔻' }}
          {{ Math.abs(user.return_rate ?? 0).toFixed(2) }}%
        </span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from '@/stores/axios.js'
import { RouterLink } from 'vue-router'
const ranking = ref([])
const defaultImg = '/default-profile.png'

const fetchRanking = async () => {
  try {
    const res = await axios.get('/api/trade/ranking/')
    ranking.value = res.data
    console.log('프로필:', top3.value[0].profile_image)
  } catch (err) {
    console.error('❌ 랭킹 불러오기 실패:', err)
  }
}

onMounted(() => {
  fetchRanking()
})

const top3 = computed(() => ranking.value.slice(0, 3))
const others = computed(() => ranking.value.slice(3))
</script>

<style scoped>
.ranking-board {
  padding: 2rem;
  font-family: 'Pretendard', sans-serif;
  text-align: center;
}

.ranking-title {
  font-size: 1.6rem;
  margin-bottom: 4rem;
  font-weight: 700;
}

.top-3-wrap {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 2rem;
  position: relative;
  align-items: flex-start;
}

.top-card {
  width: 110px;
  padding: 14px;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  position: relative;
}

.rank-1 {
  order: 2;
  background-color: #fff5d7;
  margin-top: 0px;
  transform: scale(1.3);
  z-index: 1;
  animation: crownBounce1 2.4s infinite ease-in-out;
}

.rank-2 {
  order: 1;
  background-color: #f0f2f5;
  margin-top: 40px;
  animation: crownBounce 2.4s infinite ease-in-out;
}

.rank-3 {
  order: 3;
  background-color: #fdecef;
  margin-top: 40px;
  animation: crownBounce 2.4s infinite ease-in-out;
}

@keyframes crownBounce {
  0%, 100% { transform: scale(1.2) translateY(0); }
  50% { transform: scale(1.25) translateY(-5px); }
}
@keyframes crownBounce1 {
  0%, 100% { transform: scale(1.3) translateY(0); }
  50% { transform: scale(1.35) translateY(-5px); }
}



@keyframes pop {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(-3px); }
}

@keyframes floatUp {
  0% {
    transform: translateY(0);
    opacity: 0;
  }
  50% {
    transform: translateY(-10px);
    opacity: 1;
  }
  100% {
    transform: translateY(-20px);
    opacity: 0;
  }
}
.rank-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: gold;
  color: #000;
  padding: 2px 8px;
  font-size: 0.75rem;
  border-radius: 12px;
  font-weight: bold;
}

.top-profile {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  margin-bottom: 6px;
}

.top-nickname {
  font-weight: bold;
  font-size: 1rem;
}

.top-profit {
  font-size: 0.9rem;
}

.ranking-list {
  list-style: none;
  padding: 0;
  margin: 0 auto;
  max-width: 500px;
}

.ranking-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 8px 12px;
  border-bottom: 1px solid #eee;
  font-size: 0.9rem;
}

.rank-num,
.mini-profile,
.nickname {
  flex-shrink: 0;
}

.mini-profile {
  width: 28px;
  height: 28px;
  border-radius: 50%;
}

.nickname {
  flex: 1;
  text-align: left;
}

.amount {
  text-align: right;
  font-weight: 600;
}

.nickname-link {
  flex: 1;
  text-align: left;
  color: #333;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s ease;
}

.nickname-link:hover {
  color: #007bff;
  text-decoration: underline;
}

.top-nickname-link {
  display: block;
  font-weight: bold;
  font-size: 1rem;
  color: #333;
  text-decoration: none;
  text-align: center; /* ⭐ 중앙 정렬 */
  margin-top: 6px;
}

.top-nickname-link:hover {
  color: #007bff;
  text-decoration: underline;
}
</style>
