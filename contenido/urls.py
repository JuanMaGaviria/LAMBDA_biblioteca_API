from django.urls import path
from .views import *

urlpatterns = [
    path('recursos/', RecursoList.as_view(), name='recursoList'),
    path('recursos/<int:pk>/', RecursoRetrieve.as_view(), name='recursoRetrieve'),
    path('recursos/crear/', RecursoCreate.as_view(), name='recursoCreate'),
    path('recursos/actualizar/<int:pk>/', RecursoUpdate.as_view(), name='recursoUpdate'),
    path('recursos/<int:pk>/estado/', RecursoToggleValidado.as_view(), name='recurso-toggle-status'),
    path('recursos/eliminar/<int:pk>/', RecursoDelete.as_view(), name='EliminarRecurso'),

     # URLs para votación de recursos
     # Nuevas URLs para votación
    path('recursos/mis-votos/', MisVotosRecursos.as_view(), name='mis-votos-recursos'),
    path('recursos/votar/', VotarRecurso.as_view(), name='votar-recurso'),
    path('recursos/remover-voto/', RemoverVotoRecurso.as_view(), name='remover-voto-recurso'),
    
    # URLs alternativas que incluyen información de votos
    path('recursos-con-votos/', RecursoListConVotos.as_view(), name='recurso-list-con-votos'),
    path('recursos-con-votos/<int:pk>/', RecursoRetrieveConVotos.as_view(), name='recurso-detail-con-votos'),
]