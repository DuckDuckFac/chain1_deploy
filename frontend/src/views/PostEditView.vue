<template>
  <div class="edit-container">
    <div class="edit-card">
      <button @click="goBack" class="back-button">← 뒤로가기</button>
      <h2 class="title">✏️ 게시글 수정</h2>
      <form @submit.prevent="updatePost" class="edit-form">
        <input
          v-model="title"
          type="text"
          placeholder="제목을 입력하세요 (10자 이내)"
          maxlength="10"
          required
        />
        <textarea
          v-model="content"
          placeholder="내용을 입력하세요"
          required
        ></textarea>
        <button type="submit" class="submit-btn">수정 완료</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/stores/axios'

const route = useRoute()
const router = useRouter()

const postId = route.params.id
const title = ref('')
const content = ref('')

const goBack = () => {
  router.back()
}

const fetchPost = async () => {
  try {
    const res = await axios.get(`/communities/${postId}/`)
    title.value = res.data.title
    content.value = res.data.content
  } catch (err) {
    console.error('게시글 불러오기 실패:', err)
  }
}

const updatePost = async () => {
  if (!title.value.trim() || !content.value.trim()) {
    alert('제목과 내용을 모두 입력해주세요.')
    return
  }
  if (title.value.trim().length > 10) {
    alert('제목은 10자 이하로 입력해주세요!')
    return
  }
  try {
    await axios.patch(`/communities/${postId}/`, {
      title: title.value,
      content: content.value,
    })
    alert('게시글이 수정되었습니다.')
    router.replace({ name: 'post-detail', params: { id: postId } })
  } catch (err) {
    console.error('게시글 수정 실패:', err)
    alert(`수정 실패! ${JSON.stringify(err.response?.data || '다시 시도해주세요.')}`)
  }
}

onMounted(fetchPost)
</script>

<style scoped>
.edit-container {
  max-width: 700px;
  margin: 2rem auto;
  padding: 1rem;
}

.edit-card {
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
  margin-bottom: 1.5rem;
  font-size: 1.3rem;
  color: #333;
}

.edit-form input,
.edit-form textarea {
  width: 100%;
  padding: 12px;
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 0.95rem;
  box-sizing: border-box;
}

.edit-form textarea {
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
