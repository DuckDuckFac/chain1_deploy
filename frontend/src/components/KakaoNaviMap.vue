<template>
    <div ref="mapRef" class="map-area">

      <div v-if="distance > 0" class="distance-box">
        <h4 class="info-header">이동 정보</h4>
        <p><Car class="lucide-icon car" /> 차량 기준 시간: {{ durationText }}</p>
        <p><Footprints class="lucide-icon Footprints" /> 도보 예상 시간: {{ walkTime }}분</p>
        <p><Bike class="lucide-icon bike" /> 자전거 예상 시간: {{ bicycleTime }}분</p>
      </div>
    </div>
</template>

<script setup>
import { onMounted, watch, ref, computed } from 'vue'
import { Car, Footprints, Bike } from 'lucide-vue-next'
import axios from 'axios'

const props = defineProps({ searchKeyword: String })

const mapRef = ref(null)
const sdkLoaded = ref(false)
const map = ref(null)
let currentPos = null
const markers = ref([])
const distance = ref(0)
const duration = ref(0)
let polyline = null     
let destinationMarker = null
let infoWindow = null

const durationText = computed(() => {
  const min = Math.round(duration.value / 60)
  return `${min}분`
})

const walkTime = computed(() => Math.round(distance.value / 67))
const bicycleTime = computed(() => Math.round(distance.value / 250))

const formattedDistance = computed(() => {
  return distance.value >= 1000
    ? `${(distance.value / 1000).toFixed(1)}km`
    : `${distance.value}m`
})

function loadKakaoSdk() {
  return new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps) {
      kakao.maps.load(resolve)
      sdkLoaded.value = true
      return
    }
    const script = document.createElement('script')
    const key = import.meta.env.VITE_KAKAO_MAP_KEY
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?autoload=false&appkey=${key}&libraries=services`
    script.onload = () => {
      kakao.maps.load(() => {
        sdkLoaded.value = true
        resolve()
      })
    }
    script.onerror = reject
    document.head.appendChild(script)
  })
}

onMounted(async () => {
  await loadKakaoSdk()

  map.value = new kakao.maps.Map(mapRef.value, {
    center: new kakao.maps.LatLng(36.3504, 127.3845),
    level: 4,
  })
  infoWindow = new kakao.maps.InfoWindow({ removable: true })
  navigator.geolocation.getCurrentPosition(pos => {
    const lat = pos.coords.latitude
    const lng = pos.coords.longitude
    currentPos = new kakao.maps.LatLng(lat, lng)
    map.value.setCenter(currentPos)

    const markerImage = new kakao.maps.MarkerImage(
      'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png',
      new kakao.maps.Size(24, 35)
    )

    const myMarker = new kakao.maps.Marker({
      map: map.value,
      position: currentPos,
      image: markerImage
    })

    const iwContent = `
      <div style="padding:5px; font-weight:bold;">
        📍 현재 위치
      </div>
    `

    const infowindow = new kakao.maps.InfoWindow({
      position: currentPos,
      content: iwContent,
      removable: false
    })

    infowindow.open(map.value, myMarker)
  })
})

watch(() => props.searchKeyword, (newKeyword) => {
  if (!sdkLoaded.value || !newKeyword) return
  searchPlaces(newKeyword)
})

function searchPlaces(keyword) {
  const ps = new kakao.maps.services.Places()
  clearMarkers()
  ps.keywordSearch(keyword, (data, status) => {
    if (status !== kakao.maps.services.Status.OK) return

    const bounds = new kakao.maps.LatLngBounds()
data.forEach(place => {
  const pos = new kakao.maps.LatLng(place.y, place.x)
  const marker = new kakao.maps.Marker({
    position: pos,
    map: map.value,
    title: place.place_name  // 👉 장소명을 title로 저장
  })
  markers.value.push(marker)
  bounds.extend(pos)

kakao.maps.event.addListener(marker, 'click', () => {
  if (!currentPos) return alert("현재 위치를 불러오는 중입니다.")

  // ✅ 기존 선, 마커 제거
  if (polyline instanceof kakao.maps.Polyline) {
    polyline.setMap(null)
    polyline = null
  }
  if (destinationMarker instanceof kakao.maps.Marker) {
    destinationMarker.setMap(null)
    destinationMarker = null
  }

  // ✅ 도착지 마커 생성
  const destImage = new kakao.maps.MarkerImage(
    'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png',
    new kakao.maps.Size(24, 35)
  )
  destinationMarker = new kakao.maps.Marker({
    map: map.value,
    position: pos,
    image: destImage,
    title: marker.getTitle()
  })

  // ✅ 단 하나의 InfoWindow를 재사용
  infoWindow.setContent(`<div style="padding:5px; font-weight:bold;">📌 ${marker.getTitle()}</div>`)
  infoWindow.setPosition(pos)
  infoWindow.open(map.value, destinationMarker)

  fetchDirections(currentPos, pos)
})
})

    map.value.setBounds(bounds)
  })
}

function clearMarkers() {
  markers.value.forEach(m => m.setMap(null))
  markers.value = []
}

async function fetchDirections(origin, destination) {
  try {
    if (polyline) {
      polyline.setMap(null)
      polyline = null
    }
    if (destinationMarker) {
      destinationMarker.setMap(null)
      destinationMarker = null
    }

    const res = await axios.get('https://apis-navi.kakaomobility.com/v1/directions', {
      headers: {
        Authorization: `KakaoAK ${import.meta.env.VITE_KAKAO_MAP_REST_KEY}`,
      },
      params: {
        origin: `${origin.getLng()},${origin.getLat()}`,
        destination: `${destination.getLng()},${destination.getLat()}`,
        priority: 'RECOMMEND'
      }
    })

    const section = res.data.routes[0].sections[0]
    distance.value = section.distance
    duration.value = section.duration

    const path = section.roads.flatMap(road => {
      const coords = []
      for (let i = 0; i < road.vertexes.length; i += 2) {
        coords.push(new kakao.maps.LatLng(road.vertexes[i + 1], road.vertexes[i]))
      }
      return coords
    })

    polyline = new kakao.maps.Polyline({
      path,
      strokeWeight: 5,
      strokeColor: '#FF6E00',
      strokeOpacity: 0.9,
      strokeStyle: 'solid',
      map: map.value,
    })

    const markerImage = new kakao.maps.MarkerImage(
      'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png',
      new kakao.maps.Size(24, 35)
    )

    destinationMarker = new kakao.maps.Marker({
      map: map.value,
      position: destination,
      image: markerImage,
      title: "도착지"
    })

  } catch (e) {
    console.error('\u274c \uac74너 \uc694청 \uc2e4패:', e)
    alert("\uac74너 \uc815보를 \uac00져오는 \ub370 \uc2e4패했습니다.")
  }
}
</script>

<style scoped>
.map-area {
  width: 100%;
  height: 600px;
  margin-top: 10px;
  position: relative; /* 🔥 기준점 역할 */
}

.distance-box {
  position: absolute; /* 🔥 지도 위 고정 */
  top: 16px;
  right: 16px;
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 0.75rem 1.25rem 1.25rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: #333;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  min-width: 240px;
  z-index: 10; /* 🔥 지도 위에 보이게 */
}

.info-header {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.8rem;
  color: #222;
}

.distance-box p {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0.4rem 0;
}

.lucide-icon {
  width: 18px;
  height: 18px;
  stroke: #adb5bd;
}

</style>
