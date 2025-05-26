import redis
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OHLC
from .serializers import OHLCSerializer
from django.utils.dateparse import parse_datetime
from rest_framework.decorators import api_view


class OHLCView(APIView):
    def post(self, request):
        print('🔥 POST 요청 수신:', request.data)
        serializer = OHLCSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            print('✅ 저장됨:', instance)
            return Response(serializer.data, status=201)
        print('❌ 유효성 실패:', serializer.errors)
        return Response(serializer.errors, status=400)

class OHLCListView(APIView):
    def get(self, request, code, interval):
        queryset = OHLC.objects.filter(code=code, interval=interval).order_by('timestamp')
        serializer = OHLCSerializer(queryset, many=True)
        return Response(serializer.data)
    
