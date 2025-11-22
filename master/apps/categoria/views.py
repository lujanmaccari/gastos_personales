from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View,CreateView
from .models import Categoria
from django.urls import reverse_lazy

# Create your views here.
class CategoriaView(LoginRequiredMixin, TemplateView):
    template_name = 'categoria/categoria.html'


class CategoriaFieldsMixin:
    fields = ['nombre','descripcion', 'color', 'icono']


class CategoriaCreateView(LoginRequiredMixin,CategoriaFieldsMixin, CreateView):
    model = Categoria
    template_name = 'categoria/categoria_form.html'

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('categoria')
    
