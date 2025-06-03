from rest_framework import serializers
from .models import Area, Categoria

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id', 'nombre', 'descripcion', 'is_active', 'updated_at', 'created_at']

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'is_active', 'updated_at', 'created_at']