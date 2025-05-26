import { defineStore } from 'pinia'
import { reactive } from 'vue'
import { io } from 'socket.io-client'
import axios from 'axios'
axios.defaults.baseURL = 'http://localhost:8000'

export const useStockChartStore = defineStore('stockChart', () => {
  const stockCodes = [
    '042700', '003550', '066570', '005380', '000660', '005930', '006400',
    '018260', '035420', '035720', '034730', '03473K', '036570', '251270',
    '263750', '293490', '112040', '042000', '030520', '058970'
  ]

  const intervals = ['1m', '3m', '5m', '10m', '15m', '30m', '60m']
  const durations = {
    '1m': 60_000,
    '3m': 3 * 60_000,
    '5m': 5 * 60_000,
    '10m': 10 * 60_000,
    '15m': 15 * 60_000,
    '30m': 30 * 60_000,
    '60m': 60 * 60_000,
  }

  const tickMap = reactive({})
  const ohlcMap = reactive({})
  const currentPriceMap = reactive({})

  const socket = io('http://localhost:5000')

  stockCodes.forEach(code => {
    tickMap[code] = {}
    ohlcMap[code] = {}
    intervals.forEach(tf => {
      tickMap[code][tf] = []
      ohlcMap[code][tf] = []
    })
  })

socket.on('stock_data', (data) => {
  // console.log('📡 소켓 수신:', data)
  const code = data.code
  currentPriceMap[code] = {
    ...data,
    current_price: parseInt(data.current_price),
    change: parseInt(data.change),
    rate: parseFloat(data.rate),  // ✅ 숫자 변환
  }

  const price = parseInt(data.current_price)
  if (!tickMap[code] || isNaN(price)) return

  intervals.forEach(tf => {
    tickMap[code][tf].push(price)
  })
})

  function createOHLC(code, tf, durationMs) {
    // console.log(`✅ createOHLC 시작됨 → ${code} ${tf}`)
    setInterval(async () => {
      const prices = tickMap[code][tf]
      if (!prices || prices.length === 0) return

      const o = prices[0]
      const h = Math.max(...prices)
      const l = Math.min(...prices)
      const c = prices[prices.length - 1]
      const now = new Date()

      const candle = {
          time: Math.floor(now.getTime() / 1000), 
          open: o,
          high: h,
          low: l,
          close: c
        }
      ohlcMap[code][tf].push(candle)
      if (ohlcMap[code][tf].length > 60) ohlcMap[code][tf].shift()
      tickMap[code][tf] = []
      console.log('🔥 봉 저장 요청', {
      code,
      interval: tf,
      timestamp: now.toISOString(),
      open: o,
      high: h,
      low: l,
      close: c
    })
      try {
        await axios.post('/api/ohlc/', {
          code,
          interval: tf,
          timestamp: now.toISOString(),
          open: o, high: h, low: l, close: c,
        })
      } catch (err) {
        console.error('❌ 서버 저장 실패', err)
      }
    }, durationMs)
  }

async function preloadOHLC(targetCode) {
  const codesToLoad = targetCode ? [targetCode] : stockCodes

  for (const code of codesToLoad) {
    for (const tf of intervals) {
      try {
        const res = await axios.get(`/api/ohlc/${code}/${tf}/`)
        ohlcMap[code][tf] = res.data.map(item => ({
          time: Math.floor(new Date(item.timestamp).getTime() / 1000),
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
        }))
      } catch (err) {
        console.error(`❌ ${code} ${tf} 봉 로드 실패`, err)
      }
    }
  }
}
function startOHLCFor(code, tf) {
  // 중복 생성 방지 (이미 타이머 있으면 return)
  if (!tickMap[code] || !tickMap[code][tf]) return
  if (ohlcMap[code][tf].__running) return  // ✅ 중복 방지용 플래그

  createOHLC(code, tf, durations[tf])
  ohlcMap[code][tf].__running = true
}

  return {
    stockCodes,
    intervals,
    ohlcMap,
    currentPriceMap,
    preloadOHLC,
    startOHLCFor,
  }
})
