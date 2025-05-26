from django.urls import path
from .views import OHLCView, OHLCListView
from . import views

urlpatterns = [
    path('', OHLCView.as_view()),  # POST /api/ohlc/
    path('<str:code>/<str:interval>/', OHLCListView.as_view()),  # GET /api/ohlc/005930/1m/

]