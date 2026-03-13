import pyotp

class MFAService:

    @staticmethod
    def generate_secret():
        return pyotp.random_base32()

    @staticmethod
    def get_qr_uri(user):
        totp = pyotp.TOTP(user.mfa_secret)

        return totp.provisioning_uri(
            name=user.email,
            issuer_name="SynthetixOS"
        )

    @staticmethod
    def verify_otp(user, otp):
        totp = pyotp.TOTP(user.mfa_secret)
        return totp.verify(otp)