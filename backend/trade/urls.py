from django.urls import path
from . import views

app_name = 'trade'

urlpatterns = [
    # 🔹 가상 계좌 조회
    path('account/', views.MyVirtualAccountAPIView.as_view(), name='account'),

    # 🔹 전체 거래 내역 조회
    path('trades/', views.TradeListAPIView.as_view(), name='trades'),

    # 🔹 매수 / 매도
    path('buy-now/', views.BuyStockView.as_view(), name='buy-now'),
    path('sell-now/', views.SellStockView.as_view(), name='sell-now'),

    # 🔹 보유 종목 리스트
    path('holdings/', views.HoldingListView.as_view(), name='holdings'),

    # 요약
    path('summary/', views.AccountSummaryAPIView.as_view(), name='summary'),

    # 예약
    path('reserve/', views.ReserveTradeView.as_view(), name='reserve'),
    path('reserve/<str:code>/', views.ReservedTradeListView.as_view(), name='reserve-list'),
    path('reserve/<str:code>/<int:pk>/', views.ReservedTradeDeleteView.as_view(), name='reserve-delete'),

    # 체결
    path('auto-execute/', views.auto_execute_reserved_trades, name='auto-execute'),

    # 좋아요
    path('like/<str:code>/', views.ToggleLikeStockView.as_view(), name='like-stock'),

    # 랭킹
    path('ranking/', views.RankingAPIView.as_view(), name='ranking'),

    # 교환
    path('exchange/', views.PointExchangeAPIView.as_view(), name='exchange'),
]
