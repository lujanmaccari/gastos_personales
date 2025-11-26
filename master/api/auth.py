from ninja.security import HttpBearer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

class AuthBearer(HttpBearer):
    """
    Autenticación basada en Token Bearer.
    El token debe enviarse en el header: Authorization: Bearer <token>
    """
    def authenticate(self, request, token):
        try:
            user = User.objects.filter(auth_token__key=token).first()
            if user:
                return user
        except:
            pass
        return None


class SessionAuth:
    def __call__(self, request):
        if request.user.is_authenticated:
            return request.user
        return None

session_auth =  SessionAuth()