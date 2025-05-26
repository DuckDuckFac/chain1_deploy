# eventlet 위치 중요 (절대 아래로 내리지 마세요)
import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import websocket as ws_client
import threading
import requests
import json
import os

# Flask 앱 설정
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# .env 환경변수 불러오기
load_dotenv()
APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
WS_URL = 'ws://ops.koreainvestment.com:31000'

# 종목 정보
stock_info_map = {
    '042700': {'name': '한미반도체', 'prev_close': 81900},
    '003550': {'name': 'LG', 'prev_close': 68600},
    '066570': {'name': 'LG전자', 'prev_close': 71300},
    '005380': {'name': '현대차', 'prev_close': 190100},
    '000660': {'name': 'SK하이닉스', 'prev_close': 204500},
    '005930': {'name': '삼성전자', 'prev_close': 56800},
    '006400': {'name': '삼성SDI', 'prev_close': 164700},
    '018260': {'name': '삼성에스디에스', 'prev_close': 129400},
    '035420': {'name': 'NAVER', 'prev_close': 187800},
    '035720': {'name': '카카오', 'prev_close': 37400},
    '034730': {'name': 'SK', 'prev_close': 137100},
    '03473K': {'name': 'SK우', 'prev_close': 123600},
    '036570': {'name': '엔씨소프트', 'prev_close': 158300},
    '251270': {'name': '넷마블', 'prev_close': 50200},
    '263750': {'name': '펄어비스', 'prev_close': 36750},
    '293490': {'name': '카카오게임즈', 'prev_close': 14180},
    '112040': {'name': '위메이드', 'prev_close': 24750},
    '042000': {'name': '카페24', 'prev_close': 45000},
    '030520': {'name': '한글과컴퓨터', 'prev_close': 22050},
    '058970': {'name': '엠로', 'prev_close': 49800},
}

# 실시간 체결 요청 → Django
def trigger_django_check(code, price):
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/trade/auto-execute/",
            json={"code": code, "price": price},
            timeout=3
        )
        print(f"🔁 예약 체결 요청 → {code} @ {price}: {response.status_code}")
    except Exception as e:
        print(f"❌ Django 예약 체결 실패: {e}")

# 프론트와 백에 동시에 데이터 전달
def broadcast_stock_data(data):
    socketio.emit('stock_data', data)
    try:
        trigger_django_check(data["code"], int(data["current_price"]))
    except Exception as e:
        print(f"❌ 예약체결 실패: {e}")

# 체결 데이터 프론트로 emit
def emit_trade_executed(user_id, code, name, quantity, trade_type, avg_price):
    data = {
        "user_id": user_id,
        "code": code,
        "name": name,
        "quantity": quantity,
        "trade_type": trade_type,
        "avg_price": avg_price
    }
    socketio.emit('trade_executed', data)

# 체결 데이터 수신 엔드포인트
@app.route('/trade-executed/', methods=['POST'])
def trade_executed():
    data = request.get_json()
    print('[체결 완료] emit:', data)
    socketio.emit('trade_executed', data)
    return jsonify({'message': 'emitted'})

# 주문/체결 알림 (선택적으로 사용)
@app.route('/notify-trade/', methods=['POST'])
def notify_trade():
    data = request.json
    account_id = data['account_id']
    trade_id = data['trade_id']
    socketio.emit('trade_update', {'account_id': account_id, 'trade_id': trade_id})
    return '', 200

# H0STASP0 파싱
def parse_hoka(raw):
    parts = raw.split('^')
    code = parts[0]
    current_price = int(parts[21])
    ask_1 = parts[3]
    bid_1 = parts[13]
    volume = parts[53]

    info = stock_info_map.get(code)
    if not info:
        name = '알수없음'
        prev_price = current_price
        change = 0
        rate = 0.0
    else:
        name = info['name']
        prev_price = info['prev_close']
        change = current_price - prev_price
        rate = round((change / prev_price) * 100, 2)

    return {
        "code": code,
        "name": name,
        "current_price": str(current_price),
        "ask_1": ask_1,
        "bid_1": bid_1,
        "volume": volume,
        "change": str(change),
        "rate": str(rate),
    }

# 인증키 발급
def get_approval(key, secret):
    print("🔑 인증키 요청 시작")
    url = 'https://openapi.koreainvestment.com:9443/oauth2/Approval'
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": key,
        "secretkey": secret
    }
    res = requests.post(url, headers=headers, data=json.dumps(body), timeout=5)
    print("🔑 인증키 수신 완료")
    return res.json()["approval_key"]

# 실시간 WebSocket 수신
def connect_stock_ws():
    print("✅ WebSocket 연결 시도 중...")
    approval_key = get_approval(APP_KEY, APP_SECRET)
    ws = ws_client.WebSocket()
    ws.connect(WS_URL, ping_interval=60)

    code_list = [
        ['1', 'H0STASP0', code] for code in stock_info_map.keys()
    ]

    for i, j, k in code_list:
        payload = {
            "header": {
                "approval_key": approval_key,
                "custtype": "P",
                "tr_type": i,
                "content-type": "utf-8"
            },
            "body": {
                "input": {
                    "tr_id": j,
                    "tr_key": k
                }
            }
        }
        ws.send(json.dumps(payload))

    while True:
        try:
            data = ws.recv()
            if data[0] in ['0', '1']:
                recvstr = data.split('|')
                trid = recvstr[1]
                content = recvstr[3]

                if trid == 'H0STASP0':
                    parsed = parse_hoka(content)
                    print("📤 프론트/백 전송:", parsed)
                    broadcast_stock_data(parsed)
        except Exception as e:
            print("WebSocket 오류:", e)
            break

@app.route('/')
def index():
    return "✅ Flask + Socket.IO 실시간 주식 서버 실행 중!"

# 좋아요, 댓글 알림
@app.route('/notify/like', methods=['POST'])
def notify_like():
    data = request.get_json()
    socketio.emit('post_liked', data)
    return jsonify({'status': 'ok'})

@app.route('/notify/comment', methods=['POST'])
def notify_comment():
    data = request.get_json()
    socketio.emit('post_commented', data)
    return jsonify({'status': 'ok'})

# 서버 실행
if __name__ == '__main__':
    threading.Thread(target=connect_stock_ws, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000)
