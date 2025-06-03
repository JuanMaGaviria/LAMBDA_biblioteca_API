from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import Http404
from ..models import Categoria
from ..serializers import CategoriaSerializer

def get_categoria(pk):
    try:
        return Categoria.objects.get(pk=pk)
    except Categoria.DoesNotExist:
        raise Http404('Categoria no encontrada')

class CategoriaList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        categorias = Categoria.objects.all()
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data)

class CategoriaRetrieve(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        categoria = get_categoria(pk)
        serializer = CategoriaSerializer(categoria)
        return Response(serializer.data)

class CategoriaCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CategoriaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoriaUpdate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        categoria = get_categoria(pk)
        serializer = CategoriaSerializer(categoria, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoriaDelete(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        categoria = get_categoria(pk)
        categoria.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CategoriaToggleStatus(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        categoria = get_categoria(pk)
        # Invertir el estado actual
        new_status = not categoria.is_active
        categoria.is_active = new_status
        categoria.save()
        # Serializar el resultado para responder
        serializer = CategoriaSerializer(categoria)
        return Response(
            {
                "message": f"Estado actualizado correctamente a {'activo' if new_status else 'inactivo'}",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
 