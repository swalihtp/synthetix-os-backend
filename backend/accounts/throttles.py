from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginThrottle(AnonRateThrottle):
    scope = 'login'

class RegisterThrottle(AnonRateThrottle):
    scope = 'register'

class ForgotPasswordThrottle(AnonRateThrottle):
    scope = 'forgot_password'

class ResetPasswordThrottle(AnonRateThrottle):
    scope = 'reset_password'

class VerifyEmailThrottle(AnonRateThrottle):
    scope = 'verify_email'

class ResendOTPThrottle(AnonRateThrottle):
    scope = 'resend_otp'

class GoogleLoginThrottle(AnonRateThrottle):
    scope = 'google_login'

# --- User throttles

class ProfileThrottle(UserRateThrottle):
    scope = 'profile'

class ChangePasswordThrottle(UserRateThrottle):
    scope = 'change_password'

class MFAThrottle(UserRateThrottle):
    scope = 'mfa'