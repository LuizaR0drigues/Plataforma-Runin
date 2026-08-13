from django.shortcuts import render
from django.http import HttpResponse

def bbq_home(request):
    return render(request, 'home.html')

def bbq_cadastro(request): 
    return render(request, "cadastro.html")