<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const access = route.query.access
const refresh = route.query.refresh

if (access && refresh) {
  userStore.loginWithGoogle(access, refresh, () => {
    router.push({ name: 'main' }) // 로그인 성공 후 이동
  })
}

</script>

<template>
  <div>구글 로그인 처리 중입니다...</div>
</template>
