import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .models import DepositProduct, SavingProduct
from rest_framework.permissions import IsAuthenticated
from accounts.models import ProductLike
from accounts.serializers import ProductLikeSerializer
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
# 금융감독원 Open API 엔드포인트
DEPOSIT_URL = 'https://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json'
SAVING_URL = 'https://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json'

PARAMS = {
    'auth': settings.FINLIFE_API_KEY,  # .env에 FINLIFE_API_KEY를 등록해야 함
    'topFinGrpNo': '030300',
    'pageNo': 1,
}

# 옵션 데이터와 기본 데이터 매핑 후 최고금리 포함시키기
def attach_rates(base_list, option_list):
    grouped = {}
    for opt in option_list:
        grouped.setdefault(opt['fin_prdt_cd'], []).append(opt)

    result = []
    for item in base_list:
        code = item['fin_prdt_cd']
        options = grouped.get(code, [])
        item['intr_rate'] = max((o.get('intr_rate') or 0.0) for o in options) if options else 0.0
        item['intr_rate2'] = max((o.get('intr_rate2') or 0.0) for o in options) if options else 0.0
        result.append(item)
    return result

# POST 요청으로 데이터 가져와 DB에 저장
class FinlifeUpdateAPIView(APIView):
    def post(self, request):
        deposit_data = requests.get(DEPOSIT_URL, params=PARAMS).json().get('result', {})
        saving_data = requests.get(SAVING_URL, params=PARAMS).json().get('result', {})

        deposit = attach_rates(deposit_data.get('baseList', []), deposit_data.get('optionList', []))
        saving = attach_rates(saving_data.get('baseList', []), saving_data.get('optionList', []))

        DepositProduct.objects.all().delete()
        SavingProduct.objects.all().delete()

        for item in deposit:
            DepositProduct.objects.update_or_create(
                fin_prdt_cd=item['fin_prdt_cd'],
                defaults={
                    'kor_co_nm': item.get('kor_co_nm', ''),
                    'fin_prdt_nm': item.get('fin_prdt_nm', ''),
                    'intr_rate': item.get('intr_rate', 0.0),
                    'intr_rate2': item.get('intr_rate2', 0.0),
                    'join_member': item.get('join_member', ''),
                    'join_way': item.get('join_way', ''),
                    'spcl_cnd': item.get('spcl_cnd', ''),
                    'mtrt_int': item.get('mtrt_int', ''),
                    'intr_rate_type_nm': item.get('intr_rate_type_nm', ''),
                    'save_trm': item.get('save_trm', ''),
                }

            )


            for item in saving:
                SavingProduct.objects.update_or_create(
                    fin_prdt_cd=item['fin_prdt_cd'],
                    defaults={
                        'kor_co_nm': item.get('kor_co_nm', ''),
                        'fin_prdt_nm': item.get('fin_prdt_nm', ''),
                        'intr_rate': item.get('intr_rate', 0.0),
                        'intr_rate2': item.get('intr_rate2', 0.0),
                        'join_member': item.get('join_member', ''),
                        'join_way': item.get('join_way', ''),
                        'spcl_cnd': item.get('spcl_cnd', ''),
                        'mtrt_int': item.get('mtrt_int', ''),
                        'intr_rate_type_nm': item.get('intr_rate_type_nm', ''),
                        'save_trm': item.get('save_trm', ''),
                    }

                )


        return Response({"message": "예적금 상품이 DB에 저장되었습니다."})
class FinlifeProductAPIView(APIView):
    def get(self, request):
        deposit_data = requests.get(DEPOSIT_URL, params=PARAMS).json().get('result', {})
        saving_data = requests.get(SAVING_URL, params=PARAMS).json().get('result', {})

        deposit = attach_rates(deposit_data.get('baseList', []), deposit_data.get('optionList', []))
        saving = attach_rates(saving_data.get('baseList', []), saving_data.get('optionList', []))

        return Response({
            'deposit': deposit,
            'saving': saving,
        })


class ProductLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProductLikeSerializer(data=request.data)
        if serializer.is_valid():
            product_type = serializer.validated_data['product_type']
            fin_prdt_cd = serializer.validated_data['fin_prdt_cd']

            # 상품이 DB에 없다면 외부 API에서 가져와 저장
            if product_type == 'deposit':
                if not DepositProduct.objects.filter(fin_prdt_cd=fin_prdt_cd).exists():
                    self.fetch_and_save_deposit(fin_prdt_cd)
            elif product_type == 'saving':
                if not SavingProduct.objects.filter(fin_prdt_cd=fin_prdt_cd).exists():
                    self.fetch_and_save_saving(fin_prdt_cd)

            # ✅ 여기서 기존 좋아요가 있는지 명확하게 체크
            like_qs = ProductLike.objects.filter(
                user=request.user,
                fin_prdt_cd=fin_prdt_cd
            )

            if like_qs.exists():
                like_qs.delete()
                return Response({'message': '좋아요 취소!'}, status=200)

            # ✅ 없으면 새로 추가
            ProductLike.objects.create(
                user=request.user,
                product_type=product_type,
                fin_prdt_cd=fin_prdt_cd
            )
            return Response({'message': '좋아요 완료!'}, status=201)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # 🔽 금감원 API에서 예금 상품 1개 검색해 저장
    def fetch_and_save_deposit(self, fin_prdt_cd):
        res = requests.get(DEPOSIT_URL, params=PARAMS).json().get('result', {})
        base_list = res.get('baseList', [])
        option_list = res.get('optionList', [])
        combined = attach_rates(base_list, option_list)

        for item in combined:
            if item['fin_prdt_cd'] == fin_prdt_cd:
                DepositProduct.objects.update_or_create(
                    fin_prdt_cd=fin_prdt_cd,
                    defaults={
                        'kor_co_nm': item.get('kor_co_nm', ''),
                        'fin_prdt_nm': item.get('fin_prdt_nm', ''),
                        'intr_rate': item.get('intr_rate', 0.0),
                        'intr_rate2': item.get('intr_rate2', 0.0),
                        'join_member': item.get('join_member', ''),
                        'join_way': item.get('join_way', ''),
                        'spcl_cnd': item.get('spcl_cnd', ''),
                        'mtrt_int': item.get('mtrt_int', ''),
                        'intr_rate_type_nm': item.get('intr_rate_type_nm', ''),
                        'save_trm': item.get('save_trm', ''),
                    }
                )
                break


    # 🔽 금감원 API에서 적금 상품 1개 검색해 저장
    def fetch_and_save_saving(self, fin_prdt_cd):
        res = requests.get(SAVING_URL, params=PARAMS).json().get('result', {})
        base_list = res.get('baseList', [])
        option_list = res.get('optionList', [])
        combined = attach_rates(base_list, option_list)

        for item in combined:
            if item['fin_prdt_cd'] == fin_prdt_cd:
                SavingProduct.objects.update_or_create(
                    fin_prdt_cd=fin_prdt_cd,
                    defaults={
                        'kor_co_nm': item.get('kor_co_nm', ''),
                        'fin_prdt_nm': item.get('fin_prdt_nm', ''),
                        'intr_rate': item.get('intr_rate', 0.0),
                        'intr_rate2': item.get('intr_rate2', 0.0),
                        'join_member': item.get('join_member', ''),
                        'join_way': item.get('join_way', ''),
                        'spcl_cnd': item.get('spcl_cnd', ''),
                        'mtrt_int': item.get('mtrt_int', ''),
                        'intr_rate_type_nm': item.get('intr_rate_type_nm', ''),
                        'save_trm': item.get('save_trm', ''),
                    }
                )
                break


    
class MyLikedProductsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        likes = ProductLike.objects.filter(user=user)

        deposit_codes = [like.fin_prdt_cd for like in likes if like.product_type == 'deposit']
        saving_codes = [like.fin_prdt_cd for like in likes if like.product_type == 'saving']

        deposit_products = DepositProduct.objects.filter(fin_prdt_cd__in=deposit_codes)
        saving_products = SavingProduct.objects.filter(fin_prdt_cd__in=saving_codes)

        print('현재 로그인 사용자:', request.user)
        print('좋아요 개수:', ProductLike.objects.filter(user=request.user).count())


        # 상품 정보를 JSON 형태로 직렬화
        def serialize_product(p, product_type):
            return {
                'kor_co_nm': p.kor_co_nm,           # 회사명
                'fin_prdt_nm': p.fin_prdt_nm,       # 상품명
                'intr_rate': p.intr_rate,           # 기본 금리
                'intr_rate2': p.intr_rate2,         # 우대 금리
                'fin_prdt_cd': p.fin_prdt_cd,        # 상품 코드
                'product_type': product_type,
            }

        return Response({
            'deposit': [serialize_product(p, 'deposit') for p in deposit_products],
            'saving': [serialize_product(p, 'saving') for p in saving_products],
        })

    
class FinlifeDetailAPIView(APIView):
    def get(self, request, fin_prdt_cd):
        product_type = request.GET.get('product_type')
        if not product_type:
            return Response({'error': 'product_type 쿼리 파라미터가 필요합니다.'}, status=400)

        product = None

        if product_type == 'deposit':
            try:
                product = DepositProduct.objects.get(fin_prdt_cd=fin_prdt_cd)
            except DepositProduct.DoesNotExist:
                self.fetch_and_save_deposit(fin_prdt_cd)
                product = DepositProduct.objects.filter(fin_prdt_cd=fin_prdt_cd).first()
        elif product_type == 'saving':
            try:
                product = SavingProduct.objects.get(fin_prdt_cd=fin_prdt_cd)
            except SavingProduct.DoesNotExist:
                self.fetch_and_save_saving(fin_prdt_cd)
                product = SavingProduct.objects.filter(fin_prdt_cd=fin_prdt_cd).first()
        else:
            return Response({'error': 'product_type은 deposit 또는 saving만 가능합니다.'}, status=400)

        if not product:
            return Response({'error': '상품을 찾을 수 없습니다.'}, status=404)

        data = {
            'kor_co_nm': product.kor_co_nm,
            'fin_prdt_nm': product.fin_prdt_nm,
            'intr_rate': product.intr_rate,
            'intr_rate2': product.intr_rate2,
            'fin_prdt_cd': product.fin_prdt_cd,
            'join_member': getattr(product, 'join_member', ''),
            'join_way': getattr(product, 'join_way', ''),
            'spcl_cnd': getattr(product, 'spcl_cnd', ''),
            'mtrt_int': getattr(product, 'mtrt_int', ''),
            'intr_rate_type_nm': getattr(product, 'intr_rate_type_nm', ''),
            'save_trm': getattr(product, 'save_trm', ''),
            'etc_note': getattr(product, 'etc_note', ''),
            'dcls_strt_day': getattr(product, 'dcls_strt_day', ''),
            'fin_co_subm_day': getattr(product, 'fin_co_subm_day', ''),
            'product_type': product_type,
        }

        return Response(data)

    def fetch_and_save_deposit(self, fin_prdt_cd):
        res = requests.get(DEPOSIT_URL, params=PARAMS).json().get('result', {})
        base_list = res.get('baseList', [])
        option_list = res.get('optionList', [])
        combined = attach_rates(base_list, option_list)

        for item in combined:
            if item['fin_prdt_cd'] == fin_prdt_cd:
                DepositProduct.objects.update_or_create(
                    fin_prdt_cd=fin_prdt_cd,
                    defaults={
                        'kor_co_nm': item.get('kor_co_nm', ''),
                        'fin_prdt_nm': item.get('fin_prdt_nm', ''),
                        'intr_rate': item.get('intr_rate', 0.0),
                        'intr_rate2': item.get('intr_rate2', 0.0),
                        'join_member': item.get('join_member', ''),
                        'join_way': item.get('join_way', ''),
                        'spcl_cnd': item.get('spcl_cnd', ''),
                        'mtrt_int': item.get('mtrt_int', ''),
                        'intr_rate_type_nm': item.get('intr_rate_type_nm', ''),
                        'save_trm': item.get('save_trm', ''),
                        'etc_note': item.get('etc_note', ''),
                        'dcls_strt_day': item.get('dcls_strt_day', ''),
                        'fin_co_subm_day': item.get('fin_co_subm_day', ''),
                        }
                )
                break

    def fetch_and_save_saving(self, fin_prdt_cd):
        res = requests.get(SAVING_URL, params=PARAMS).json().get('result', {})
        base_list = res.get('baseList', [])
        option_list = res.get('optionList', [])
        combined = attach_rates(base_list, option_list)

        for item in combined:
            if item['fin_prdt_cd'] == fin_prdt_cd:
                SavingProduct.objects.update_or_create(
                    fin_prdt_cd=fin_prdt_cd,
                    defaults={
                        'kor_co_nm': item.get('kor_co_nm', ''),
                        'fin_prdt_nm': item.get('fin_prdt_nm', ''),
                        'intr_rate': item.get('intr_rate', 0.0),
                        'intr_rate2': item.get('intr_rate2', 0.0),
                        'join_member': item.get('join_member', ''),
                        'join_way': item.get('join_way', ''),
                        'spcl_cnd': item.get('spcl_cnd', ''),
                        'mtrt_int': item.get('mtrt_int', ''),
                        'intr_rate_type_nm': item.get('intr_rate_type_nm', ''),
                        'save_trm': item.get('save_trm', ''),
                        'etc_note': item.get('etc_note', ''),
                        'dcls_strt_day': item.get('dcls_strt_day', ''),
                        'fin_co_subm_day': item.get('fin_co_subm_day', ''),
                    }
                )
                break

