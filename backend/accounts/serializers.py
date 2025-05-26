# accounts/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile,User, UserProfile, VirtualAccount
from community.models import Comment  # 댓글 모델 import
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'password', 'email', 'date_joined', 'last_login', 'is_verified']

    def create(self, validated_data):  
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # 이 부분 유지
    my_post_count = serializers.SerializerMethodField()
    my_bookmark_count = serializers.SerializerMethodField()

    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'birth_date', 'gender', 'asset', 'income', 'job',
            'interests', 'my_post_count', 'my_bookmark_count',
            'total_exp', 'usable_points', 'community_level', 'image','background_image'
                ]

    def get_my_post_count(self, obj):
        return obj.user.community_set.count()

    def get_my_bookmark_count(self, obj):
        return obj.user.like_communities.count()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # 사용자 추가 정보 포함
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'nickname': self.user.nickname,
            'email': self.user.email,
        }
        return data
    
class VirtualAccountSerializer(serializers.ModelSerializer):
    liked_stocks = serializers.SerializerMethodField()

    class Meta:
        model = VirtualAccount
        fields = ['id', 'user', 'balance', 'profit', 'liked_stocks']
        read_only_fields = ['id', 'user', 'balance', 'profit']

    def get_liked_stocks(self, obj):
        return [
            {
                'code': stock.code,
                'name': stock.name or '',  # name이 None인 경우도 대응
            }
            for stock in obj.liked_stocks.all()
        ]
    
# 예적금 상품 좋아요
class ProductLikeSerializer(serializers.Serializer):
    product_type = serializers.ChoiceField(choices=[('deposit', '예금'), ('saving', '적금')])
    fin_prdt_cd = serializers.CharField()


