from django.urls import path
from .views.areas import *
from .views.categorias import *


urlpatterns = [
    #Areas
    path('areas/', AreaList.as_view(), name='ListaAreas'),
    path('areas/<int:pk>/', AreaRetrieve.as_view(), name='ObtenerArea'),
    path('areas/crear/', AreaCreate.as_view(), name='CrearArea'),
    path('areas/editar/<int:pk>/', AreaUpdate.as_view(), name='ActualizarArea'),
    path('areas/<int:pk>/estado/', AreaToggleStatus.as_view(), name='Area-toggle-status'),
    path('areas/eliminar/<int:pk>/', AreaDelete.as_view(), name='EliminarArea'),

    #Categorias
    path('categorias/', CategoriaList.as_view(), name='ListaCategorias'),
    path('categorias/<int:pk>/', CategoriaRetrieve.as_view(), name='ObtenerCategoria'),
    path('categorias/crear/', CategoriaCreate.as_view(), name='CrearCategoria'),
    path('categorias/editar/<int:pk>/', CategoriaUpdate.as_view(), name='ActualizarCategoria'),
    path('categorias/<int:pk>/estado/', CategoriaToggleStatus.as_view(), name='Categoria-toggle-status'),
    path('categorias/eliminar/<int:pk>/', CategoriaDelete.as_view(), name='EliminarCategoria')
]