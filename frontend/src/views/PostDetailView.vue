<template>
  <div class="post-detail">
    <!-- ✅ 뒤로가기 버튼 -->
    <router-link :to="{ name: 'community' }" class="back-button">전체 게시글로</router-link>

    <h2>{{ post.title }}</h2>
    <div class="post-header">
      <img :src="getProfileImage(post.user?.profile_image)" alt="프사" class="mini-profile-image" />
      <strong class="author-nickname">
      <strong>[Lv.{{ post.user?.level || 0 }}]
        
      </strong>
      {{ post.user?.nickname }}
            <img
        :src="getLevelImage(post.user?.level)"
        alt="레벨 아이콘"
        class="level-icon-1"
      />
    </strong>
    </div>

    <p>{{ post.content }}</p>

    <!-- 수정 및 삭제 버튼 -->
    <div class="post-actions" v-if="userInfo?.username === post.user">
      <button @click="goToEdit(post.id)"><PencilIcon class="icon" /> 수정</button>
      <button @click="deletePost(post.id)">🗑️ 삭제</button>
    </div>

    <div class="meta">
      <span class="meta-group">
        <button @click="toggleBookmark(post.id)" v-if="isLogin">
          <Bookmark :class="['bookmark-icon', { bookmarked: isBookmarked(post) }]" />
        </button>
        <span>{{ post.like_users_count }}개</span>
      </span>
      <span class="meta-group">
        <MessageSquare class="meta-icon" />
        <span>{{ totalCommentCount  }}개</span>
      </span>
      <span class="meta-group">
        <span class="created-at">{{ formatTime(post.created_at) }}</span>
      </span>
    </div>

    <!-- 댓글 작성 -->
    <div class="comment-input-row">
      <textarea
        v-model="newCommentContent"
        @keydown.enter.exact.prevent="submitComment"
        placeholder="댓글을 입력하세요..."
        class="comment-input"
      ></textarea>
      <button class="comment-submit-btn" @click="submitComment">작성</button>
    </div>

    <!-- 댓글 목록 -->
    <div class="comments">
      <div v-for="comment in comments" :key="comment.id" class="comment-box">
        <div class="comment-header">
          <div class="comment-user-info">
            <img :src="getProfileImage(comment.user?.profile_image)" alt="프사" class="mini-profile-image" />
            <strong class="author-nickname">
            <strong>[Lv.{{ comment.user.level }}]</strong>
            {{ comment.user.nickname }}
            <img
              :src="getLevelImage(comment.user.level)"
              alt="레벨 아이콘"
              class="level-icon"
            />
          </strong>
            <small class="comment-time">{{ formatTime(comment.created_at) }}</small>
          </div>

          <div
            v-if="comment.user && userInfo && comment.user.username === userInfo.username"
            class="comment-actions"
          >
            <button @click="editComment(comment)">
              <Pencil class="icon" /> 수정
            </button>
            <button @click="deleteComment(comment.id)">
              <Trash2 class="icon" /> 삭제
            </button>
          </div>
        </div>


        <div v-if="editingComment?.id === comment.id" class="comment-edit-row">
          <input v-model="editingContent" class="comment-edit-input" />
          <button class="save-btn" @click="updateComment(comment.id)">저장</button>
          <button class="cancel-btn" @click="cancelEdit">취소</button>
        </div>
        <div v-else>
          <p>
            {{ comment.content }}
            <span v-if="isEdited(comment)" class="edited-text"></span>
          </p>
        </div>

      </div>
      <button v-if="nextPageUrl" @click="fetchComments(nextPageUrl)" class="load-more-btn">⬇️ 댓글 더 보기</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/stores/axios'
import { useUserStore } from '@/stores/user'
import { PencilIcon } from '@heroicons/vue/24/solid'
import { Bookmark, MessageSquare,Pencil, Trash2 } from 'lucide-vue-next'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/ko'
dayjs.extend(relativeTime)
dayjs.locale('ko')

const route = useRoute()
const router = useRouter()
const { userInfo, isLogin } = useUserStore()

const post = ref({})
const comments = ref([])
const newCommentContent = ref('')
const editingComment = ref(null)
const editingContent = ref('')
const postId = route.params.id
const nextPageUrl = ref(null)
const totalCommentCount = ref(0)


const getLevelImage = (level) => {
  if (level >= 100) return '/level/100.png'
  if (level >= 80) return '/level/80.png'
  if (level >= 60) return '/level/60.png'
  if (level >= 40) return '/level/40.png'
  if (level >= 20) return '/level/20.png'
  return '/level/1.png'
}



const fetchPost = async () => {
  const res = await axios.get(`/communities/${postId}/`)
  post.value = res.data
  comments.value = res.data.comments
}

// ✅ 기본 URL을 인자로 받도록 수정
const fetchComments = async (url = `/communities/${postId}/comments/`, reset = false) => {
  const res = await axios.get(url)
  if (reset) {
    comments.value = res.data.results  // ✨ 초기화할 때만 덮어씀
  } else {
    comments.value.push(...res.data.results)  // ✨ 추가
  }
  nextPageUrl.value = res.data.next
  totalCommentCount.value = res.data.count 
}

const submitComment = async () => {
  if (!newCommentContent.value.trim()) return
  await axios.post(`/communities/${postId}/comments/`, {
    content: newCommentContent.value,
  })
  newCommentContent.value = ''
  await fetchComments(undefined, true)  // ✅ 전체 다시 불러오기
}



const editComment = (comment) => {
  editingComment.value = comment
  editingContent.value = comment.content
}

const updateComment = async (commentId) => {
  const res = await axios.put(`/communities/${postId}/comments/${commentId}/`, { content: editingContent.value })
  const index = comments.value.findIndex(c => c.id === commentId)
  if (index !== -1) comments.value[index] = res.data
  cancelEdit()
}

const cancelEdit = () => {
  editingComment.value = null
  editingContent.value = ''
}

const deleteComment = async (commentId) => {
  await axios.delete(`/communities/${postId}/comments/${commentId}/`)
  await fetchComments(undefined, true)
}

const toggleBookmark = async (postId) => {
  await axios.post(`/communities/${postId}/like/`)
  await fetchPost()
}

const isBookmarked = (post) => {
  console.log(userInfo.value)
  return post.like_users?.includes(userInfo?.id)
}

const deletePost = async (postId) => {
  if (!confirm("정말 삭제하시겠습니까?")) return
  try {
    await axios.delete(`/communities/${postId}/`)
    alert("게시글이 삭제되었습니다.")
    router.push({ name: 'community' })
  } catch (err) {
    alert("삭제 중 오류가 발생했습니다.")
  }
}

const goToEdit = (postId) => {
  router.push({ name: 'post-edit', params: { id: postId } })
}

const formatTime = (timestamp) => {
  const now = dayjs()
  const time = dayjs(timestamp)
  const diff = now.diff(time, 'minute')
  if (diff < 1) return '방금 전'
  if (diff < 60) return `${diff}분 전`
  if (now.isSame(time, 'day')) return `${time.hour()}시 ${time.minute()}분`
  return time.format('YYYY.MM.DD')
}

const isEdited = (comment) => {
  return comment.created_at !== comment.updated_at
}

const getProfileImage = (path) => {
  if (!path || path === 'null' || path === 'undefined') return '/default-profile.png'
  return path.startsWith('http') ? path : `http://127.0.0.1:8000${path}`
}

onMounted(() => {
  fetchPost()
  fetchComments(undefined, true)
})

</script>

<style scoped>
body {
  background-color: #f8f9fa;
}
.post-detail {
  padding: 2rem;
  max-width: 960px;
  margin: 0 auto;
  background-color: 0 2px 12px rgba(0, 0, 0, 0.04);
  min-height: 100vh;
}
.back-button {
  display: inline-block;
  margin-bottom: 1rem;
  font-size: 0.95rem;
  color: #007bff;
  text-decoration: none;
}
.back-button:hover {
  text-decoration: underline;
}
.post-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 1rem 0;
}
.mini-profile-image {
  width: 30px;
  height: 30px;
  object-fit: cover;
  border-radius: 50%;
  border: 1px solid #ccc;
}
.author-nickname {
  font-size: 0.95rem;
  font-weight: 500;
  color: #333;
}
.created-at {
  font-size: 0.8rem;
  color: #999;
  margin-left: 6px;
}
.post-actions {
  margin: 1rem 0;
  display: flex;
  gap: 0.5rem;
}
.post-actions button {
  background: transparent;
  border: none;
  color: #888;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}
.post-actions .icon {
  width: 16px;
  height: 16px;
}
.meta {
  font-size: 0.85rem;
  color: #999;
  margin-top: 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}
.meta-group {
  display: flex;
  align-items: center;
  gap: 4px;
}
.meta-icon {
  width: 18px;
  height: 18px;
  stroke: #999;
}
.meta button {
  background-color: transparent !important;
  border: none !important;
  box-shadow: none;
  padding: 0;
  margin: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.bookmark-icon {
  width: 18px;
  height: 18px;
  stroke: #999;
  fill: none;
  transition: stroke 0.2s ease, fill 0.2s ease;
}
.bookmark-icon.bookmarked {
  stroke: #007bff;
  fill: #007bff;
}
.comment-input-row {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  margin: 1rem 0;
}
.comment-input {
  flex: 1;
  height: 80px;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 0.9rem;
  resize: none;
  box-sizing: border-box;
}
.comment-submit-btn {
  height: 80px;
  padding: 0 18px;
  background-color: #007bff;
  color: white;
  font-weight: bold;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.comment-submit-btn:hover {
  background-color: #0056b3;
}
.comments {
  margin-top: 2rem;
  border-top: 1px solid #ccc;
  padding-top: 1rem;
}
.comment-box {
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}
.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.comment-user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.comment-actions {
  display: flex;
  gap: 6px;
}

.comment-actions .icon {
  width: 15px;
  height: 15px;
  margin-right: 4px;
  color: #666;
}

.comment-actions button {
  background-color: transparent;
  border: none;
  color: #666;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 6px;
  transition: color 0.2s ease;
}
.comment-actions button:hover {
  color: #333;
}
.comment-edit-row {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-top: 6px;
}

.comment-edit-input {
  flex: 1;
  padding: 8px 12px;
  font-size: 0.9rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  outline: none;
  transition: border-color 0.2s ease;
}

.comment-edit-input:focus {
  border-color: #007bff;
}
.comment-time {
  color: #999;
  font-size: 0.8rem;
  margin-left: 6px;
}


.save-btn,
.cancel-btn {
  background-color: transparent;
  border: none;
  font-size: 0.85rem;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: color 0.2s ease;
}

.save-btn {
  color: #007bff;
  font-weight: 600;
}

.cancel-btn {
  color: #666;
}

.save-btn:hover {
  color: #0056b3;
}

.cancel-btn:hover {
  color: #333;
}

.edited-text {
  font-size: 0.85rem;
  color: #999;
  margin-left: 4px;
}
.level-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
  margin-bottom: 4px;
  vertical-align: middle;
}
.level-icon-1 {
  width: 28px;
  height: 28px;
  object-fit: contain;
  margin-bottom: 4px;
  vertical-align: middle;
}
.load-more-btn {
  margin: 1rem auto 0;
  display: block;
  padding: 10px 20px;
  font-size: 0.95rem;
  font-weight: 600;
  background-color: #f2f4f8;
  color: #007bff;
  border: 1px solid #007bff;
  border-radius: 30px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  box-shadow: 0 2px 6px rgba(0, 123, 255, 0.1);
}

.load-more-btn:hover {
  background-color: #e0f0ff;
  transform: translateY(-2px);
}
</style>
