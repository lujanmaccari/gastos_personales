from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, View

from .forms import CustomUserCreationForm
from .models import EmailVerification

User = get_user_model()


def _send_account_verified_email(user):
    subject = "¡Tu cuenta de SpendWise fue verificada!"
    html_message = render_to_string('email/account_verified.html', {'user': user})
    send_mail(
        subject=subject,
        message=(
            f"Hola {user.first_name or user.username}, "
            "tu cuenta de SpendWise fue verificada correctamente. "
            "Ya podés iniciar sesión y empezar a gestionar tus finanzas."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,
    )


def _send_verification_email(user, code):
    subject = "Verificá tu cuenta en SpendWise"
    html_message = render_to_string('email/verify_email.html', {
        'user': user,
        'code': code,
        'expiry_minutes': EmailVerification.EXPIRY_MINUTES,
    })
    send_mail(
        subject=subject,
        message=(
            f"Tu código de verificación de SpendWise es: {code}. "
            f"Expira en {EmailVerification.EXPIRY_MINUTES} minutos."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "usuario/register.html"

    def get_form_class(self):
        form_class = super().get_form_class()
        form_class._meta.model = User
        return form_class

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        verification, code = EmailVerification.generate(user)
        try:
            _send_verification_email(user, code)
            messages.success(
                self.request,
                f"Te enviamos un código de verificación a {user.email}.",
            )
        except Exception:
            messages.warning(
                self.request,
                "Tu cuenta fue creada, pero no pudimos enviar el email. "
                "Podés solicitar un nuevo código desde la pantalla de verificación.",
            )
        return redirect(f"/verificar-email/?uid={user.pk}")


class CustomLoginView(LoginView):
    template_name = "usuario/login.html"

    def form_invalid(self, form):
        username = form.data.get('username', '')
        if username:
            try:
                user = User.objects.get(username=username)
                if not user.is_active and hasattr(user, 'email_verification'):
                    messages.info(
                        self.request,
                        "Verificá tu cuenta antes de iniciar sesión. Revisá tu email.",
                    )
                    return redirect(f'/verificar-email/?uid={user.pk}')
            except User.DoesNotExist:
                pass
        messages.error(self.request, "Usuario o contraseña incorrectos.")
        return super().form_invalid(form)

    def get_success_url(self):
        messages.success(self.request, "Sesión iniciada correctamente.")
        return reverse("dashboard")


class LogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Sesión cerrada correctamente.")
        return redirect("login")

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Sesión cerrada correctamente.")
        return redirect("login")


class VerifyEmailView(View):
    template_name = 'usuario/verify_email.html'

    def _get_pending_user(self, uid):
        try:
            return User.objects.get(pk=uid, is_active=False)
        except (User.DoesNotExist, ValueError, TypeError):
            return None

    def get(self, request):
        uid = request.GET.get('uid')
        user = self._get_pending_user(uid)
        if not user:
            messages.error(request, "Enlace inválido o la cuenta ya fue verificada.")
            return redirect('login')
        return render(request, self.template_name, {'uid': uid, 'email': user.email})

    def post(self, request):
        uid = request.POST.get('uid')
        code = request.POST.get('code', '').strip()
        user = self._get_pending_user(uid)

        if not user:
            messages.error(request, "Enlace inválido o la cuenta ya fue verificada.")
            return redirect('login')

        try:
            verification = user.email_verification
        except EmailVerification.DoesNotExist:
            messages.error(request, "No hay verificación pendiente para esta cuenta.")
            return redirect('login')

        result = verification.verify(code)

        if result == 'ok':
            user.is_active = True
            user.save(update_fields=['is_active'])
            verification.delete()
            _send_account_verified_email(user)
            messages.success(request, "¡Cuenta verificada! Ya podés iniciar sesión.")
            return redirect('login')

        ctx = {'uid': uid, 'email': user.email, 'code': code}

        if result == 'expired':
            ctx['error'] = 'El código expiró. Solicitá uno nuevo.'
            ctx['show_resend'] = True
        elif result == 'max_attempts':
            ctx['error'] = 'Demasiados intentos fallidos. Solicitá un nuevo código.'
            ctx['show_resend'] = True
        else:
            remaining = EmailVerification.MAX_ATTEMPTS - verification.attempts
            ctx['error'] = f'Código incorrecto. Te quedan {remaining} intento{"s" if remaining != 1 else ""}.'

        return render(request, self.template_name, ctx)


class ResendVerificationView(View):
    def post(self, request):
        uid = request.POST.get('uid')
        try:
            user = User.objects.get(pk=uid, is_active=False)
        except (User.DoesNotExist, ValueError, TypeError):
            messages.error(request, "Cuenta no encontrada.")
            return redirect('login')

        try:
            old = user.email_verification
            if not old.can_resend():
                messages.warning(request, "Esperá un momento antes de solicitar otro código.")
                return redirect(f'/verificar-email/?uid={uid}')
        except EmailVerification.DoesNotExist:
            pass

        verification, code = EmailVerification.generate(user)
        try:
            _send_verification_email(user, code)
            messages.success(request, "Te enviamos un nuevo código. Revisá tu email.")
        except Exception:
            messages.error(request, "No se pudo enviar el email. Intentá de nuevo más tarde.")

        return redirect(f'/verificar-email/?uid={uid}')
