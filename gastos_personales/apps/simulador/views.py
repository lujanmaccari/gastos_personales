import math

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import TemplateView, View


class SimuladorView(LoginRequiredMixin, TemplateView):
    template_name = "simulador/simulador.html"


class SimuladorCalculoView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        try:
            ingresos = float(request.POST.get("ingresos", 0))
            gastos = float(request.POST.get("gastos", 0))
            meta = float(request.POST.get("meta", 0))
        except ValueError:
            return JsonResponse({"error": "Valores inválidos"}, status=400)

        ahorro_mensual = ingresos - gastos
        tasa_ahorro = round(ahorro_mensual / ingresos * 100, 1) if ingresos > 0 else 0

        if ahorro_mensual <= 0:
            return JsonResponse({
                "tipo": "deficit",
                "ahorro_mensual": round(ahorro_mensual, 2),
                "deficit": round(abs(ahorro_mensual), 2),
                "tasa_ahorro": 0,
            })

        if meta <= 0:
            return JsonResponse({
                "tipo": "sin_meta",
                "ahorro_mensual": round(ahorro_mensual, 2),
                "tasa_ahorro": tasa_ahorro,
            })

        meses_para_meta = math.ceil(meta / ahorro_mensual)

        anios = meses_para_meta // 12
        meses_rest = meses_para_meta % 12
        if anios > 0 and meses_rest > 0:
            tiempo_texto = f"{anios} año{'s' if anios > 1 else ''} y {meses_rest} mes{'es' if meses_rest > 1 else ''}"
        elif anios > 0:
            tiempo_texto = f"{anios} año{'s' if anios > 1 else ''}"
        else:
            tiempo_texto = f"{meses_para_meta} mes{'es' if meses_para_meta > 1 else ''}"

        # Proyección: máximo 36 meses en el gráfico
        meses_a_mostrar = min(meses_para_meta, 36)
        proyeccion = []
        saldo = 0
        for _ in range(meses_a_mostrar):
            saldo = min(saldo + ahorro_mensual, meta)
            proyeccion.append(round(saldo, 2))

        labels = [f"Mes {i + 1}" for i in range(meses_a_mostrar)]

        # Cuánto ahorrar extra para llegar un 25% antes
        meses_acelerado = max(1, math.ceil(meses_para_meta * 0.75))
        ahorro_acelerado = math.ceil(meta / meses_acelerado)
        extra_mensual = max(0, ahorro_acelerado - ahorro_mensual)

        return JsonResponse({
            "tipo": "ok",
            "ahorro_mensual": round(ahorro_mensual, 2),
            "tasa_ahorro": tasa_ahorro,
            "meses_objetivo": meses_para_meta,
            "tiempo_texto": tiempo_texto,
            "proyeccion": proyeccion,
            "labels": labels,
            "meta": round(meta, 2),
            "extra_mensual": round(extra_mensual, 2),
            "meses_acelerado": meses_acelerado,
        })
