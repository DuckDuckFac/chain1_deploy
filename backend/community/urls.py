# community/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import CommunityViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'communities', CommunityViewSet)

comments_router = NestedDefaultRouter(router, r'communities', lookup='community')
comments_router.register(
    r'comments', 
    CommentViewSet, 
    basename='community-comments'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(comments_router.urls)),
]
