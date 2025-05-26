<template>
  <div class="create-container">
    <div class="create-card">
      <!-- 🔙 뒤로가기 버튼 -->
      <button @click="goBack" class="back-button">〈 뒤로가기</button>

      <h2 class="title">📝 게시글 작성</h2>
      <form @submit.prevent="submitPost" class="create-form">
        <label for="title">제목</label>
        <input
          v-model="title"
          id="title"
          placeholder="제목을 입력하세요 (10자 이내)"
          maxlength="10"
          required
        />

        <label for="content">내용</label>
        <textarea
          v-model="content"
          id="content"
          placeholder="내용을 입력하세요"
          required
        ></textarea>

        <button type="submit" class="submit-btn">작성 완료</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const title = ref('')
const content = ref('')
const router = useRouter()
const userStore = useUserStore()
const isLogin = computed(() => userStore.isLogin)

const goBack = () => {
  router.back()
}

const submitPost = async () => {
  if (!isLogin.value) {
    alert('로그인이 필요합니다')
    return
  }

  if (!title.value.trim()) {
    alert('제목을 입력해주세요 (공백만 입력할 수 없습니다)')
    return
  }

  try {
    await axios.post('http://127.0.0.1:8000/communities/', {
      title: title.value,
      content: content.value,
    })
    router.push({ name: 'community' })
  } catch (err) {
    console.error('작성 실패:', err.response?.data || err.message)
    alert('작성 실패 😢')
  }
}
</script>

<style scoped>
.create-container {
  max-width: 700px;
  margin: 2rem auto;
  padding: 1rem;
}

.create-card {
  background-color: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.08);
}

.back-button {
  background: none;
  border: none;
  color: #007bff;
  font-size: 0.95rem;
  margin-bottom: 1rem;
  cursor: pointer;
}
.back-button:hover {
  text-decoration: underline;
}

.title {
  font-size: 1.4rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 1.5rem;
}

.create-form label {
  font-weight: 600;
  margin-bottom: 0.4rem;
  display: block;
  font-size: 0.95rem;
  color: #444;
}

.create-form input,
.create-form textarea {
  width: 100%;
  padding: 12px;
  margin-bottom: 1.2rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 0.95rem;
  box-sizing: border-box;
}

.create-form textarea {
  height: 180px;
  resize: vertical;
}

.submit-btn {
  display: block;
  width: 100%;
  padding: 12px;
  font-size: 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.submit-btn:hover {
  background-color: #0056b3;
}
</style>
