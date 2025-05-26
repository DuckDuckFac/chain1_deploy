<template>
  <div id="map" ref="mapRef" class="map-area"></div>
</template>

<script setup>
import { watch, onMounted, ref } from 'vue'

const props = defineProps({ searchKeyword: String })
const mapRef = ref(null)
let map, infowindow, markers = []

const sdkLoaded = ref(false)  // ✅ SDK 로딩 완료 여부

function loadKakaoMapSdk() {
  return new Promise((resolve) => {
    if (window.kakao && window.kakao.maps) {
      console.log("✅ Kakao SDK already loaded")
      kakao.maps.load(() => {
        sdkLoaded.value = true
        resolve()
      })
      return
    }

    const script = document.createElement('script')
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?autoload=false&appkey=${import.meta.env.VITE_KAKAO_MAP_KEY}&libraries=services`
    script.onload = () => {
      console.log("✅ Kakao SDK loaded")
      kakao.maps.load(() => {
        sdkLoaded.value = true
        resolve()
      })
    }
    script.onerror = () => {
      console.error("❌ Kakao SDK load failed")
    }
    document.head.appendChild(script)
  })
}

onMounted(async () => {
  await loadKakaoMapSdk()

  map = new kakao.maps.Map(mapRef.value, {
    center: new kakao.maps.LatLng(37.49818, 127.027386),
    level: 3,
  })
  infowindow = new kakao.maps.InfoWindow({ zIndex: 1 })

  // ✅ 로딩 이후 searchKeyword가 존재하면 바로 실행
  if (props.searchKeyword) {
    searchBank(props.searchKeyword)
  }
})

// ✅ kakao 객체가 준비되었을 때만 실행
watch(() => props.searchKeyword, (newKeyword) => {
  if (sdkLoaded.value && newKeyword) {
    searchBank(newKeyword)
  }
})

function searchBank(keyword) {
  console.log("📍 searchBank 실행됨:", keyword)
  const ps = new kakao.maps.services.Places()

  markers.forEach(marker => marker.setMap(null))
  markers = []

  ps.keywordSearch(keyword, (data, status) => {
    if (status !== kakao.maps.services.Status.OK) return
    const bounds = new kakao.maps.LatLngBounds()

    data.forEach(place => {
      const position = new kakao.maps.LatLng(place.y, place.x)
      const marker = new kakao.maps.Marker({ position, map })
      markers.push(marker)
      bounds.extend(position)

      kakao.maps.event.addListener(marker, 'click', () => {
        infowindow.setContent(`<div style="padding:5px;font-size:13px;">${place.place_name}</div>`)
        infowindow.open(map, marker)
      })
    })

    map.setBounds(bounds)
  })
}
</script>

<style scoped>
.map-area {
  width: 100%;
  height: 600px;
}
</style>
