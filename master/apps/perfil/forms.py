from django import forms
from .models import Perfil

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ("moneda", "limite_gasto_mensual", "avatar")
        widgets = {
            "limite_gasto_mensual": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }
