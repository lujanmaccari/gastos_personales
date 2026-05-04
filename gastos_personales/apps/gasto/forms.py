from django import forms
from .models import Gasto
from apps.categoria.models import Categoria
from django.forms.widgets import DateInput, Textarea, NumberInput, Select

class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['fecha', 'categoria', 'monto', 'descripcion']
        widgets = {
            'fecha': DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition'
            }),
            'categoria': Select(attrs={
                'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition'
            }),
            'monto': NumberInput(attrs={
                'step': '0.01',
                'class': 'w-full pl-8 pr-4 py-3 bg-white border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition'
            }),
            'descripcion': Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-3 bg-white border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition resize-none',
                'placeholder': 'Agregar descripción del gasto...'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        if user:

            self.fields['categoria'].queryset = Categoria.objects.filter(usuario=user)
        else:
            self.fields['categoria'].queryset = Categoria.objects.all()  
