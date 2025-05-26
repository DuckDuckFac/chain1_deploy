<template>
  <div>
    <!-- 💬 플로팅 챗봇 버튼 -->
    <button class="chatbot-float-btn" @click="open = !open">
      <img src="/chatbot.png" alt="챗봇 열기" class="chatbot-float-icon" />
    </button>


    <!-- 🤖 챗봇 모달 -->
    <div v-show="open" ref="modal" class="chatbot-modal">
      <div class="chatbot-top">
        <img src="/chatbot.png" alt="챗봇 꿍스" class="chatbot-avatar" />
        <h2 class="chatbot-title">금융챗봇 꿍스에게 물어봐!</h2>
        <button class="close-btn" @click="open = false">✖</button>
      </div>

      <div class="chatbot-body" ref="chatBody">
        <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
          <div class="message-text">
            <div v-if="msg.loading" class="loading-bubble">
              <strong>🐤 꿍스:&nbsp; </strong>
              <span class="loading-dots">
                답변 생성 중 <span class="dot dot1">.</span><span class="dot dot2">.</span><span class="dot dot3">.</span>
              </span>
            </div>

            <p v-else class="chat-message-text">
              <strong v-if="msg.role === 'bot'">🐤 꿍스:&nbsp;</strong>
              {{ msg.content }}
            </p>
          </div>

          <!-- 🎯 GPT 추천 결과 -->
          <div v-if="msg.role === 'bot' && msg.recommendations && msg.recommendations.length > 0">
            <button class="toggle-recommend-btn" @click="showRecommendations = !showRecommendations">
              추천 상품 {{ showRecommendations ? '숨기기' : '보기' }}
              <component :is="showRecommendations ? ChevronUp : ChevronDown" class="toggle-icon" />
            </button>
            <transition name="fade">
              <div v-show="showRecommendations" class="card-list">
                <div v-for="(item, i) in msg.recommendations" :key="i" class="product-card">
                  <!-- 기존 카드 구조 그대로 유지 -->
                  <div class="card-header">
                    <p class="bank">{{ item.kor_co_nm }}</p>
                    <Egg
                      @click="toggleLike(item.fin_prdt_cd)"
                      :class="{ icon: true, liked: likedProducts.has(item.fin_prdt_cd), 'egg-clickable': true }"
                    />
                  </div>
                  <p class="title">{{ item.fin_prdt_nm }}</p>
                  <p class="content">📈 기본금리: <span>{{ item.intr_rate }}%</span></p>
                  <p class="content">💰 최고금리: <span>{{ item.intr_rate2 }}%</span></p>
                  <div class="card-footer">
                    <button class="detail-button" @click="openModal(item)">상세보기</button>
                  </div>
                </div>
                <p v-if="msg.reason" class="recommend-reason">📝 {{ msg.reason }}</p>
              </div>
            </transition>
          </div>

        </div>
      </div>

      <div class="chatbot-input">
        <input
          v-model="userInput"
          @keyup.enter="sendMessage"
          placeholder="챗봇에게 질문해보세요..."
        />
        <button @click="sendMessage"><Send class="icon icon-send" /></button>
      </div>

      <!-- 크기 조절 핸들 -->
      <div class="resizer right" @mousedown="initResize($event, 'right')"></div>
      <div class="resizer bottom" @mousedown="initResize($event, 'bottom')"></div>
      <div class="resizer corner" @mousedown="initResize($event, 'corner')"></div>
      <div class="resizer top" @mousedown="initResize($event, 'top')"></div>
      <div class="resizer left" @mousedown="initResize($event, 'left')"></div>
    </div>

    <!-- 💡 chatbot-modal 바깥에 위치해야 함 -->
    <div v-if="showProductModal && selectedProduct" class="product-modal-overlay" @click.self="closeModal">
      <div class="product-modal-box">
        <button class="product-modal-close" @click="closeModal">✖</button>
        <h3>{{ selectedProduct.kor_co_nm }} - {{ selectedProduct.fin_prdt_nm }}</h3>

        <div v-if="modalReason" class="recommend-reason">
          <strong>🐥 추천 이유:</strong><br />
          {{ modalReason }}
        </div>

        <BasicBarChart :intrRate="selectedProduct.intr_rate" :intrRate2="selectedProduct.intr_rate2" />

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
            <th>만기 후 이자율</th>
            <td>{{ selectedProduct.mtrt_int || '-' }}</td>
          </tr>
          <tr>
            <th>기타</th>
            <td>{{ selectedProduct.etc_note || '-' }}</td>
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
      </div>
    </div>


  </div>
  <div v-if="showToast" class="toast">
  {{ toastMessage }}
  </div>

</template>


<script setup>
import { ref, nextTick, onMounted } from 'vue'
import axios from '@/stores/axios.js'
import { Send,Egg,ChevronDown, ChevronUp  } from 'lucide-vue-next'

const open = ref(false)
const userInput = ref('')
const messages = ref([])
const chatBody = ref(null)
const modal = ref(null)

const selectedProduct = ref(null)
const showProductModal = ref(false)
const modalReason = ref('')
const allProducts = ref({ deposit: [], saving: [] })
const likedProducts = ref(new Set())

const showToast = ref(false)
const toastMessage = ref('')
const showRecommendations = ref(false)


const showToastMessage = (message) => {
  toastMessage.value = message
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 2000)
}


const scrollToBottom = () => {
  nextTick(() => {
    if (chatBody.value) {
      chatBody.value.scrollTop = chatBody.value.scrollHeight
    }
  })
}

const sendMessage = async () => {
  const content = userInput.value.trim()
  if (!content) return

  messages.value.push({ role: 'user', content })
  userInput.value = ''
  scrollToBottom()

const loading = { role: 'bot', loading: true }
messages.value.push(loading)

  scrollToBottom()

  try {
    const { data } = await axios.post('/chat/', { message: content })

    let parsed
    try {
      parsed = JSON.parse(data.text)
    } catch (e) {
      parsed = { 설명: data.text, 추천상품: [], 추천이유: '' }
    }

    messages.value.pop()

    if (parsed.추천상품?.length === 0 && parsed.설명?.includes('덕덕이는')) {
      messages.value.push({
        role: 'bot',
        content: parsed.설명,
        recommendations: []
      })
    } else {
      messages.value.push({
        role: 'bot',
        content: parsed.설명,
        recommendations: parsed.추천상품 || [],
        reason: parsed.추천이유 || ''
      })
    }
  } catch (err) {
    messages.value.pop()
    messages.value.push({ role: 'bot', content: '⚠️ 서버 오류가 발생했습니다.' })
  } finally {
    scrollToBottom()
  }
}

const openModal = (item) => {
  const all = [...allProducts.value.deposit, ...allProducts.value.saving]
  const full = all.find(p => p.fin_prdt_cd === item.fin_prdt_cd)
  selectedProduct.value = full || item

  const msgWithReason = messages.value.find(
    msg => msg.recommendations?.some(r => r.fin_prdt_cd === item.fin_prdt_cd)
  )
  modalReason.value = msgWithReason?.reason || ''
  showProductModal.value = true
}

const closeModal = () => {
  selectedProduct.value = null
  modalReason.value = ''
  showProductModal.value = false
}

const toggleLike = async (productCode) => {
  const isDeposit = allProducts.value.deposit.some(p => p.fin_prdt_cd === productCode)
  const isSaving = allProducts.value.saving.some(p => p.fin_prdt_cd === productCode)
  const productType = isDeposit ? 'deposit' : isSaving ? 'saving' : null

  if (!productType) {
    alert('상품 타입을 확인할 수 없습니다.')
    return
  }

  try {
    await axios.post('/finlife/like/', {
      product_type: productType,
      fin_prdt_cd: productCode,
    })

    if (likedProducts.value.has(productCode)) {
      likedProducts.value.delete(productCode)
      showToastMessage('둥지에서 빠져나갔어요! 🐥')
    } else {
      likedProducts.value.add(productCode)
      showToastMessage('둥지에 담겼어요! 🐣')
    }
  } catch (err) {
    showToastMessage('😢둥지에 안들어가요..')
  }

}

onMounted(async () => {
  try {
    const res = await axios.get('/finlife/')
    res.data.saving = Array.from(new Map(res.data.saving.map(item => [item.fin_prdt_cd, item])).values())
    allProducts.value = res.data
  } catch (err) {
    console.warn('전체 상품 목록 로딩 실패:', err)
  }

  try {
    const likeRes = await axios.get('/finlife/like/mine/')
    for (const code of [...likeRes.data.deposit, ...likeRes.data.saving]) {
      likedProducts.value.add(code)
    }
  } catch (err) {
    console.warn('좋아요 목록 불러오기 실패 (비로그인일 수 있음)')
  }
})

const formatDate = (yyyymmdd) => {
  if (!yyyymmdd || yyyymmdd.length < 8) return '-'
  return `${yyyymmdd.slice(0, 4)}-${yyyymmdd.slice(4, 6)}-${yyyymmdd.slice(6, 8)}`
}

const initResize = (e, direction) => {
  e.preventDefault()
  const startX = e.clientX
  const startY = e.clientY
  const startWidth = modal.value.offsetWidth
  const startHeight = modal.value.offsetHeight

  const doDrag = (event) => {
    const minWidth = 300
    const maxWidth = Math.min(window.innerWidth * 0.9, 600)
    const minHeight = 400
    const maxHeight = Math.min(window.innerHeight * 0.9, 700)
    const modalEl = modal.value
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight

    if (direction === 'right' || direction === 'corner') {
      const newWidth = startWidth + (event.clientX - startX)
      if (newWidth >= minWidth && modalEl.offsetLeft + newWidth <= viewportWidth) {
        modalEl.style.width = newWidth + 'px'
      }
    }
    if (direction === 'bottom' || direction === 'corner') {
      const newHeight = startHeight + (event.clientY - startY)
      if (newHeight >= minHeight && modalEl.offsetTop + newHeight <= viewportHeight) {
        modalEl.style.height = newHeight + 'px'
      }
    }
    if (direction === 'left') {
      const deltaX = event.clientX - startX
      const newWidth = startWidth - deltaX
      if (newWidth >= minWidth && newWidth <= maxWidth) {
        modalEl.style.width = newWidth + 'px'
      }
    }
    if (direction === 'top') {
      const deltaY = event.clientY - startY
      const newHeight = startHeight - deltaY
      if (newHeight >= minHeight && newHeight <= maxHeight) {
        modalEl.style.height = newHeight + 'px'
      }
    }
  }

  const stopDrag = () => {
    window.removeEventListener('mousemove', doDrag)
    window.removeEventListener('mouseup', stopDrag)
  }

  window.addEventListener('mousemove', doDrag)
  window.addEventListener('mouseup', stopDrag)
}
</script>



<style scoped>
.chatbot-float-btn {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: #007bff;
  border: none;
  border-radius: 50%;
  width: 56px;
  height: 56px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0; 
}

.chatbot-float-icon {
  width: 80%;
  height: 80%;
  object-fit: contain;
  margin-top: 3px;
}


.chatbot-float-btn {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 50%;
  width: 56px;
  height: 56px;
  font-size: 22px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  z-index: 9999;
  transition: transform 0.2s;
}
.chatbot-float-btn:hover {
  transform: scale(1.05);
}

.chatbot-modal {
  position: fixed;
  bottom: 80px; /* ✔️ 화면 하단에서 살짝 위 */
  right: 20px;  /* ✔️ 오른쪽에 고정 */
  width: 350px;
  height: 500px;
  background: #ffffff;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  min-width: 300px;
  min-height: 400px;
  max-width: 600px;
  max-height: 700px;
  z-index: 9999;
  border: 1px solid #ccc;
  transform-origin: bottom right;

  /* 🔒 위치를 고정시켜서 드래그로 움직이지 못하게 할 거예요 */
  left: auto !important;
  top: auto !important;
}


.chatbot-header {
  background-color: white;
  padding: 1rem 1rem 0rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #494846;
  font-weight: 200;
  font-size: 14px;
  /* border-bottom: 1px solid #ddd; */
}
.chatbot-top {
  position: relative;
  text-align: center;
  padding-top: 1rem;
  padding-bottom: 0.5rem;
}
.chatbot-title {
  margin-top: 0.5rem;
  font-size: 16px;
  color: #333;
  font-weight: bold;
}

.chatbot-avatar {
  width: 64px;
  height: 64px;
  object-fit: contain;
  display: inline-block;
}

.close-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #bfbfbf;
}

.chatbot-body {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background-color: white;
}

.chatbot-input {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  /* border-top: 1px solid #ddd; */
  background: white;
  
}
.chatbot-input input {
  flex: 1;
  height: 38px;
  padding: 0.6rem 0.8rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 14px;
  margin-right: 0.5rem;
  box-sizing: border-box;
}
.chatbot-input button {
  height: 38px;
  background-color: #ffcc00;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0 1rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 4px; 
}
.chatbot-input button:hover {
  background-color: #0069d9;
}

.message {
  margin-bottom: 1rem;
}
.message.user .message-text {
  background: #e9f5ff;
  padding: 0.7rem;
  border-radius: 20px;
}
.message.bot .message-text {
  background: #f2f2f2;
  padding: 0.7rem;
  border-radius: 20px;
}
.chat-message-text {
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: break-word;
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 0.5rem;
}
.product-card {
  position: relative;
  background: white;
  /* border: 1px solid #ccc; */
  border-radius: 20px;
  padding: 0.8rem;
  padding-top: 1rem;
  box-shadow: 0 1px 7px rgba(0, 20, 92, 0.1);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 180px;
}
.product-card .bank {
  font-weight: bold;
  font-size: 16px;
  color: #333;
  margin-bottom: 5px;
}
.product-card .title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 1.5rem;
  margin-top: 0px;
  color: #787878;
}
.product-card .content{
  margin: 0px 0px 5px 0px;
}
.product-card .content span{
  font-weight: 600;
}
.toggle-recommend-btn {
  background: none;
  border: none;
  color: #007bff;
  font-size: 0.9rem;
  margin: 0.3rem 0 0.5rem 0;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.toggle-icon {
  width: 16px;
  height: 16px;
  stroke-width: 2;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.recommend-reason {
  background-color: #f5faff;
  border-left: 4px solid #007bff;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  margin-bottom: 16px;
  color: #444;
  line-height: 1.5;
}

.like-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.egg-clickable {
  cursor: pointer;
}



.icon {
  width: 20px;
  height: 20px;
  stroke: #c7c7c7;
  stroke-width: 1.3;
  fill: none;
}
.icon.liked {
  stroke: #ffcc00;
  fill: #ffcc00;
}

.icon-send{
  stroke: white;
}


.product-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.product-modal-box {
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
.product-modal-box h3 {
  font-size: 1.2rem;
  font-weight: bold;
  color: #222;
  margin-bottom: 1rem;
  line-height: 1.4;
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

.product-modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  background: transparent;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
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
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1px;
}
.card-footer {
  margin-top: auto;
  text-align: right;
}

.detail-button {
  background: none;
  border: none;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 0.8rem;
  cursor: pointer;
  color: #919191;
}

.detail-button:hover {
  color: #2d2d2d;
}



.resizer {
  position: absolute;
  background: transparent;
  z-index: 10000;
}
.resizer.right {
  width: 8px;
  top: 0;
  right: 0;
  bottom: 0;
  cursor: ew-resize;
}
.resizer.bottom {
  height: 8px;
  left: 0;
  right: 0;
  bottom: 0;
  cursor: ns-resize;
}
.resizer.corner {
  width: 12px;
  height: 12px;
  right: 0;
  bottom: 0;
  cursor: nwse-resize;
}
.resizer.top {
  height: 8px;
  top: 0;
  left: 0;
  right: 0;
  cursor: ns-resize;
}
.resizer.left {
  width: 8px;
  top: 0;
  bottom: 0;
  left: 0;
  cursor: ew-resize;
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

.loading-bubble {
  display: inline-block;
  background: #f2f2f2;
  padding: 0rem 0.8rem;
  border-radius: 12px;
  margin-bottom: 0rem;
  font-size: 14px;
  max-width: fit-content;
  line-height: 1.4;
}
.bot-label {
  margin-right: 4px;
  white-space: nowrap;
}

.loading-dots {
  display: inline-block;
}

.dot {
  animation: blink 1.4s infinite both;
  font-weight: bold;
  font-size: 16px;
  color: #007bff;
}

.dot1 { animation-delay: 0s; }
.dot2 { animation-delay: 0.2s; }
.dot3 { animation-delay: 0.4s; }

@keyframes blink {
  0% { opacity: 0; }
  20% { opacity: 1; }
  100% { opacity: 0; }
}

</style>
