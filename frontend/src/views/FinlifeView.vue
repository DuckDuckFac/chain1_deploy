<template>
  <div class="container">
    <!-- 나에게 맞는 추천 상품 영역 -->
    <div class="recommend-products">
      <h3>
        <span class="nickname">{{ userInfo?.nickname || '사용자' }}</span>
        <span class="duckbot"> 님을 위한 챗봇 AI 덕덕이의 추천 ✨</span>
      </h3>

      <div v-if="isLoadingRecommendation">
        <p>⏳ 추천 상품을 불러오고 있어요. 잠시만 기다려주세요...</p>
      </div>

      <div v-if="showLoginButton">
        <button class="login-button" @click="goToLogin">🔐 로그인하고 추천받기</button>
      </div>
      <div v-else-if="showProfileButton">
        <button class="goToProfile-button" @click="goToProfile">📋 금융정보 입력하고 추천받기</button>
      </div>

      <div v-else-if="gptRecommendations.length" class="recommend-carousel">
        <button class="nav-btn left" @click="scrollRecommendations('left')">
          <ChevronLeft class="icon" />
        </button>
        <div class="recommend-list" ref="recommendContainer">
          <!-- 카드 -->
          <div v-for="(item, index) in gptRecommendations" :key="index" class="recommend-card">
            <div class="card-top">
              <div class="title-row">
                <div class="product-title">
                  <strong class="bank-name">{{ item.kor_co_nm }}</strong>
                  <span class="product-type">{{ item.fin_prdt_nm }}</span>
                </div>
              </div>
              <div class="icon-buttons">
                <button class="graph-button" @click="toggleProductSelection(item, { target: { checked: !isSelected(item) } })">
                  <BarChart2 :class="['icon', { selected: isSelected(item) }]" />
                </button>
                <button class="like-button" @click="toggleLike(item.fin_prdt_cd)">
                  <Egg :class="{ icon: true, liked: likedProductsSet.has(item.fin_prdt_cd) }" />
                </button>
              </div>
            </div>
            <div class="card-divider"></div>
            <div class="rate-info">
              <p>기본 금리 <strong>{{ item.intr_rate }}%</strong></p>
              <p>최고 금리 <strong>{{ item.intr_rate2 }}%</strong></p>
            </div>
            <div class="card-footer">
              <button class="detail-button" @click="openModal(item)">상세보기</button>
            </div>
          </div>
        </div>
        <button class="nav-btn right" @click="scrollRecommendations('right')">
          <ChevronRight class="icon" />
        </button>
      </div>
    </div>
    

    <!-- 그래프 영역 -->
    <div class="rate-chart-wrapper">
      <div class="rate-chart" v-if="selectedProducts.length">
        <canvas id="productChart"></canvas>
        <div style="margin-top: 10px">
          <div class="selected-tags">
            <div
              v-for="item in selectedProducts"
              :key="item.fin_prdt_cd"
              class="tag"
            >
              {{ item.fin_prdt_nm }}
              <button class="remove-btn" @click="toggleProductSelection(item, { target: { checked: false } })">
                ×
              </button>
            </div>
          </div>

          <div class="clear-all-btn">
            <button @click="clearAllSelections">전체 선택 해제</button>
          </div>
        </div>
      </div>
    </div>

  <!-- 📄 전체 예/적금 리스트 -->
  <div>
      <div class="tab-toggle">
        <button
          :class="{ 'tab-button': true, active: currentTab === 'deposit' }"
          @click="currentTab = 'deposit'"
        >
          예금
        </button>
        <span class="divider">|</span>
        <button
          :class="{ 'tab-button': true, active: currentTab === 'saving' }"
          @click="currentTab = 'saving'"
        >
          적금
        </button>
    </div>
      <div class="sort-filter-row">
        <div class="custom-select-group">
          <!-- <label for="sortSelect">정렬 기준</label> -->
          <select id="sortSelect" v-model="sortKey">
            <option value="">기본순 (선택 안 함)</option>
            <option value="intr_rate2">최고 금리순</option>
            <option value="intr_rate">기본 금리순</option>
          </select>
        </div>
        <div class="custom-select-group">
          <!-- <label for="bankFilter">은행</label> -->
          <select id="bankFilter" v-model="filteredBank">
            <option value="">전체</option>
            <option v-for="bank in bankOptions" :key="bank" :value="bank">{{ bank }}</option>
          </select>
        </div>
      </div>
    <div v-if="currentTab === 'deposit' || currentTab === 'saving'">
      <table class="product-table">
        <thead>
          <tr>
            <th></th> <!-- 좋아요 -->
            <th>은행</th>
            <th>상품명</th>
            <th>기본 금리</th>
            <th>최고 금리</th> 
            <th></th> <!-- 상세보기 -->
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in paginatedProducts" :key="product.fin_prdt_cd">
            <!-- 좋아요, 그래프 -->
            <td>
              <div class="icon-pair">
                <button class="graph-button" @click="toggleProductSelection(product, { target: { checked: !isSelected(product) } })">
                  <BarChart2 :class="{ icon: true, selected: isSelected(product) }" />
                </button>
                <button class="like-button" @click="toggleLike(product.fin_prdt_cd)">
                  <Egg :class="{ icon: true, liked: likedProductsSet.has(product.fin_prdt_cd) }" />
                </button>
              </div>
            </td>

            <!-- 은행명 -->
            <td>{{ product.kor_co_nm }}</td>

            <!-- 상품명 -->
            <td>{{ product.fin_prdt_nm }}</td>

            <!-- 기본 금리 -->
            <td>{{ product.intr_rate }}%</td>

            <!-- 최고 금리 -->
            <td>{{ product.intr_rate2 }}%</td>

            <!-- 상세보기 -->
            <td>
              <button class="detail-button" @click="openModal(product)">상세보기</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 페이지네이션 그대로 유지 -->
      <div class="pagination">
        <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1">이전</button>
        <span>{{ currentPage }} / {{ totalPages }}</span>
        <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages">다음</button>
      </div>
    </div>
    </div>
  </div>

    <!-- 상세 모달 -->
<div v-if="showModal && selectedProduct" class="modal-overlay" @click.self="closeModal">
  <div class="modal-box">
    <button class="modal-close-button" @click="closeModal">✖</button>
    <h3>{{ selectedProduct.kor_co_nm }} - {{ selectedProduct.fin_prdt_nm }}</h3>

    <div class="recommend-reason">
      <strong>🤖 덕덕이의 추천 이유:</strong><br />
      {{ gptRecommendationReason }}
    </div>
    <!-- 📈 금리 그래프 -->
    <BasicBarChart :intrRate="selectedProduct.intr_rate" :intrRate2="selectedProduct.intr_rate2" />
    <!-- 📊 핵심 정보 표로 구성 -->

    <table class="product-info-table">
           <tbody>
      <tr>
        <th>가입 방법</th>
        <td>{{ selectedProduct.join_way || '-' }}</td>
      </tr>
      <tr>
        <th>가입 대상</th>
        <td>{{ selectedProduct.join_member || '-' }}</td>
      </tr>
      <tr>
        <th>우대 조건</th>
        <td>{{ selectedProduct.spcl_cnd || '-' }}</td>
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
        <th>공시 시작일</th>
        <td>{{ formatDate(selectedProduct.dcls_strt_day) }}</td>
      </tr>
      <tr>
        <th>공시 제출일</th>
        <td>{{ formatDate(selectedProduct.fin_co_subm_day) }}</td>
      </tr>
      </tbody>
    </table>

    <!-- 📌 긴 내용은 아래로 분리 -->
    <div class="long-info-block" v-if="selectedProduct.mtrt_int">
      <h4>📌 만기 후 이자율</h4>
      <p>{{ selectedProduct.mtrt_int }}</p>
    </div>

    <div class="long-info-block" v-if="selectedProduct.etc_note">
      <h4>📌 기타</h4>
      <p>{{ selectedProduct.etc_note }}</p>
    </div>


  </div>
</div>


    <!-- ✅ 토스트 메시지 표시 -->
<div v-if="showToast" class="toast">
  {{ toastMessage }}
</div>

</template>



<script setup>
import { ref, onMounted, computed,nextTick } from 'vue'
import axios from '@/stores/axios.js'
import BasicBarChart from '@/components/BasicBarChart.vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Chart, registerables } from 'chart.js'
import { ChevronLeft, ChevronRight, Heart, BarChart2,Egg } from 'lucide-vue-next'

Chart.register(...registerables)

const { userInfo } = useUserStore()
const router = useRouter()
const currentTab = ref('deposit')
const products = ref({ deposit: [], saving: [] })
const likedProducts = ref(new Set())//전체객체
const likedProductsSet = ref(new Set()) // fin_prdt_cd만 모은 Set
const isLikeLoaded = ref(false)
const itemsPerPage = 10
const currentPage = ref(1)
const sortKey = ref('')
const gptRecommendations = ref([])
const loginRequired = ref(false)
const needProfile = ref(false)
const selectedProduct = ref(null)
const showModal = ref(false)
const isLoadingRecommendation = ref(false)
const filteredBank = ref('')
const toastMessage = ref('')
const showToast = ref(false)
const gptRecommendationReason = ref('')
const showLoginButton = computed(() => loginRequired.value && !needProfile.value)
const showProfileButton = computed(() => !loginRequired.value && needProfile.value)
const isLoggedIn = computed(() => !!userInfo?.id)  // 로그인 여부
const recommendContainer = ref(null)
const selectedProducts = ref([])
let chart = null

const scrollRecommendations = (direction) => {
  const container = recommendContainer.value
  const scrollAmount = 320  // 카드 하나 너비 + 여백


  if (container) {
    container.scrollBy({
      left: direction === 'left' ? -scrollAmount : scrollAmount,
      behavior: 'smooth',
    })
  }
}

watch(selectedProducts, async () => {
  await nextTick()
  renderChart()
}, { deep: true })

watch(selectedProducts, () => {
  renderChart()
}, { deep: true })

const toggleProductSelection = (item, event) => {
  if (event.target.checked) {
    selectedProducts.value.push(item)
  } else {
    selectedProducts.value = selectedProducts.value.filter(
      p => p.fin_prdt_cd !== item.fin_prdt_cd
    )
  }
}

const isSelected = (item) => {
  return selectedProducts.value.some(p => p.fin_prdt_cd === item.fin_prdt_cd)
}

const clearAllSelections = () => {
  selectedProducts.value = []
}

const renderChart = () => {
  const ctx = document.getElementById('productChart')?.getContext('2d')
  if (!ctx) return
  if (chart) chart.destroy()

  const labels = selectedProducts.value.map(p => p.fin_prdt_nm)
  const baseRates = selectedProducts.value.map(p => p.intr_rate)
  const maxRates = selectedProducts.value.map(p => p.intr_rate2)

  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels.length === 1 ? [...labels, ''] : labels,
      datasets: [
        {
          label: '기본 금리',
          data: labels.length === 1 ? [...baseRates, 0] : baseRates,
          backgroundColor: 'rgba(205, 206, 210, 0.8)'
        },
        {
          label: '최고 금리',
          data: labels.length === 1 ? [...maxRates, 0] : maxRates,
          backgroundColor: 'rgba(0, 123, 255, 0.8)'
        }
      ]
    },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 1000,
          easing: 'easeOutQuart'
        },
        plugins: {
          legend: {
          position: 'top',
          labels: {
          font: {
          size: 14 // ✅ 범례 폰트 크기
        }
      }
    },
    title: {
      display: true,
      text: '선택한 상품 금리 비교 그래프',
      color: '#000',
      font: {
        size: 25 // ✅ 제목 폰트 크기
      }
    }
  },
  scales: {
    x: {
      ticks: {
        color: '#000',
        font: {
          size: 15 // ✅ X축 폰트 크기
        },
        callback: function (val, index) {
          return labels[index] === '' ? '' : this.getLabelForValue(val)
        }
      },
      grid: {
        color: '#eee'
      }
    },
    y: {
      ticks: {
        color: '#000',
        font: {
          size: 13 // ✅ Y축 폰트 크기
        }
      },
      grid: {
        color: '#eee'
      }
    }
  }}}
)}
watch(selectedProducts, async () => {
  await nextTick()
  renderChart()
}, { deep: true })

const showToastMessage = (message) => {


  toastMessage.value = message
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 2000)  // 2초 뒤 사라짐
}

const bankOptions = computed(() => {
  const list = currentTab.value === 'deposit' ? products.value.deposit : products.value.saving
  const banks = list.map(item => item.kor_co_nm)
  return [...new Set(banks)].sort()
})


const openModal = async (product) => {
  const fin_prdt_cd = product.fin_prdt_cd
  let product_type = null

  const isDeposit = products.value.deposit.some(p => p.fin_prdt_cd === fin_prdt_cd)
  if (isDeposit) {
    product_type = 'deposit'
  } else {
    const isSaving = products.value.saving.some(p => p.fin_prdt_cd === fin_prdt_cd)
    if (isSaving) {
      product_type = 'saving'
    }
  }

  if (!product_type) {
    alert('상품 타입을 확인할 수 없습니다.')
    return
  }

  try {
    const res = await axios.get(`/finlife/detail/${fin_prdt_cd}/`, {
      params: { product_type }
    })
    selectedProduct.value = res.data
    showModal.value = true
  } catch (err) {
    console.error('상세보기 요청 실패:', err)
    alert('상세 정보를 불러오지 못했습니다.')
  }
}


const closeModal = () => {
  showModal.value = false
  selectedProduct.value = null
}

const paginatedProducts = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return sortedProducts.value.slice(start, end)
})
const totalPages = computed(() => {
  const list = currentTab.value === 'deposit' ? products.value.deposit : products.value.saving
  return Math.ceil(list.length / itemsPerPage)
})

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) currentPage.value = page
}

import { watch } from 'vue'

const profileInfo = ref({})  // 🔥 새로 추가: 금융정보 저장용
const profileData = computed(() => profileInfo.value.results?.[0] || {})


const fetchGptRecommendation = async () => {
  isLoadingRecommendation.value = true
  const cacheKey = 'gptRecommendationCache'
  const cached = sessionStorage.getItem(cacheKey)

  if (cached) {
    try {
      const parsed = JSON.parse(cached)
      gptRecommendations.value = parsed.추천상품 || []
      gptRecommendationReason.value = parsed.추천이유 || ''
      if (parsed.토스트) showToastMessage(parsed.토스트)
      isLoadingRecommendation.value = false
      return
    } catch {
      sessionStorage.removeItem(cacheKey)
    }
  }

  try {
    const gptRes = await axios.post('/chat/', { message: '추천 상품 요청' })
    const meta = gptRes.data

    if (meta.login_required) {
      loginRequired.value = true
      return
    }
    if (meta.need_profile) {
      needProfile.value = true
      return
    }

    let raw = meta.text.trim()
    if (raw.startsWith('```')) {
      raw = raw.replace(/^```json\n?|^```\n?/, '')
      raw = raw.replace(/```$/, '')
    }

    const jsonEndIndex = raw.lastIndexOf('}')
    raw = raw.slice(0, jsonEndIndex + 1)
    const parsed = JSON.parse(raw)

    gptRecommendations.value = parsed.추천상품 || []
    gptRecommendationReason.value = parsed.추천이유 || ''

    sessionStorage.setItem(cacheKey, JSON.stringify({
      추천상품: parsed.추천상품,
      추천이유: parsed.추천이유,
      토스트: '🐣 맞춤 추천이 도착했어요!',
    }))

    showToastMessage('🐣 맞춤 추천이 도착했어요!')
  } catch (err) {
    console.warn('GPT 추천 상품 불러오기 실패:', err)
  } finally {
    isLoadingRecommendation.value = false
  }
}


watch(
  () => userInfo,
  async (info) => {
    // ✅ 항상 전체 상품은 불러오기
    try {
      const res = await axios.get('/finlife/')
      const raw = res.data
      raw.saving = Array.from(new Map(raw.saving.map(item => [item.fin_prdt_cd, item])).values())
      products.value = raw
    } catch (err) {
      console.error('상품 불러오기 실패:', err)
    }

    // ✅ 비로그인 상태면 로그인 버튼 조건 설정하고 종료
    if (!info || Object.keys(info).length === 0) {
      loginRequired.value = true    // ✅ 이거 추가!
      needProfile.value = false     // ✅ 혹시 이전 값이 남아있을 수도 있어서 초기화
      return
    }

    // ✅ 좋아요 목록 불러오기 (로그인 사용자만)
    try {
      const likeRes = await axios.get('/finlife/like/mine/')
      const likedList = [...likeRes.data.deposit, ...likeRes.data.saving]
      likedProducts.value = likedList
      likedProductsSet.value = new Set(likedList.map(p => String(p.fin_prdt_cd).trim()))
      isLikeLoaded.value = true
    } catch (err) {
      console.warn('좋아요 목록 실패 (비로그인일 수 있음)', err)
    }

    // ✅ 금융정보 확인
    try {
      const profileRes = await axios.get('/accounts/profile/')
      profileInfo.value = profileRes.data
    } catch (err) {
      console.warn('⚠️ 금융정보 로딩 실패:', err)
    }

    // ✅ GPT 추천 조건 분기
    const hasProfile =
      profileData.value.asset &&
      profileData.value.income &&
      profileData.value.job

    if (!hasProfile) {
      loginRequired.value = false
      needProfile.value = true
      return
    }

    loginRequired.value = false
    needProfile.value = false

    // ✅ GPT 추천 요청
    await fetchGptRecommendation()
  },
  { immediate: true }
)


const goToLogin = () => {
  router.push({ name: 'login' })
}
const goToProfile = () => {
  if (userInfo?.nickname) {
    router.push({ name: 'user-profile', params: { nickname: userInfo.nickname } })
  } else {
    alert('사용자 정보를 불러올 수 없습니다. 다시 로그인해주세요.')
  }
}

const toggleLike = async (productCode, productType) => {
  try {
    if (!isLoggedIn.value) {
      showToastMessage('로그인 후 둥지에 담아보세요!')
      return
    }

    if (!productType) {
      const isDeposit = products.value.deposit.some(p => p.fin_prdt_cd === productCode)
      productType = isDeposit ? 'deposit' : 'saving'
    }

    const res = await axios.post('/finlife/like/', {
      product_type: productType,
      fin_prdt_cd: productCode,
    })

    const status = res.data.message

    if (status === '좋아요 취소!') {
      likedProductsSet.value.delete(productCode)
      showToastMessage('둥지에서 빠져나갔어요! 🐥')
    } else if (status === '좋아요 완료!') {
      likedProductsSet.value.add(productCode)
      showToastMessage('둥지에 담겼어요! 🐣')
    }

  } catch (err) {
    console.error('좋아요 실패', err)
    showToastMessage('😢둥지에 안들어가요..잠시 후 다시 시도해주세요!')
  }
}


const sortedProducts = computed(() => {
  let list = currentTab.value === 'deposit' ? products.value.deposit : products.value.saving

  if (filteredBank.value) {
    list = list.filter(item => item.kor_co_nm === filteredBank.value)
  }

  if (sortKey.value === 'intr_rate2' || sortKey.value === 'intr_rate') {
    list = [...list].sort((a, b) => (b[sortKey.value] || 0) - (a[sortKey.value] || 0))
  }

  return list
})

const formatDate = (yyyymmdd) => {
  if (!yyyymmdd || yyyymmdd.length < 8) return '-'
  return `${yyyymmdd.slice(0, 4)}-${yyyymmdd.slice(4, 6)}-${yyyymmdd.slice(6, 8)}`
}


</script>

<style scoped>

.container {
  max-width: 1660px;
  margin: 0 auto;
  padding: 0 48px;;
  box-sizing: border-box;
}
/* 기본 텍스트 및 레이아웃 */


body {
  font-family: 'Pretendard', sans-serif;
  background-color: #fff;
  color: #222;
  margin: 0;
  padding: 0;
}

.nickname {
  color: #007bff;
  font-weight: 700;
  font-size: 1.5rem;
}

.duckbot {
  color: #CDCED2;
  font-weight: 700;
  font-size: 1rem;
}

.recommend-products h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #555;
}



/* 추천 카드 영역 */
.recommend-list {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding: 20px 32px 30px 37px;
  scrollbar-width: none; 
}

.recommend-card {
  flex: 0 0 auto;
  width: 240px;
  border-radius: 16px;
  padding: 20px;
  background: white;
  border: 1px solid #e1e1e198;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease-in-out;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 180px;
  position: relative;
}

.recommend-card:hover {
  transform: scale(1.03);
  border-color: #007bff;
  box-shadow: 0 6px 16px rgba(0, 82, 214, 0.2);
}

.title-row {
  display: flex;
  flex-direction: column;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.bank-name {
  font-weight: 700;
  font-size: 1rem;
  color: #222;
}

.product-type {
  font-size: 0.85rem;
  color: #666;
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
  max-width: 150px;
}

.card-divider {
  border-top: 1px solid #eee;
  margin: 12px 0;
}

.rate-info p {
  font-size: 0.9rem;
  margin: 4px 0;
  color: #333;
}

.rate-info strong {
  font-weight: 500;
  color: #000;
}

.card-footer {
  margin-top: auto;
  text-align: right;
}

.detail-button {
  background: none;
  border: none;
  color: #bbb;
  font-size: 0.8rem;
  cursor: pointer;
}

.product-title {
  display: flex;
  flex-direction: column;
}

/* 아이콘 버튼 */

.icon-pair {
  display: flex;
  gap: 8px;              /* 아이콘 간 간격 */
  align-items: center;   /* 수직 정렬 */
  justify-content: center;
}

.icon-buttons {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  gap: 8px;
}

.graph-button,
.like-button {
  background: none;
  border: none;
  outline: none;
  padding: 0;
  cursor: pointer;
}

.icon {
  width: 20px;
  height: 20px;
  stroke: #c7c7c7;
  stroke-width: 1.3;
  fill: none;
}

.icon.selected {
  stroke: #007bff; /* ✅ 선택되면 파란색 */
}

.icon.liked {
  stroke: #ffcc00;
  fill: #ffcc00;
}

/* 캐러셀 화살표 버튼 */
.recommend-carousel {
  position: relative;
}

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: white;
  border: 1px solid rgba(0, 0, 0, 0);
  border-radius: 50%;
  padding: 6px;
  cursor: pointer;
  z-index: 10;

}

.nav-btn.left {
  left: 0;
}

.nav-btn.right {
  right: 0;
}

/* 그래프 */
.rate-chart {
  background-color: #ffffff;
  border-radius: 16px;
  padding: 24px;
  margin: 40px auto;
  max-width: 720px;          
  min-height: 480px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

canvas#productChart {
  width: 100% !important;
  max-width: 680px;          
  height: 480px !important;  
}
.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.tag {
  display: flex;
  align-items: center;
  background-color: #f1f4f7;
  color: #333;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.remove-btn {
  background: none;
  border: none;
  color: #666;
  margin-left: 6px;
  font-size: 1rem;
  cursor: pointer;
}

.remove-btn:hover {
  color: #e00;
}

.clear-all-btn {
  text-align: right;
  margin-top: 8px;
}

.clear-all-btn button {
  background: none;
  border: none;
  color: #d33; /* 약간 빨간색 */
  font-size: 0.85rem;
  cursor: pointer;
  padding: 4px 8px;
  transition: color 0.2s ease;
}

.clear-all-btn button:hover {
  color: #a00; /* hover 시 더 진하게 */
  text-decoration: underline;
}
/* 탭 버튼 */
.tab-buttons {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 40px;
}

.tab-buttons button {
  background: #f3f3f3;
  border: none;
  padding: 8px 20px;
  font-size: 0.9rem;
  border-radius: 20px;
  cursor: pointer;
}

.tab-buttons button.active {
  background: #007bff;
  color: white;
  font-weight: bold;
}

/* 정렬 및 필터 */
.sort-filter-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 16px;
  margin: 12px 0;
}

.sort-filter-row label,
.sort-filter-row select {
  font-size: 0.85rem;
  color: #555;
}

/* 예/적금 테이블 */
.deposit-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
}

.deposit-table th,
.deposit-table td {
  padding: 12px 16px;
  font-size: 0.85rem;
  text-align: left;
}

.deposit-table th {
  background-color: #f8f8f8;
  color: #999;
  border-bottom: 1px solid #ddd;
}

.deposit-table tr:nth-child(even) {
  background-color: #fafafa;
}

.deposit-table tr:nth-child(odd) {
  background-color: #fff;
}

.deposit-table td {
  border-bottom: 1px solid #eee;
}

/* 반응형 */
@media (max-width: 768px) {
  .container {
    padding: 0 16px;
  }
  .recommend-list {
    gap: 12px;
  }
  .recommend-card {
    width: 180px;
  }

}

/* 모달 배경 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4); /* 반투명 배경 */
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* 모달 상자 */
.modal-box {
  background: #ffffff;
  padding: 24px;
  border-radius: 16px;
  width: 90%;
  max-width: 560px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  font-family: 'Pretendard', sans-serif;
  animation: popUp 0.3s ease-out;
  color: #333;
  font-size: 0.92rem;
  position: relative;
}

/* 모달 제목 */
.modal-box h3 {
  font-size: 1.2rem;
  font-weight: bold;
  color: #222;
  margin-bottom: 1rem;
  line-height: 1.4;
}

/* 덕덕이 추천 이유 박스 */
.modal-box .recommend-reason {
  background-color: #f5faff;
  border-left: 4px solid #007bff;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  margin-bottom: 16px;
  color: #444;
  line-height: 1.5;
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
  margin-top: 14px;
}
.long-info-block h4 {
  font-size: 0.92rem;
  margin-bottom: 6px;
  color: #333;
}
.long-info-block p {
  white-space: pre-line;
  font-size: 0.88rem;
  color: #555;
  line-height: 1.5;
}


/* 닫기 버튼 */
.modal-close-button {
  position: absolute;
  top: 12px;
  right: 12px;
  background: transparent;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
}

/* 데이터 항목 */
.modal-box p {
  margin: 6px 0;
  font-size: 0.9rem;
  color: #444;
  line-height: 1.5;
}

.modal-box p strong {
  color: #007bff;
  font-weight: 600;
}

/* 애니메이션 */
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

/* 💰 예금/적금 상품 테이블 스타일 추가 */
.product-table {
  width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
  margin-top: 12px;
  font-size: 0.9rem;
}
.product-table th,
.product-table td {
  padding: 14px 16px;
  text-align: left;
  border: none;               /* 세로선 제거 */
  border-bottom: 1px solid #eee; /* 가로선만 */
}
.product-table th {
  background-color: #f4f6f8;
  color: #999;
  font-weight: 600;
  font-size: 0.85rem;
}
.product-table tr:nth-child(odd) {
  background-color: #fff;
}

.product-table tr:nth-child(even) {
  background-color: #f4f6f8;
}

/* 버튼 세트 가운데 정렬 */
.product-table td .icon-pair {
  justify-content: flex-start;
}


/* 탭 버튼 */
.tab-toggle {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin: 24px 0;
}

.tab-button {
  background: none;
  border: none;
  font-size: 1.2rem;
  font-weight: 500;
  color: #888;
  cursor: pointer;
  padding: 4px 12px;
  transition: color 0.2s ease;
}

.tab-button.active {
  color: #111; /* 검정 강조 */
  font-weight: 700;
  border-bottom: 2px solid #111; /* 클릭된 느낌 강조 */
}

.tab-button:hover {
  color: #000;
}

.divider {
  color: #ccc;
  font-size: 1.2rem;
  pointer-events: none;
  user-select: none;
}

/* 정렬 버튼 */
.sort-filter-row {
  display: flex;
  justify-content: flex-end;
  gap: 20px;
  margin: 12px 0;
}

.custom-select-group {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #888;
}

.custom-select-group select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background: url("data:image/svg+xml;charset=UTF-8,%3Csvg width='10' height='6' viewBox='0 0 10 6' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%23bbb' stroke-width='1.5' fill='none' fill-rule='evenodd'/%3E%3C/svg%3E") no-repeat right 8px center;
  background-color: transparent;
  border: none;
  padding: 4px 28px 4px 8px;
  font-size: 0.85rem;
  color: #bbb;
  cursor: pointer;
}

.custom-select-group select option {
  color: #555; /* 팝업된 리스트의 글씨색 */
  background: white;
  border: none;
}

.toast {
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
  animation: fadeInOut 2s ease forwards;
  z-index: 9999;
}

@keyframes fadeInOut {
  0%   { opacity: 0; transform: translateX(-50%) translateY(20px); }
  10%  { opacity: 1; transform: translateX(-50%) translateY(0); }
  90%  { opacity: 1; }
  100% { opacity: 0; transform: translateX(-50%) translateY(20px); }
}

/* 로그인 버튼튼 */
.login-button {
  background: #e0f0ff;
  color: #007bff;
  font-weight: 600;
  padding: 10px 20px;
  font-size: 0.95rem;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.2);
  transition: background 0.3s ease, box-shadow 0.3s ease;
}

.login-button:hover {
  background: #d4eaff;
  box-shadow: 0 4px 10px rgba(0, 123, 255, 0.2);
}

/* ✅ 페이지네이션 커스텀 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin: 24px 0;
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
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 2px 6px rgba(0, 123, 255, 0.1);
}

.pagination button:hover {
  background-color: #d0e8ff;
}

.pagination button:disabled {
  background-color: #f0f4f7;
  color: #aaa;
  cursor: not-allowed;
  box-shadow: none;
}

.pagination span {
  font-size: 0.9rem;
  color: #555;
  font-weight: 500;
}

/* 금융상품 추천 버튼튼 */

.goToProfile-button {
  display: block;
  margin: 16px 0 0 0;
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

.goToProfile-button:hover {
  background: #d4eaff;
}

</style>

