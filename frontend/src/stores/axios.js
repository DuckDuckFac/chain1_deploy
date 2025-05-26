// src/axios.js
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const API_URL = 'http://127.0.0.1:8000'

const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ✅ 요청 시 토큰 자동 추가
axiosInstance.interceptors.request.use(config => {
  const userStore = useUserStore()
  const token = userStore.token
  console.log('📤 요청 전 토큰:', token)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ✅ 응답 시 401 → refresh 토큰으로 재요청
axiosInstance.interceptors.response.use(
  response => response,
  async error => {
    const userStore = useUserStore()
    const originalRequest = error.config

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      userStore.refreshToken
    ) {
      originalRequest._retry = true
      try {
        const res = await axios.post(`${API_URL}/accounts/token/refresh/`, {
          refresh: userStore.refreshToken
        })
        const newAccess = res.data.access
        userStore.token = newAccess
        originalRequest.headers.Authorization = `Bearer ${newAccess}`
        return axiosInstance(originalRequest)
      } catch (e) {
        console.error('🔁 토큰 갱신 실패:', e)
        userStore.logout()
        return Promise.reject(e)
      }
    }

    // 최종적으로 reject 반환
    return Promise.reject(error)
  }
)

export default axiosInstance
