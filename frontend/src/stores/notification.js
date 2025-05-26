import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/stores/axios'

export const justOpened = ref(false)

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])
  const showModal = ref(false)
  const tradeExecutedQueue = ref([])

  const openModal = () => showModal.value = true
  const closeModal = () => showModal.value = false

  const addNotification = (data) => {
  console.log('🧪 큐에 들어가는 알림:', data)
  
  tradeExecutedQueue.value = [...tradeExecutedQueue.value, data]
}
  const removeNotification = async (index) => {
    const notif = notifications.value[index]
    notifications.value.splice(index, 1)

    try {
      if (notif.id) {
        await axios.delete(`/accounts/notifications/${notif.id}/`)
        console.log('🗑️ 서버 알림 삭제됨', notif.id)
      }
    } catch (err) {
      console.error('❌ 알림 삭제 실패', err)
    }
  }

  const unreadCount = computed(() =>
    notifications.value.filter(n => !n.read).length
  )

  const markAllRead = async () => {
    const unreadIds = notifications.value
      .filter(n => !n.read && n.id)
      .map(n => n.id)

    notifications.value.forEach(n => (n.read = true))

    try {
      if (unreadIds.length > 0) {
        await axios.patch('/accounts/notifications/mark-read/', { ids: unreadIds })
        console.log('✅ 읽음 처리됨', unreadIds)
      }
    } catch (err) {
      console.error('❌ 읽음 처리 실패', err)
    }
  }

  const fetchNotificationsFromServer = async () => {
    try {
      const res = await axios.get('/accounts/notifications/')
      notifications.value = res.data.map(n => ({ ...n, read: false }))
    } catch (err) {
      console.error('🔴 알림 불러오기 실패', err)
    }
  }

  return {
    notifications,
    unreadCount,
    showModal,
    tradeExecutedQueue,
    addNotification,
    markAllRead,
    openModal,
    closeModal,
    removeNotification,
    fetchNotificationsFromServer,
  }
}, {
  persist: true
})