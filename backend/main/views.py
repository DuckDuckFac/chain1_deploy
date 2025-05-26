from django.http import JsonResponse
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
import json
import os

class KakaoBankSearchAPIView(APIView):
    def get(self, request):
        # 정적 파일(data.json)에서 불러오기
        json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'data.json')
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)

        return Response({
            "mapInfo": data["mapInfo"],
            "bankInfo": data["bankInfo"],
            "apiKey": settings.KAKAO_MAP_API,
            "restApiKey": settings.KAKAO_MAP_REST_API,
        })
