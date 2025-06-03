from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import uuid

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, correo, password=None, role=None, **extra_fields):
        if not correo:
            raise ValueError('El usuario debe tener un correo electrónico')
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, role=role, **extra_fields)  # Aquí asignamos el role
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, correo, nombre_completo, password=None):
        """
        Creates and saves a superuser with the given email, first name, last name, and password.
        """
        user = self.create_user(
            correo,
            password=password,
            nombre_completo=nombre_completo,
        )
        user.is_admin = True
        user.is_superuser = True
        user.save()
        return user

class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre_completo = models.CharField(max_length=200, verbose_name='Nombre completo')
    correo = models.EmailField(verbose_name='Correo', max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    role = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    #token settings
    reset_password_token = models.CharField(max_length=200, blank=True, null=True)
    reset_password_token_expires_at = models.DateTimeField(blank=True, null=True)
    objects = UserManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre_completo']
    
    class  Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombre_completo}".title()
    
    def create_reset_token(self):
       
        token = str(uuid.uuid4())
       
        self.reset_password_token = token
        self.reset_password_token_expires_at = timezone.now() + timedelta(hours=1)
        self.save()

      

    @property
    def is_staff(self):
        return self.is_admin
    
    @property
    def get_full_name(self):
        return f"{self.nombre_completo}".title()
    
