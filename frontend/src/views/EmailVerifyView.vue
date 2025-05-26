<template>
  <div class="verify-email">
    <h2>📧 이메일 인증 중...</h2>
    <p v-if="loading">잠시만 기다려주세요.</p>
    <p v-else-if="success">✅ 이메일 인증이 완료되었습니다!</p>
    <p v-else>❌ 유효하지 않거나 만료된 링크입니다.</p>

    <div v-if="success" class="button-group">
      <RouterLink to="/" class="action-btn">🏠 홈으로 가기</RouterLink>
      <RouterLink :to="{ name: 'profile-interestedit', params: { nickname: userStore.userInfo?.nickname } }" class="action-btn">
        ✍️ 나의 관심분야 작성하기
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import axios from '@/stores/axios'

const route = useRoute()
const loading = ref(true)
const success = ref(false)
const userStore = useUserStore()

onMounted(async () => {
  const code = route.params.code
  try {
    const res = await axios.get(`/accounts/verify-email/${code}/`)
    success.value = res.status === 200
  } catch (err) {
    success.value = false
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.verify-email {
  max-width: 400px;
  margin: 100px auto;
  text-align: center;
}

.button-group {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-btn {
  display: inline-block;
  padding: 12px;
  background-color: #007bff;
  color: white;
  font-weight: 600;
  border-radius: 8px;
  text-decoration: none;
  transition: background-color 0.2s ease;
}

.action-btn:hover {
  background-color: #0056b3;
}
</style>
