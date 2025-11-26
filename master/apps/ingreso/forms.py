from django import forms
from .models import Fuente

class FuenteForm(forms.ModelForm):
    class Meta:
        model = Fuente
        fields = ["nombre"]