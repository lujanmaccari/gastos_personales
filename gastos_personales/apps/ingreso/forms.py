from django import forms
from django import forms
from .models import Ingreso, Fuente
from django.forms.widgets import DateInput, Textarea, NumberInput, Select

class FuenteForm(forms.ModelForm):
    class Meta:
        model = Fuente
        fields = ["nombre"]

class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = ['fecha', 'fuente', 'monto', 'descripcion']
        widgets = {
            'fecha': DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition'
            }),
            'fuente': Select(attrs={
                'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition'
            }),
            'monto': NumberInput(attrs={
                'step': '0.01',
                'class': 'w-full pl-8 pr-4 py-3 bg-white border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition'
            }),
            'descripcion': Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition resize-none',
                'placeholder': 'Agregar descripción opcional...'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['fuente'].queryset = Fuente.objects.filter(usuario=user)
        else:
            self.fields['fuente'].queryset = Fuente.objects.all()