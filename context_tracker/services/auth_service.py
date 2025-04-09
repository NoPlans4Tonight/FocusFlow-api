import jwt
from django.conf import settings
from ..repositories.api_key_repository import APIKeyRepository

class AuthService:
    def __init__(self):
        self.api_key_repo = APIKeyRepository()

    def validate_credentials(self, headers):
        auth_header = headers.get('Authorization')
        api_key = headers.get('X-API-KEY')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                return {'is_valid': True, 'user_id': payload.get('user_id')}
            except jwt.ExpiredSignatureError:
                return {'is_valid': False, 'error': 'Unauthorized: Token has expired', 'status': 401}
            except jwt.InvalidTokenError:
                return {'is_valid': False, 'error': 'Unauthorized: Invalid token', 'status': 401}
        elif api_key:
            if self.api_key_repo.get_api_key_by_user(api_key):
                return {'is_valid': True}
            return {'is_valid': False, 'error': 'Unauthorized: Invalid API key', 'status': 401}
        else:
            return {'is_valid': False, 'error': 'Unauthorized: Missing credentials', 'status': 401}