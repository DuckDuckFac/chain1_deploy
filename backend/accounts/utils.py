from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings

def send_verification_email(user):
    code = user.email_verify_code  # UUIDField 기반
    link = f"{settings.FRONT_BASE_URL}/verify-email/{code}"
    logo_url = "http://localhost:8000/static/email/Nest.png"
    subject = "[NEST] 이메일 인증을 완료해주세요"
    
    html_content = f"""
    <div style="font-family: 'Pretendard', 'Arial', sans-serif; background-color: #f5f7fa; padding: 40px;">
      <div style="max-width: 540px; margin: 0 auto; background: white; padding: 30px 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
        <div style="text-align: center; margin-bottom: 24px;">
          <img src="{logo_url}" alt="NEST 로고" width="150" />
          <h2 style="margin: 0; font-size: 1.6rem; color: #007bff;">이메일 인증 요청</h2>
        </div>
        <p style="font-size: 1rem; color: #333;">안녕하세요, <strong>{user.nickname or user.username}</strong> 님 👋</p>
        <p style="font-size: 0.95rem; color: #555;">
          아래 버튼을 클릭해 이메일 인증을 완료해주세요. NEST의 다양한 서비스를 안전하게 이용하실 수 있습니다.
        </p>
        <div style="text-align: center; margin: 32px 0;">
          <a href="{link}" target="_blank"
            style="background-color: #007bff; color: white; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: bold; display: inline-block;">
            이메일 인증하기
          </a>
        </div>
        <p style="font-size: 0.85rem; color: #888;">
          위 버튼이 동작하지 않는다면, 아래 링크를 복사하여 브라우저에 붙여넣어 주세요:<br />
          <span style="color: #007bff;">{link}</span>
        </p>
        <hr style="margin: 30px 0;" />
        <p style="font-size: 0.8rem; color: #aaa;">본 메일은 NEST 회원가입 시 발송되었으며, 인증 완료 후 안전하게 서비스를 이용할 수 있습니다.</p>
      </div>
    </div>
    """

    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
