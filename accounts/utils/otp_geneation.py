import random
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password


def generate_otp():
    return str(random.randint(100000, 999999))


def get_expiry():
    return timezone.now() + timedelta(minutes=10)


def hash_otp(otp):
    return make_password(otp)