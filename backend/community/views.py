
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404

from .models import Community, Comment
from .serializers import CommunitySerializer, CommentSerializer

# 소켓서버
import requests
SOCKET_SERVER = "http://127.0.0.1:5000"

class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all().order_by('-created_at')
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)
        # ✅ 게시글 작성 시 포인트 +10
        profile = self.request.user.userprofile
        profile.total_exp += 10
        profile.usable_points += 10
        profile.update_level()
    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        community = self.get_object()
        user = request.user
        author_profile = community.user.userprofile

        if user in community.like_users.all():
            # ✅ 좋아요 취소
            community.like_users.remove(user)
        else:
            # ✅ 좋아요 추가
            community.like_users.add(user)
            author_profile.total_exp += 2
            author_profile.usable_points += 2
            author_profile.update_level()

            # 🔔 알림 전송
            try:
                requests.post(f"{SOCKET_SERVER}/notify/like", json={
                    "target_user_id": community.user.id,
                    "user_id": community.user.id,
                    "post_title": community.title,
                    "post_id": community.id,
                })
            except Exception as e:
                print("❌ 좋아요 알림 실패:", e)

        return Response({
            'liked': user in community.like_users.all(),
            'count': community.like_users.count()
        })


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(community_id=self.kwargs['community_pk'])

    def perform_create(self, serializer):
        community = get_object_or_404(Community, pk=self.kwargs['community_pk'])
        comment = serializer.save(user=self.request.user, community=community)

        # ✅ 댓글 작성 시 포인트 +5
        profile = self.request.user.userprofile
        profile.total_exp += 5
        profile.usable_points += 5
        profile.update_level()

        # 🔔 댓글 알림 전송
        try:
            requests.post(f"{SOCKET_SERVER}/notify/comment", json={
                "target_user_id": community.user.id,
                "user_id": community.user.id,
                "post_title": community.title,
                "post_id": community.id,
            })
        except Exception as e:
            print("❌ 댓글 알림 실패:", e)

    def perform_destroy(self, instance):
        instance.delete()

