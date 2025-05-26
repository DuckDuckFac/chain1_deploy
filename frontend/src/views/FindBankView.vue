<template>
  <div class="find-bank-container">
    <div class="selector-box">
      <BankSelector @search="handleSearch" />
    </div>
    <KakaoNaviMap :searchKeyword="searchKeyword" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import BankSelector from '@/components/BankSelector.vue'
import KakaoNaviMap from '@/components/KakaoNaviMap.vue'

const searchKeyword = ref('')

function handleSearch(keyword) {
  searchKeyword.value = keyword
}
</script>

<style scoped>
.find-bank-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem 1rem;
  background-color: #ffffff;
  border-radius: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  min-height: 80vh;
  box-sizing: border-box;
}
.selector-box {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 10px;
}
</style>
