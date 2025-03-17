from django.contrib.auth.backends import BaseBackend
from rest_framework.authtoken.models import Token
from .models import RegisteredUser

class TokenAuthBackend(BaseBackend):
    def authenticate(self, request, token=None):
        try:
            token_obj = Token.objects.get(key=token)
            return token_obj.user
        except Token.DoesNotExist:
            return None
