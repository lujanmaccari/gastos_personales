from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values(): # help text arafue, si o si el register algún simbolo y mayus
            field.help_text = ""


        # personalización de etiquetas y placeholders

        self.fields["username"].label = "Username"
        self.fields["username"].widget.attrs.update({
            "placeholder": "Ingresá tu usuario",
        })

        self.fields["email"].widget.attrs.update({
            "placeholder": "tu@correo.com",
        })

        self.fields["password1"].label = "Password"
        self.fields["password1"].widget.attrs.update({
            "placeholder": "Ingresá tu contraseña",
        })

        self.fields["password2"].label = "Password confirmation"
        self.fields["password2"].widget.attrs.update({
            "placeholder": "Repetí la contraseña",
        })

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email__iexact=email).exists(): # validación de unicidad
            raise forms.ValidationError("Este email ya está registrado.")
        return email
