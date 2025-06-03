from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import Http404
from ..models import Area
from ..serializers import AreaSerializer

def get_area(pk):
    try:
        return Area.objects.get(pk=pk)
    except Area.DoesNotExist:
        raise Http404('Area no encontrada')

class AreaList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        areas = Area.objects.all()
        serializer = AreaSerializer(areas, many=True)
        return Response(serializer.data)

class AreaRetrieve(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        area = get_area(pk)
        serializer = AreaSerializer(area)
        return Response(serializer.data)

class AreaCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AreaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AreaUpdate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        area = get_area(pk)
        serializer = AreaSerializer(area, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AreaDelete(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        area = get_area(pk)
        area.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AreaToggleStatus(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        area = get_area(pk)
        # Invertir el estado actual
        new_status = not area.is_active
        area.is_active = new_status
        area.save()
        
        # Serializar el resultado para responder
        serializer = AreaSerializer(area)
        return Response(
            {
                "message": f"Estado actualizado correctamente a {'activo' if new_status else 'inactivo'}",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
 