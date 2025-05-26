# community/serializers.py
from rest_framework import serializers
from .models import Community, Comment
from accounts.serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthorSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['nickname', 'username', 'profile_image', 'level']

    def get_profile_image(self, obj):
        try:
            if obj.userprofile.image:
                return obj.userprofile.image.url
        except:
            pass
        return None

    def get_level(self, obj):
        try:
            return obj.userprofile.community_level or 0  # 숫자형 그대로
        except:
            return 0
        
        
class CommentSerializer(serializers.ModelSerializer):
    user = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('id', 'user', 'community', 'created_at', 'updated_at')

    def get_user(self, obj):
        try:
            profile = obj.user.userprofile
            level_point = profile.community_level or 0
            level_title = profile.level.title if profile.level else "Lv.0"
        except:
            level_point = 0
            level_title = "Lv.0"

        return {
            'username': obj.user.username,
            'nickname': obj.user.nickname,
            'level': level_point,        # 🔵 숫자형 (비교용)
            'level_title': level_title,  # 🟡 표시용
        }

class CommunitySerializer(serializers.ModelSerializer):
    user = AuthorSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True, source='comment_set')
    like_users_count = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = '__all__'
        read_only_fields = ('user', 'like_users', 'created_at', 'updated_at')

    def get_like_users_count(self, obj):
        return obj.like_users.count()

