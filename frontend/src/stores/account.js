// stores/account.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '@/stores/axios'

export const useAccountStore = defineStore('account', () => {
  const account = ref(null)
  const likedStocks = ref([])

  // ✅ 1. 계좌 정보 가져오기
  const fetchAccount = async () => {
    try {
      const res = await axios.get('/api/trade/account/')
      account.value = res.data
    } catch (err) {
      console.error('❌ 계좌 정보 불러오기 실패:', err)
    }
  }

  // ✅ 2. 좋아요 종목 목록 가져오기
  const fetchLikedStocks = async () => {
    try {
      const res = await axios.get('/api/stock/liked/')
      likedStocks.value = res.data
    } catch (err) {
      console.error('❌ 관심 종목 불러오기 실패:', err)
    }
  }
  const loadLikedStocks = async () => {
      await fetchLikedStocks()
    }
  // ✅ 3. 좋아요 토글
  const toggleLike = async (code, name = '') => {
    try {
      const res = await axios.post(`/api/trade/like/${code}/`, { name })
      if (res.data.liked) {
        // 추가
        if (!likedStocks.value.some(s => s.code === code)) {
          likedStocks.value.push({ code, name })
        }
      } else {
        // 제거
        likedStocks.value = likedStocks.value.filter(s => s.code !== code)
      }
      return res.data
    } catch (err) {
      console.error('❌ 좋아요 토글 실패:', err)
    }
  }

  return {
    account,
    likedStocks,
    fetchAccount,     
    fetchLikedStocks,
    toggleLike,
    loadLikedStocks,
  }
})
