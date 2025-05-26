from django.db import models

# 예금 상품 모델
class DepositProduct(models.Model):
    fin_prdt_cd = models.CharField(max_length=20, unique=True)  # 상품 코드
    kor_co_nm = models.CharField(max_length=100)  # 은행 이름
    fin_prdt_nm = models.CharField(max_length=100)  # 상품 이름
    intr_rate = models.FloatField(default=0.0)  # 기본 금리
    intr_rate2 = models.FloatField(default=0.0)  # 최고 금리


 # ✅ 상세 정보 필드 추가
    join_member = models.TextField(blank=True, null=True)
    join_way = models.TextField(blank=True, null=True)
    spcl_cnd = models.TextField(blank=True, null=True)
    mtrt_int = models.TextField(blank=True, null=True)
    intr_rate_type_nm = models.CharField(max_length=100, blank=True, null=True)
    save_trm = models.CharField(max_length=10, blank=True, null=True)
    etc_note = models.TextField(blank=True, null=True)
    dcls_strt_day = models.CharField(max_length=20, blank=True, null=True)
    fin_co_subm_day = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"[예금] {self.kor_co_nm} - {self.fin_prdt_nm}"


# 적금 상품 모델
class SavingProduct(models.Model):
    fin_prdt_cd = models.CharField(max_length=20, unique=True)
    kor_co_nm = models.CharField(max_length=100)
    fin_prdt_nm = models.CharField(max_length=100)
    intr_rate = models.FloatField(default=0.0)
    intr_rate2 = models.FloatField(default=0.0)

     # ✅ 상세 정보 필드 추가
    join_member = models.TextField(blank=True, null=True)
    join_way = models.TextField(blank=True, null=True)
    spcl_cnd = models.TextField(blank=True, null=True)
    mtrt_int = models.TextField(blank=True, null=True)
    intr_rate_type_nm = models.CharField(max_length=100, blank=True, null=True)
    save_trm = models.CharField(max_length=10, blank=True, null=True)
    etc_note = models.TextField(blank=True, null=True)
    dcls_strt_day = models.CharField(max_length=20, blank=True, null=True)
    fin_co_subm_day = models.CharField(max_length=20, blank=True, null=True)


    def __str__(self):
        return f"[적금] {self.kor_co_nm} - {self.fin_prdt_nm}"
