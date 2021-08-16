from django.urls import path
from .views import aplicacao_pagina

urlpatterns = [
    path('', aplicacao_pagina, name='aplicacao')
]