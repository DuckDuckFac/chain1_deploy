from django.urls import path
from .views import KakaoBankSearchAPIView

urlpatterns = [
    path('bank-info/', KakaoBankSearchAPIView.as_view(), name='bank-info'),
]