from django import forms
from .models import Categoria, Color, Icono
from apps.utils.categoria.sincronizar_color_icono import get_or_create_icono, get_or_create_color


class CategoriaForm(forms.ModelForm):
    # Estos campos reciben el valor desde el frontend
    icono = forms.CharField(widget=forms.HiddenInput(), required=True)
    color = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = Categoria
        fields = ['nombre', 'icono', 'color']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Comida, Transporte, Ocio...'
            })
        }

    def clean_icono(self):
        """
        Obtiene o crea el icono basándose en el valor enviado.
        Acepta tanto la clase de FontAwesome como el nombre de la categoría.
        """
        value = self.cleaned_data.get('icono', '').strip()
        
        if not value:
            raise forms.ValidationError("Debe seleccionar un icono")
        
        # Si viene la clase completa de FontAwesome (ej: 'fas fa-utensils')
        if value.startswith('fas fa-'):
            try:
                icono_obj = Icono.objects.get(icono=value)
                return icono_obj
            except Icono.DoesNotExist:
                # Si no existe, crearlo automáticamente
                icono_obj = Icono.objects.create(
                    icono=value,
                    nombre=value.replace('fas fa-', '').capitalize()
                )
                return icono_obj
        
        # Si viene el nombre de la categoría (ej: 'comida', 'transporte')
        # Usar la función que mapea nombres a íconos
        icono_obj = get_or_create_icono(value)
        return icono_obj

    def clean_color(self):
        """
        Obtiene o crea el color basándose en el nombre.
        Usa la lógica de calculations.py para mantener consistencia.
        """
        value = self.cleaned_data.get('color', '').strip()
        
        if not value:
            raise forms.ValidationError("Debe seleccionar un color")
        
        # Usar la función que mapea nombres a colores
        color_obj = get_or_create_color(value)
        return color_obj
