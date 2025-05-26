import { defineStore } from "pinia"
import { ref, computed } from "vue"
import { useRouter } from "vue-router"
import axios from "axios"
import swal from "sweetalert"

export const useUserStore = defineStore("user", () => {
  const API_URL = "http://127.0.0.1:8000"


  const token = ref(null)
  const refreshToken = ref(null)
  const userInfo = ref(null)
  const userProfile = ref(null)

  const isLogin = computed(() => !!token.value)

  const parseJwt = (token) => {
    try {
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      return JSON.parse(decodeURIComponent(atob(base64).split('').map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
      }).join('')))
    } catch (err) {
      return null
    }
  }

  const createUser = async (userPayload) => {
    try {
      await axios.post(`${API_URL}/accounts/signup/`, userPayload)
      const res = await axios.post(`${API_URL}/accounts/token/`, {
        username: userPayload.username,
        password: userPayload.password,
      })

      token.value = res.data.access
      refreshToken.value = res.data.refresh
      axios.defaults.headers.common["Authorization"] = `Bearer ${token.value}`
      userInfo.value = res.data.user


      return true
    } catch (err) {
      console.error("🔥 서버 응답:", err.response?.data || err.message)
      swal("회원가입 중 오류가 발생했어요.", "error")
      return false
    }
  }

const loginUser = async ({ username, password }) => {
  try {
    const res = await axios.post(`${API_URL}/accounts/token/`, { username, password })

    token.value = res.data.access
    refreshToken.value = res.data.refresh
    axios.defaults.headers.common["Authorization"] = `Bearer ${token.value}`
    userInfo.value = res.data.user
    await getProfile()

    swal(`${username}님, 환영합니다!`, { timer: 1000, buttons: false })

    return true   // ✅ 성공
  } catch (err) {
    swal("로그인 실패", "아이디 또는 비밀번호가 올바르지 않습니다.", "error")
    return false  // ❌ 실패
  }
}

  const logoutUser = () => {
    token.value = null
    refreshToken.value = null
    userInfo.value = null
    userProfile.value = null
    delete axios.defaults.headers.common["Authorization"]
  }

const getProfile = async () => {
  if (!token.value) return
  try {
    const res = await axios.get(`${API_URL}/accounts/profile/`, {
  headers: {
    Authorization: `Bearer ${token.value}`
  }
})
    const profile = res.data.results?.[0]

    userProfile.value = profile

    // ✅ userInfo 통째로 업데이트 (프로필에서)
    
    if (profile?.user) {
      userInfo.value = {
        id: profile.user.id,
        username: profile.user.username,
        email: profile.user.email,
        nickname: profile.user.nickname
      }
    }

    console.log('📦 userInfo 업데이트 결과:', userInfo.value)
  } catch (err) {
    console.error('❌ 프로필 요청 실패:', err.response?.status, err.response?.data)
  }
}


  const updateProfile = async (payload) => {
    try {
      const profileId = userProfile.value?.id
      if (!profileId) throw new Error("프로필 ID 없음")

      const res = await axios.put(`${API_URL}/accounts/profile/${profileId}/`, payload)
      userProfile.value = res.data
      swal("프로필이 성공적으로 수정되었습니다.", "🙂", "success")
    } catch (err) {
      swal("프로필 수정 실패", "다시 시도해주세요.", "error")
      console.error(err)
    }
  }
const loginWithGoogle = async (access, refresh, onLoginComplete) => {
  token.value = access
  refreshToken.value = refresh
  axios.defaults.headers.common["Authorization"] = `Bearer ${token.value}`

  // ✅ access 토큰 디코딩해서 유저 정보 추정 (선택)
  const decoded = parseJwt(access)
  if (decoded) {
    userInfo.value = {
      id: decoded.user_id,
      username: decoded.username || '',
      email: decoded.email || '',
      nickname: '', // 일단 비워두고 아래에서 프로필로 채움
    }
  }

  // ✅ 프로필 불러와서 userInfo.nickname까지 갱신
  await getProfile()
  if (userProfile.value?.user?.nickname) {
    userInfo.value.nickname = userProfile.value.user.nickname
  }

  if (onLoginComplete) onLoginComplete()
}

const loginWithKakao = async (access, refresh, onLoginComplete) => {
  token.value = access
  refreshToken.value = refresh
  axios.defaults.headers.common["Authorization"] = `Bearer ${token.value}`

  // ✅ access 토큰 디코딩해서 유저 정보 추정
  const decoded = parseJwt(access)
  if (decoded) {
    userInfo.value = {
      id: decoded.user_id,
      username: decoded.username || '',
      email: decoded.email || '',
      nickname: '', // 일단 비워두고 아래에서 프로필로 채움
    }
  }

  await getProfile()

  // ✅ getProfile()에서 가져온 nickname 반영
  if (userProfile.value?.user?.nickname) {
    userInfo.value.nickname = userProfile.value.user.nickname
  }

  if (onLoginComplete) onLoginComplete()
}
  // ✅ interceptor: access 만료되면 refresh로 갱신
  axios.interceptors.response.use(
    response => response,
    async error => {
      const originalRequest = error.config
      if (error.response?.status === 401 && !originalRequest._retry && refreshToken.value) {
        originalRequest._retry = true
        try {
          const res = await axios.post(`${API_URL}/accounts/token/refresh/`, {
            refresh: refreshToken.value,
          })
          token.value = res.data.access
          axios.defaults.headers.common["Authorization"] = `Bearer ${token.value}`
          originalRequest.headers["Authorization"] = `Bearer ${token.value}`
          return axios(originalRequest)
        } catch (refreshErr) {
          console.error("🔁 토큰 갱신 실패:", refreshErr)
          logoutUser()
        }
      }

      return Promise.reject(error)
    }
    
  )

  return {
    token,
    refreshToken,
    userInfo,
    userProfile,
    isLogin,
    createUser,
    loginUser,
    logoutUser,
    getProfile,
    updateProfile,
    loginWithGoogle,
    loginWithKakao,
  }
}, {
  persist: true
})

