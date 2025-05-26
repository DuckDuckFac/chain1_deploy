from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import CommunityLevel

@receiver(post_migrate)
def create_community_levels(sender, **kwargs):
    try:
        if CommunityLevel.objects.count() == 0:
            for i in range(1, 101):
                CommunityLevel.objects.create(
                    level=i,
                    min_score=(i - 1) * 100,
                    title=f"Lv.{i}"
                )
            print("✅ CommunityLevel 1~100 자동 생성 완료 (post_migrate)")
    except Exception as e:
        print("⚠️ CommunityLevel 자동 생성 실패:", e)