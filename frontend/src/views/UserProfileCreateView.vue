<template>
  <div class="profile-form">
    <!-- Step 1 -->
    <div v-if="step === 1">
      <h2>기본 정보 입력</h2>
      <form @submit.prevent="goToStep2">
        <input type="date" v-model="form.birth_date" required />

        <select v-model="form.gender" required>
          <option disabled value="">성별 선택</option>
          <option value="M">남성</option>
          <option value="F">여성</option>
          <option value="N">선택 안함</option>
        </select>

        <select v-model="form.asset" required>
          <option disabled value="">자산 선택</option>
          <option value="1">1000만원 이하</option>
          <option value="2">3000만원 이하</option>
          <option value="3">5000만원 이하</option>
          <option value="4">1억 이하</option>
          <option value="5">1억 초과</option>
        </select>

        <select v-model="form.income" required>
          <option disabled value="">소득 선택</option>
          <option value="none">없음</option>
          <option value="under30">3000만원 이하</option>
          <option value="under50">5000만원 이하</option>
          <option value="over50">5000만원 초과</option>
        </select>

        <select v-model="form.job" required>
          <option disabled value="">직업 선택</option>
          <option value="student">학생</option>
          <option value="employee">직장인</option>
          <option value="self">자영업자</option>
          <option value="unemployed">무직</option>
        </select>

        <button type="submit">다음</button>
        <button type="button" @click="skipToStep2">건너뛰기</button>
      </form>
    </div>

    <!-- Step 2 -->
    <div v-else>
      <h2>관심사 입력</h2>
      <form @submit.prevent="submitFinal">
        <div class="checkbox-group">
          <label v-for="option in interestOptions" :key="option">
            <input type="checkbox" :value="option" v-model="selectedInterests" />
            {{ option }}
          </label>
        </div>

        <button type="submit">제출 완료</button>
        <button type="button" @click="finishWithoutInterests">건너뛰기</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const step = ref(1)
const userStore = useUserStore()
const router = useRouter()
const API_URL = 'http://127.0.0.1:8000'

// form 구조
const form = ref({
  birth_date: '',
  gender: '',
  asset: '',
  income: '',
  job: '',
  interests: ''
})

// 관심사 체크박스 옵션
const interestOptions = [
  '예금/적금',
  '신용대출',
  '주택청약',
  '전세자금 대출',
  '보험 (건강/자동차)',
  '신용카드 혜택',
  '주식 투자',
  'ETF / 리츠',
  '펀드',
  '연금/노후 준비',
  '비상금 마련',
  '사회초년생 금융',
]

const selectedInterests = ref([])

// Step1 필수값 검증
const validate = () => {
  return (
    form.value.birth_date &&
    form.value.gender &&
    form.value.asset &&
    form.value.income &&
    form.value.job
  )
}

// 마운트 시 프로필 불러오기
onMounted(async () => {
  try {
    await userStore.getProfile()
    if (!userStore.userProfile?.id) {
      console.warn('프로필 없음')
    } else {
      console.log('✅ 프로필 ID:', userStore.userProfile.id)
    }
  } catch (err) {
    console.error('프로필 불러오기 실패:', err)
  }
})

// Step1 저장
const goToStep2 = async () => {
  if (!validate()) {
    alert('모든 항목을 입력해주세요.')
    return
  }

  const profileId = userStore.userProfile?.id
  if (!profileId) {
    alert('프로필 ID가 없습니다.')
    return
  }

  try {
    const payload = { ...form.value, interests: '' }
    const res = await axios.patch(`${API_URL}/accounts/profile/${profileId}/`, payload, {
      headers: {
        Authorization: `Bearer ${userStore.token}`
      }
    })
    userStore.userProfile = res.data
    step.value = 2
  } catch (err) {
    console.error('기본 정보 저장 실패:', err.response?.data || err.message)
    alert('기본 정보 저장에 실패했습니다.')
  }
}

// Step1 건너뛰기
const skipToStep2 = () => {
  step.value = 2
}

// Step2 관심사 저장
const submitFinal = async () => {
  const profileId = userStore.userProfile?.id
  if (!profileId) {
    alert('프로필 ID가 없습니다.')
    return
  }

  const interestText = selectedInterests.value.join(', ')

  try {
    const res = await axios.patch(`${API_URL}/accounts/profile/${profileId}/`, {
      interests: interestText
    }, {
      headers: {
        Authorization: `Bearer ${userStore.token}`
      }
    })

    userStore.userProfile = res.data
    alert('프로필 정보가 저장되었습니다.')
    router.push({ name: 'main' })
  } catch (err) {
    console.error('관심사 저장 실패:', err.response?.data || err.message)
    alert('관심사 저장 실패')
  }
}

// Step2 건너뛰기
const finishWithoutInterests = () => {
  router.push({ name: 'main' })
}
</script>

<style scoped>
.profile-form {
  max-width: 500px;
  margin: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
input, select, button {
  padding: 10px;
  font-size: 1rem;
}
button {
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
}
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-bottom: 12px;
}
</style>