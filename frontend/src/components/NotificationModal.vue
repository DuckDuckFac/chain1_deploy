<!-- src/components/NotificationModal.vue -->
<template>
  <div v-if="notificationStore.showModal" class="modal-overlay" @click.self="notificationStore.closeModal">
    <div class="modal-content" ref="modalRef">
      <div class="modal-header">
        <h3>📢 알림</h3>
        <button class="close-btn" @click="notificationStore.closeModal">✖</button>
      </div>

      <div v-if="notificationStore.notifications.length === 0" class="empty">알림이 없습니다.</div>
      <ul v-else class="notif-list">
        <li
          v-for="(notif, index) in notificationStore.notifications"
          :key="index"
          class="notif-item"
        >
          <span class="message" @click="goTo(notif, index)">
            {{ notif.message }}
          </span>
          <button class="x-btn" @click="notificationStore.removeNotification(index)">x</button>
        </li>
      </ul>
    </div>
  </div>
 
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useNotificationStore, justOpened } from '@/stores/notification'
import { useRouter } from 'vue-router'

const notificationStore = useNotificationStore()
const router = useRouter()

const modalRef = ref(null)


const goTo = (notif, index) => {
  if (notif.route) {
    router.push(notif.route)
    notificationStore.removeNotification(index)
    notificationStore.closeModal()
  }
}

const handleClickOutside = (event) => {
  if (justOpened.value) return  // 클릭 직후 무시
  if (notificationStore.showModal && modalRef.value && !modalRef.value.contains(event.target)) {
    notificationStore.closeModal()
  }
}
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

</script>

<style scoped>
.modal-overlay {
  position: absolute; /* 기존 fixed → absolute */
  top: 28px;           /* 종 아이콘 아래에 붙게 조정 */
  right: 0;
  background-color: white;
  border: 1px solid #ddd;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 260px;
  z-index: 9999;
  border-radius: 8px;

}

.modal-content {
  padding: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
}

.empty {
  text-align: center;
  padding: 1rem;
  color: #999;
}

.notif-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.notif-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #eee;
}

.message {
  flex-grow: 1;
  cursor: pointer;
  font-size: 14px;
}

.x-btn {
  background: none;
  border: none;
  font-size: 12px;
  color: #999;
  cursor: pointer;
}
</style>
