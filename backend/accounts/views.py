# accounts/views.py
import requests
from django.conf import settings
from django.shortcuts import redirect
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView, View
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from .models import UserProfile, VirtualAccount, Notification
from .serializers import UserSerializer, UserProfileSerializer
from ohlc.models import OHLC 
from rest_framework.decorators import action,api_view,permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from urllib.parse import urlencode  
from django.http import JsonResponse
from django.db.models import Q
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
User = get_user_model()
from .utils import send_verification_email

# 회원가입
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(**serializer.validated_data)
            UserProfile.objects.create(user=user)
            login(request, user)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# 비밀번호, 닉네임 수정
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

# 로그인
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response(UserSerializer(user).data)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


# 로그아웃
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


# 프로필 조회/수정
class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# 회원탈퇴퇴
class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({'message': '회원 탈퇴가 완료되었습니다.'}, status=status.HTTP_204_NO_CONTENT)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer  

# 아이디 중복 확인 체크
@api_view(['GET'])
def check_username(request):
    username = request.GET.get('username')
    exists = User.objects.filter(username=username).exists()
    return Response({'exists': exists})

@api_view(['GET'])
def check_nickname(request):
    nickname = request.GET.get('nickname')
    exists = User.objects.filter(nickname=nickname).exists()
    return Response({'exists': exists})


# interest 수정
@api_view(['PATCH'])
def update_interests(request, pk):
    try:
        profile = UserProfile.objects.get(pk=pk)
    except UserProfile.DoesNotExist:
        return Response({'error': '프로필 없음'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

#배경이미지
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def reset_background_image(request, pk):
    try:
        profile = UserProfile.objects.get(pk=pk, user=request.user)
    except UserProfile.DoesNotExist:
        return Response({'error': '프로필이 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)

    profile.background_image = None
    profile.save()
    return Response({'message': '기본 배경으로 초기화되었습니다.'}, status=status.HTTP_200_OK)

# 닉네임 기반 조회
@api_view(['GET'])
@permission_classes([AllowAny])
def get_profile_by_nickname(request, nickname):
    try:
        user = User.objects.get(nickname=nickname)
        profile = UserProfile.objects.get(user=user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': '유저를 찾을 수 없습니다.'}, status=404)
    except UserProfile.DoesNotExist:
        return Response({'error': '프로필이 없습니다.'}, status=404)
    

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    if not user.check_password(current_password):
        return Response({'detail': '현재 비밀번호가 틀렸습니다.'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    return Response({'detail': '비밀번호가 변경되었습니다.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_current_password(request):
    user = request.user
    password = request.data.get('current_password')

    if user.check_password(password):
        return Response({'valid': True})
    else:
        return Response({'valid': False}, status=400)
    

# 카카오 로그인
class KakaoLoginCallback(View):
    def get(self, request):
        code = request.GET.get('code')
        redirect_uri = 'http://localhost:8000/accounts/kakao/callback/'

        token_url = 'https://kauth.kakao.com/oauth/token'
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': settings.KAKAO_REST_API_KEY,
            'redirect_uri': redirect_uri,
            'code': code,
        }

        token_response = requests.post(token_url, data=token_data).json()
        access_token = token_response.get('access_token')

        profile_url = 'https://kapi.kakao.com/v2/user/me'
        headers = {'Authorization': f'Bearer {access_token}'}
        profile_response = requests.get(profile_url, headers=headers).json()

        kakao_id = profile_response['id']
        email = profile_response['kakao_account'].get('email', f'{kakao_id}@kakao.com')
        nickname = email.split('@')[0]
        
        # ✅ nickname 포함해서 유저 생성
        user, _ = User.objects.get_or_create(
            username=email,
            defaults={'email': email, 'nickname': nickname}
        )

        # 프로필도 생성
        UserProfile.objects.get_or_create(user=user)

        refresh = RefreshToken.for_user(user)
        query = urlencode({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })

        return redirect(f'http://localhost:5173/accounts/kakao/callback/?{query}')

class GoogleLoginCallback(View):
    def get(self, request):
        code = request.GET.get('code')
        redirect_uri = 'http://localhost:8000/accounts/google/login/callback/'

        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'code': code,
        }

        token_response = requests.post(token_url, data=token_data).json()
        access_token = token_response.get('access_token')
        if not access_token:
            return JsonResponse({'error': 'access_token 없음', 'details': token_response}, status=400)

        # 사용자 정보 요청
        user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        profile_response = requests.get(user_info_url, headers=headers).json()

        email = profile_response.get('email')
        nickname_raw = profile_response.get('name') or email.split('@')[0]

        def generate_unique_nickname(base):
            nickname = base
            counter = 1
            while User.objects.filter(nickname=nickname).exists():
                nickname = f"{base}{counter}"
                counter += 1
            return nickname

        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'nickname': generate_unique_nickname(nickname_raw)
            }
        )
        UserProfile.objects.get_or_create(user=user)

        refresh = RefreshToken.for_user(user)
        query = urlencode({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })
        return redirect(f'http://localhost:5173/accounts/google/callback/?{query}')

class NaverLoginCallback(View):
    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')

        # 1. access_token 요청
        token_url = 'https://nid.naver.com/oauth2.0/token'
        token_params = {
            'grant_type': 'authorization_code',
            'client_id': settings.NAVER_CLIENT_ID,
            'client_secret': settings.NAVER_CLIENT_SECRET,
            'code': code,
            'state': state,
        }
        token_response = requests.get(token_url, params=token_params).json()
        access_token = token_response.get('access_token')

        if not access_token:
            return JsonResponse({'error': 'access_token 없음', 'details': token_response}, status=400)

        # 2. 사용자 정보 요청
        headers = {'Authorization': f'Bearer {access_token}'}
        profile_url = 'https://openapi.naver.com/v1/nid/me'
        profile_response = requests.get(profile_url, headers=headers).json()

        if profile_response.get('resultcode') != '00':
            return JsonResponse({'error': '네이버 사용자 정보 조회 실패'}, status=400)

        naver_user = profile_response['response']
        email = naver_user.get('email')
        user_id = naver_user.get('id')

        # 3. 닉네임 설정 (중복 방지 포함)
        base_nickname = naver_user.get('nickname') or (email.split('@')[0] if email else f'naver_{user_id[:6]}')

        def generate_unique_nickname(base):
            nickname = base
            counter = 1
            while User.objects.filter(nickname=nickname).exists():
                nickname = f"{base}{counter}"
                counter += 1
            return nickname

        unique_nickname = generate_unique_nickname(base_nickname)

        # 4. username과 email 설정
        if not email:
            email = f'{user_id}@naver.local'
        username = email

        # 5. 유저 생성 또는 가져오기
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'nickname': unique_nickname}
        )
        UserProfile.objects.get_or_create(user=user)

        # 6. JWT 발급 후 리디렉션
        refresh = RefreshToken.for_user(user)
        query = urlencode({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })
        return redirect(f'http://localhost:5173/accounts/naver/callback/?{query}')


# 알람
class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = request.user.notifications.order_by('-timestamp')
        data = [
            {
                "message": n.message,
                "route_name": n.route_name,
                "route_params": n.route_params,
                "timestamp": n.timestamp,
                "read": n.read,
            }
            for n in notifications
        ]
        return Response(data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_notifications_read(request):
    ids = request.data.get('ids', [])
    if not isinstance(ids, list):
        return Response({'error': 'ids must be a list'}, status=400)

    updated_count = Notification.objects.filter(user=request.user, id__in=ids).update(read=True)
    return Response({'updated': updated_count}, status=200)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, pk):
    notif = get_object_or_404(Notification, id=pk, user=request.user)
    notif.delete()
    return Response({'message': '알림이 삭제되었습니다.'}, status=204)



@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def reset_profile_image(request, pk):
    try:
        profile = UserProfile.objects.get(pk=pk)
    except UserProfile.DoesNotExist:
        return Response({'error': '프로필이 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)

    # 이미지 필드를 None으로 설정 (또는 기본 경로 문자열로 지정 가능)
    profile.image = None
    profile.save()
    return Response({'message': '기본 이미지로 초기화되었습니다.'}, status=status.HTTP_200_OK)


# 이메일 인증
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        UserProfile.objects.get_or_create(user=user)

        send_verification_email(user)  # UUID 기반 링크 전송
        login(request, user)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            "message": "가입 성공! 이메일을 확인해주세요.",
            "access": access_token,
            "refresh": refresh_token,
            "user": UserSerializer(user).data
        }, status=201)
    return Response(serializer.errors, status=400)



from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, code):  # <- URL에서 code를 받음
    try:
        user = User.objects.get(email_verify_code=code)
    except User.DoesNotExist:
        return Response({"message": "잘못된 인증 코드입니다."}, status=400)

    if user.is_verified:
        return Response({"message": "이미 인증된 계정입니다."})

    user.is_verified = True
    user.save()
    return Response({"message": "이메일 인증이 완료되었습니다."}, status=200)
