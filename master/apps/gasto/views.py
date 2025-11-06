from django.shortcuts import render

# Create your views here.
def gastos(request):
    return render(request, 'gasto/gasto.html')