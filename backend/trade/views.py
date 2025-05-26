from decimal import Decimal
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import Trade, Holding, ReservedTrade
from ohlc.models import OHLC
from .serializers import TradeSerializer, RankingSerializer
from accounts.models import VirtualAccount
from accounts.serializers import VirtualAccountSerializer
import logging, requests, threading
from stock.models import Stock
from rest_framework.permissions import IsAuthenticatedOrReadOnly

logger = logging.getLogger(__name__)

class TradeListAPIView(generics.ListAPIView):
    serializer_class = TradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Trade.objects.filter(user=user).order_by('-trade_time')

        # 🔍 필터 파라미터 받기
        trade_type = self.request.query_params.get('type')
        keyword = self.request.query_params.get('keyword')

        if trade_type in ['buy', 'sell']:
            queryset = queryset.filter(trade_type=trade_type)

        if keyword:
            queryset = queryset.filter(name__icontains=keyword)

        return queryset



class MyVirtualAccountAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        account, created = VirtualAccount.objects.get_or_create(user=request.user)
        serializer = VirtualAccountSerializer(account)
        return Response(serializer.data)


# ✅ 공통 거래 처리 함수
def process_trade(user, code, name, quantity, price, trade_type):
    account = get_object_or_404(VirtualAccount, user=user)
    price = Decimal(str(price))
    total_price = Decimal(quantity) * Decimal(str(price))

    if trade_type == 'buy':
        if account.balance < total_price:
            return {"error": "잔액이 부족합니다."}

        holding = Holding.objects.filter(account=account, code=code).first()
        if not holding:
            holding = Holding.objects.create(
            account=account,
            code=code,
            name=name,
            quantity=0,
            average_price=Decimal('0.0')
    )

        total_qty = holding.quantity + quantity
        prev_total = Decimal(holding.quantity) * Decimal(str(holding.average_price))  # 🔍 float → Decimal 변환
        new_total = Decimal(quantity) * price
        new_avg = (prev_total + new_total) / total_qty
        holding.quantity = total_qty
        holding.average_price = new_avg
        holding.name = name
        holding.save()

        account.balance -= total_price
        account.save()

    elif trade_type == 'sell':
        holding = Holding.objects.filter(account=account, code=code).first()
        if not holding or holding.quantity < quantity:
            return {"error": "보유 수량 부족"}

        holding.quantity -= quantity
        if holding.quantity == 0:
            holding.delete()
        else:
            holding.save()

        account.balance += total_price
        account.profit += total_price
        account.save()

    else:
        return {"error": "잘못된 거래 유형입니다."}

    Trade.objects.create(
        user=user,
        account=account,
        trade_type=trade_type,
        code=code,
        name=name,
        quantity=quantity,
        price=price,
        total_price=total_price
    )

    return {
        "success": True,
        "message": f"{trade_type.upper()} 거래 완료",
        "code": code,
        "name": name,
        "quantity": holding.quantity if trade_type == 'buy' else quantity,
        "average_price": float(holding.average_price) if trade_type == 'buy' else None,
        "balance": account.balance
    }


# 🔻 보유 종목 리스트
class HoldingListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        account = get_object_or_404(VirtualAccount, user=request.user)
        holdings = Holding.objects.filter(account=account, quantity__gt=0)

        result = [
            {
                "code": h.code,
                "name": h.name,
                "quantity": h.quantity,
                "average_price": h.average_price
            }
            for h in holdings
        ]
        return Response(result)


# 🔻 매수 API
class BuyStockView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        result = process_trade(
            user=request.user,
            code=data.get('code'),
            name=data.get('name', ''),
            quantity=int(data.get('quantity', 0)),
            price=float(data.get('price', 0)),
            trade_type='buy'
        )

        if result.get("error"):
            return Response({"detail": result["error"]}, status=400)
        return Response(result, status=201)


# 🔻 매도 API
class SellStockView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        result = process_trade(
            user=request.user,
            code=data.get('code'),
            name=data.get('name', ''),
            quantity=int(data.get('quantity', 0)),
            price=float(data.get('price', 0)),
            trade_type='sell'
        )

        if result.get("error"):
            return Response({"detail": result["error"]}, status=400)
        return Response(result, status=201)

class AccountSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        account, _ = VirtualAccount.objects.get_or_create(user=user)
        holdings = Holding.objects.filter(account=account)

        holding_data = []
        total_eval = 0

        for h in holdings:
            # 최신 OHLC close 값 가져오기
            latest_ohlc = OHLC.objects.filter(code=h.code, interval='1m').order_by('-timestamp').first()
            if not latest_ohlc:
                continue
            current_price = latest_ohlc.close

            eval_amt = h.quantity * current_price
            profit_amt = (current_price - h.average_price) * h.quantity
            rate = round((profit_amt / (h.average_price * h.quantity)) * 100, 2) if h.average_price > 0 else 0.0

            holding_data.append({
                "code": h.code,
                "name": h.name,
                "quantity": h.quantity,
                "average_price": h.average_price,
                "current_price": current_price,
                "evaluation_amount": eval_amt,
                "profit": profit_amt,
                "rate": rate
            })

            total_eval += eval_amt

        result = {
            "balance": account.balance,
            "profit": account.profit,
            "total_evaluation": total_eval,
            "total_asset": account.balance + total_eval,
            "holdings": holding_data
        }

        return Response(result)
    
# 매수 매도 예약
class ReserveTradeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        ReservedTrade.objects.create(
            user=request.user,
            account=request.user.virtualaccount,
            code=data['code'],
            name=data['name'],
            target_price=data['target_price'],
            quantity=data['quantity'],
            trade_type=data['trade_type']
        )
        return Response({"message": "예약 거래가 등록되었습니다."}, status=201)
    
def check_reserved_trades(code, current_price):
    reservations = ReservedTrade.objects.filter(code=code, executed=False)

    def handle_one(r):
        try:
            if (r.trade_type == 'BUY' and current_price <= r.target_price) or \
               (r.trade_type == 'SELL' and current_price >= r.target_price):
                r.executed = True
                r.save()
                result = process_trade(
                    user=r.user,
                    code=r.code,
                    name=r.name,
                    quantity=r.quantity,
                    price=r.target_price,
                    trade_type=r.trade_type.lower()
                )

                # result로 알림 emit
                print('📤 Flask로 체결 알림 전송 시도') 
                requests.post(
                    "http://localhost:5000/trade-executed/",
                    json={
                        "user_id": r.user.id,
                        "code": r.code,
                        "name": r.name,
                        "quantity": r.quantity,
                        "trade_type": r.trade_type,
                        "avg_price": float(result.get("average_price")) if result.get("average_price") else None,
                        "price": float(r.target_price),
                    },
                    timeout=2
                )
        except Exception as e:
            logger.error(f"[체결 중 예외 발생] 예약ID: {r.id}, 예외: {e}")


    for r in reservations:
        threading.Thread(target=handle_one, args=(r,)).start()


class ReservedTradeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, code):
        user = request.user
        reserves = ReservedTrade.objects.filter(user=user, code=code).order_by('-id')
        result = [
            {
                "id": r.id,
                "trade_type": r.trade_type,
                "target_price": r.target_price,
                "quantity": r.quantity,
                "executed": r.executed
            }
            for r in reserves
        ]
        return Response(result)
    
class ReservedTradeDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, code, pk):
        reserve = get_object_or_404(ReservedTrade, pk=pk, user=request.user, executed=False)
        reserve.delete()
        return Response({"message": "예약 거래가 삭제되었습니다."}, status=204)
    

@api_view(['POST'])
@permission_classes([AllowAny])  # 내부 전용이라면 인증 제외
def auto_execute_reserved_trades(request):
    code = request.data.get('code')
    price = request.data.get('price')

    if not code or price is None:
        return Response({"error": "code 또는 price 누락"}, status=400)

    try:
        check_reserved_trades(code, float(price))
        return Response({"message": "체결 시도 완료"}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
# 체결 처리 알림
def notify_trade_execution(account_id, trade_id):
    data = {
        'account_id': account_id,
        'trade_id': trade_id,
    }
    requests.post('http://FLASK_SERVER_URL/notify-trade/', json=data)


# 즉시 매수
class BuyNowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code")
        quantity = int(request.data.get("quantity", 0))
        user = request.user
        stock = OHLC.objects.filter(code=code, interval="1m").order_by("-timestamp").first()
        stock_obj = Stock.objects.filter(code=code).first()
        stock_name = stock_obj.name if stock_obj else "이름 없음"

        # stock.close 값이 None인지도 체크해야 함
        if not stock or stock.close is None:
            return Response({"detail": "현재가를 찾을 수 없습니다."}, status=400)

        result = process_trade(user, code, stock_name, quantity, float(stock.close), 'buy')
        if result.get("error"):
            return Response({"detail": result["error"]}, status=400)
        return Response(result, status=201)

# 즉시 매도
class SellNowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code")
        quantity = int(request.data.get("quantity", 0))
        user = request.user
        stock = OHLC.objects.filter(code=code, interval="1m").order_by("-timestamp").first()
        stock_obj = Stock.objects.filter(code=code).first()
        stock_name = stock_obj.name if stock_obj else "이름 없음"

        if not stock or stock.close is None:
            return Response({"detail": "현재가를 찾을 수 없습니다."}, status=400)

        result = process_trade(user, code, stock_name, quantity, float(stock.close), 'sell')
        if result.get("error"):
            return Response({"detail": result["error"]}, status=400)
        return Response(result, status=201)

# 좋아요
class ToggleLikeStockView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, code):
        account = VirtualAccount.objects.get(user=request.user)
        
        # Stock 존재 여부를 먼저 확인하되, 없으면 liked=False로 처리
        try:
            stock = Stock.objects.get(code=code)
            liked = account.liked_stocks.filter(id=stock.id).exists()
        except Stock.DoesNotExist:
            liked = False  # 종목이 DB에 없으면 관심 종목일 수 없음
        
        return Response({'liked': liked})

    def post(self, request, code):
        try:
            name = request.data.get("name", "")  # 🔹 Vue에서 넘겨받은 name
            stock, _ = Stock.objects.get_or_create(code=code)
            
            # 🔸 Stock 모델에 name이 없으면 업데이트
            if not stock.name and name:
                stock.name = name
                stock.save()

            account = VirtualAccount.objects.get(user=request.user)
            if account.liked_stocks.filter(id=stock.id).exists():
                account.liked_stocks.remove(stock)
                liked = False
            else:
                account.liked_stocks.add(stock)
                liked = True
            return Response({'liked': liked})
        except Stock.DoesNotExist:
            return Response({'detail': '종목이 존재하지 않습니다.'}, status=404)
        

class RankingAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        accounts = VirtualAccount.objects.select_related('user').all()
        sorted_accounts = sorted(accounts, key=lambda x: x.return_rate, reverse=True)
        serializer = RankingSerializer(sorted_accounts, many=True, context={'request': request})
        return Response(serializer.data)
    
class PointExchangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        profile = user.userprofile
        account = user.virtualaccount

        point_amount = int(request.data.get('points', 0))
        rate = 10000  # 1포인트 = 1만원

        if profile.usable_points < point_amount:
            return Response({"error": "포인트 부족"}, status=400)

        exchange_amount = point_amount * rate

        # ✅ 포인트 차감
        profile.usable_points -= point_amount
        profile.save()

        # ✅ 자산 증가 (잔고 + 초기 자본)
        account.balance += exchange_amount
        account.initial_balance += exchange_amount
        account.save()

        return Response({
            "message": f"{point_amount}포인트를 {exchange_amount:,}원으로 교환 완료",
            "usable_points": profile.usable_points,
            "balance": account.balance,
            "initial_balance": account.initial_balance,
        })
