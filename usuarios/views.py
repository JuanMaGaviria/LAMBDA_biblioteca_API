import os
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from threading import Thread
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group
from .models import Usuario
from .serializers import *
from biblioteca.permisos import HasUserManagementPermission
from dotenv import load_dotenv

load_dotenv()

def get_user(pk):
    try:
        return Usuario.objects.get(pk=pk)
    except Usuario.DoesNotExist:
        raise Http404('Usuario no encontrado.')

class UsuarioPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UsuarioListView(ListAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UsuarioPagination
    filter_backends = [SearchFilter]
    search_fields = ['correo', 'nombre_completo']
    
    def get_queryset(self):
        return Usuario.objects.exclude(pk=self.request.user.pk)

class UsuarioRetrieve(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = get_user(pk)
        serializer = UsuarioSerializer(user)
        return Response(serializer.data)

class UsuarioCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Asignar grupo 'Colaborador' por defecto
            try:
                group = Group.objects.get(name='Colaborador')
                user.groups.add(group)
            except Group.DoesNotExist:
                pass  # Opcional: Manejar si el grupo no existe
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UsuarioUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        user = get_user(pk)
        serializer = UsuarioSerializer(user, data=request.data)
        print(serializer)  # Verifica los datos recibidos aquí
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        user = get_user(pk)
        serializer = UsuarioSerializer(user, data=request.data, partial=True)
        print(serializer)  # Verifica los datos recibidos aquí
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UsuarioLoginView(APIView):
    def post(self, request):
        serializer = UsuarioLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['correo']
        refresh = RefreshToken.for_user(user)
        user_serializer = UsuarioSerializer(user)
        response_data = {
            'access_token': str(refresh.access_token),
            'user': user_serializer.data  # Incluye 'role'
        }
        return Response(response_data, status=status.HTTP_200_OK)

class UsuarioRefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({"error": "No se ha proporcionado un refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            return Response({"access_token": new_access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "El refresh token no es válido o ha expirado."}, status=status.HTTP_400_BAD_REQUEST)

class UsuarioPasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['correo']
            envio = Thread(target=user.create_reset_token)
            envio.start()
            return Response({"message": "Correo enviado."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UsuarioPasswordChangeView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "La contraseña ha sido cambiada"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UsuarioGetProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

class UsuarioSendProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UsuarioSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UsuarioToggleStatus(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        usuario = get_user(pk)
        new_status = not usuario.is_active
        usuario.is_active = new_status
        usuario.save()
        serializer = UsuarioSerializer(usuario)
        return Response(
            {
                "message": f"Estado actualizado correctamente a {'activo' if new_status else 'inactivo'}",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

class UsuarioDelete(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        usuario = get_user(pk)
        usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class GroupListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtener todos los grupos disponibles
        groups = Group.objects.all()
        group_list = [{"id": group.id, "name": group.name} for group in groups]
        return Response(group_list, status=status.HTTP_200_OK)