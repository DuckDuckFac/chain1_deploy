<template>
  <div class="login-container">
    <h1 class="login-title">로그인</h1>

    <form class="login-form" @submit.prevent="submit">
      <input
        v-model="username"
        type="text"
        placeholder="아이디"
        required
        class="login-input"
      />
      <input
        v-model="password"
        type="password"
        placeholder="비밀번호"
        required
        class="login-input"
      />
      <button type="submit" class="login-submit">로그인</button>
    </form>

    <div class="social-login-icons">
      <img
        src="/google_login.png"
        alt="구글 로그인"
        class="social-icon"
        @click="goGoogle"
      />
      <img
        src="/kakao_login.png"
        alt="카카오 로그인"
        class="social-icon"
        @click="goKakao"
      />
      <img
        src="/naver_login.png"
        alt="네이버 로그인"
        class="social-icon"
        @click="goNaver"
      />
    </div>
  </div>
  <div class="signup-prompt">
  아직 NEST 회원이 아닌가요?
  <router-link to="/signup" class="signup-link">가입하기</router-link>
</div>
</template>


<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const username = ref('')
const password = ref('')
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
const googleredirectUri = 'http://localhost:8000/accounts/google/login/callback/'
const naverClientId = import.meta.env.VITE_NAVER_CLIENT_ID
const naverRedirectUri = import.meta.env.VITE_NAVER_REDIRECT_URI
const state = crypto.randomUUID()

const submit = async () => {
  const success = await userStore.loginUser({
    username: username.value,
    password: password.value,
  })

  if (success) {
    const next = route.query.next || '/'
    router.push(next)
  }
}

const goKakao = () => {
  window.location.href = `https://kauth.kakao.com/oauth/authorize?client_id=aa3ab3f5fa692d02cc51ba5ff54c1fa7&redirect_uri=http://localhost:8000/accounts/kakao/callback/&response_type=code`
}
const goGoogle = () => {
  window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${googleClientId}&redirect_uri=${googleredirectUri}&response_type=code&scope=email%20profile&access_type=offline`
}
const goNaver = () => {
  window.location.href = `https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id=${naverClientId}&redirect_uri=${naverRedirectUri}&state=${state}`
}
</script>

<style scoped>
.login-container {
  max-width: 420px;
  margin: 80px auto 24px auto;
  padding: 32px 24px;
  border-radius: 16px;
  background-color: #fff;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.04);
}

.login-title {
  text-align: center;
  font-size: 1.8rem;
  font-weight: 700;
  color: #222;
  margin-bottom: 24px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.login-input {
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 0.95rem;
  background-color: #f9f9f9;
  transition: border-color 0.2s ease;
}

.login-input:focus {
  border-color: #007bff;
  outline: none;
  background-color: #fff;
}

.login-submit {
  background-color: #007bff;
  color: white;
  font-weight: 600;
  padding: 12px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.login-submit:hover {
  background-color: #0068d9;
}

.social-login {
  margin-top: 28px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.social-btn {
  font-weight: 600;
  padding: 12px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.95rem;
}

.kakao {
  background-color: #fae100;
  color: #3c1e1e;
}

.google {
  background-color: #f1f1f1;
  color: #555;
}

.naver {
  background-color: #03c75a;
  color: white;
}

.social-login-icons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 28px;
}

.social-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%; /* ✅ 완전한 원형 */
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08); /* ✅ 기본 그림자 */
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  object-fit: cover; 
}
.signup-prompt {
  margin-top: 6px;
  text-align: center;
  font-size: 0.9rem;
  color: #888;
}

.signup-link {
  margin-left: 4px;
  color: #007bff;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s ease, border-bottom 0.2s ease;
}

.signup-link:hover {
  text-decoration: underline;
  color: #0056b3;
}


</style>
