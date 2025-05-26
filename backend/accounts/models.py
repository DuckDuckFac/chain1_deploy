from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from stock.models import Stock
from community.models import CommunityLevel 
import uuid

# Create your models here.
class User(AbstractUser):
    nickname = models.CharField(max_length=10, unique=True)
    is_verified = models.BooleanField(default=False)
    email_verify_code = models.UUIDField(default=uuid.uuid4)

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    asset = models.CharField(max_length=20, blank=True, null=True)
    income = models.CharField(max_length=20, blank=True, null=True)
    job = models.CharField(max_length=20, blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    
    #프로필사진
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    background_image = models.ImageField(upload_to='backgrounds/', blank=True, null=True)

    total_exp = models.IntegerField(default=0) 
    usable_points = models.IntegerField(default=0) 
    community_level = models.IntegerField(default=1)

    def update_level(self):
        level_obj = (
            CommunityLevel.objects
            .filter(min_score__lte=self.total_exp)
            .order_by('-min_score')
            .first()
        )
        if level_obj:
            self.community_level = level_obj.level
        else:
            self.community_level = 1
        self.save()

class VirtualAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    initial_balance = models.DecimalField(max_digits=15, decimal_places=2, default=10000000)  # 초기 자본
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=10000000)  # 현재 현금
    profit = models.IntegerField(default=0)

    liked_stocks = models.ManyToManyField(
        Stock,
        related_name="liked_by_users",
        blank=True
    )

    def __str__(self):
        return f"{self.user.username}의 계좌"

    @property
    def total_asset_value(self):
        """
        현금 + 보유 주식 평가금액 (현재가 기반)
        """
        total = float(self.balance)
        for holding in self.holding_set.all():
            total += float(holding.quantity) * float(holding.get_current_price())
        return round(total, 2)

    @property
    def total_profit(self):
        """
        현재 총 자산 - 초기 자본
        """
        return round(self.total_asset_value - float(self.initial_balance), 2)

    @property
    def return_rate(self):
        """
        수익률 (%)
        """
        if self.initial_balance == 0:
            return 0.0
        return round((self.total_profit / float(self.initial_balance)) * 100, 2)

class ProductLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_type = models.CharField(max_length=10, choices=[('deposit', '예금'), ('saving', '적금')])
    fin_prdt_cd = models.CharField(max_length=20)

    class Meta:
        unique_together = ('user', 'product_type', 'fin_prdt_cd')

#알람
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    route_name = models.CharField(max_length=50, null=True, blank=True)
    route_params = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)


