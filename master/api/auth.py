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
            # Aquí puedes implementar tu lógica de validación de token
            # Por ahora usaremos una validación simple
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


# Para usar autenticación de sesión (más simple para desarrollo)
# from ninja.security import django_auth

# Exportar para uso en otros módulos
session_auth =  SessionAuth()