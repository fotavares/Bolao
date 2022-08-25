from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='inicio'),
    path('inicio', views.dashboard, name='inicio'),
    path('editar-perfil', views.perfil, name='perfil'),
    path('apostar', views.apostar, name='apostar'),
    path('ranking', views.ranking, name='ranking'),
    path('historico', views.historico, name='historico'),
    path('resultado', views.resultado, name='resultado'),
    path('regras', views.regras, name="regras"),
    path("cadastro", views.SignUpView.as_view(), name="cadastro"),
    path('conta/login', auth_views.LoginView.as_view(), name='login'),
    path('conta/troca-senha',
         views.troca_senha, name='trocasenha'),
    path('conta/sair',
         auth_views.LogoutView.as_view(), name='sair'),


]
