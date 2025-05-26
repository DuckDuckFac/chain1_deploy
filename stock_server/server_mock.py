import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import random
import threading
import requests

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

# 종목 전일 종가 기반 정보
stock_info_map = {
    '042700': {'name': '한미반도체', 'prev_close': 81900},
    '003550': {'name': 'LG', 'prev_close': 68600},
    '066570': {'name': 'LG전자', 'prev_close': 71300},
    '005380': {'name': '현대차', 'prev_close': 190100},
    '000660': {'name': 'SK하이닉스', 'prev_close': 204500},
    '005930': {'name': '삼성전자', 'prev_close': 56800},
    '006400': {'name': '삼성SDI', 'prev_close': 164700},
    '018260': {'name': '삼성SDS', 'prev_close': 129400},
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

# 현재가 저장소 초기화
current_prices = {code: info['prev_close'] for code, info in stock_info_map.items()}


def emit_trade_executed(user_id, code, name, quantity, trade_type, avg_price):
    socketio.emit('trade_executed', {
        "user_id": user_id,
        "code": code,
        "name": name,
        "quantity": quantity,
        "trade_type": trade_type,
        "avg_price": avg_price
    })


# 가격 변동 시뮬레이션
def simulate_price(code, price):
    surge_chance = 0.0005  # 0.05% 확률로 급등락
    if random.random() < surge_chance:
        change_pct = random.uniform(-0.3, 0.3)
    else:
        change_pct = random.uniform(-0.01, 0.01)

    new_price = price * (1 + change_pct)

    base_price = stock_info_map[code]['prev_close']
    min_price = base_price * 0.7
    max_price = base_price * 1.3

    return round(max(min(new_price, max_price), min_price), 2)


# 데이터 생성 및 emit
def mock_data_loop():
    while True:
        for code, info in stock_info_map.items():
            name = info['name']
            prev_close = info['prev_close']
            old_price = current_prices[code]
            new_price = simulate_price(code, old_price)
            current_prices[code] = new_price

            change = round(new_price - prev_close, 2)
            rate = round((change / prev_close) * 100, 2)

            sample = {
                "code": code,
                "name": name,
                "current_price": str(new_price),
                "ask_1": str(round(new_price * random.uniform(1.001, 1.01), 2)),
                "bid_1": str(round(new_price * random.uniform(0.99, 0.999), 2)),
                "volume": str(random.randint(100, 10000)),
                "change": str(change),
                "rate": str(rate),
            }
            print("emit 확인", sample)
            socketio.emit('stock_data', sample, namespace='/')
            trigger_django_check(code, new_price)
            eventlet.sleep(0.1)
        eventlet.sleep(1)


def trigger_django_check(code, price):
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/trade/auto-execute/",
            json={"code": code, "price": price},
            timeout=3
        )
        # print(f"🔁 예약 체결 요청 → {code} @ {price}: {response.status_code}")
    except Exception as e:
        print(f"❌ Django 예약 체결 요청 실패: {e}")


@app.route('/trade-executed/', methods=['POST'])
def trade_executed():
    data = request.get_json()
    print('[체결 완료] emit:', data)
    socketio.emit('trade_executed', data, namespace='/')
    return jsonify({'message': 'emitted'})


@app.route('/notify-trade/', methods=['POST'])
def notify_trade():
    data = request.json
    account_id = data['account_id']
    trade_id = data['trade_id']

    socketio.emit('trade_update', {
        'account_id': account_id,
        'trade_id': trade_id,
    })
    return '', 200


@app.route('/')
def index():
    return "🧪 Flask + SocketIO 20종목 Mock Server"


# 좋아요, 댓글 알림
@app.route('/notify/like', methods=['POST'])
def notify_like():
    data = request.get_json()
    print('[좋아요] emit:', data)
    socketio.emit('post_liked', data)
    
    return jsonify({'status': 'ok'})

@app.route('/notify/comment', methods=['POST'])
def notify_comment():
    data = request.get_json()
    print('[댓글] emit:', data)
    socketio.emit('post_commented', data)

    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    threading.Thread(target=mock_data_loop, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000)
