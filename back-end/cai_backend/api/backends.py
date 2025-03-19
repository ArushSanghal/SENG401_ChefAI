from django.contrib.auth.backends import BaseBackend
from .models import RegisteredUser

class RegisteredUserBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = RegisteredUser.objects.get(email=email)
            if user.check_password(password):
                return user
        except RegisteredUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return RegisteredUser.objects.get(pk=user_id)
        except RegisteredUser.DoesNotExist:
            return None