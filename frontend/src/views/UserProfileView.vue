<template>
  <!-- 배경 이미지 -->
  <div class="cover-image-wrapper">
    <div
      class="cover-image"
      :style="{ backgroundImage: `url(${getCoverImageUrl(profile?.background_image)})` }"
    >
      <button v-if="isMine" @click="resetCoverImage" class="cover-reset-btn">
        <ArrowPathIcon class="icon-reset-white" />
      </button>
      <label v-if="isMine" for="coverInput" class="cover-upload-btn">배경 변경</label>
      <input type="file" id="coverInput" class="file-hidden" @change="onCoverChange" />
    </div>
  </div>

  <!-- 프로필 이미지 + 닉네임 등 -->
  <div class="top-info-wrapper">
    <div class="top-info">
      <div class="profile-image-wrapper">
        <img
          :src="previewUrl || getProfileImageUrl(profile?.image)"
          alt="프로필 이미지"
          class="profile-image"
        />
        <label v-if="isMine" for="fileInput" class="file-icon-overlay" title="사진 선택">
          <Cog6ToothIcon class="file-icon" />
        </label>
        <input type="file" id="fileInput" class="file-hidden" @change="onFileChange" />
      </div>

      <div class="text-info">
        <!-- 닉네임 -->
        <div class="nickname-edit">
          <template v-if="isMine">
            <template v-if="!editingNickname">
              <h3>{{ profile?.user?.nickname || '닉네임 없음' }}</h3>
              <button @click="startEditing" class="icon-button" title="닉네임 변경">
                <PencilIcon class="icon-svg" />
              </button>
            </template>
            <template v-else>
              <input v-model="newNickname" @keyup.enter="updateNickname" placeholder="새 닉네임 입력" />
              <button @click="updateNickname" class="nickname-confirm-btn">수정 완료</button>
              <button @click="cancelNicknameEdit" class="nickname-cancel-btn">취소</button>
              <p v-if="nicknameMessage" :style="{ color: nicknameValid ? 'green' : 'red' }">
                {{ nicknameMessage }}
              </p>
            </template>
          </template>

          <template v-else>
            <h3>{{ profile?.user?.nickname || '닉네임 없음' }}</h3>
          </template>
        </div>

        <!-- 레벨/경험치 -->
        <p v-if="profile">
          <span class="level">
          Lv.{{ profile.community_level || 1 }}
          <img :src="getLevelEgg(profile.community_level)" alt="레벨 이미지" class="level-egg" />
        </span>
          <span class="stats">
            (총 경험치: {{ profile.total_exp || 0 }} XP / 포인트: {{ profile.usable_points || 0 }} pt)
          </span>
        </p>

        <!-- 기본 이미지 버튼 -->
        <div v-if="isMine" class="button-row">
          <button @click="resetImage" class="plain-button">
            <ArrowPathIcon class="icon-inline" />
            기본 이미지로 변경
          </button>
          <button v-if="selectedImage" @click="uploadImage" class="outlined-button">사진 업로드</button>
          <button v-if="selectedImage" @click="cancelImageSelection" class="outlined-button cancel-upload">취소</button>
        </div>
      </div>
    </div>
  </div>

  <!-- 프로필 하단 정보 -->
  <div class="container">
    <div class="profile-container">
      <!-- 왼쪽: 상세 정보 -->
      <div class="profile-section">
        <div class="profile">
          <div class="profile-header-row">
            <h3>나의 프로필</h3>
            <button v-if="isMine" @click="router.push({ name: 'profile-interestedit' })" class="edit-interest-btn">수정</button>
          </div>
          <hr class="divider" />
          <ul class="profile-info-list">
            <li><strong>성별</strong> <span class="tag-box">{{ genderMap[profile?.gender] || '아직 정보가 없어요' }}</span></li>
            <li><strong>자산</strong> <span class="tag-box">{{ assetMap[profile?.asset] || '아직 정보가 없어요' }}</span></li>
            <li><strong>소득</strong> <span class="tag-box">{{ incomeMap[profile?.income] || '아직 정보가 없어요' }}</span></li>
            <li><strong>직업</strong> <span class="tag-box">{{ jobMap[profile?.job] || '아직 정보가 없어요' }}</span></li>
            <li>
              <strong>관심 분야</strong>
              <div class="interest-tags">
                <span class="tag-box interest-tag" v-for="(tag, i) in interestTags" :key="i">{{ tag }}</span>
              </div>
            </li>
          </ul>
          <div class="edit-buttons" v-if="isMine">
            <button @click="router.push({ name: 'profile-edit' })" class="edit-profile-btn">회원정보 수정</button>
          </div>
        </div>
      </div>

      <!-- 오른쪽: 좋아요한 상품 -->
      <div class="liked-section">
        <img src="/mypage-nest.png" alt="둥지" class="nest-overlay" />
        <LikedProducts
          title="나의 예금"
          :likedProducts="likedDepositProducts"
          @unliked="fetchLikedProducts"
          @show-detail="showProductDetail"
        />
        <LikedProducts
          title="나의 적금"
          :likedProducts="likedSavingProducts"
          @unliked="fetchLikedProducts"
          @show-detail="showProductDetail"
        />
      </div>
    </div>

    <!-- 상품 상세 모달 -->
    <div v-if="selectedProduct" class="product-detail-modal">
      <div class="modal-content">
        <h2>{{ selectedProduct.fin_prdt_nm }}</h2>
        <div class="modal-divider"></div>

        <!-- 요약 정보를 표로 -->
        <table class="product-info-table">
        <tbody>
          <tr>
            <th>금융회사</th>
            <td>{{ selectedProduct.kor_co_nm }}</td>
          </tr>
          <tr>
            <th>상품유형</th>
            <td>{{ selectedProduct.product_type === 'deposit' ? '예금' : '적금' }}</td>
          </tr>
          <tr>
            <th>가입 대상</th>
            <td>{{ selectedProduct.join_member }}</td>
          </tr>
          <tr>
            <th>가입 방법</th>
            <td>{{ selectedProduct.join_way }}</td>
          </tr>
          <tr>
            <th>금리 유형</th>
            <td>{{ selectedProduct.intr_rate_type_nm }}</td>
          </tr>
          <tr>
            <th>기본 금리</th>
            <td>{{ selectedProduct.intr_rate }}%</td>
          </tr>
          <tr>
            <th>최고 금리</th>
            <td>{{ selectedProduct.intr_rate2 }}%</td>
          </tr>
          <tr>
            <th>저축 기간</th>
            <td>{{ selectedProduct.save_trm }}개월</td>
          </tr>
          </tbody>
        </table>

        <!-- 긴 설명은 따로 블록으로 -->
        <div class="long-info-block" v-if="selectedProduct.spcl_cnd">
          <h4>📌 우대 조건</h4>
          <p>{{ selectedProduct.spcl_cnd }}</p>
        </div>

        <div class="long-info-block" v-if="selectedProduct.mtrt_int">
          <h4>📌 만기 후 이자율</h4>
          <p>{{ selectedProduct.mtrt_int }}</p>
        </div>

        <div class="modal-footer">
          <button @click="closeProductDetail">닫기</button>
        </div>
      </div>
    </div>

  </div>

  <!-- 토스트 메시지 -->
  <div v-if="showToast" class="toast-message">
    {{ toastMessage }}
  </div>
</template>




<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/stores/axios.js' 
import { useUserStore } from '@/stores/user'
import LikedProducts from '@/components/LikedProducts.vue'
import { PencilIcon,Cog6ToothIcon,ArrowPathIcon } from '@heroicons/vue/24/solid'

const selectedProduct = ref(null)
const likedDepositProducts = ref([])
const likedSavingProducts = ref([])
const API_URL = 'http://127.0.0.1:8000'
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const userProfile = userStore.userProfile
const selectedImage = ref(null)
const previewUrl = ref(null)
const toastMessage = ref('')
const showToast = ref(false)

//배경이미지
const selectedCover = ref(null)

const getLevelEgg = (level) => {
  if (!level) return '/level/1.png'
  if (level >= 100) return '/level/100.png'
  if (level >= 80) return '/level/80.png'
  if (level >= 60) return '/level/60.png'
  if (level >= 40) return '/level/40.png'
  if (level >= 20) return '/level/20.png'
  return '/level/1.png'
}

const resetCoverImage = async () => {
  try {
    await axios.patch(`${API_URL}/accounts/profile/${profile.value.id}/reset-background/`)
    showToastMessage('햇볕은 쨍쨍 🌤️')
    await fetchProfile()
  } catch (err) {
    console.error('기본 배경 초기화 실패:', err)
    alert('기본 배경으로 되돌릴 수 없었어요 😢')
  }
}


const getCoverImageUrl = (path) => {
  if (!path || path === 'null' || path === 'undefined') {
    return new URL('/default-cover.png', import.meta.url).href
  }
  return path.startsWith('http') ? path : `http://127.0.0.1:8000${path}`
}

const onCoverChange = (event) => {
  const file = event.target.files[0]
  selectedCover.value = file
  uploadCoverImage()
}

const uploadCoverImage = async () => {
  if (!selectedCover.value) return
  const formData = new FormData()
  formData.append('background_image', selectedCover.value)

  try {
    await axios.patch(`${API_URL}/accounts/profile/${profile.value.id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    showToastMessage('배경 이미지 변경성공!')
    await fetchProfile()
    selectedCover.value = null
  } catch (err) {
    console.error('배경 이미지 업로드 실패:', err)
    alert('배경 이미지 업로드에 실패했어요 😢')
  }
}

const interestTags = computed(() => {
  const raw = profile.value?.interests || ''
  return raw.split(',').map(tag => tag.trim()).filter(Boolean)
})


const showProductDetail = async (product) => {
  console.log('😎상세보기 product:', product)
  // 필드가 부족하면 서버에서 상세 정보 요청
  if (!product.join_member || !product.join_way || !product.spcl_cnd) {
    try {
      const res = await axios.get(`${API_URL}/finlife/detail/${product.fin_prdt_cd}/`, {
        params: {
          product_type: product.product_type || getProductType(product.fin_prdt_cd),
        }
      })
      selectedProduct.value = res.data
      return
    } catch (err) {
      console.error('상품 상세정보 요청 실패:', err)
      alert('상품 상세 정보를 불러오지 못했습니다.')
      return
    }
  }

  // 정보 충분하면 그대로 모달에 띄움
  selectedProduct.value = product
}
const cancelImageSelection = () => {
  selectedImage.value = null
  previewUrl.value = null
}

const resetImage = async () => {
  try {
    await axios.patch(`${API_URL}/accounts/profile/${profile.value.id}/reset-image/`)
    showToastMessage('삐약삐약 🐣')
    await fetchProfile()
  } catch (err) {
    console.error('기본 이미지 초기화 실패:', err)
    alert('기본 이미지로 되돌리는 데 실패했습니다.')
  }
}

const getProductType = (code) => {
  return code.startsWith('HK') ? 'saving' : 'deposit'
}

const closeProductDetail = () => {
  selectedProduct.value = null
}




// value값에 맞춰서
const genderMap = { M: '남성', F: '여성', N: '선택 안함' }
const assetMap = {
  '1': '1000만원 이하',
  '2': '3000만원 이하',
  '3': '5000만원 이하',
  '4': '1억 이하',
  '5': '1억 초과'
}
const incomeMap = {
  none: '없음',
  under30: '3000만원 이하',
  under50: '5000만원 이하',
  over50: '5000만원 초과'
}
const jobMap = {
  student: '학생',
  employee: '직장인',
  self: '자영업자',
  unemployed: '무직'
}

const profile = ref(null)
const isMine = ref(false)
// 닉네임 수정 -------------------------
const editingNickname = ref(false)
const newNickname = ref('')
const nicknameMessage = ref('')
const nicknameValid = ref(false)

const startEditing = () => {
  editingNickname.value = true
  newNickname.value = profile.value?.user?.nickname || ''
}
watch(newNickname, async (val) => {
  const trimmed = val.trim()
  if (!trimmed) {
    nicknameMessage.value = ''
    nicknameValid.value = false
    return
  }

  if (trimmed === userStore.userInfo.nickname) {
    nicknameMessage.value = '현재 사용 중인 닉네임입니다.'
    nicknameValid.value = true
    return
  }

  try {
    const res = await axios.get(`${API_URL}/accounts/check-nickname/`, {
      params: { nickname: trimmed }
    })
    nicknameValid.value = !res.data.exists
    nicknameMessage.value = res.data.exists
      ? '이미 사용 중인 닉네임입니다.'
      : '사용 가능한 닉네임입니다.'
  } catch {
    nicknameMessage.value = '닉네임 확인 실패'
    nicknameValid.value = false
  }
})

const updateNickname = async () => {
  if (!nicknameValid.value) {
    alert('사용 가능한 닉네임을 입력해주세요.')
    return
  }

  try {
    await axios.patch(`${API_URL}/accounts/users/${userStore.userInfo.id}/`, {
      username: userStore.userInfo.username,
      nickname: newNickname.value
    }, {
      headers: {
        Authorization: `Bearer ${userStore.token}`
      }
    })

    // ✅ 상태 및 전역 반영
    userStore.userInfo.nickname = newNickname.value
    await userStore.getProfile()

    // ✅ URL 이동 먼저
    await router.push({ name: 'user-profile', params: { nickname: newNickname.value } })

    // ✅ fetchProfile에 닉네임 직접 전달
    await fetchProfile(newNickname.value)

    // ✅ UI 초기화
    editingNickname.value = false
    nicknameMessage.value = ''
    newNickname.value = ''

    swal('닉네임 변경 완료', '닉네임이 성공적으로 변경되었습니다.', 'success')
  } catch (err) {
    console.error('닉네임 변경 실패:', err.response?.data || err.message)
    alert('닉네임 변경 중 오류가 발생했습니다.')
  }
}

const cancelNicknameEdit = () => {
  editingNickname.value = false
  newNickname.value = ''
  nicknameMessage.value = ''
  nicknameValid.value = false
}


//프로필사진-----------------------------------------------


const getProfileImageUrl = (path) => {
  if (!path || path === 'null' || path === 'undefined') {
    return new URL('/default-profile.png', import.meta.url).href
  }
  return path.startsWith('http') ? path : `http://127.0.0.1:8000${path}`
}



const onFileChange = (event) => {
  const file = event.target.files[0]
  selectedImage.value = file
  previewUrl.value = URL.createObjectURL(file)  // ✅ 미리보기 URL 생성
}


const uploadImage = async () => {
  if (!selectedImage.value) {
    alert('사진을 선택해주세요!')
    return
  }

  const formData = new FormData()
  formData.append('image', selectedImage.value)

  try {
    const res = await axios.patch(`${API_URL}/accounts/profile/${profile.value.id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    alert('프로필 사진이 업로드되었습니다!')
    await fetchProfile()
    profile.value.image = res.data.image  // 프로필에 이미지 갱신
    selectedImage.value = null
    previewUrl.value = null

  } catch (err) {
    console.error('업로드 실패:', err)
    if (err.response) {
    console.error('응답 데이터:', err.response.data)
    console.error('응답 상태코드:', err.response.status)
  }
    alert('업로드에 실패했습니다.')
  }
}



const showToastMessage = (message) => {
  toastMessage.value = message
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 2000)
}


// esc 닫기
const handleKeyDown = (e) => {
  if (e.key === 'Escape' && editingNickname.value) {
    cancelNicknameEdit()
  }

}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

//-----------------------------------------------------------------------

const fetchProfile = async (nicknameParam = route.params.nickname) => {
  try {
    const res = await axios.get(`${API_URL}/accounts/profile-by-nickname/${nicknameParam}/`)
    profile.value = res.data
    isMine.value = (userStore.userInfo?.id === res.data.user?.id)
  } catch (err) {
    console.error('프로필 불러오기 실패:', err)
    alert('해당 유저의 프로필을 찾을 수 없습니다.')
  }
}
const fetchLikedProducts = async () => {
  try {
    const res = await axios.get(`${API_URL}/finlife/like/mine/`, {
      withCredentials: true
    })
    console.log('🎯 좋아요 응답 데이터:', res.data)

    likedDepositProducts.value = res.data.deposit || []
    likedSavingProducts.value = res.data.saving || []
  } catch (err) {
    console.error('❌ 좋아요한 상품 불러오기 실패:', err)
  }
}

const handleUnlike = (type, productCode) => {
  if (type === 'deposit') {
    likedDepositProducts.value = likedDepositProducts.value.filter(
      p => p.fin_prdt_cd !== productCode
    )
  } else if (type === 'saving') {
    likedSavingProducts.value = likedSavingProducts.value.filter(
      p => p.fin_prdt_cd !== productCode
    )
  }


}





onMounted(() => {
  fetchProfile()
  fetchLikedProducts()
})

//메모리 누수 방지
onUnmounted(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
})

</script>

<style scoped>
.container {
  max-width: 1660px;
  margin: 0 auto;
  padding: 0 24px;
  box-sizing: border-box;
  overflow-x: hidden;
  font-family: 'Pretendard', sans-serif;
  color: #222;
}
.cover-image-wrapper {
  width: 100%;
  height: 200px;
  overflow: hidden;
  border-radius: 16px 16px 0 0;
  margin-bottom: 1.5rem;
}
.cover-image {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  position: relative;
}
.cover-upload-btn,
.cover-reset-btn {
  position: absolute;
  bottom: 12px;
  background: rgba(255, 255, 255, 0.75);
  padding: 4px 10px;
  font-size: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  z-index: 10;
}
.cover-reset-btn {
  right: 100px;
  background: none;
  border: none;
  padding: 0;
}
.cover-upload-btn {
  right: 16px;
}
.top-info-wrapper {
  position: relative;
  margin-top: -80px;
  z-index: 2;
  padding: 0 2rem;
  overflow-x: hidden;
}
.top-info {
  display: flex;
  align-items: center;
  gap: 24px;
  transform: translateX(40px);
}
.profile-container {
  display: grid;
  grid-template-columns: 8fr 4fr;
  gap: 2rem;
  padding: 2rem;
}
.profile {
  margin-top: 50px;
  background: white;
  border-radius: 16px;
  padding: 24px;
  position: relative;
  top: -60px;
  z-index: 1;
}
.profile-image {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 50%;
  margin-bottom: 1rem;
}
.text-info {
  transform: translateY(18px);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.nickname-edit {
  display: flex;
  align-items: center;
  gap: 10px;
}
.nickname-edit input {
  padding: 6px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.nickname-confirm-btn,
.nickname-cancel-btn {
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.nickname-confirm-btn {
  background-color: #e0f3ff;
  border: 1px solid #a3d3ff;
  color: #007bff;
}
.nickname-confirm-btn:hover {
  background-color: #d1eaff;
}
.nickname-cancel-btn {
  background-color: #f2f2f2;
  border: 1px solid #ccc;
  color: #666;
}
.nickname-cancel-btn:hover {
  background-color: #e0e0e0;
}
.icon-button {
  all: unset;
  cursor: pointer;
  display: flex;
  align-items: center;
}
.icon-svg {
  width: 20px;
  height: 20px;
  color: #666;
  transition: color 0.2s ease;
}
.icon-button:hover .icon-svg {
  color: #4e4e4e;
}
.profile-image-wrapper {
  position: relative;
  display: inline-block;
}
.profile-info-list {
  list-style: none;
  padding: 0;
  margin: 1rem 0;
}
.profile-info-list li {
  margin-bottom: 20px;
  font-size: 0.95rem;
}
.level {
  color: #007bff;
  font-weight: bold;
  margin-right: 8px;
}
.stats {
  color: #888;
}
.profile-header-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 0.5rem;
}
.edit-interest-btn {
  all: unset;
  cursor: pointer;
  font-size: 0.9rem;
  color: #aaa;
}
.file-icon {
  width: 20px;
  height: 20px;
  color: #444;
}
.file-icon-overlay {
  position: absolute;
  bottom: 16px;
  right: 16px;
  width: 28px;
  height: 28px;
  background-color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.2);
}
.file-icon-overlay:hover .file-icon {
  color: #007bff;
}
.file-hidden {
  display: none;
}
.button-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 0px;
}
.plain-button {
  background: none;
  border: none;
  padding: 4px 6px;
  font-size: 0.85rem;
  color: #333;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: color 0.2s ease;
}
.plain-button:hover {
  color: #007bff;
}
.outlined-button {
  background: none;
  border: 1px solid #ccc;
  padding: 4px 8px;
  font-size: 0.85rem;
  color: #555;
  cursor: pointer;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  height: 28px;
}
.outlined-button:hover {
  border-color: #007bff;
  color: #007bff;
}
.icon-inline,
.icon-reset-white {
  width: 18px;
  height: 18px;
}
.icon-inline {
  vertical-align: middle;
  color: #333;
}
.icon-reset-white {
  color: white;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.3);
}
.divider {
  border: none;
  border-bottom: 1px solid #ccc;
  margin: 0.5rem 0 1rem;
}
.tag-box {
  display: inline-block;
  padding: 2px 8px;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #444;
}
.interest-tag {
  background-color: #e6f2ff;
  border: 1px solid #a3d3ff;
  border-radius: 16px;
  font-size: 0.85rem;
  color: #007bff;
  font-weight: 500;
  padding: 6px 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.interest-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}
.edit-profile-btn {
  all: unset;
  cursor: pointer;
  font-size: 0.9rem;
  color: #555;
  margin-top: 0.5rem;
}
.edit-profile-btn:hover {
  color: #4e4e4e;
}
.nest-overlay {
  position: absolute;
  top: -50px;
  right: 24px;
  width: 120px;
  z-index: 10;
  pointer-events: none;
}
.liked-section {
  position: relative;
  min-width: 0;
  background: #fff;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
}
.product-detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}
.modal-content {
  background: #ffffff;
  padding: 24px;
  border-radius: 16px;
  width: 90%;
  max-width: 540px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  font-family: 'Pretendard', sans-serif;
  animation: popUp 0.3s ease-out;
  color: #333;
  font-size: 0.92rem;
}
.modal-content h2 {
  font-size: 1.1rem;
  font-weight: bold;
  color: #222;
  margin-bottom: 12px;
  line-height: 1.4;
}
.modal-divider {
  border-bottom: 1px solid #e0e0e0;
  margin: 12px 0 16px;
}
.modal-content p {
  margin: 8px 0;
  line-height: 1.5;
  color: #444;
  font-size: 0.9rem;
}
.modal-content strong {
  color: #007bff;
  font-weight: 600;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
.modal-content button {
  padding: 8px 16px;
  background-color: #e0f0ff;
  color: #007bff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: background-color 0.2s ease;
}
.modal-content button:hover {
  background-color: #d2e8ff;
}
.product-info-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
  font-size: 0.9rem;
}
.product-info-table th {
  text-align: left;
  padding: 8px 10px;
  width: 40%;
  color: #007bff;
  font-weight: 600;
  background-color: #f5faff;
  border-bottom: 1px solid #e0e0e0;
  vertical-align: top;
}
.product-info-table td {
  padding: 8px 10px;
  border-bottom: 1px solid #e0e0e0;
  color: #444;
}
.long-info-block {
  margin-top: 10px;
}
.long-info-block h4 {
  font-size: 0.92rem;
  margin-bottom: 4px;
  color: #333;
}
.long-info-block p {
  white-space: pre-line;
  font-size: 0.88rem;
  color: #555;
  line-height: 1.5;
}
@keyframes popUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
.toast-message {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  background: #fffbdd;
  border: 1px solid #f0c36d;
  color: #8a6d3b;
  padding: 12px 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  font-weight: bold;
  font-size: 0.9rem;
  animation: fadeInOut 2s ease forwards;
  z-index: 9999;
}
@keyframes fadeInOut {
  0%   { opacity: 0; transform: translateX(-50%) translateY(20px); }
  10%  { opacity: 1; transform: translateX(-50%) translateY(0); }
  90%  { opacity: 1; }
  100% { opacity: 0; transform: translateX(-50%) translateY(20px); }
}

.level-egg {
  width: 28px;
  height: 28px;
  margin-bottom: 4px;
  vertical-align: middle;
}
</style>

