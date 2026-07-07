from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core.mail import send_mail


class EmailService:

    @staticmethod
    def send_password_reset_email(frontend_url, uid, token, user):
        subject = "Password Reset Request"

        reset_link = f"{frontend_url}/reset-password/{uid}/{token}"

        text_content = f"""
        Hi {user.full_name},

        You requested a password reset.

        Reset your password here:
        {reset_link}

        If you didn’t request this, ignore this email.
        """

        html_content = f"""
        <p>Hi {user.full_name},</p>
        <p>You requested a password reset.</p>
        <p>
            <a href="{reset_link}" style="color:blue;">
                Reset Password
            </a>
        </p>
        <p>If you didn’t request this, ignore this email.</p>
        """

        email = EmailMultiAlternatives(
            subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email]
        )

        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

    @staticmethod
    def send_verification_email(user, otp):

        verify_url = f"{settings.FRONTEND_URL}" f"/verify-email?email={user.email}"

        subject = "Verify your Synthetix OS account"

        text_content = f"""
    Welcome to Synthetix OS.

    Your verification code is: {otp}

    Verify your account:
    {verify_url}

    This code expires in 10 minutes.
    """

        html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    </head>
    <body style="
        margin:0;
        padding:0;
        background:#0a0a0a;
        font-family:Arial,sans-serif;
    ">

    <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
    <td align="center" style="padding:40px 20px;">

    <table
        width="600"
        cellpadding="0"
        cellspacing="0"
        style="
            background:#111111;
            border:1px solid #222222;
            border-radius:12px;
            overflow:hidden;
        "
    >

    <tr>
    <td
        style="
            padding:32px;
            border-bottom:1px solid #222222;
        "
    >
    <h1 style="
        margin:0;
        color:#10b981;
        font-size:28px;
    ">
    Synthetix OS
    </h1>

    <p style="
        margin-top:10px;
        color:#888888;
    ">
    AI Workforce Orchestration Platform
    </p>
    </td>
    </tr>

    <tr>
    <td style="padding:32px;">

    <h2 style="
        color:#ffffff;
        margin-top:0;
    ">
    Verify your account
    </h2>

    <p style="
        color:#cfcfcf;
        line-height:1.7;
    ">
    Hello {user.full_name},
    </p>

    <p style="
        color:#cfcfcf;
        line-height:1.7;
    ">
    Thank you for creating your Synthetix OS account.
    To activate your workspace, please verify your email address.
    </p>

    <div
        style="
            margin:30px 0;
            text-align:center;
        "
    >

    <div style="
        color:#888888;
        font-size:12px;
        text-transform:uppercase;
        letter-spacing:2px;
    ">
    Verification Code
    </div>

    <div style="
        margin-top:10px;
        font-size:36px;
        font-weight:bold;
        color:#10b981;
        letter-spacing:8px;
    ">
    {otp}
    </div>

    </div>

    <div style="
        text-align:center;
        margin:40px 0;
    ">
    <a
        href="{verify_url}"
        style="
            background:#10b981;
            color:#000000;
            text-decoration:none;
            padding:14px 28px;
            border-radius:8px;
            font-weight:bold;
            display:inline-block;
        "
    >
    Verify Account
    </a>
    </div>

    <p style="
        color:#888888;
        font-size:14px;
        line-height:1.7;
    ">
    This verification code will expire in
    <strong>10 minutes</strong>.
    </p>

    <p style="
        color:#888888;
        font-size:14px;
        line-height:1.7;
    ">
    If you did not create this account, you can safely ignore this email.
    </p>

    </td>
    </tr>

    <tr>
    <td
        style="
            border-top:1px solid #222222;
            padding:24px 32px;
            color:#666666;
            font-size:12px;
            text-align:center;
        "
    >
    © 2026 Synthetix OS

    <br><br>

    Secure AI Workforce Platform
    </td>
    </tr>

    </table>

    </td>
    </tr>
    </table>

    </body>
    </html>
    """

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )

        email.attach_alternative(html_content, "text/html")

        email.send()

    @staticmethod
    def send_admin_invitation(email, invitation_url):
        subject = "Administrator Account Invitation"
        
        print(f"EMAIL: {email}")
        print(f"TYPE: {type(email)}")

        message = f"""
            Hello,

            You have been invited as an administrator.

            Please use the link below to set your password:

            {invitation_url}

            This link expires in 48 hours.

            If you were not expecting this invitation, please ignore this email.
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )