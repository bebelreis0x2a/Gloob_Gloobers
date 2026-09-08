from django.contrib import admin
from django.urls import path
from ranking import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/ranking/novo/', views.registrar_pontuacao),
    path('api/ranking/', views.listar_ranking),
]