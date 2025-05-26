# accounts/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    
)
from .views import MyTokenObtainPairView


app_name = 'accounts'

router = DefaultRouter()
router.register(r'profile', views.UserProfileViewSet, basename='profile')
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('profile-by-nickname/<str:nickname>/', views.get_profile_by_nickname),
    path('profile/<int:pk>/interests/', views.update_interests),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('delete/', views.DeleteAccountView.as_view(), name='delete'),
    path('check-username/', views.check_username),
    path('check-nickname/', views.check_nickname),
    path('change-password/', views.change_password, name='change_password'),
    path('check-password/', views.check_current_password),
    path('', include(router.urls)),
    path('notifications/', views.NotificationListAPIView.as_view(), name='notification'),
    path('profile/<int:pk>/reset-image/', views.reset_profile_image, name='reset-profile-image'),
    path('profile/<int:pk>/reset-background/', views.reset_background_image),

    path('kakao/callback/', views.KakaoLoginCallback.as_view(), name='kakao_callback'),

    path('google/login/callback/', views.GoogleLoginCallback.as_view(), name='google_callback'),

    path('naver/login/callback/', views.NaverLoginCallback.as_view(), name='naver-login-callback'),

    #이메일
    path('register/', views.register),
    path('verify-email/<uuid:code>/', views.verify_email),
]
urlpatterns += [
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark-notifications-read'),
    path('notifications/<int:pk>/', views.delete_notification, name='delete-notification'),
]