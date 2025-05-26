<template>
  <div class="selector">
    <div class="custom-select-wrapper">
      <select v-model="sido" @change="updateSigungu">
        <option value="">광역시 / 도 선택</option>
        <option v-for="s in sidoList" :key="s">{{ s }}</option>
      </select>
      <ChevronDown class="custom-arrow-icon" />
    </div>

    <div class="custom-select-wrapper">
      <select v-model="sigungu">
        <option value="">시 / 군 / 구 선택</option>
        <option v-for="g in sigunguList" :key="g">{{ g }}</option>
      </select>
      <ChevronDown class="custom-arrow-icon" />
    </div>

    <div class="custom-select-wrapper">
      <select v-model="bank">
        <option value="">은행 선택</option>
        <option v-for="b in bankList" :key="b">{{ b }}</option>
      </select>
      <ChevronDown class="custom-arrow-icon" />
    </div>

    <button @click="search">찾기</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ChevronDown } from 'lucide-vue-next'

const sido = ref('')
const sigungu = ref('')
const bank = ref('')
const sidoList = ref([])
const sigunguList = ref([])
const bankList = ref([])
const allData = ref([])
const emit = defineEmits(['search'])

onMounted(async () => {
  const { data } = await axios.get('/api/bank-info/')
  sidoList.value = data.mapInfo.map(i => i.name)
  bankList.value = data.bankInfo
  allData.value = data.mapInfo
})

function updateSigungu() {
  const selected = allData.value.find(r => r.name === sido.value)
  sigunguList.value = selected?.countries || []
}

function search() {
  if (!sido.value || !sigungu.value || !bank.value) {
    alert("모든 항목을 선택해주세요.")
    return
  }
  emit('search', `${sido.value} ${sigungu.value} ${bank.value}`)
}
</script>

<style scoped>
.selector {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}

.custom-select-wrapper {
  position: relative;
  width: 220px;
}

.custom-select-wrapper select {
  width: 100%;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  padding: 0.6rem 0.8rem;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 0.95rem;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
}

.custom-arrow-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  stroke: #888;
  pointer-events: none;
}

.selector button {
  background-color: #007bff;
  color: white;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.selector button:hover {
  background-color: #0056b3;
}
</style>
