from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .models import Usuario
from django.contrib.auth.models import Group

class UsuarioSerializer(serializers.ModelSerializer):
    # Cambia de SerializerMethodField a PrimaryKeyRelatedField para el role
    role = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), required=False)
    role_name = serializers.SerializerMethodField()  # Campo adicional para devolver el nombre del rol

    class Meta:
        model = Usuario
        fields = ['id', 'nombre_completo', 'correo', 'is_active', 'role', 'role_name', 'updated_at', 'password', 'is_admin']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'is_admin': {'write_only': True}
        }

    def __init__(self, *args, **kwargs):
        super(UsuarioSerializer, self).__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields['password'].required = False 

    def get_role_name(self, obj):
        # Devuelve el nombre del rol asociado
        return obj.role.name if obj.role else None

    def create(self, validated_data):
        correo = validated_data['correo'].lower()
        is_admin = validated_data.pop('is_admin', False)
        
        if is_admin:
            user = Usuario.objects.create_superuser(
                nombre_completo=validated_data['nombre_completo'],
                correo=correo,
                password=validated_data['password'],
                role=validated_data.get('role')
            )
        else:
            user = Usuario.objects.create_user(
                nombre_completo=validated_data['nombre_completo'],
                correo=correo,
                password=validated_data['password'],
                role=validated_data.get('role')
            )
        return user

    def update(self, instance, validated_data):
        instance.nombre_completo = validated_data.get('nombre_completo', instance.nombre_completo)
        instance.correo = validated_data.get('correo', instance.correo).lower()
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.is_admin = validated_data.get('is_admin', instance.is_admin)
        instance.is_superuser = instance.is_admin

        # Aquí no es necesario buscar el role porque ya lo hemos asignado a través de PrimaryKeyRelatedField
        role_data = validated_data.get('role', None)
        if role_data:
            instance.role = role_data  # Ya es el objeto Group, no es necesario buscarlo

        print(f"Role before save: {instance.role}")  # Verifica que el role esté asignado correctamente
        instance.save()  # Guardar la instancia después de asignar el role
        return instance

class UsuarioLoginSerializer(serializers.Serializer):
    correo = serializers.CharField(max_length=100, required=False)
    password = serializers.CharField(max_length=100, required=False)

    def validate(self, data):
        correo = data.get('correo', None)
        password = data.get('password', None)

        if not correo or not password:
            raise serializers.ValidationError({"error": "Debe proporcionar un correo electrónico y una contraseña."})

        correo = correo.lower()
        try:
            user = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({"error": "No se encontró un usuario con este correo electrónico."})

        if not user.check_password(password):
            raise serializers.ValidationError({"error": "La contraseña proporcionada es incorrecta."})

        if not user.is_active:
            raise serializers.ValidationError({"error": "Su cuenta está inactiva, contacte al administrador."})

        data['correo'] = user
        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    correo = serializers.EmailField()

    def validate_correo(self, value):
        try:
            user = Usuario.objects.get(correo=value)
            if not user.is_active:
                raise serializers.ValidationError("Su cuenta está inactiva. Contacte al administrador.")
            return user
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("No se encontró un usuario con este correo electrónico.")

class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_token(self, value):
        try:
            user = Usuario.objects.get(reset_password_token=value)
            if user.reset_password_token_expires_at < timezone.now():
                raise serializers.ValidationError("El token ha expirado.")
            return value
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Token inválido.")

    def save(self):
        token = self.validated_data['token']
        new_password = self.validated_data['new_password']
        user = Usuario.objects.get(reset_password_token=token)
        user.set_password(new_password)
        user.reset_password_token = None
        user.reset_password_token_expires_at = None
        user.save()