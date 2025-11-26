from django.contrib.auth import get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DeleteView, View
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from .models import Perfil
from .forms import PerfilForm
from apps.usuario.models import Moneda
from apps.ingreso.models import Fuente

User = get_user_model()


class PerfilDetailView(LoginRequiredMixin, TemplateView):
    template_name = "perfil/perfil.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        usuario = self.request.user
        perfil, _ = Perfil.objects.get_or_create(usuario=usuario)

        ctx.update({
            "perfil": perfil,
            "form": PerfilForm(),
            "monedas": Moneda.objects.filter(usuario=self.request.user),
            "fuentes": Fuente.objects.filter(usuario=self.request.user),
        })
        return ctx


class PerfilUpdateView(LoginRequiredMixin, View): 

    def post(self, request):
        usuario = request.user
        perfil, _ = Perfil.objects.get_or_create(usuario=usuario)
        form = PerfilForm(request.POST, request.FILES)

        if not form.is_valid():
            for error in form.errors.values():
                messages.error(request, error)
            return redirect("perfil_detail")

        
        usuario.first_name = request.POST.get("first_name", usuario.first_name)
        usuario.last_name = request.POST.get("last_name", usuario.last_name)
        usuario.email = request.POST.get("email", usuario.email)

      
        moneda_id = request.POST.get("moneda")
        if moneda_id:
            try:
                usuario.moneda = Moneda.objects.get(pk=moneda_id)
            except Moneda.DoesNotExist:
                messages.error(request, "La moneda seleccionada no existe.")
                return redirect("perfil_detail")

       
        if form.cleaned_data.get("avatar"):
            perfil.avatar = form.cleaned_data["avatar"]

       
        p1 = form.cleaned_data.get("password1")
        if p1:
            usuario.set_password(p1)
            usuario.save()
            perfil.save()
            messages.success(request, "Contraseña actualizada. Iniciá sesión nuevamente.")
            logout(request)
            return redirect("login")

        
        usuario.save()
        perfil.save()

        messages.success(request, "Perfil actualizado correctamente.")
        return redirect("perfil_detail")

    
class PerfilDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "perfil/perfil_confirm_delete.html"
    success_url = reverse_lazy("login")

    def get_object(self, queryset=None):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Tu cuenta ha sido eliminada correctamente.")
        return super().delete(request, *args, **kwargs)


class MonedaCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        nombre = request.POST.get("moneda", "").strip()
        abrev = request.POST.get("abreviatura", "").strip()

        if not nombre or not abrev:
            messages.error(request, "Completá nombre y abreviatura.")
            return redirect("perfil_detail")

        Moneda.objects.create(usuario=request.user, moneda=nombre, abreviatura=abrev )
        messages.success(request, "Moneda creada.")
        return redirect("perfil_detail")


class MonedaDeleteView(LoginRequiredMixin, DeleteView):
    model = Moneda
    success_url = reverse_lazy("perfil_detail")

    def get_queryset(self):
        return Moneda.objects.filter(usuario=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        moneda = self.get_object()
        moneda.delete()
        messages.success(request, "Moneda eliminada.")
        return redirect("perfil_detail")



class FuenteCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        nombre = request.POST.get("nombre", "").strip()

        if not nombre:
            messages.error(request, "Ingresá un nombre.")
            return redirect("perfil_detail")

        Fuente.objects.create(nombre=nombre, usuario=request.user)
        messages.success(request, "Fuente creada.")
        return redirect("perfil_detail")


class FuenteDeleteView(LoginRequiredMixin, DeleteView):
    model = Fuente
    success_url = reverse_lazy("perfil_detail")

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        fuente = self.get_object()
        fuente.delete()
        messages.success(request, "Fuente eliminada.")
        return redirect("perfil_detail")