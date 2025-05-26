<template>
  <div class="stock-wrapper">
    <!-- 왼쪽: VirtualAccountCard (작게) -->
    <div class="left-side">
      <VirtualAccountCard style="margin-bottom: 30px;" />
      <RankingPreview />
    </div>

    <!-- 오른쪽: 주식 실시간 정보 -->
    <div class="right-side">
      <h1>📈 실시간 주식 정보</h1>
      <StockRealtime />
    </div>
  </div>
</template>

<script setup>
import VirtualAccountCard from '@/components/VirtualAccountCard.vue'
import StockRealtime from '@/components/StockRealtime.vue'
import RankingPreview from '@/components/RankingPreview.vue'
</script>

<style scoped>
.stock-wrapper {
  display: flex;
  gap: 2rem;
  padding: 1rem;
  max-width: 1660px;
  margin: 0 auto;
}

/* 왼쪽 - 좁고 고정 */
.left-side {
  flex: 0 0 250px;
  
}

/* 오른쪽 - 가변 */
.right-side {
  flex: 1;
}
</style>
