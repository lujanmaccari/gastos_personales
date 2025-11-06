from django.shortcuts import render

# Create your views here.
def ingresos(request):
    return render(request, 'ingreso/ingreso.html')