from django.core.management.base import BaseCommand
from finlife.views import attach_rates, DEPOSIT_URL, SAVING_URL, PARAMS
from finlife.models import DepositProduct, SavingProduct
import requests
from django.db import transaction
from collections import OrderedDict

class Command(BaseCommand):
    help = '금감원 API에서 예적금 데이터 가져와서 DB에 저장합니다.'

    def handle(self, *args, **options):
        print("📡 금감원 API 요청 중...")
        deposit_data = requests.get(DEPOSIT_URL, params=PARAMS, timeout=10).json().get('result', {})
        saving_data = requests.get(SAVING_URL, params=PARAMS, timeout=10).json().get('result', {})

        deposit_list = attach_rates(deposit_data.get('baseList', []), deposit_data.get('optionList', []))
        saving_list = attach_rates(saving_data.get('baseList', []), saving_data.get('optionList', []))

        deposit_objs = []
        saving_objs = []
        # 중복 제거용 dict
        deposit_dict = OrderedDict()
        for item in deposit_list:
            code = item['fin_prdt_cd']
            if code not in deposit_dict:
                deposit_dict[code] = DepositProduct(
                    fin_prdt_cd=code,
                    kor_co_nm=item.get('kor_co_nm', ''),
                    fin_prdt_nm=item.get('fin_prdt_nm', ''),
                    intr_rate=item.get('intr_rate', 0.0),
                    intr_rate2=item.get('intr_rate2', 0.0),
                    join_member=item.get('join_member', ''),
                    join_way=item.get('join_way', ''),
                    spcl_cnd=item.get('spcl_cnd', ''),
                    mtrt_int=item.get('mtrt_int', ''),
                    intr_rate_type_nm=item.get('intr_rate_type_nm', ''),
                    save_trm=item.get('save_trm', ''),
                    etc_note=item.get('etc_note', ''),             
                    dcls_strt_day=item.get('dcls_strt_day', ''),    
                    fin_co_subm_day=item.get('fin_co_subm_day', '')
                )

        deposit_objs = list(deposit_dict.values())

        saving_dict = OrderedDict()
        for item in saving_list:
            code = item['fin_prdt_cd']
            if code not in saving_dict:
                saving_dict[code] = SavingProduct(
                    fin_prdt_cd=code,
                    kor_co_nm=item.get('kor_co_nm', ''),
                    fin_prdt_nm=item.get('fin_prdt_nm', ''),
                    intr_rate=item.get('intr_rate', 0.0),
                    intr_rate2=item.get('intr_rate2', 0.0),
                    join_member=item.get('join_member', ''),
                    join_way=item.get('join_way', ''),
                    spcl_cnd=item.get('spcl_cnd', ''),
                    mtrt_int=item.get('mtrt_int', ''),
                    intr_rate_type_nm=item.get('intr_rate_type_nm', ''),
                    save_trm=item.get('save_trm', ''),
                    etc_note=item.get('etc_note', ''),             
                    dcls_strt_day=item.get('dcls_strt_day', ''),    
                    fin_co_subm_day=item.get('fin_co_subm_day', '')
                )

        saving_objs = list(saving_dict.values())

        with transaction.atomic():
            DepositProduct.objects.all().delete()
            SavingProduct.objects.all().delete()
            DepositProduct.objects.bulk_create(deposit_objs)
            SavingProduct.objects.bulk_create(saving_objs)
        print(f"✅ 저장 완료: 예금 {len(deposit_objs)}개, 적금 {len(saving_objs)}개")
