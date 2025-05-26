<template>
  <div class="search-box" ref="searchBox">
    <input
      type="text"
      v-model="query"
      @focus="showDropdown = true"
      @input="onSearch"
      placeholder="종목검색"
      class="search-input"
    />
    <Search class="search-icon" />
    <!-- 드롭다운 -->
    <div v-if="showDropdown" class="search-dropdown">
      <!-- 최근 검색 -->
      <div v-if="recentSearches.length > 0">
        <p class="dropdown-title">
          🕘 최근 검색
          <button class="clear-btn" @click.stop="clearAllRecent">전체 삭제</button>
        </p>
        <ul>
          <li v-for="(term, i) in recentSearches" :key="term">
            <span @click="searchRecent(term)" class="recent-term">{{ term }}</span>
            <button class="remove-btn" @click.stop="removeRecent(i)">✕</button>
          </li>
        </ul>
      </div>

      <!-- 검색 결과 -->
      <div v-if="filteredStocks.length > 0">
        <p class="dropdown-title">🔍 종목 검색 결과</p>
        <ul>
          <li v-for="stock in filteredStocks" :key="stock.code" @click="selectStock(stock)">
            <span>{{ stock.name }} ({{ stock.code }})</span>
            <span class="rate" :class="{ up: stock.rate > 0, down: stock.rate < 0 }">
              {{ stock.rate > 0 ? '+' : '' }}{{ stock.rate.toFixed(2) }}%
            </span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import socket from '@/stores/socket'
import { Search } from 'lucide-vue-next'

const router = useRouter()
const query = ref('')
const showDropdown = ref(false)
const searchBox = ref(null)

const stockMap = ref({})
socket.on('stock_data', (data) => {
  stockMap.value[data.code] = data
})

const stock_info_map = {
  '042700': { name: '한미반도체' },
  '003550': { name: 'LG' },
  '066570': { name: 'LG전자' },
  '005380': { name: '현대차' },
  '000660': { name: 'SK하이닉스' },
  '005930': { name: '삼성전자' },
  '006400': { name: '삼성SDI' },
  '018260': { name: '삼성SDS' },
  '035420': { name: 'NAVER' },
  '035720': { name: '카카오' },
  '034730': { name: 'SK' },
  '03473K': { name: 'SK우' },
  '036570': { name: '엔씨소프트' },
  '251270': { name: '넷마블' },
  '263750': { name: '펄어비스' },
  '293490': { name: '카카오게임즈' },
  '112040': { name: '위메이드' },
  '042000': { name: '카페24' },
  '030520': { name: '한글과컴퓨터' },
  '058970': { name: '엠로' },
}

const stockList = Object.entries(stock_info_map).map(([code, info]) => ({
  code,
  name: info.name,
}))

const filteredStocks = computed(() => {
  const q = query.value.trim().toLowerCase()  // 소문자로 변환
  if (!q) return []

  return stockList
    .filter((item) => item.name.toLowerCase().includes(q))  // 소문자로 비교
    .map((item) => ({
      ...item,
      rate: Number(stockMap.value[item.code]?.rate) || 0,
    }))
})

const RECENT_KEY = 'recentSearches'
const recentSearches = ref(JSON.parse(localStorage.getItem(RECENT_KEY)) || [])

const saveRecent = (term) => {
  const idx = recentSearches.value.indexOf(term)
  if (idx !== -1) recentSearches.value.splice(idx, 1)
  recentSearches.value.unshift(term)
  if (recentSearches.value.length > 5) recentSearches.value.pop()
  localStorage.setItem(RECENT_KEY, JSON.stringify(recentSearches.value))
}

const removeRecent = (index) => {
  recentSearches.value.splice(index, 1)
  localStorage.setItem(RECENT_KEY, JSON.stringify(recentSearches.value))
}

const clearAllRecent = () => {
  recentSearches.value = []
  localStorage.removeItem(RECENT_KEY)
}

const selectStock = (stock) => {
  query.value = stock.name
  saveRecent(stock.name)
  router.push({ name: 'stock-detail', params: { code: stock.code } })
  showDropdown.value = false
}

const searchRecent = (term) => {
  query.value = term
  const code = getCodeByName(term)
  if (code) {
    router.push({ name: 'stock-detail', params: { code } })
  }
  showDropdown.value = false
}

const getCodeByName = (name) => {
  return Object.entries(stock_info_map).find(([code, info]) => info.name === name)?.[0] || ''
}

const onSearch = () => {
  showDropdown.value = true
}

const handleClickOutside = (e) => {
  if (searchBox.value && !searchBox.value.contains(e.target)) {
    showDropdown.value = false
  }
}
onMounted(() => {
  window.addEventListener('click', handleClickOutside)
})
onBeforeUnmount(() => {
  window.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.search-box {
  position: relative;
  width: 280px;
  background-color: #f4f6f8;
  border-radius: 30px;
  padding: 8px 16px;
  display: flex;
  align-items: center;
}
.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}
.search-input::placeholder {
  color: #b0b8c1;
  font-weight: 600;
}
.search-icon {
  width: 18px;
  height: 18px;
  color: #b0b8c1;
  flex-shrink: 0;
}

.search-dropdown {
  position: absolute;
  top: 42px;
  width: 100%;
  background: white;
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-height: 350px;
  overflow-y: auto;
  z-index: 1000;
}
.dropdown-title {
  font-weight: bold;
  padding: 8px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  background-color: #f9f9f9;
}
.clear-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 0.8rem;
  cursor: pointer;
}
.search-dropdown ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.search-dropdown li {
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}
.search-dropdown li:hover {
  background-color: #f0f0f0;
}
.remove-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 0.8rem;
  cursor: pointer;
  margin-left: 10px;
}
.rate {
  font-size: 0.85rem;
  font-weight: bold;
}
.up {
  color: red;
}
.down {
  color: blue;
}
</style>
