from rest_framework import serializers
from accounts.models import VirtualAccount
from .models import Trade, Holding, ReservedTrade

# ✅ 가상 계좌 정보 조회용
class VirtualAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualAccount
        fields = ['id', 'user', 'balance', 'profit']
        read_only_fields = ['user', 'profit']


# 보유 종목 정보
class HoldingSerializer(serializers.ModelSerializer):
    average_price = serializers.SerializerMethodField()

    class Meta:
        model = Holding
        fields = ['code', 'name', 'quantity', 'average_price']

    def get_average_price(self, obj):
        trades = Trade.objects.filter(
            user=obj.user,
            code=obj.code,
            trade_type='BUY',
            executed=True
        )
        total_qty = sum(t.quantity for t in trades)
        total_amount = sum(t.quantity * t.executed_price for t in trades)

        if total_qty == 0:
            return 0
        return total_amount // total_qty

# 거래 기록 조회용
class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = ['id', 'user', 'code', 'name', 'price', 'quantity', 'trade_type', 'trade_time']


# 매수용
class BuyTradeSerializer(serializers.Serializer):
    code = serializers.CharField()
    price = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


# 매도용
class SellTradeSerializer(serializers.Serializer):
    code = serializers.CharField()
    price = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class ReservedTradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservedTrade
        fields = '__all__'
        read_only_fields = ['user', 'account', 'executed']


class RankingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    profile_image = serializers.SerializerMethodField()
    total_asset = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()
    return_rate = serializers.SerializerMethodField()

    class Meta:
        model = VirtualAccount
        fields = ['username', 'nickname', 'profile_image', 'total_asset', 'profit', 'return_rate']

    def get_total_asset(self, obj):
        return obj.total_asset_value

    def get_profit(self, obj):
        return obj.total_profit

    def get_return_rate(self, obj):
        return obj.return_rate

    def get_profile_image(self, obj):
        request = self.context.get('request')
        profile = getattr(obj.user, 'userprofile', None)

        if profile and profile.image:
            return request.build_absolute_uri(profile.image.url) if request else profile.image.url
        return None