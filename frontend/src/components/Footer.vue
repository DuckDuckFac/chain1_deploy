<template>
  <footer class="footer">
    <div class="footer-links">
      <a href="https://www.ssafy.com/ksp/jsp/swp/swpMain.jsp" target="_blank">SSAFY 공식 사이트</a>
      <a href="https://edu.ssafy.com/edu/main/index.do" target="_blank">SSAFY 교육 사이트</a>
    </div>
    <div class="footer-contact">
      <p><strong>email </strong>pizzayumnum@naver.com | dksejrgus2@naver.com</p>
      <p><strong>instagram </strong><a href="https://www.instagram.com/kwonjaeun" target="_blank">@kwonjaeun</a> | <a href="https://www.instagram.com/5l_uck" target="_blank">@ol_uck</a></p>
    </div>
    <p class="copyright">© 2025 DuckDuckFin. All rights reserved.</p>
  </footer>
</template>

<script setup>
// 로직 없음
</script>

<style scoped>
.footer {
  padding: 30px;
  background-color: #f7f7f7;
  text-align: center;
  font-size: 14px;
  color: #555;
  border-top: 1px solid #ddd;
}

.footer-links {
  margin-bottom: 10px;
}

.footer-links a {
  margin: 0 10px;
  text-decoration: none;
  color: #007acc;
}

.footer-links a:hover {
  text-decoration: underline;
}

.footer-contact p {
  margin: 4px 0;
}

.footer-contact a {
  color: #555;
  text-decoration: none;
}

.footer-contact a:hover {
  text-decoration: underline;
}

</style>
