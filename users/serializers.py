from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from enum import Enum
import re

User = get_user_model()

class RoleEnum(Enum):
    ADMIN = 'admin'
    EMPLEADO = 'empleado'

    @classmethod
    def choices(cls):
        return [(role.value, role.name.title()) for role in cls]

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    role = serializers.ChoiceField(choices=RoleEnum.choices(), default=RoleEnum.EMPLEADO.value)
    
    class Meta:
        model = User
        fields = ['id', 'nombres', 'apellidos', 'email', 'role', 'password', 'is_active']
        read_only_fields = ['id']

    def create(self, validated_data):
        request = self.context.get('request')
        current_user = request.user if request else None

        # Solo admin puede crear usuarios
        if not current_user or current_user.role != RoleEnum.ADMIN.value:
            raise PermissionDenied("Solo el administrador puede crear nuevos usuarios.")

        password = validated_data.pop('password', None)
        user = self.Meta.model(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        request = self.context.get('request')
        current_user = request.user if request else None

        # Solo admin puede modificar usuarios distintos a sí mismo
        if current_user and current_user.role != RoleEnum.ADMIN.value:
            if instance != current_user:
                raise PermissionDenied("No tienes permiso para modificar a otros usuarios.")
            
            # Empleado no puede cambiar su rol ni is_active
            if 'role' in validated_data or 'is_active' in validated_data:
                raise PermissionDenied("No puedes modificar tu rol ni el estado de la cuenta.")

        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance

    def validate_email(self, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise serializers.ValidationError("Correo electrónico no válido.")
        
        dominio = value.split('@')[1]
        if dominio in ['gmail.com']:
            raise serializers.ValidationError("No se permiten correos personales.")
        
        return value

    def validate_role(self, value):
        if value not in [r.value for r in RoleEnum]:
            raise serializers.ValidationError("Rol inválido.")
        return value

    def validate(self, data):
        # Evita duplicados solo al crear
        if self.instance is None:
            if User.objects.filter(
                nombres=data.get('nombres'), 
                apellidos=data.get('apellidos'), 
                is_active=True
            ).exists():
                raise serializers.ValidationError("Ya existe un usuario activo con estos nombres y apellidos.")
        return data
