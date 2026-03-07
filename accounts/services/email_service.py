from django.core.mail import EmailMultiAlternatives
from django.conf import settings


class EmailService:

    @staticmethod
    def send_password_reset_email(frontend_url, uid, token, user):
        subject = "Password Reset Request"

        reset_link = f"{frontend_url}/reset-password/{uid}/{token}"

        text_content = f"""
Hi {user.first_name},

You requested a password reset.

Reset your password here:
{reset_link}

If you didn’t request this, ignore this email.
"""

        html_content = f"""
        <p>Hi {user.first_name},</p>
        <p>You requested a password reset.</p>
        <p>
            <a href="{reset_link}" style="color:blue;">
                Reset Password
            </a>
        </p>
        <p>If you didn’t request this, ignore this email.</p>
        """

        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )

        email.attach_alternative(html_content, "text/html")
        email.send()
        
