from django.urls import path
from .views import *

urlpatterns = [
    path('usuarios/', UsuarioListView.as_view(), name='usuariosList'),
    path('usuarios/<int:pk>/', UsuarioRetrieve.as_view(), name='usuarioRetrieve'),
    path('usuarios/crear/', UsuarioCreateView.as_view(), name='usuarioCreate'),
    path('usuarios/actualizar/<int:pk>/', UsuarioUpdateView.as_view(), name='usuarioUpdate'),
    path('usuarios/<int:pk>/estado/', UsuarioToggleStatus.as_view(), name='usuario-toggle-status'),

    path('usuarios/login/', UsuarioLoginView.as_view(), name='usuarioLogin'),
    # Ruta para la renovación del access_token usando refresh_token
    path('usuarios/refresh-token/', UsuarioRefreshTokenView.as_view(), name='usuarioRefreshToken'),
    
    path('usuarios/rest-password-request/', UsuarioPasswordResetRequestView.as_view(), name='usuarioResetPasswordRequest'),
    path('usuarios/rest-password/', UsuarioPasswordChangeView.as_view(), name='usuarioResetPassword'),
    
    path('usuarios/profile-get/', UsuarioGetProfileView.as_view(), name='usuarioGetProfile'),
    path('usuarios/profile-send/', UsuarioSendProfileView.as_view(), name='usuarioSendProfile'),
    path('usuarios/eliminar/<int:pk>/', UsuarioDelete.as_view(), name='EliminarUsuario'),

    path('roles/', GroupListView.as_view(), name='RolesList'),
]