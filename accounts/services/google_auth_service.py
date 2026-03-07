from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings

class GoogleAuthService:

    @staticmethod
    def verify_google_token(token):
        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            return {
                "email": idinfo["email"],
                "name": idinfo.get("name"),
                "picture": idinfo.get("picture"),
                "sub": idinfo["sub"]
            }

        except ValueError:
            return None