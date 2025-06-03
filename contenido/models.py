import os
import re
from unidecode import unidecode
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from biblioteca.modeloBase import BaseModel
from maestros.models import Categoria, Area
from usuarios.models import Usuario

class Recurso(BaseModel):
    titulo = models.CharField(max_length=400, verbose_name="Titulo")
    subtitulo = models.CharField(max_length=400, verbose_name="Subtitulo", null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True) 
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True) 
    descripcion = models.TextField(max_length=2000, verbose_name="Descripcion")
    validado = models.BooleanField(default=False, verbose_name="Validado")
    numero_likes = models.IntegerField(default=0, verbose_name="Numero likes")
    numero_dislikes = models.IntegerField(default=0, verbose_name="Numero dislikes")
    numero_mejora = models.IntegerField(default=0, verbose_name="Numero mejoras")

    class Meta:
        verbose_name = "Recurso"
        verbose_name_plural = "Recursos"
        db_table = "recursos"

    def __str__(self):
        return self.titulo.title()
    
class Contenido(BaseModel):
    TIPO_CHOICES = (
        ('text', 'Texto'),
        ('image', 'Imagen'),
        ('video', 'Video'),
        ('code', 'Código'),
        ('link', 'Enlace'),
    )
    tipo_contenido = models.CharField(max_length=20, choices=TIPO_CHOICES)
    contenido_bloque = models.TextField()
    posicion = models.IntegerField()
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Contenido"
        verbose_name_plural = "Contenidos"
        db_table = "contenidos"

    def __str__(self):
        return self.posicion.title()
    
class VotoRecurso(BaseModel):
    TIPO_VOTO_CHOICES = (
        ('like', 'Me gusta'),
        ('dislike', 'No me gusta'),
        ('mejora', 'Necesita mejora'),
    )
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name="Usuario")
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE, verbose_name="Recurso")
    tipo_voto = models.CharField(max_length=10, choices=TIPO_VOTO_CHOICES, verbose_name="Tipo de voto")
    
    class Meta:
        verbose_name = "Voto de Recurso"
        verbose_name_plural = "Votos de Recursos"
        db_table = "votos_recursos"
        unique_together = ('usuario', 'recurso')  # Un usuario solo puede votar una vez por recurso
    
    def __str__(self):
        return f"{self.usuario.username} - {self.recurso.titulo} - {self.get_tipo_voto_display()}"

# Señales para actualizar automáticamente los contadores en el modelo Recurso
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=VotoRecurso)
def actualizar_contadores_voto_guardado(sender, instance, created, **kwargs):
    """Actualiza los contadores cuando se guarda un voto"""
    recurso = instance.recurso
    
    # Recalcular todos los contadores
    votos = VotoRecurso.objects.filter(recurso=recurso)
    
    recurso.numero_likes = votos.filter(tipo_voto='like').count()
    recurso.numero_dislikes = votos.filter(tipo_voto='dislike').count()
    recurso.numero_mejora = votos.filter(tipo_voto='mejora').count()
    
    recurso.save(update_fields=['numero_likes', 'numero_dislikes', 'numero_mejora'])

@receiver(post_delete, sender=VotoRecurso)
def actualizar_contadores_voto_eliminado(sender, instance, **kwargs):
    """Actualiza los contadores cuando se elimina un voto"""
    recurso = instance.recurso
    
    # Recalcular todos los contadores
    votos = VotoRecurso.objects.filter(recurso=recurso)
    
    recurso.numero_likes = votos.filter(tipo_voto='like').count()
    recurso.numero_dislikes = votos.filter(tipo_voto='dislike').count()
    recurso.numero_mejora = votos.filter(tipo_voto='mejora').count()
    
    recurso.save(update_fields=['numero_likes', 'numero_dislikes', 'numero_mejora'])