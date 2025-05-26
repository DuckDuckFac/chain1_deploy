from django import forms
from .models import Community, Comment


class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ('title', 'content')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
