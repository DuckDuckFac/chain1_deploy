# finlife/urls.py
from django.urls import path
from .views import FinlifeProductAPIView,FinlifeUpdateAPIView,ProductLikeAPIView,MyLikedProductsAPIView,FinlifeDetailAPIView

app_name = 'finlife'

urlpatterns = [
    path('', FinlifeProductAPIView.as_view(), name='finlife_api'),
    path('update/', FinlifeUpdateAPIView.as_view(), name='update_products'),
]
urlpatterns += [
    path('like/', ProductLikeAPIView.as_view(), name='like_product'),
    path('like/mine/', MyLikedProductsAPIView.as_view(), name='my_likes'),
    path('detail/<str:fin_prdt_cd>/', FinlifeDetailAPIView.as_view(), name='product_detail'),
]