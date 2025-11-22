from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import math

class SimuladorView(LoginRequiredMixin, TemplateView):
    template_name = "simulador/simulador.html"

class SimuladorCalculoView(LoginRequiredMixin, View):
    """Recibe ingresos, gastos y meta, devuelve proyección acumulada y meses necesarios"""

    def post(self, request, *args, **kwargs):
        try:
            ingresos = float(request.POST.get("ingresos", 0))
            gastos = float(request.POST.get("gastos", 0))
            meta = float(request.POST.get("meta", 0))
        except ValueError:
            return JsonResponse({"error": "Valores inválidos"}, status=400)

        ahorro_mensual = ingresos - gastos

        if ahorro_mensual <= 0:
            return JsonResponse({
                "error": "No es posible proyectar ahorro con los datos ingresados",
                "ahorro_mensual": ahorro_mensual
            }, status=400)

        # Calcular meses necesarios para alcanzar la meta, minimo 1
        meses_para_meta = max(1, math.ceil(meta / ahorro_mensual))

        # Generar proyeccion acumulada por mes (hasta que llegue a la meta o 12 meses)
        proyeccion = []
        saldo = 0

        for mes in range(1, max(12, meses_para_meta) + 1):
            saldo += ahorro_mensual
            proyeccion.append(min(saldo, meta)) 

        return JsonResponse({
            "ahorro_mensual": ahorro_mensual,
            "meses_objetivo": meses_para_meta,
            "proyeccion": proyeccion
        })
