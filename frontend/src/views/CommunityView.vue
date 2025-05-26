<template>
  <div class="community-container">
    <aside class="profile-sidebar">
      <template v-if="isLogin">
        <div class="center-align-box">
          <img
            :src="getProfileImage(userProfile?.image)"
            alt="프로필 이미지"
            class="profile-img"
          />
          <div class="user-level-info">
          
          <strong class="nickname">
            [Lv.{{ userProfile?.community_level || 0 }}] {{ userProfile?.user?.nickname }}님 <img :src="levelImage" alt="레벨 이미지" class="level-badge" /> 
          </strong>
        </div>
          <div class="profile-actions">
            <span class="profile-count" @click="showMyPosts">작성한 글 <strong>{{ userProfile?.my_post_count }}</strong></span> |
            <span class="profile-count" @click="showBookmarkedPosts">북마크 <strong>{{ userProfile?.my_bookmark_count }}</strong></span>
          </div>
        </div>

        <button class="write-btn" @click="goToCreate"><PencilIcon class="icon" /> 게시글 작성</button>
      </template>
      <template v-else>
        <p>로그인이 필요한 기능입니다</p>
        <button @click="goToLogin" class="login-button">로그인하러 가기</button>
      </template>
    </aside>



    <!-- 🟩 오른쪽: 게시글 목록 -->
    <section class="post-list">

      <div class="post-title-box">
        <div class="search-bar">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="제목 또는 내용을 검색하세요"
            class="search-input"
          />
          <button class="search-button">검색</button>
            <div class="custom-select-wrapper">
              <select v-model="sortOption" class="sort-dropdown">
                <option value="latest">📅 최신순</option>
                <option value="oldest">📂 오래된순</option>
                <option value="popular">🔥 인기순</option>
              </select>
              <ChevronDown class="custom-arrow-icon" />
            </div>
        </div>
        <button 
          v-if="filterType !== 'all'" 
          @click="showAllPosts" 
          style="cursor: pointer; font-size: 0.9rem; padding: 0.2rem 0.5rem;">
          &lt; 전체게시글
        </button>
        <h2>{{ postListTitle }}</h2>
        <!-- ⬇️ 필터 상태일 때만 전체글 버튼 표시 -->

      </div>
      
      <div v-for="post in filteredPosts"
            :key="post.id"
            class="post-card"
            >
        <div class="post-user">
          <img
            :src="getProfileImage(post.user.profile_image)"
            alt="프사"
            class="mini-profile-image"
          />
          <span class="author-nickname">

            [Lv.{{ post.user.level || 0 }}]            
            {{ post.user.nickname }}
            <img
              :src="getLevelImage(post.user.level)"
              alt="레벨 뱃지"
              class="level-badge-1"
            /> 
          </span>
          <span class="created-at">{{ formatTime(post.created_at) }}</span>
          <!-- <span>{{ post }}</span> -->
        </div>

        <!-- 수정 & 삭제 버튼 (작성자 본인만 표시) -->
        <div v-if="post.user.nickname === userInfo?.nickname" class="post-actions">
          <button @click="editPost(post.id)">수정<PencilIcon class="icon" /> </button>
          <button @click="deletePost(post.id)">🗑️ 삭제</button>
        </div>


        <h3 @click="goToDetail(post.id)">{{ post.title }}</h3>
        <p>
          {{ post.content.length > 100 ? post.content.slice(0, 100) + '...' : post.content }}
        <span
          v-if="post.content.length > 100"
          class="read-more"
          @click.stop="goToDetail(post.id)"
        >
          더보기
        </span>
        </p>
        <div class="meta">
          <span class="meta-group">
            <button @click="toggleBookmark(post)" v-if="isLogin">
              <Bookmark :class="['bookmark-icon', { bookmarked: isBookmarked(post) }]" />
            </button>
            <span>{{ post.like_users_count }}</span>
          </span>
          <span class="meta-group">
            <MessageSquare class="meta-icon" />
            <span>{{ post.comments.length }}개</span>
          </span>
        </div>
         </div>

      <!-- 페이지네이션 -->
      <div class="pagination">
        <button
          v-for="page in totalPages"
          :key="page"
          @click="changePage(page)"
          :class="{ active: page === currentPage }"
        >
          {{ page }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import axios from '@/stores/axios' 
import { useRouter,useRoute } from 'vue-router'
import { PencilIcon } from '@heroicons/vue/24/solid'
import { Bookmark,MessageSquare, ChevronDown } from 'lucide-vue-next'



const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo)
const userProfile = computed(() => userStore.userProfile)
const isLogin = computed(() => userStore.isLogin)
const getProfile = userStore.getProfile
const posts = ref([])
const filterType = ref('all')  // all | my | bookmark
const router = useRouter()
const route = useRoute()
const defaultImage = '/default-profile.png'
const myPostCount = ref(0)
const myBookmarkCount = ref(0)
const sortOption = ref('latest')  // 기본값은 최신순
const searchQuery = ref('')
const goToLogin = () => router.push({ name: 'login', query: { next: route.fullPath } })
//페이지네이션 변수들
const currentPage = ref(1)
const postsPerPage = 10
const totalPosts = ref(0)

// 레벨 이미지
const levelImage = computed(() => {
  const level = userProfile?.community_level || 0
  if (level >= 100) return '/level/100.png'
  if (level >= 80) return '/level/80.png'
  if (level >= 60) return '/level/60.png'
  if (level >= 40) return '/level/40.png'
  if (level >= 20) return '/level/20.png'
  return '/level/1.png'
})


const getLevelImage = (level) => {
  if (!level) return '/level/1.png'
  if (level >= 100) return '/level/100.png'
  if (level >= 80) return '/level/80.png'
  if (level >= 60) return '/level/60.png'
  if (level >= 40) return '/level/40.png'
  if (level >= 20) return '/level/20.png'
  return '/level/1.png'
}

const changePage = async (page) => {
  currentPage.value = page
  if (filterType.value === 'all') {
    await fetchPosts(page)  // 서버에서 새 페이지 가져옴
  }
}

watch(sortOption, async () => {
  currentPage.value = 1
  await fetchPosts() 
})



watch(() => route.name, async (newVal) => {
  if (newVal === 'main' && isLogin) {
    await getProfile()  // ✅ 게시글 작성하고 돌아왔을 때도 최신 정보로
    await fetchPosts()
  }
})

//filterType 변경 시 fetchPosts 다시 실행
watch(filterType, async () => {
  currentPage.value = 1
  await fetchPosts()
})

watch(searchQuery, () => {
  currentPage.value = 1
})





// ✅ 필터링된 게시글 기준 페이지 수 계산
const totalPages = computed(() => {
  const nickname = userInfo.value?.nickname
  let count = 0

  if (filterType.value === 'my') {
    count = posts.value.filter(post => post.user.nickname === nickname).length
  } else if (filterType.value === 'bookmark') {
    count = posts.value.filter(post => post.like_users?.includes(userInfo.value?.id)).length
  } else {
    count = totalPosts.value
  }
  
  return Math.ceil(count / postsPerPage)
})

//북마크 기능-------------------------------------------------------------
const toggleBookmark = async (post) => {
  try {
    await axios.post(`http://127.0.0.1:8000/communities/${post.id}/like/`)

    // UI 즉시 반응
    const userId = userInfo.value?.id
    const likeUsers = post.like_users || []

    if (likeUsers.includes(userId)) {
      post.like_users = likeUsers.filter(id => id !== userId)
    } else {
      post.like_users = [...likeUsers, userId]
    }

    post.like_users_count = post.like_users.length

    // 서버 반영 약간 기다렸다가 fetch
    setTimeout(async () => {
      await getProfile()
      await fetchPosts(currentPage.value)
    }, 300)  // 300~500ms 정도 딜레이

  } catch (err) {
    console.error('북마크 처리 실패:', err)
  }
  
}

const isBookmarked = (post) => {
  return post.like_users?.includes(userInfo.value?.id)
}

//게시글 가져오기--------------------------------------------------------
const fetchPosts = async (page = 1) => {
  const offset = (page - 1) * postsPerPage

  try{
    let url = `http://127.0.0.1:8000/communities/`
    // ✅ 정렬 기준이 인기순인 경우 → 전체 불러오기!
    if (sortOption.value === 'popular' || filterType.value !== 'all') {
      url += `?limit=1000&offset=0`
    } else {
      url += `?limit=${postsPerPage}&offset=${offset}`
    }

    const res = await axios.get(url)
    await getProfile()

    posts.value = res.data.results
    totalPosts.value = res.data.count
    currentPage.value = page
    if (isLogin) {
      const username = userInfo.value?.username
      myPostCount.value = res.data.results.filter(post => post.user === username).length
      myBookmarkCount.value = res.data.results.filter(post =>
        post.like_users?.includes(userInfo.value?.id)
      ).length
    }
  } catch (err) {
    console.error('게시글 불러오기 실패:', err)
  }
}


//게시글 작성 이동--------------------------------------------------------
const goToCreate = () => {
  router.push({ name: 'post-create' })
}


//게시글 상세 조회 이동---------------------------------------------------------
const goToDetail = (postId) => {
  router.push({ name: 'post-detail', params: { id: postId } })
}

// 수정 기능------------------------------------------------------------
const editPost = (postId) => {
  router.push({ name: 'post-edit', params: { id: postId } })
}

// 삭제 기능------------------------------------------------------------
const deletePost = async (postId) => {
  const confirmDelete = confirm('정말 이 게시글을 삭제하시겠습니까?')
  if (!confirmDelete) return
  try {
    await axios.delete(`http://127.0.0.1:8000/communities/${postId}/`)
    alert('삭제되었습니다.')
    await fetchPosts()
  } catch (err) {
    console.error('삭제 실패:', err)
    alert('삭제 중 문제가 발생했습니다.')
  }
}
//시간 포맷 함수----------------------------------------------------------------
const formatTime = (timestamp) => {
  const now = new Date()
  const time = new Date(timestamp)
  const diff = Math.floor((now - time) / 60000)

  if (diff < 1) return '방금 전'
  if (diff < 60) return `${diff}분 전`
  if (now.toDateString() === time.toDateString()) return `${time.getHours()}시 ${time.getMinutes()}분`
  return `${time.getMonth() + 1}월 ${time.getDate()}일`
}




//필터링
const filteredPosts = computed(() => {
  const nickname = userInfo.value?.nickname
  let filtered = posts.value

  // 🔍 제목/내용 검색 필터
  if (searchQuery.value) {
    const keyword = searchQuery.value.toLowerCase()
    filtered = filtered.filter(
      post =>
        post.title.toLowerCase().includes(keyword) ||
        post.content.toLowerCase().includes(keyword)
    )
  }

  // 🧑‍💻 내가 쓴 글
  if (filterType.value === 'my') {
    filtered = filtered.filter(post => post.user.nickname === nickname)
  }
  // 📌 내가 북마크한 글
  else if (filterType.value === 'bookmark') {
    filtered = filtered.filter(post => post.like_users?.includes(userInfo.value?.id))
  }

  // 🔁 정렬
  if (sortOption.value === 'latest') {
    filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } else if (sortOption.value === 'oldest') {
    filtered.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
  } else if (sortOption.value === 'popular') {
    filtered.sort((a, b) => b.like_users_count - a.like_users_count)
  }

  // ✂️ 페이지네이션 (선택)
  const start = (currentPage.value - 1) * postsPerPage
  const end = start + postsPerPage
  return filtered.slice(start, end)
})




watch(filteredPosts, (newVal) => {
  console.log('🧪 필터링된 게시글:', newVal)
})

const showAllPosts = () => {
  filterType.value = 'all'
  currentPage.value = 1  // ✅ 페이지 초기화 추가
}
const showMyPosts = () => {
  filterType.value = 'my'
  currentPage.value = 1
  
}
const showBookmarkedPosts = () => {
  filterType.value = 'bookmark'
  currentPage.value = 1
}


//상단 제목 변경기능------------------------------------------------------
const postListTitle = computed(() => {
  if (filterType.value === 'my') return '📄 내가 작성한 글'
  if (filterType.value === 'bookmark') return '🔖 내가 북마크한 글'
  return ''
})


//각 게시글 프사----------------------------------------------------------
const getProfileImage = (path) => {
  if (!path || path === 'null' || path === 'undefined') {
    return '/default-profile.png'
  }
  return path.startsWith('http') ? path : `http://127.0.0.1:8000${path}`
}





//최초 실행----------------------------------------------------------------
onMounted(async () => {
  if (isLogin) {
    await getProfile()
  }
  fetchPosts()
  console.log('✅ 전체 게시글:', posts)
})


</script>

<style scoped>
/* 레이아웃 전체 */
.community-container {
  max-width: 1660px;
  margin: 0 auto;
  padding: 2rem 48px;
  display: flex;
  gap: 2rem;
  background-color: #f8f9fa;
  min-height: 100vh;
  box-sizing: border-box;
}

/* 왼쪽 프로필 박스 */
.profile-sidebar {
  width: 250px;
  padding: 1.5rem;
  border-radius: 1rem;
  background-color: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.center-align-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 1.5rem;
}
.profile-img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.08);
}
.nickname {
  font-size: 1.1rem;
  font-weight: 700;
  color: black;
}
.profile-actions {
  font-size: 0.85rem;
  color: #666;
}
.profile-count {
  cursor: pointer;
  transition: color 0.2s ease;
}
.profile-count:hover {
  color: #007bff;
}

.write-btn {
  display: block;
  width: 100%;
  padding: 0.6rem 1rem;
  background-color: #e0f0ff;
  color: #007bff;
  font-weight: 600;
  border-radius: 10px;
  text-align: center;
  transition: background-color 0.2s, color 0.2s;
}
.write-btn:hover {
  background-color: #d0e8ff;
  color: #0056b3;
}
.write-btn .icon {
  width: 17px;
  height: 17px;
  margin-right: 6px;
  vertical-align: middle;
  margin-bottom: 3px;
}

/* 게시글 리스트 */
.post-list {
  flex: 1;
  padding: 1rem;
}

.post-card {
  background-color: #fff;
  border-radius: 1rem;
  padding: 1.2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s ease;
  position: relative;
}
.post-card:hover {
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.1);
}
.post-card h3 {
  margin: 0.5rem 0;
  cursor: pointer;
  color: #333;
  transition: color 0.2s;
}
.post-card h3:hover {
  color: #007bff;
}
.post-card p {
  color: #444;
  line-height: 1.5;
  font-size: 0.95rem;
}

.created-at {
  font-size: 0.75rem;
  color: #aaa;
  display: flex;
  align-items: center;
  gap: 3px;
  margin-left: 6px;
}

.meta {
  font-size: 0.85rem;
  color: #999;
  margin-top: 0.8rem;
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
  width: 16px;
  height: 16px;
  stroke: #999;
  margin-right: 4px;
  vertical-align: middle;
  margin-right: 2px;
}

/* 수정/삭제 버튼 오른쪽 배치 */
.post-actions {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  gap: 0.5rem;
}

.post-actions button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background-color: transparent; /* ✅ 배경 제거 */
  color: #888;                  /* ✅ 텍스트 회색 */
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s ease;
  font-size: 0.85rem;
  box-shadow: none;
}

.post-actions button:hover {
  color: #444; /* ✅ hover 시 진한 회색 */
  background-color: transparent;
}

.post-actions .icon {
  width: 15px;
  height: 15px;
  margin-bottom: 2px;
  vertical-align: middle;
  color: #888;
}
/* 북마크 아이콘 버튼 */
.meta button {
  background-color: transparent !important;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  transition: color 0.2s ease;
}
.meta button:hover .bookmark-icon {
  stroke: #007bff;
  fill: #007bff;
}

.meta .bookmark-icon {
  width: 18px;
  height: 18px;
  stroke: #999;
  fill: none;
  transition: stroke 0.2s ease, fill 0.2s ease;
}
.meta .bookmark-icon.bookmarked {
  stroke: #007bff;
  fill: #007bff;
}

/* 필터 타이틀 */
.post-title-box {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
  margin-top: 1rem;
  margin-bottom: 1rem;
}

.author-nickname {
  font-size: 0.85rem;
  color: #555;
}

button {
  font-size: 0.9rem;
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 6px;
  background-color: #edf2fa;
  color: #007bff;
  cursor: pointer;
  transition: background-color 0.2s;
}
button:hover {
  background-color: #dcefff;
}
button:disabled {
  background-color: #e5e7eb;
  cursor: not-allowed;
}

.pagination {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
  gap: 8px;
}
.pagination button {
  background-color: #e0f0ff;
  color: #007bff;
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
  box-shadow: 0 2px 6px rgba(0, 123, 255, 0.1);
}
.pagination .active {
  background-color: #007bff;
  color: white;
  font-weight: bold;
}

.read-more {
  color: #9ca3af;
  font-size: 0.85rem;
  margin-left: 0.5rem;
  cursor: pointer;
  transition: color 0.2s ease;
}
.read-more:hover {
  color: #6b7280;
}
.custom-select-wrapper {
  position: relative;
  display: inline-block;
}

.sort-dropdown {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  padding: 0.4rem 2rem 0.4rem 0.8rem;
  font-size: 0.9rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  background-color: #f8fafc;
}
.custom-arrow-icon {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  stroke: #333; /* 선 느낌 */
  pointer-events: none;
}
.mini-profile-image {
  width: 26px;
  height: 26px;
  object-fit: cover;
  border-radius: 50%;
  margin-right: 6px;
  border: 1px solid #ccc;
}
.post-user {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.search-input {
  width: 360px;
  height: 36px;
  padding: 4px 12px; 
  font-size: 0.9rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  box-sizing: border-box;
}


.search-button {
  height: 36px;
  padding: 0 14px;
  font-size: 0.9rem;
  border: none;
  border-radius: 6px;
  background-color: #007bff;
  color: white;
  cursor: pointer;
}

.sort-dropdown {
  height: 36px;
  padding: 0 10px;
  font-size: 0.9rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  background-color: #f8fafc;
}

/* 로그인 버튼 */
.login-button {
  display: block;
  margin: 16px auto 0;
  background: #e0f0ff;
  color: #007bff;
  font-weight: 600;
  padding: 10px 20px;
  font-size: 0.95rem;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.15);
  transition: background 0.3s ease, box-shadow 0.3s ease;
}

.login-button:hover {
  background: #d4eaff;
}

.level-badge {
  width: 28px;
  height: 28px;
  
  margin-bottom: 6px;
  vertical-align: middle;
}
.level-badge-1 {
  width: 24px;
  height: 24px;
  
  margin-bottom: 4px;
  vertical-align: middle;
}
</style>


