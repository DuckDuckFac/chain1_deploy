<template>
  <div class="profile-form">
    <div v-if="step === 1" class="step-section">
      <h2 class="form-title">기본 정보 입력</h2>
      <form @submit.prevent="goToStep2" class="form-section">
        <div class="row-two">
          <div class="input-group">
            <label>생년월일</label>
            <input type="date" v-model="form.birth_date" required />
          </div>
          <div class="input-group">
            <label>성별</label>
            <select v-model="form.gender" required>
              <option disabled value="">선택</option>
              <option value="M">남성</option>
              <option value="F">여성</option>
              <option value="N">선택 안함</option>
            </select>
          </div>
        </div>

        <div class="input-group">
          <label>자산 규모</label>
          <select v-model="form.asset" required>
            <option disabled value="">선택</option>
            <option value="1">1000만원 이하</option>
            <option value="2">3000만원 이하</option>
            <option value="3">5000만원 이하</option>
            <option value="4">1억 이하</option>
            <option value="5">1억 초과</option>
          </select>
        </div>

        <div class="input-group">
          <label>연간 소득</label>
          <select v-model="form.income" required>
            <option disabled value="">선택</option>
            <option value="none">없음</option>
            <option value="under30">3000만원 이하</option>
            <option value="under50">5000만원 이하</option>
            <option value="over50">5000만원 초과</option>
          </select>
        </div>

        <div class="input-group">
          <label>직업</label>
          <select v-model="form.job" required>
            <option disabled value="">선택</option>
            <option value="student">학생</option>
            <option value="employee">직장인</option>
            <option value="self">자영업자</option>
            <option value="unemployed">무직</option>
          </select>
        </div>

        <div class="btn-group">
          <button type="submit" class="btn-primary">다음</button>
          <button type="button" @click="skipToStep2" class="btn-secondary">건너뛰기</button>
        </div>
      </form>
    </div>
    <!-- Step 2 -->
      <div v-else class="step-section">
        <h2 class="form-title">관심사 입력</h2>
        <form @submit.prevent="submitFinal" class="form-section">
          <div class="interest-box">
            <div
              v-for="interest in allInterests"
              :key="interest"
              class="image-button"
              :class="{ selected: selectedInterests.includes(interest) }"
              @click="toggleInterest(interest)"
            >
              <img :src="`/interest/${interestImageMap[interest]}`" :alt="interest" />
              <p class="label">{{ interest }}</p>
            </div>
          </div>
          <div class="btn-group">
            <button type="submit" class="btn-primary">제출 완료</button>
            <button type="button" @click="finishWithoutInterests" class="btn-secondary">건너뛰기</button>
          </div>
        </form>
      </div>
  </div>
  
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import Swal from 'sweetalert2'

const step = ref(1)
const userStore = useUserStore()
const router = useRouter()
const API_URL = 'http://127.0.0.1:8000'

const form = ref({
  birth_date: '',
  gender: '',
  asset: '',
  income: '',
  job: '',
  interests: ''
})

const selectedInterests = ref([])
const allInterests = [
  '예금/적금', '신용대출', '주택청약', '전세자금 대출',
  '보험 (건강/자동차)', '신용카드 혜택', '주식 투자',
  'ETF / 리츠', '펀드', '연금/노후 준비',
  '비상금 마련', '사회초년생 금융'
]
const interestImageMap = {
  '사회초년생 금융': 'baby_duck.png',
  '신용카드 혜택': 'creditbenefit_duck.png',
  '신용대출': 'creditloan_duck.png',
  '예금/적금': 'deposit_duck.png',
  '전세자금 대출': 'depositloan_duck.png',
  '비상금 마련': 'emergency_duck.png',
  'ETF / 리츠': 'ETF_duck.png',
  '펀드': 'fund_duck.png',
  '주택청약': 'house_duck.png',
  '보험 (건강/자동차)': 'insurance_duck.png',
  '연금/노후 준비': 'old_duck.png',
  '주식 투자': 'stock_duck.png'
}

const toggleInterest = (interest) => {
  const idx = selectedInterests.value.indexOf(interest)
  if (idx === -1) {
    selectedInterests.value.push(interest)
  } else {
    selectedInterests.value.splice(idx, 1)
  }
}

const validate = () => {
  return (
    form.value.birth_date &&
    form.value.gender &&
    form.value.asset &&
    form.value.income &&
    form.value.job
  )
}

onMounted(async () => {
  await userStore.getProfile()
  if (userStore.userProfile) {
    Object.assign(form.value, userStore.userProfile)
    selectedInterests.value = (userStore.userProfile.interests || '').split(', ').filter(Boolean)
  }
})

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
    const payload = {
      ...userStore.userProfile,
      birth_date: form.value.birth_date,
      gender: form.value.gender,
      asset: form.value.asset,
      income: form.value.income,
      job: form.value.job,
      interests: '',
      image: null
    }

    const res = await axios.patch(`${API_URL}/accounts/profile/${profileId}/`, payload, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${userStore.token}`
      }
    })

    userStore.userProfile = res.data
    step.value = 2
  } catch (err) {
    console.error('1단계 저장 실패:', err.response?.data || err.message)
    alert('기본 정보 저장 실패')
  }
}

const skipToStep2 = () => {
  step.value = 2
}

const submitFinal = async () => {
  const profileId = userStore.userProfile?.id
  if (!profileId) {
    Swal.fire('프로필 ID가 없습니다.', '', 'error') // 실패 시 Swal 사용
    return
  }

  try {
    const payload = {
      interests: selectedInterests.value.join(', ')
    }

    const res = await axios.patch(`${API_URL}/accounts/profile/${profileId}/`, payload, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${userStore.token}`
      }
    })

    userStore.userProfile = res.data
    // 성공 시 Swal 사용
    Swal.fire('프로필 저장 완료', '프로필 정보가 저장되었습니다.', 'success')
    router.push({ name: 'user-profile', params: { nickname: userStore.userInfo.nickname } })
  } catch (err) {
    console.error('관심사 저장 실패:', err.response?.data || err.message)
    // 실패 시 Swal 사용
    Swal.fire('오류 발생', '관심사 저장 실패', 'error')
  }
}

const finishWithoutInterests = () => {
  swal('관심사를 건너뛰고 프로필을 저장합니다.', '', 'warning')
  router.push({ name: 'user-profile', params: { nickname: userStore.userInfo.nickname } })
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

.row-two {
  display: flex;
  gap: 1rem;
}

.row-two .input-group {
  flex: 1;
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

.input-group input,
.input-group select {
  padding: 12px 14px;
  font-size: 0.95rem;
  border: 1px solid #ddd;
  border-radius: 10px;
  background-color: #f8f9fa;
  transition: border-color 0.2s ease;
}

.input-group input:focus,
.input-group select:focus {
  border-color: #007bff;
  background-color: #fff;
  outline: none;
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

.interest-box {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  justify-content: center;
}

.image-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  border: 2px solid transparent;
  padding: 16px;
  border-radius: 12px;
  transition: border-color 0.3s ease, transform 0.2s ease;
  background-color: #fdfdfd;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

.image-button:hover {
  transform: scale(1.03);
}

.image-button.selected {
  border-color: #007bff;
  background-color: #e7f1ff;
  transform: scale(1.05);
}

.image-button img {
  width: 120px;
  height: auto;
  object-fit: contain;
  margin-bottom: 10px;
}

.image-button .label {
  font-size: 1rem;
  font-weight: 500;
  color: #333;
  text-align: center;
}
.image-button:hover {
  transform: scale(1.03);
  box-shadow: 0 4px 10px rgba(0, 123, 255, 0.2);
}

</style>