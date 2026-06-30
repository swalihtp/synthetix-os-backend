from django.conf import settings
from rest_framework.permissions import BasePermission


class LambdaAuthentication(BasePermission):

    def has_permission(self, request, view):
        return request.headers.get("X-API-KEY") == settings.LAMBDA_API_KEY
