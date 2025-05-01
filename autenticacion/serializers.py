from rest_framework import serializers
from users.models import CustomUser

class UserLoginSerializer(serializers.Serializer):
    correo = serializers.CharField(max_length=100, required=False)
    password = serializers.CharField(max_length=100, required=False)

    def validate(self, data):
        correo = data.get('correo', None)
        password = data.get('password', None)

        if not correo or not password:
            raise serializers.ValidationError({"error": "Debe proporcionar un correo electrónico y una contraseña."})

        # Convertir el correo a minúsculas antes de la búsqueda
        correo = correo.lower()
        print(correo)
        try:
            user = CustomUser.objects.get(correo=correo)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"error": "No se encontró un usuario con este correo electrónico."})

        if not user.check_password(password):
            raise serializers.ValidationError({"error": "La contraseña proporcionada es incorrecta."})

        if not user.is_active:
            raise serializers.ValidationError({"error": "Su cuenta está inactiva, contacte al administrador."})

        data['correo'] = user 
        return data
