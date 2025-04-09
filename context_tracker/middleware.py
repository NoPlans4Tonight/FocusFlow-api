import jwt
from django.http import JsonResponse
from django.conf import settings
from .models import APIKey
from .services.auth_service import AuthService

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_service = AuthService()

    def __call__(self, request):
        # Skip authentication for non-protected routes
        if request.path not in ['/log/', '/stop/', '/status/', '/entries/']:
            return self.get_response(request)

        # Validate credentials using AuthService
        auth_result = self.auth_service.validate_credentials(request.headers)
        if not auth_result['is_valid']:
            return JsonResponse({'error': auth_result['error']}, status=auth_result['status'])

        # Attach user_id to the request if valid
        request.user_id = auth_result.get('user_id')
        return self.get_response(request)