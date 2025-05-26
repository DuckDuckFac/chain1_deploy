from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from accounts.models import UserProfile
from .gpt import ask_gpt
import requests  # 💡 금감원 API 호출용
from django.conf import settings


class ChatbotAPIView(APIView):
    permission_classes = [AllowAny]

    def get_real_products(self):
        """
        내부 /finlife/ API에서 예금 상품 20개 가져와 GPT용 필드로 정제
        """
        try:
            response = requests.get("http://localhost:8000/finlife/")
            data = response.json()
            deposit_list = data.get("deposit", [])[:100]

            product_list = [{
                "fin_prdt_cd": item["fin_prdt_cd"],
                "kor_co_nm": item["kor_co_nm"],
                "fin_prdt_nm": item["fin_prdt_nm"],
                "intr_rate": item["intr_rate"],
                "intr_rate2": item["intr_rate2"],
                'join_member': item['join_member'],
                'join_way': item['join_way'],
                'spcl_cnd': item['spcl_cnd'],
                'mtrt_int': item['mtrt_int'],
            } for item in deposit_list]
            for item in deposit_list:
                print(item)
            return product_list
        except Exception as e:
            print("❌ 상품 불러오기 실패:", e)
            return []

    def post(self, request):
        message = request.data.get("message", "")
        user = request.user if request.user.is_authenticated else None

        # ✅ 1. 비로그인 사용자
        if not user:
            reply = ask_gpt(message, mode="guest")
            return Response({
                "text": reply,
                "login_required": True
            })

        # ✅ 2. 로그인은 했지만 금융정보가 없는 사용자
        try:
            profile = user.userprofile
            has_info = profile.asset and profile.income and profile.job
        except UserProfile.DoesNotExist:
            profile = None
            has_info = False

        if not has_info:
            reply = ask_gpt(message, mode="no_profile")
            return Response({
                "text": reply,
                "need_profile": True,
                "link": "/accounts/profile/update/"
            })

        # ✅ 3. 금융정보 입력 완료된 사용자 → 실제 금감원 상품 추천
        product_list = self.get_real_products()
        reply = ask_gpt(message, user_profile=profile, mode="detail", product_list=product_list)
        if not reply:
            return Response({"text": "⚠️ GPT 응답이 비어 있습니다."}, status=500)
        return Response({ "text": reply })
