from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializers import UserLoginSerializer
from django.http import Http404

# Create your views here.
class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) # Lanza una excepción si no es válido
        
        user = serializer.validated_data['correo']
        refresh = RefreshToken.for_user(user)

        response_data = {
            'access_token': str(refresh.access_token),
            'user_id': user.id,
            'correo': user.correo,
            'nombre': user.nombre,
            'apellido': user.apellido,
            'nombre_completo': f"{user.nombre} {user.apellido}".title(),
        }

        return Response(response_data, status=status.HTTP_200_OK)