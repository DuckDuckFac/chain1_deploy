<template>
<header :class="['navbar', { 'navbar-overlay': isMainPage, 'scrolled': isScrolled }]">
    <!-- 로고 영역 -->
    <div class="navbar-left" @click="goHome">
      <!-- 조건에 따라 영상 또는 이미지만 보이도록 설정 -->
      <video
        src="/Logo1.mp4"
        autoplay
        muted
        playsinline
        loop
        class="logo-video"
      ></video>

    </div>
  <!-- 가운데: 메뉴 -->
  <nav class="navbar-center">
    <RouterLink to="/finlife" class="nav-link" active-class="active">금리비교</RouterLink>
    <RouterLink to="/community" class="nav-link" active-class="active">커뮤니티</RouterLink>
    <RouterLink to="/stock" class="nav-link" active-class="active">종목목록</RouterLink>
    <RouterLink to="/findbank" class="nav-link" active-class="active">은행찾기</RouterLink>
    <RouterLink
      v-if="userStore.isLogin && userNickname"
      :to="{ name: 'user-profile', params: { nickname: userNickname } }"
      class="nav-link"
      active-class="active"
      exact-active-class="active"
    >
      MY
    </RouterLink>

  </nav>
  
  <!-- 오른쪽: 검색 + 로그인/회원가입 -->
  <div class="navbar-right">
    <!-- 알림 벨 버튼 -->
  <div class="notif-container">
    <button class="notif-btn" @click="openNotificationModal">
      <!-- ✅ 조건에 따라 이미지 바뀜 -->
      <img
        :src="notificationStore.unreadCount > 0 ? '/NestInEgg.png' : '/EmptyNest.png'"
        alt="알림"
        class="notif-icon"
      />
      <span v-if="notificationStore.unreadCount > 0" class="notif-count">
        {{ notificationStore.unreadCount > 9 ? '9+' : notificationStore.unreadCount }}
      </span>
    </button>
    <NotificationModal />
  </div>
    <StockSearch />
    <div v-if="userStore.isLogin" class="auth">
      <button @click="logout" class="auth-btn">로그아웃</button>
    </div>
    <div v-else class="auth">
      <RouterLink to="/login" class="auth-btn">로그인</RouterLink>
    </div>
  </div>
</header>



</template>

<script setup>
import { ref, computed,onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { useNotificationStore, justOpened } from '@/stores/notification'
import StockSearch from './StockSearch.vue'
import NotificationModal from './NotificationModal.vue'
const userStore = useUserStore()
const router = useRouter()
const notificationStore = useNotificationStore()
const logoVideoPath = '/Logo1.mp4'
const userNickname = computed(() => userStore.userInfo?.nickname)
const goHome = () => router.push('/')
const logout = () => {
  if (confirm('정말 로그아웃 하시겠습니까?')) {
    userStore.logoutUser()
    router.push({ name: 'main' })
  }
}

// 클릭 이벤트
const openNotificationModal = () => {
  console.log('🔔 알림 버튼 클릭됨')
  notificationStore.openModal()
  notificationStore.markAllRead()
  justOpened.value = true
  setTimeout(() => {
    justOpened.value = false
  }, 100)
}

defineProps({
  isMainPage: Boolean
})


const isScrolled = ref(false)

const handleScroll = () => {
  isScrolled.value = window.scrollY > 0
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  background-color: rgba(255, 255, 255, 0);

  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 40px;
  font-family: 'Pretendard', sans-serif;
}
.navbar.scrolled {
  background-color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(8px); /* 선택사항 */
}
.navbar-left {
  font-size: 1.6rem;
  font-weight: 900;
  cursor: pointer;
}

.navbar-center {
  flex: 1;
  display: flex;
  justify-content: center;
  gap: 32px;
}

.nav-link {
  color: #9a9a9a;
  font-weight: 600;
  text-decoration: none;
}
.nav-link.active {
  color: #000;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-left: auto;
}

.auth-btn {
  color: #888;
  font-weight: 500;
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
}

.stock-search {
  background-color: #f4f6f8;
  border-radius: 30px;
  padding: 6px 14px;
  display: flex;
  align-items: center;
}
.notif-container {
  position: relative;
  display: inline-block;
}
.notif-btn {
  position: relative;
  font-size: 20px;
  background: none;
  border: none;
  cursor: pointer;
  margin-right: 16px;
}

.notif-count {
  position: absolute;
  top: -4px;
  right: -8px;
  background-color: red;
  color: white;
  border-radius: 50%;
  padding: 2px 6px;
  font-size: 12px;
  font-weight: bold;
  line-height: 1;
}
.notif-icon {
  width: 50px;
  height: 50px;
  object-fit: contain;
}
.logo-gif {
  height: 60px;
  object-fit: contain;
  cursor: pointer;
}
.logo-video, .logo-image {
  height: 60px;
  object-fit: contain;
  cursor: pointer;
  pointer-events: none;
}
</style>