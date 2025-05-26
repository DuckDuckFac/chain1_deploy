from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import UserProfile
# from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # model = User
        model = get_user_model()
        fields = ('username','nickname','email')
        labels = {
            'username': '아이디',
            'nickname': '닉네임',
            'email': '이메일 주소',
        }


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        # model = User
        model = get_user_model()
        fields = ('first_name', 'nickname', 'email',)

#사용자 금융 정보 기입 폼
# accounts/forms.py

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['birth_date', 'gender', 'asset', 'income', 'job']

        labels = {
            'birth_date': '생년월일',
            'gender': '성별',
            'asset': '자산',
            'income': '연봉',
            'job': '직업',
        }
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


