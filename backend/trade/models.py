from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import VirtualAccount
from ohlc.models import OHLC

User = get_user_model()



class Trade(models.Model):
    BUY = 'BUY'
    SELL = 'SELL'
    TRADE_TYPE_CHOICES = [(BUY, '매수'), (SELL, '매도')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trades')
    account = models.ForeignKey('accounts.VirtualAccount', on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=30)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=15, decimal_places=2)  # 거래 단가
    total_price = models.DecimalField(max_digits=20, decimal_places=2)  # 수량 * 단가
    trade_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account.user.username} - {self.trade_type} - {self.stock_code}"
    
class Holding(models.Model):
    account = models.ForeignKey('accounts.VirtualAccount', on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=30)
    quantity = models.PositiveIntegerField()
    average_price = models.DecimalField(max_digits=15, decimal_places=2)

    def get_current_price(self):
        # 가장 최근 1분봉 close 가격을 현재가로 사용
        latest_price = OHLC.objects.filter(code=self.code, interval="1m").order_by('-timestamp').first()
        return latest_price.close if latest_price else 0



class ReservedTrade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(VirtualAccount, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=30)
    target_price = models.DecimalField(max_digits=15, decimal_places=2)
    quantity = models.PositiveIntegerField()
    trade_type = models.CharField(max_length=4, choices=[('BUY', '매수'), ('SELL', '매도')])
    created_at = models.DateTimeField(auto_now_add=True)
    executed = models.BooleanField(default=False)