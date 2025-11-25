from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from apps.usuario.models import Moneda

User = get_user_model()


class MonedaForm(forms.ModelForm):
    class Meta:
        model = Moneda
        fields = ["moneda", "abreviatura"]


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(required=True, label="Nombre")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "placeholder": "Elegí un nombre de usuario",
        })
        self.fields["first_name"].widget.attrs.update({
            "placeholder": "Tu nombre",
        })
        self.fields["email"].widget.attrs.update({
            "placeholder": "Ingresá tu email",
        })
        self.fields["password1"].widget.attrs.update({
            "placeholder": "Ingresá tu contraseña",
        })
        self.fields["password2"].widget.attrs.update({
            "placeholder": "Repetí la contraseña",
        })

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este email ya está registrado.")
        return email

# cuando se registre se guarda first_name y el __str__ del model Usuario lo muestra