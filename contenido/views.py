from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import Http404
from .models import Recurso, Contenido, VotoRecurso
from .serializers import RecursoSerializer, ContenidoSerializer
from django.http import JsonResponse
from django.core.exceptions import ValidationError
import pandas as pd
from collections import defaultdict
from django.db import transaction

def get_recurso(pk):
    try:
        return Recurso.objects.get(pk=pk)
    except Recurso.DoesNotExist:
        raise Http404('Recurso no encontrado')


class MisVotosRecursos(APIView):
    """Obtiene todos los votos del usuario logueado"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            votos = VotoRecurso.objects.filter(usuario=request.user).values(
                'recurso', 'tipo_voto'
            )
            
            return Response({
                'success': True,
                'votos': list(votos)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VotarRecurso(APIView):
    """Permite al usuario votar en un recurso"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            recurso_id = request.data.get('recurso_id')
            tipo_voto = request.data.get('tipo_voto')
            
            # Validaciones
            if not recurso_id or not tipo_voto:
                return Response({
                    'success': False,
                    'error': 'Faltan datos requeridos'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if tipo_voto not in ['like', 'dislike', 'mejora']:
                return Response({
                    'success': False,
                    'error': 'Tipo de voto inválido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener el recurso
            try:
                recurso = Recurso.objects.get(id=recurso_id)
            except Recurso.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Recurso no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Verificar si el usuario ya votó en este recurso
            voto_existente = VotoRecurso.objects.filter(
                usuario=request.user, 
                recurso=recurso
            ).first()
            
            if voto_existente:
                # Si ya votó, actualizar el voto
                voto_existente.tipo_voto = tipo_voto
                voto_existente.save()
            else:
                # Si no ha votado, crear nuevo voto
                VotoRecurso.objects.create(
                    usuario=request.user,
                    recurso=recurso,
                    tipo_voto=tipo_voto
                )
            
            # Refrescar el recurso para obtener los contadores actualizados
            recurso.refresh_from_db()
            
            return Response({
                'success': True,
                'message': 'Voto registrado correctamente',
                'numero_likes': recurso.numero_likes,
                'numero_dislikes': recurso.numero_dislikes,
                'numero_mejora': recurso.numero_mejora
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RemoverVotoRecurso(APIView):
    """Permite al usuario remover su voto de un recurso"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            recurso_id = request.data.get('recurso_id')
            
            if not recurso_id:
                return Response({
                    'success': False,
                    'error': 'ID de recurso requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener el recurso
            try:
                recurso = Recurso.objects.get(id=recurso_id)
            except Recurso.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Recurso no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Buscar y eliminar el voto del usuario
            voto_existente = VotoRecurso.objects.filter(
                usuario=request.user, 
                recurso=recurso
            ).first()
            
            if voto_existente:
                voto_existente.delete()
                message = 'Voto removido correctamente'
            else:
                message = 'No había voto previo'
            
            # Refrescar el recurso para obtener los contadores actualizados
            recurso.refresh_from_db()
            
            return Response({
                'success': True,
                'message': message,
                'numero_likes': recurso.numero_likes,
                'numero_dislikes': recurso.numero_dislikes,
                'numero_mejora': recurso.numero_mejora
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Función auxiliar para agregar información de votos del usuario a los recursos
def agregar_votos_usuario_a_recursos(recursos, usuario):
    """Función auxiliar para agregar información de votos del usuario a los recursos"""
    if not usuario.is_authenticated:
        return recursos
    
    # Obtener todos los votos del usuario para estos recursos
    votos_usuario = VotoRecurso.objects.filter(
        usuario=usuario,
        recurso__in=[r.id for r in recursos]
    ).values('recurso', 'tipo_voto')
    
    # Crear un diccionario para acceso rápido
    votos_dict = {voto['recurso']: voto['tipo_voto'] for voto in votos_usuario}
    
    # Agregar información de voto a cada recurso
    for recurso in recursos:
        recurso.voto_usuario = votos_dict.get(recurso.id, None)
    
    return recursos


# Modifica tu RecursoList existente para incluir información de votos
class RecursoListConVotos(APIView):
    """Lista de recursos con información de votos del usuario"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            # Obtenemos todos los recursos
            recursos = Recurso.objects.all()
            
            # Agregamos información de votos del usuario
            recursos_con_votos = agregar_votos_usuario_a_recursos(recursos, request.user)
            
            # Serializamos los datos
            serializer = RecursoSerializer(recursos_con_votos, many=True)
            
            # Agregamos manualmente la información de votos a cada recurso serializado
            data = serializer.data
            for i, recurso in enumerate(recursos_con_votos):
                if hasattr(recurso, 'voto_usuario'):
                    data[i]['voto_usuario'] = recurso.voto_usuario
                else:
                    data[i]['voto_usuario'] = None
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecursoRetrieveConVotos(APIView):
    """Detalle de recurso con información de voto del usuario"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            recurso = get_recurso(pk)
            
            # Obtener voto del usuario si existe
            voto_usuario = None
            if request.user.is_authenticated:
                voto_obj = VotoRecurso.objects.filter(
                    usuario=request.user, 
                    recurso=recurso
                ).first()
                if voto_obj:
                    voto_usuario = voto_obj.tipo_voto
            
            serializer = RecursoSerializer(recurso)
            data = serializer.data
            data['voto_usuario'] = voto_usuario
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Http404:
            return Response({
                'error': 'Recurso no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RecursoList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Obtenemos todos los recursos
        recursos = Recurso.objects.all()
        serializer = RecursoSerializer(recursos, many=True)
        return Response(serializer.data)


class RecursoRetrieve(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        recurso = get_recurso(pk)
        serializer = RecursoSerializer(recurso)
        return Response(serializer.data)


class RecursoCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        # Verificar si la solicitud contiene una lista o un diccionario (un recurso o varios)
        if isinstance(request.data, list):
            # Caso de múltiples recursos
            created_resources = []
            errors = []

            for recurso_data in request.data:
                # Verificar duplicidad por título (opcional, adaptar según necesidades)
                titulo = recurso_data.get('titulo')
                if Recurso.objects.filter(titulo=titulo).exists():
                    errors.append({"error": f"El recurso con título '{titulo}' ya existe."})
                    continue

                # Validar que se proporcionen contenidos
                contenidos = recurso_data.get('contenido')
                if not contenidos or len(contenidos) == 0:
                    errors.append({"error": f"Debe incluir al menos un contenido en el recurso con título '{titulo}'."})
                    continue

                # Crear el recurso y sus contenidos
                serializer = RecursoSerializer(data=recurso_data)
                if serializer.is_valid():
                    try:
                        # Aquí usamos el método create del serializer (no necesitamos crear manualmente los contenidos)
                        recurso = serializer.save()
                        created_resources.append(serializer.data)
                    except Exception as e:
                        # Si cualquier parte falla, revertimos la transacción
                        transaction.set_rollback(True)
                        errors.append({"error": f"Error al procesar el recurso con título '{titulo}': {str(e)}"})
                else:
                    errors.append({"error": f"Errores al validar el recurso con título '{titulo}': {serializer.errors}"})

            # Si se generaron errores, los devolvemos, si no, devolvemos los recursos creados
            if errors:
                return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"created_resources": created_resources}, status=status.HTTP_201_CREATED)

        elif isinstance(request.data, dict):
            # Caso de un solo recurso
            recurso_data = request.data
            # Verificar duplicidad por título (opcional)
            titulo = recurso_data.get('titulo')
            if titulo and Recurso.objects.filter(titulo=titulo).exists():
                return Response(
                    {"error": f"El recurso con título '{titulo}' ya existe."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validar que se proporcionen contenidos
            contenidos = recurso_data.get('contenido')
            if not contenidos or len(contenidos) == 0:
                return Response(
                    {"error": "Debe incluir al menos un contenido en el recurso."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Crear el recurso y sus contenidos
            serializer = RecursoSerializer(data=recurso_data)
            if serializer.is_valid():
                try:
                    # Aquí simplemente llamamos a save() del serializer que ya maneja la creación de contenidos
                    recurso = serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    # Si cualquier parte falla, revertimos la transacción
                    transaction.set_rollback(True)
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(
                {"error": "La solicitud debe contener un objeto JSON válido (un recurso o una lista de recursos)."},
                status=status.HTTP_400_BAD_REQUEST
            )



class RecursoUpdate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def put(self, request, pk):
        recurso = get_recurso(pk)
        serializer = RecursoSerializer(recurso, data=request.data)
        if serializer.is_valid():
            try:
                # Simplemente usamos el método update() del serializer que ya maneja
                # la actualización de los contenidos
                serializer.save()
                return Response(serializer.data)
                
            except Exception as e:
                transaction.set_rollback(True)
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecursoDelete(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        recurso = get_recurso(pk)
        # Borrar los contenidos antes de borrar el recurso
        recurso.contenido.all().delete()
        recurso.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecursoToggleValidado(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        recurso = get_recurso(pk)
        new_status = not recurso.validado
        recurso.validado = new_status
        recurso.save()

        serializer = RecursoSerializer(recurso)
        return Response(
            {
                "message": f"Estado actualizado correctamente a {'validado' if new_status else 'no validado'}",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class RecursoBulkUpload(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        excel_file = request.FILES.get('recursos')
        if not excel_file:
            return Response(
                {"error": "No se encontró el archivo Excel en la petición."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            df = pd.read_excel(excel_file)
            
            # Agrupar filas por título para manejar relaciones anidadas
            recursos_dict = defaultdict(lambda: {'contenido': []})
            
            # Procesar todas las filas del Excel
            for _, row in df.iterrows():
                # Validar campos obligatorios
                if not row.get('titulo'):
                    return Response(
                        {"error": "El campo 'titulo' es obligatorio en el archivo."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Extraer información básica del recurso
                titulo = str(row['titulo'])
                
                # Si es la primera vez que vemos este recurso, agregar datos del recurso
                if 'categoria' not in recursos_dict[titulo]:
                    recursos_dict[titulo].update({
                        'titulo': titulo,
                        'subtitulo': row.get('subtitulo', ''),
                        'categoria': row['categoria'],
                        'area': row['area'],
                        'descripcion': row.get('descripcion', ''),
                        'validado': row.get('validado', False),
                        'numero_likes': row.get('numero_likes', 0),
                        'numero_dislikes': row.get('numero_dislikes', 0),
                        'numero_mejora': row.get('numero_mejora', 0)
                    })
                
                # Extraer información del contenido
                if 'tipo_contenido' in row and pd.notna(row['tipo_contenido']):
                    contenido_data = {
                        'tipo_contenido': row['tipo_contenido'],
                        'contenido_bloque': row['contenido_bloque'],
                        'posicion': int(row.get('posicion', 0))
                    }
                    recursos_dict[titulo]['contenido'].append(contenido_data)
            
            # Crear recursos y contenidos usando las relaciones de Django
            recursos_creados = []
            errores = []
            
            for titulo, recurso_data in recursos_dict.items():
                # Verificar si el recurso ya existe
                if Recurso.objects.filter(titulo=titulo).exists():
                    errores.append(f"El recurso con título '{titulo}' ya existe.")
                    continue
                
                try:
                    # Crear recurso
                    recurso = Recurso.objects.create(
                        titulo=recurso_data['titulo'],
                        subtitulo=recurso_data['subtitulo'],
                        categoria=recurso_data['categoria'],
                        area=recurso_data['area'],
                        descripcion=recurso_data['descripcion'],
                        validado=recurso_data['validado'],
                        numero_likes=recurso_data['numero_likes'],
                        numero_dislikes=recurso_data['numero_dislikes'],
                        numero_mejora=recurso_data['numero_mejora']
                    )
                    
                    # Crear contenidos del recurso
                    for contenido_data in recurso_data['contenido']:
                        Contenido.objects.create(
                            recurso=recurso,
                            **contenido_data
                        )
                    
                    recursos_creados.append(recurso.titulo)
                
                except Exception as e:
                    errores.append(f"Error al crear el recurso '{titulo}': {str(e)}")
                    transaction.set_rollback(True)
            
            # Retornar resultado
            if errores:
                return Response(
                    {"error": "Errores durante la carga:", "detalles": errores},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {"message": f"Carga masiva de recursos realizada exitosamente. Recursos creados: {len(recursos_creados)}",
                 "recursos_creados": recursos_creados},
                status=status.HTTP_201_CREATED
            )
        
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "Error procesando el archivo: " + str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )