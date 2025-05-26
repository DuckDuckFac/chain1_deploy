<template>
  <div class="profile-form">
    <h2 class="form-title">회원 정보 수정</h2>

    <!-- 호 사자 정보 -->
    <div class="form-section">
      <!-- <div class="input-group">
        <label>닉네임</label>
        <p>{{ userStore.userInfo.nickname }}</p>
      </div> -->
      <div class="input-group">
        <label>이메일</label>
        <p>{{ userStore.userInfo.email }}</p>
      </div>

      <div class="input-group">
        <label>닉네임 변경</label>
        <input
          v-model="form.nickname"
          :class="{ invalid: nicknameMessage === '이미 사용 중인 닉네임입니다.' }"
        />
        <p
          v-if="nicknameMessage"
          :style="{
            color:
              nicknameMessage === '사용 가능한 닉네임입니다.' ||
              nicknameMessage === '현재 사용 중인 닉네임입니다.'
                ? 'green'
                : 'red'
          }"
        >
          {{ nicknameMessage }}
        </p>
      </div>

      <div class="input-group">
        <label>현재 비밀번호</label>
        <input
          type="password"
          v-model="form.currentPassword"
          placeholder="비밀번호 수정 시 입력"
        />
        <p v-if="currentPasswordMessage" :style="{ color: currentPasswordValid ? 'green' : 'red' }">
          {{ currentPasswordMessage }}
        </p>
      </div>

      <div class="input-group">
        <label>새 비밀번호</label>
        <input type="password" v-model="form.newPassword" />
        <p class="hint">
          8자 이상 입력해주세요. 영문 대소문자, 숫자, 특수문자 중 2가지 이상 조합을 권장합니다.<br />
          공백은 사용할 수 없으며, 아이디나 생년월일과 같은 쉬용 비밀번호는 피해주세요.
        </p>
      </div>

      <div class="input-group">
        <label>새 비밀번호 확인</label>
        <input
          type="password"
          v-model="form.confirmPassword"
          :class="{ invalid: passwordMismatch }"
        />
        <p v-if="passwordMismatch" style="color: red;">비밀번호가 일치하지 않습니다.</p>
        <p v-else-if="passwordMatch" style="color: green;">비밀번호가 일치합니다.</p>
      </div>

      <div class="btn-group">
        <button type="submit" class="btn-primary" @click.prevent="updateProfile">수정</button>
        <button type="button" @click="goToMyPage" class="btn-secondary">취소</button>
      </div>
    </div>

    <p v-if="errorMessage" style="color:red">{{ errorMessage }}</p>
    <p v-if="successMessage" style="color:green">{{ successMessage }}</p>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { debounce } from 'lodash'
import { useUserStore } from '@/stores/user'
import swal from 'sweetalert'

const router = useRouter()
const userStore = useUserStore()
const API_URL = import.meta.env.VITE_API_URL

const form = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
  nickname: userStore.userInfo?.nickname || ''
})

const errorMessage = ref('')
const successMessage = ref('')

// ✅ 현재 비밀번호 유효성
const currentPasswordValid = ref(null)
const currentPasswordMessage = computed(() => {
  if (currentPasswordValid.value === null) return ''
  return currentPasswordValid.value ? '현재 비밀번호 확인 완료' : '현재 비밀번호가 틀렸습니다.'
})
const goToMyPage = () => {
  router.push({ name: 'user-profile', params: { nickname: userStore.userInfo.nickname } })
}
watch(() => form.value.currentPassword, debounce(async (val) => {
  if (!val) {
    currentPasswordValid.value = null
    return
  }
  try {
    const res = await axios.post(`${API_URL}/accounts/check-password/`, {
      current_password: val
    }, {
      headers: {
        Authorization: `Bearer ${userStore.token}`
      }
    })
    currentPasswordValid.value = res.data.valid
  } catch {
    currentPasswordValid.value = false
  }
}, 500))

// ✅ 비밀번호 일치 여부
const passwordMismatch = computed(() =>
  form.value.newPassword && form.value.confirmPassword &&
  form.value.newPassword !== form.value.confirmPassword
)

const passwordMatch = computed(() =>
  form.value.newPassword && form.value.confirmPassword &&
  form.value.newPassword === form.value.confirmPassword
)

// ✅ 닉네임 중복 확인
const nicknameMessage = ref('')
watch(() => form.value.nickname, debounce(async (val) => {
  if (!val) {
    nicknameMessage.value = ''
    return
  }

  // ✅ 자기 닉네임일 경우, 중복 체크하지 않고 메시지 고정
  if (val === userStore.userInfo.nickname) {
    nicknameMessage.value = '현재 사용 중인 닉네임입니다.'
    return
  }

  try {
    const res = await axios.get(`${API_URL}/accounts/check-nickname/`, {
      params: { nickname: val }
    })

    // ✅ 자기 닉네임이 아니면서 중복인 경우만 붉은 메시지
    nicknameMessage.value = res.data.exists
      ? '이미 사용 중인 닉네임입니다.'
      : '사용 가능한 닉네임입니다.'
  } catch {
    nicknameMessage.value = '닉네임 확인 실패'
  }
}, 500))

// ✅ 최종 프로필 수정 요청
const updateProfile = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  if (form.value.newPassword) {
  if (!currentPasswordValid.value) {
    errorMessage.value = '현재 비밀번호 확인이 필요합니다.'
    return
  }
}

  if (passwordMismatch.value) {
    errorMessage.value = '새 비밀번호가 일치하지 않습니다.'
    return
  }

  if (
    nicknameMessage.value === '이미 사용 중인 닉네임입니다.' &&
    form.value.nickname !== userStore.userInfo.nickname
  ) {
    errorMessage.value = '닉네임 중복을 확인해주세요.'
    return
  }

  try {
    // 1. 닉네임 수정

      await axios.patch(`${API_URL}/accounts/users/${userStore.userInfo.id}/`, {
        username: userStore.userInfo.username,
        nickname: form.value.nickname
      }, {
        headers: {
          Authorization: `Bearer ${userStore.token}`
        }
      })

    // 🔥 닉네임 로컬 상태 업데이트
    userStore.userInfo.nickname = form.value.nickname

    // 🔥 프로필도 다시 받아오기
    await userStore.getProfile()

    // 2. 비밀번호 수정 (입력 시만)
    if (form.value.newPassword) {
      await axios.put(`${API_URL}/accounts/change-password/`, {
        current_password: form.value.currentPassword,
        new_password: form.value.newPassword,
      }, {
        headers: {
          Authorization: `Bearer ${userStore.token}`
        }
      })
    }

    swal("수정 완료", "회원 정보가 성공적으로 수정되었습니다.", "success")
    setTimeout(() => {
      router.push({ name: 'user-profile', params: { nickname: form.value.nickname } })
    }, 1500)

  } catch (err) {
    errorMessage.value = err.response?.data?.detail || '수정 중 오류가 발생했습니다.'
    console.error('❌ 업데이트 실패:', err.response?.data)
  }
}
</script>

<style scoped>
.profile-form {
  max-width: 640px;
  margin: 80px auto;
  padding: 2rem;
  background-color: white;
  border-radius: 1rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.form-title {
  text-align: center;
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 2rem;
  color: #007bff;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 1.4rem;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group label {
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 6px;
  color: #333;
}

.input-group input {
  padding: 12px 14px;
  font-size: 0.95rem;
  border: 1px solid #ddd;
  border-radius: 10px;
  background-color: #f8f9fa;
  transition: border-color 0.2s ease;
}

.input-group input:focus {
  border-color: #007bff;
  background-color: #fff;
  outline: none;
}

input.invalid {
  border-color: red;
  background-color: #ffeaea;
}

.hint {
  font-size: 0.8rem;
  color: #666;
  margin-top: 4px;
  line-height: 1.3;
}

.btn-group {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-top: 1.5rem;
}

.btn-primary {
  background-color: #007bff;
  color: white;
  font-weight: 600;
  padding: 12px;
  font-size: 1rem;
  border: none;
  border-radius: 10px;
  cursor: pointer;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  font-weight: 600;
  padding: 12px;
  font-size: 1rem;
  border: none;
  border-radius: 10px;
  cursor: pointer;
}
</style>
