import os
import re
from unidecode import unidecode
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from biblioteca.modeloBase import BaseModel

class Area(BaseModel):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de area", unique=True)
    descripcion = models.TextField(max_length=300, verbose_name="Descripción de area")

    class Meta:
        verbose_name = "Area"
        verbose_name_plural = "Areas"
        db_table = "areas"

    def __str__(self):
        return self.nombre.title()
    
class Categoria(BaseModel):
    nombre = models.CharField(max_length=100, verbose_name="Nombre de categoria", unique=True)
    descripcion = models.TextField(max_length=300, verbose_name="Descripción de categoria")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        db_table = "categorias"

    def __str__(self):
        return self.nombre.title()
