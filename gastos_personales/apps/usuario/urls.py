from django.urls import path
from .views import CustomLoginView, LogoutView, RegisterView, ResendVerificationView, VerifyEmailView

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("verificar-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("reenviar-verificacion/", ResendVerificationView.as_view(), name="resend_verification"),
]
