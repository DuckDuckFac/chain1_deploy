<template>
  <div class="liked-products">
    <h3 class="section-title">{{ title }}</h3>

    <div v-if="likedProducts && likedProducts.length" class="carousel-wrapper">
      <div class="carousel-container">
        <button class="nav-btn left" @click="scrollLeft">
          <ChevronLeft class="nav-icon" />
        </button>

        <div class="carousel" ref="carousel">
          <div
            v-for="(product, index) in likedProducts"
            :key="index"
            class="recommend-card"
          >
            <div class="card-top">
              <div class="title-row">
                <strong class="bank-name">{{ product.kor_co_nm }}</strong>
                <span class="product-type">{{ product.fin_prdt_nm }}</span>
              </div>
              <div class="icon-buttons">
                <button class="like-button" @click="toggleLike(product.fin_prdt_cd)">
                  <Egg class="icon liked" />
                </button>
              </div>
            </div>

            <div class="card-divider"></div>

            <div class="rate-info">
              <p>기본 금리 <strong>{{ product.intr_rate }}%</strong></p>
              <div class="rate-bottom-row">
                <p>최고 금리 <strong>{{ product.intr_rate2 }}%</strong></p>
                <button class="detail-button" @click="$emit('show-detail', product)">상세보기</button>
              </div>
            </div>
          </div>
        </div>

        <button class="nav-btn right" @click="scrollRight">
          <ChevronRight class="nav-icon" />
        </button>
      </div>
    </div>

    <p v-else>좋아요한 상품이 없습니다.</p>
  </div>

  <div v-if="showToast" class="toast">
  {{ toastMessage }}
</div>
</template>





<script setup>
import { ref } from 'vue'
import axios from '@/stores/axios.js'
import { Egg } from 'lucide-vue-next'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'


const emit = defineEmits(['unliked', 'show-detail'])
// 토스트
const toastMessage = ref('')  // 토스트 메시지 내용
const showToast = ref(false)
const showToastMessage = (message) => {
  toastMessage.value = message
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 2000) 
}

defineProps({
  likedProducts: {
    type: Array,
    required: true
  },
  title: {
    type: String,
    default: '🥚 MY 상품'
  }
})

const carousel = ref(null)

const scrollLeft = () => {
  carousel.value?.scrollBy({ left: -260, behavior: 'smooth' }) // 카드 2개 기준
}
const scrollRight = () => {
  carousel.value?.scrollBy({ left: 260, behavior: 'smooth' })
}

const toggleLike = async (productCode, productType = null) => {
  try {
    const type = productType || getProductType(productCode)
    const res = await axios.post('/finlife/like/', {
      product_type: type,
      fin_prdt_cd: productCode,
    })
    const status = res.data.message
    if (status === '좋아요 취소!') {
      emit('unliked', productCode)
      showToastMessage('둥지에서 빠져나갔어요! 🐥')
    } else if (status === '좋아요 완료!') {
      alert('좋아요가 다시 등록되었어요 🐣')
    }
  } catch (err) {
    console.error('좋아요 토글 실패', err.response?.data || err)
    showToastMessage('😢둥지에 안들어가요..잠시 후 다시 시도해주세요!')
  }
}

const getProductType = (code) => {
  return code.startsWith('HK') ? 'saving' : 'deposit'
}



</script>

<style scoped>
.liked-products {
  width: 100%;
  margin-inline: auto;
  max-width: 100%;
  margin-top: 2rem;
  overflow-x: hidden;
  box-sizing: border-box;
}

.section-title {
  margin-bottom: 1rem; /* 👈 원하는 만큼 조절 가능 (1rem = 약 16px) */
  font-size: 1.1rem;
}

.carousel-wrapper {
  width: 100%;
  overflow-x: auto;
  box-sizing: border-box;
  
}

.carousel-container {
  display: flex; /* 기존 block에서 변경 */
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  max-width: 100%;
  overflow: hidden;
}

.carousel {
  display: flex;
  overflow-x: auto;
  scroll-behavior: smooth;
  gap: 20px;
  flex: 1 1 auto;
  min-width: 0;
  max-width: 100%;
  scrollbar-width: none;
}

.carousel::-webkit-scrollbar {
  display: none;
}

.nav-btn {
  all: unset; /* 모든 기본 스타일 제거 */
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.nav-icon {
  width: 20px;
  height: 20px;
  stroke: #333;
}


.recommend-card {
  flex: 0 0 auto;
  width: 240px;
  max-width: 100%;
  flex-shrink: 0;
  box-sizing: border-box;
  border-radius: 16px;
  padding: 20px;
  background: white;
  border: 1px solid #e1e1e198;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  min-height: 140px;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.title-row {
  display: flex;
  flex-direction: column;
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

.detail-button {
  background: none;
  border: none;
  color: #bbb;
  font-size: 0.8rem;
  cursor: pointer;
}

.icon-buttons {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  gap: 8px;
}

.like-button {
  background: none;
  border: none;
  cursor: pointer;
}

.icon {
  width: 20px;
  height: 20px;
  stroke: #ffcc00;
  fill: #ffcc00;
}

.rate-bottom-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
</style>
