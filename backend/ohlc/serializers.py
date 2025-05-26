from rest_framework import serializers
from .models import OHLC

class OHLCSerializer(serializers.ModelSerializer):
    class Meta:
        model = OHLC
        fields = '__all__'