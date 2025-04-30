from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('usuario', 'Usuario'),
    ]

    email = models.EmailField(unique=True)
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='usuario')
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nombres', 'apellidos']

    def __str__(self):
        return f"{self.email} ({self.role})"
