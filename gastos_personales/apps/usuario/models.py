import hashlib
import secrets
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

class Usuario(AbstractUser):
    email = models.EmailField(unique=True) 
    moneda = models.ForeignKey('usuario.Moneda', on_delete=models.SET_NULL, null=True, blank=True, related_name="usuarios_usan_moneda")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True) 


    def __str__(self):
        nombre = f"{self.first_name} {self.last_name}".strip()
        return nombre if nombre else self.username


class Moneda(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="monedas"
    )
    moneda = models.CharField(max_length=50)
    abreviatura = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.moneda} ({self.abreviatura})"


class EmailVerification(models.Model):
    MAX_ATTEMPTS = 5
    EXPIRY_MINUTES = 30
    RESEND_COOLDOWN_SECONDS = 60

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_verification',
    )
    code_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)

    @classmethod
    def generate(cls, user):
        """Creates or replaces a verification record. Returns (instance, plain_code)."""
        code = f"{secrets.randbelow(1_000_000):06d}"
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        expires_at = timezone.now() + timedelta(minutes=cls.EXPIRY_MINUTES)
        obj, _ = cls.objects.update_or_create(
            user=user,
            defaults={'code_hash': code_hash, 'expires_at': expires_at, 'attempts': 0},
        )
        return obj, code

    def verify(self, code):
        """Returns 'ok' | 'expired' | 'max_attempts' | 'invalid'."""
        if self.attempts >= self.MAX_ATTEMPTS:
            return 'max_attempts'
        if timezone.now() > self.expires_at:
            return 'expired'
        self.attempts += 1
        self.save(update_fields=['attempts'])
        if hashlib.sha256(code.encode()).hexdigest() == self.code_hash:
            return 'ok'
        return 'invalid'

    def can_resend(self):
        return (timezone.now() - self.created_at).total_seconds() >= self.RESEND_COOLDOWN_SECONDS