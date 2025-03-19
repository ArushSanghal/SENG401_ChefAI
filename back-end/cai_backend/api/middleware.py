from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import Token

#Used to clear expired tokens every 10 requests.
class TokenCleanupMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.request_count = 0

    def process_request(self, request):
        self.request_count += 1

        if self.request_count % 10 == 0:
            print(f"Cleaning up expired tokens (Request count: {self.request_count})")
            Token.objects.filter(expires_at__lt=timezone.now()).delete()

        return None