from django import forms
from apps.usuario.models import Usuario
from .models import Perfil

class PerfilForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput,
        required=False
    )
    password2 = forms.CharField(
        label="Repetir contraseña",
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = Perfil
        fields = ["avatar"]

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")

        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("Las contraseñas no coinciden.")
            if len(p1) < 8:
                raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")

        return cleaned
