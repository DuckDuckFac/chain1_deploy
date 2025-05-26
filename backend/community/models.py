from django.db import models
from django.conf import settings

# Create your models here.
class Community(models.Model):
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_communities')
    title = models.CharField(max_length=10)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Comment(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CommunityLevel(models.Model):
    level = models.IntegerField(unique=True)
    min_score = models.IntegerField()
    title = models.CharField(max_length=30, blank=True)  # ex. 새싹, 브론즈, 실버...

    def __str__(self):
        return f"Lv.{self.level} - {self.min_score}점 이상"