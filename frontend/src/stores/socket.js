import { io } from 'socket.io-client'

const socket = io('http://localhost:5000', {
  transports: ['websocket'],
})

let tradeHandler = null
let postLikeHandler = null
let postCommentHandler = null

export function registerTradeHandler(callback) {
  tradeHandler = callback
  socket.off('trade_executed')
  socket.on('trade_executed', (data) => {
    callback(data) // ✅ 여기에 data가 제대로 전달됨
  })
  console.log('📡 trade_executed 핸들러 등록됨')
}

export function registerPostLikeHandler(callback) {
  postLikeHandler = callback
  socket.off('post_liked')
  socket.on('post_liked', postLikeHandler)
  console.log('📡 post_liked 핸들러 등록됨')
}

export function registerPostCommentHandler(callback) {
  postCommentHandler = callback
  socket.off('post_commented')
  socket.on('post_commented', postCommentHandler)
  console.log('📡 post_commented 핸들러 등록됨')
}

// ✅ 재연결 시 모든 핸들러 자동 재등록
socket.on('connect', () => {
  console.log('✅ [SOCKET] 연결 성공')

  if (tradeHandler) {
    socket.off('trade_executed')
    socket.on('trade_executed', tradeHandler)
    console.log('♻️ trade 핸들러 재등록 완료')
  }

  if (postLikeHandler) {
    socket.off('post_liked')
    socket.on('post_liked', postLikeHandler)
    console.log('♻️ like 핸들러 재등록 완료')
  }

  if (postCommentHandler) {
    socket.off('post_commented')
    socket.on('post_commented', postCommentHandler)
    console.log('♻️ comment 핸들러 재등록 완료')
  }
})

export default socket
