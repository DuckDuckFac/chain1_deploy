<template>
  <div class="register-container">
    <h1 class="register-title">회원가입</h1>
    <form @submit.prevent="submit" class="register-form">
      <!-- 아이디 -->
      <input
        v-model="user.username"
        placeholder="아이디"
        :class="{ invalid: usernameMessage === '이미 사용 중인 아이디입니다.' }"
        maxlength="12"
        required
      />
      <p class="hint">
        영문 소문자 및 숫자만 사용 가능하며, 4자 이상 12자 이하로 입력해주세요.
      </p>
      <p :class="{ valid: isUsernameChecked, invalid: usernameMessage === '이미 사용 중인 아이디입니다.' }">
        {{ usernameMessage }}
      </p>

      <!-- 비밀번호 -->
      <input
        v-model="user.password"
        type="password"
        placeholder="비밀번호"
        required
      />
      <p class="hint">
        8자 이상, 영문/숫자/특수문자 중 2가지 이상 조합을 권장합니다.
      </p>

      <!-- 비밀번호 확인 -->
      <input
        v-model="passwordConfirm"
        type="password"
        placeholder="비밀번호 확인"
        :class="{ invalid: passwordMismatch }"
        required
      />
      <p v-if="passwordMismatch" class="invalid">비밀번호가 일치하지 않습니다.</p>

      <!-- 이메일 -->
      <input
        v-model="user.email"
        type="email"
        placeholder="이메일"
        required
      />

      <!-- 닉네임 -->
      <input
        v-model="user.nickname"
        placeholder="닉네임"
        :class="{ invalid: nicknameMessage === '이미 사용 중인 닉네임입니다.' }"
        maxlength="10"
        required
      />
      <p :class="{ valid: isNicknameChecked, invalid: nicknameMessage === '이미 사용 중인 닉네임입니다.' }">
        {{ nicknameMessage }}
      </p>

      <button type="submit" class="register-submit">가입하기</button>
    </form>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import swal from 'sweetalert'
import { debounce } from 'lodash'
import axiosInstance from '@/stores/axios'

const router = useRouter()
const userStore = useUserStore()

const user = ref({
  username: '',
  password: '',
  email: '',
  nickname: '',
})
const passwordConfirm = ref('')

// ✅ 비밀번호 확인
const passwordMismatch = computed(() => {
  return user.value.password && passwordConfirm.value && user.value.password !== passwordConfirm.value
})

// 중복 확인 관련 상태
const isUsernameChecked = ref(false)
const isNicknameChecked = ref(false)
const usernameMessage = ref('')
const nicknameMessage = ref('')

// ✅ 아이디 유효성 검사 정규식
const isValidUsername = (username) => /^[a-z0-9]{4,12}$/.test(username)

// ✅ 아이디 중복 체크
const checkUsername = debounce(async () => {
  const username = user.value.username
  if (!isValidUsername(username)) {
    usernameMessage.value = '영문 소문자+숫자 조합, 4~12자여야 합니다.'
    isUsernameChecked.value = false
    return
  }
  try {
    const res = await axiosInstance.get('/accounts/check-username/', {
      params: { username }
    })
    if (res.data.exists) {
      usernameMessage.value = '이미 사용 중인 아이디입니다.'
      isUsernameChecked.value = false
    } else {
      usernameMessage.value = '사용 가능한 아이디입니다.'
      isUsernameChecked.value = true
    }
  } catch (err) {
    usernameMessage.value = '서버 오류'
    isUsernameChecked.value = false
  }
}, 500)

// ✅ 닉네임 중복 체크
const checkNickname = debounce(async () => {
  const nickname = user.value.nickname
  if (!nickname || nickname.length > 10) {
    nicknameMessage.value = '닉네임은 1~10자 이내여야 합니다.'
    isNicknameChecked.value = false
    return
  }
  try {
    const res = await axiosInstance.get('/accounts/check-nickname/', {
      params: { nickname }
    })
    if (res.data.exists) {
      nicknameMessage.value = '이미 사용 중인 닉네임입니다.'
      isNicknameChecked.value = false
    } else {
      nicknameMessage.value = '사용 가능한 닉네임입니다.'
      isNicknameChecked.value = true
    }
  } catch (err) {
    nicknameMessage.value = '서버 오류'
    isNicknameChecked.value = false
  }
}, 500)

// ✅ 실시간 입력 감지
watch(() => user.value.username, (val) => {
  const filtered = val.replace(/[^a-z0-9]/gi, '').slice(0, 12)
  if (filtered !== val) user.value.username = filtered.toLowerCase()
  isUsernameChecked.value = false
  checkUsername()
})

watch(() => user.value.nickname, (val) => {
  if (val.length > 10) user.value.nickname = val.slice(0, 10)
  isNicknameChecked.value = false
  checkNickname()
})

// ✅ 회원가입 실행
const submit = async () => {
  if (!isUsernameChecked.value || !isNicknameChecked.value) {
    swal('아이디 또는 닉네임 중복 확인을 완료해주세요.')
    return
  }

  if (passwordMismatch.value) {
    swal('비밀번호가 일치하지 않습니다.')
    return
  }

  try {
    // 회원가입 요청
    const res = await axiosInstance.post('/accounts/register/', user.value)
    const { access, refresh, user: userData } = res.data

    userStore.token = access
    userStore.refreshToken = refresh
    userStore.userInfo = userData
    axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${access}`

    swal('가입 성공! 이메일을 확인해주세요.📩')
    router.push({ name: 'main' })
  } catch (err) {
    console.error('❌ 에러 응답:', err.response?.data)
    swal('가입 실패: ' + (err.response?.data?.message || '서버 오류'))
  }
}
</script>

<style scoped>
.register-container {
  max-width: 460px;
  margin: 80px auto 40px auto;
  padding: 32px 24px;
  border-radius: 16px;
  background-color: #fff;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.04);
}

.register-title {
  text-align: center;
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 24px;
  color: #222;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

input {
  padding: 12px 16px;
  font-size: 0.95rem;
  border: 1px solid #ddd;
  border-radius: 10px;
  background-color: #f9f9f9;
  transition: border-color 0.2s ease;
}

input:focus {
  border-color: #007bff;
  background-color: #fff;
  outline: none;
}

input.invalid {
  border-color: red;
  background-color: #ffeaea;
}

button.register-submit {
  background-color: #007bff;
  color: white;
  font-weight: 600;
  padding: 12px;
  font-size: 1rem;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s ease;
}

button.register-submit:hover {
  background-color: #0056b3;
}

.hint {
  font-size: 0.8rem;
  color: #666;
  margin: -6px 0 4px;
  line-height: 1.4;
}

.valid {
  color: green;
  font-size: 0.85rem;
}

.invalid {
  color: red;
  font-size: 0.85rem;
}
</style>
