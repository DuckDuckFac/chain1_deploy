from django.urls import path
from . import views

urlpatterns = [
    path('liked/', views.LikedStockListView.as_view(), name='liked-stocks'),
]