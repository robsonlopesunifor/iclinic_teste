from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def aplicacao_pagina(request):
    return HttpResponse(' pagina da aplicacao ')