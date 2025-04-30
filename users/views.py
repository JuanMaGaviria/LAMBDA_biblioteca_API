from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    #permission_classes = [IsAuthenticated]  # Solo autenticados
    
    def get_queryset(self):
        user = self.request.user
        base_queryset = User.objects.filter(is_active=True).order_by('id')

        if user.is_authenticated and user.role != 'admin':
            return base_queryset.filter(id=user.id)

        return base_queryset


    def perform_create(self, serializer):
        # El permiso ya se valida en el serializer (solo admin puede crear)
        serializer.save()

    def perform_update(self, serializer):
        # La lógica ya está en el serializer (admin puede editar a cualquiera, empleados solo a sí mismos)
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """Desactiva un usuario en lugar de eliminarlo físicamente."""
        user = self.get_object()
        request_user = request.user

        # Solo el admin puede desactivar a otros usuarios
        if request_user.role != 'admin' and user != request_user:
            return Response(
                {'detail': 'No tienes permiso para desactivar este usuario.'},
                status=status.HTTP_403_FORBIDDEN
            )

        user.is_active = False
        user.save()
        return Response({'status': 'Usuario desactivado'}, status=status.HTTP_204_NO_CONTENT)
