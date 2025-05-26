<template>
  <div id="app">
    <!-- 배경 영상 -->
<div class="video-sector">
  <!-- 배경 영상 -->
  <div class="background-video">
    <iframe
      src="https://player.vimeo.com/video/1087464044?autoplay=1&muted=1&loop=1&background=1"
      frameborder="0"
      allow="autoplay; fullscreen"
      allowfullscreen
    ></iframe>
  </div>

  <!-- 오버레이 -->
  <div class="video-overlay">
    <div class="hero-text">
      <h1>당신의 보금자리 <span class="highlight"></span></h1>
      <p>모든 금융의 시작, 지금 경험하세요.</p>
    </div>
  </div>
</div>

    <!-- NavBar -->
    <NavBar :isMainPage="isMainPage" />


  <!-- 메인 비디오 섹션 구조 -->
   <!-- 모의 투자 -->
<div class="video-section">
  <!-- 왼쪽: 영상 -->
  <div class="video-container">
    <video src="/main/virtualInvest.mp4" muted loop playsinline></video>
  </div>

  <!-- 오른쪽: 텍스트와 버튼 -->
  <div class="text-container">
    <h2>모의 투자</h2>
    <p>가상의 자산으로 안전하게 연습해보세요.</p>
    <router-link to="/stock" class="action-button">주식 투자</router-link>
  </div>
</div>

<!-- 금융 정보 -->
<div class="video-section reverse-interest">
    <!-- 왼쪽: 영상 -->
  <div class="video-container">
    <video src="/main/Depositreccommand.mp4" muted loop playsinline></video>
  </div>
  <!-- 오른쪽: 텍스트 -->
  <div class="text-container reverse">
    <h2>금리 비교</h2>
    <p>예금, 적금, 대출 금리를 한눈에 비교해보세요.</p>
    <router-link to="/finlife" class="action-button">금리비교</router-link>
  </div>
</div>

<!-- 은행찾기 -->
<div class="video-section">
    <!-- 왼쪽: 영상 -->
  <div class="video-container">
    <video src="/main/bankfind.mp4" muted loop playsinline></video>
  </div>
  <!-- 오른쪽: 텍스트 -->
  <div class="text-container">
    <h2>은행 찾기</h2>
    <p>내 주변 가까운 은행을 찾아보세요.</p>
    <router-link to="/findbank" class="action-button">은행찾기</router-link>
  </div>
</div>

<!-- 커뮤니티 -->
<div class="video-section reverse">
    <!-- 왼쪽: 영상 -->
    <div class="video-container">
      <video src="/main/community_intro.mp4" muted loop playsinline></video>
    </div>

    <!-- 오른쪽: 텍스트와 버튼 -->
    <div class="text-container reverse">
      <h2>커뮤니티</h2>
      <p>여러 사람들과 다양한 의견을 나누어보세요.</p>
      <router-link to="/community" class="action-button">커뮤니티</router-link>
    </div>
</div>
</div>

</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isMainPage = computed(() => route.path === '/')

let observer = null

onMounted(() => {
  const videos = document.querySelectorAll('video')  // 모든 <video> 수집

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        const video = entry.target
        if (entry.isIntersecting) {
          video.play().catch(() => {})  // 모바일 크롬 등 재생 실패 대비
        } else {
          video.pause()
          video.currentTime = 0
        }
      })
    },
    {
      threshold: 0.5,  // 50% 이상 보이면 재생
    }
  )

  videos.forEach(video => observer.observe(video))
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>


<style scoped>
/* 배경 영상 */
.video-sector {
  position: relative;
  padding-bottom:56.25%;
  height:0px;
  overflow: hidden;
}

/* 배경 영상 iframe */
.background-video {
  position: absolute;
  top: 0; left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.background-video iframe {
  width: 100%;
  height: 100%;
  pointer-events: none; /* 클릭 차단 */
}

/* 오버레이 */
.video-overlay {
  position: absolute;
  top: 0; left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.3); /* 반투명 검정 */
  z-index: 1; /* 영상 위로 올라오도록 */
  display: flex;
  justify-content: center;
  align-items: center;
}

.hero-text {
  position: absolute;
  top: 65%;
  left: 20%;
  transform: translate(-50%, -30%);
  /* text-align: center; */
  color: white;
  z-index: 2;
  padding: 1rem 2rem;
}

.hero-text h1 {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-shadow: 0 0 8px rgba(0, 0, 0, 0.3);
}

.hero-text p {
  font-size: 1.3rem;
  text-shadow: 0 0 6px rgba(0, 0, 0, 0.3);
}

.highlight {
  font-size: 3.5rem;
  color: #ffcc00;
}


/* 중앙 선 */
.separator {
  width: 100%;
  height: 1px;
  background-color: #ddd;
  margin: 2rem 0;
}

/* 비디오 섹션 스타일 */
.video-section {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 3rem;
  padding: 4rem 2rem;
  flex-wrap: wrap;
}
.video-section.reverse-interest {
  background-color: #69acff;
  flex-direction: row-reverse;
}
.video-section.reverse-interest video{
  box-shadow: none;
}
.video-section.reverse-interest h2{
  color: white;
}
.video-section.reverse-interest p{
  color: white;
}
.video-section.reverse-interest .action-button{
  background-color: white;
  color: #007bff;
}
.video-section.reverse {
  flex-direction: row-reverse;
  background-color: #ffd779;
  color: white;
}
.video-section.reverse p{
  color: #fff9ec;
  font-weight: 00;
}
.video-section.reverse video{
  box-shadow: none;
}
.video-section.reverse .action-button{
  background-color: white;
  color: #007bff;
}

.video-container {
  flex: 1;
  display: flex;
  justify-content: center;
}

.video-container video {
  width: 100%;
  max-width: 500px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.text-container {
  flex: 1;
  max-width: 650px;
  text-align: left;
}
.text-container.reverse {
  padding-left: 17rem;
}
.text-container h2 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.text-container p {
  font-size: 1.1rem;
  color: #555;
  margin-bottom: 4rem;
}

.action-button {
  padding: 12px 24px;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 30px;
  font-weight: bold;
  transition: background-color 0.3s ease;
}

.action-button:hover {
  background-color: #0056b3;
}




</style>
