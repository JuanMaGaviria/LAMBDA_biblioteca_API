from rest_framework import serializers
from .models import Contenido, Recurso

class ContenidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contenido
        fields = [
            'id',
            'tipo_contenido',
            'contenido_bloque',
            'posicion',
            'recurso',
        ]
        # Hacemos que el campo recurso sea de solo lectura ya que se asignará automáticamente
        read_only_fields = ['recurso']

class RecursoSerializer(serializers.ModelSerializer):
    # Definimos el campo contenido como una relación anidada que puede ser escrita
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    contenido = ContenidoSerializer(many=True, read_only=False, required=False)
    
    class Meta:
        model = Recurso
        fields = [
            'id',
            'titulo',
            'subtitulo',
            'categoria',
            'categoria_nombre',
            'area',
            'descripcion',
            'validado',
            'numero_likes',
            'numero_dislikes',
            'numero_mejora',
            'created_at',
            'updated_at',
            'contenido',  # Importante: incluir el campo contenido aquí
        ]
    
    def create(self, validated_data):
        # Extraer los datos de contenido antes de crear el recurso
        contenidos_data = validated_data.pop('contenido', [])
        
        # Crear el recurso
        recurso = Recurso.objects.create(**validated_data)
        
        # Crear cada contenido asociado al recurso
        for contenido_data in contenidos_data:
            Contenido.objects.create(recurso=recurso, **contenido_data)
            
        return recurso
    
    def update(self, instance, validated_data):
        # Extraer los datos de contenido
        contenidos_data = validated_data.pop('contenido', [])
        
        # Actualizar los campos del recurso
        instance.titulo = validated_data.get('titulo', instance.titulo)
        instance.subtitulo = validated_data.get('subtitulo', instance.subtitulo)
        instance.categoria = validated_data.get('categoria', instance.categoria)
        instance.area = validated_data.get('area', instance.area)
        instance.descripcion = validated_data.get('descripcion', instance.descripcion)
        instance.validado = validated_data.get('validado', instance.validado)
        instance.numero_likes = validated_data.get('numero_likes', instance.numero_likes)
        instance.numero_dislikes = validated_data.get('numero_dislikes', instance.numero_dislikes)
        instance.numero_mejora = validated_data.get('numero_mejora', instance.numero_mejora)
        instance.save()
        
        # Opcionalmente, eliminar contenidos existentes y crear nuevos
        if contenidos_data:
            instance.contenido.all().delete()
            for contenido_data in contenidos_data:
                Contenido.objects.create(recurso=instance, **contenido_data)
        
        return instance
    
    def to_representation(self, instance):
        # Obtener la representación estándar del recurso
        representation = super().to_representation(instance)
        
        # Obtener los contenidos del recurso
        contenidos = Contenido.objects.filter(recurso=instance).order_by('posicion')
        
        # Serializar los contenidos
        contenido_serializer = ContenidoSerializer(contenidos, many=True)
        representation['contenido'] = contenido_serializer.data
        
        return representation