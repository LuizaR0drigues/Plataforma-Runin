"""
URL configuration for forms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

app_name = "forms_bbq"

urlpatterns = [
    path('', views.bbq_home, name='home'),
    path('termo/', views.render_termo, name='termo'),
    path('cadastro/', views.render_Cadastro, name='cadastro'),
    path('validacao-iframe/', views.ex_validacao, name='ex_validacao'),
    path('sugestao-iframe/', views.ex_validacao, name='sugestao'),
    path('cadastro-iframe/', views.ex_cadastro, name='ex_cadastro'),
    path('questoes/', views.cap_perguntas, name='iniciar_validacao'),
    path('pergunta/', views.mostrar_perguntas, name='mostrar_template'),
    path('proxima/', views.proxima_perguntas, name='proximo_template'),
    path('decisao/', views.decisao_sugest, name='decisao'),
    path('sugestoes/', views.bbq_sugerir, name='sugerir'),
    path('fim/', views.bbq_fim, name='fim')
]
