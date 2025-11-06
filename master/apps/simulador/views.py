from django.shortcuts import render

# Create your views here.
def simulador_ahorro(request):
    return render(request, 'simulador/simulador.html')