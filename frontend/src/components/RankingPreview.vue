<template>
  <div class="ranking-preview-card">
    <div class="ranking-header">
      <h3 class="ranking-title">🏆 투자 랭킹</h3>
      <button class="ranking-more-btn" @click="$router.push({ name: 'ranking' })">더보기</button>
    </div>
    <ul class="ranking-list">
      <li v-for="(user, idx) in topRanking" :key="user.username" class="ranking-item">
        <span class="rank-number">{{ idx + 1 }}위</span>
        <span class="rank-nickname">{{ user.nickname || user.username }}</span>
        <span
          class="rank-rate"
          :class="{
            positive: user.return_rate > 0,
            negative: user.return_rate < 0,
            zero: user.return_rate === 0
          }"
        >
  {{ user.return_rate.toFixed(2) }}%
</span>
      </li>
    </ul>
  </div>
</template>


<script setup>
import { ref, onMounted } from 'vue'
import axios from '@/stores/axios'

const topRanking = ref([])

onMounted(async () => {
  try {
    const res = await axios.get('/api/trade/ranking/')
    topRanking.value = res.data.slice(0, 10)
  } catch (err) {
    console.error('❌ 랭킹 불러오기 실패:', err)
  }
})
</script>

<style scoped>
.ranking-preview-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  max-width: 340px;
  margin: 0 auto;
  font-family: 'Pretendard', sans-serif;
  border: 1px solid #e6ecf1;
}

.ranking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.ranking-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #222;
  margin: 0;
  margin-left: 18px;
}

.ranking-more-btn {
  background: none;
  border: none;
  color: #bbb;
  font-size: 0.85rem;
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 2px 6px;
}

.ranking-more-btn:hover {
  color: #007bff;
  text-decoration: underline;
}

.ranking-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.ranking-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 0.95rem;
  color: #333;
  border-bottom: 1px solid #f1f1f1;
}

.rank-number {
  font-weight: 600;
  color: #007bff;
  width: 32px;
  text-align: left;
}

.rank-nickname {
  flex: 1;
  text-align: left;
  padding-left: 4px;
  color: #222;
  font-weight: 500;
}

.rank-rate {
  width: 64px;
  text-align: right;
  font-weight: 500;
}

/* ✅ 수익률에 따른 색상 클래스 */
.positive {
  color: rgb(255, 63, 63);
}
.negative {
  color: #5eacff;
}
.zero {
  color: #808080;
}
</style>
