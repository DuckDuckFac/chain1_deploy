<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { onMounted } from 'vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

onMounted(async () => {
  const access = route.query.access
  const refresh = route.query.refresh

  if (!access || !refresh) {
    alert('카카오 로그인 실패: 토큰 없음')
    router.push('/login')
    return
  }

  await userStore.loginWithKakao(access, refresh, () => router.push('/'))
})
</script>

<template>
  <div>카카오 로그인 처리 중입니다...</div>
</template>
