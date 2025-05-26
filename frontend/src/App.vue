<!-- src/App.vue -->
<template>
  <div id="app">
  <NavBar :isMainPage="isMainPage" />
  <div :class="['page-content', { 'with-padding': !isMainPage }]">
    <RouterView />
  </div>
  
    <button class="scroll-top-btn" @click="scrollToTop">
      <chevron-up class="icon" />
    </button>
    <Chatbot />
    
  </div>
  <Footer />
</template>

<script setup>
import { watch, onMounted, onUnmounted, computed, watchEffect } from 'vue'
import NavBar from '@/components/NavBar.vue'
import Chatbot from '@/components/Chatbot.vue'
import Footer from '@/components/Footer.vue'
import { ChevronUp } from 'lucide-vue-next'
import {
  registerTradeHandler,
  registerPostLikeHandler,
  registerPostCommentHandler
} from '@/stores/socket'
import NotificationModal from '@/components/NotificationModal.vue'
import { useStockChartStore } from '@/stores/stockchart.js'
import { useUserStore } from '@/stores/user'
import { useAccountStore } from '@/stores/account'
import { useNotificationStore } from '@/stores/notification'


const store = useStockChartStore()
const userStore = useUserStore()
const accountStore = useAccountStore()
const notificationStore = useNotificationStore()
const isLogin = computed(() => userStore.isLogin)

const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' })

import { useRoute } from 'vue-router'
const route = useRoute()
const isMainPage = computed(() => route.path === '/')


onMounted(async () => {
  await userStore.getProfile()
  Notification.requestPermission().then(permission => {
    console.log('🔔 브라우저 알림 권한:', permission)
  })
  store.stockCodes.forEach(code => {
    store.startOHLCFor(code, '1m')  // 또는 여러 주기를 반복해서 시작 가능
  })
  if (!isLogin.value) return
  await notificationStore.fetchNotificationsFromServer()
  const uid = userStore.userInfo?.id
  if (!uid) return

  console.log('✅ 알림 핸들러 등록 시작 uid:', uid)

  registerTradeHandler((data) => {
    console.log('📥 소켓 체결 알림 수신:', data)
    notificationStore.addNotification({
      message: `${data.name} ${data.quantity}주 ${data.price}원에 ${data.trade_type === 'BUY' ? '매수' : '매도'} 체결`,
      route: { name: 'stock-detail', params: { code: data.code } },
      timestamp: new Date().toISOString(),
      user_id: data.user_id,
      code: data.code,
    })
  })

  registerPostLikeHandler((data) => {
    if (String(data.target_user_id) === String(uid)) {
      notificationStore.addNotification({
        message: `💗 '${data.post_title}'에 좋아요가 눌렸습니다.`,
        route: { name: 'post-detail', params: { id: data.post_id } },
        timestamp: new Date().toISOString(),
      })
    }
  })

  registerPostCommentHandler((data) => {
    console.log('💬 댓글 알림 수신:', data)
    if (String(data.target_user_id) === String(uid)) {
      notificationStore.addNotification({
        message: `💬 '${data.post_title}'에 댓글이 달렸습니다.`,
        route: { name: 'post-detail', params: { id: data.post_id } },
        timestamp: new Date().toISOString(),
      })
    }
  })
})

watchEffect(() => {
  while (notificationStore.tradeExecutedQueue.length > 0) {
    const next = notificationStore.tradeExecutedQueue.shift()
    console.log('📦 큐에서 꺼낸 알림:', next)
    notificationStore.notifications.unshift(next)

    if (Notification.permission === 'granted') {
      let icon = '/favicon.ico'
      if (next.message.includes('매수') || next.message.includes('매도')) icon = '/icons/trade.png'
      else if (next.message.includes('좋아요')) icon = '/icons/like.png'
      else if (next.message.includes('댓글')) icon = '/icons/comment.png'

      console.log('🔔 브라우저 알림 발생:', next.message)
      new Notification('💰 GooseBank 알림', {
        body: next.message,
        icon,
      })
    }
  }
})

</script>


<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
body {
  font-family: 'Noto Sans KR', sans-serif;
}
.page-content.with-padding {
  padding-top: 100px; /* 실제 NavBar 높이에 맞게 조정! (60~100px 정도 보통) */
}
.chatbot-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background-color: #ffe680;
  border: none;
  border-radius: 50%;
  padding: 14px;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  cursor: pointer;
  transition: all 0.3s;
}
.chatbot-btn:hover {
  transform: scale(1.1);
}

/* ⬆️ 스크롤 맨 위로 버튼 */
.scroll-top-btn {
  position: fixed;
  bottom: 90px; /* 챗봇 버튼 위에 뜨도록 */
  right: 20px;
  z-index: 9999;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: white;
  color: white;
  font-size: 24px;
  border: none;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s ease;
}
.icon {
  width: 28px;
  height: 28px;
  stroke: #007bff;
}

.scroll-top-btn:hover {
  transform: scale(1.1);
}
</style>
