from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

def create_roles_and_permissions(apps, schema_editor):
    # Obtener la aplicación 'usuarios'
    app_config = apps.get_app_config('usuarios')
    models = app_config.get_models()

    # Obtener permisos existentes para los modelos
    permission_objects = {}
    for model in models:
        content_type = ContentType.objects.get_for_model(model)
        model_name = model._meta.model_name
        permission_codenames = [
            f'view_{model_name}',
            f'add_{model_name}',
            f'change_{model_name}',
            f'delete_{model_name}',
        ]
        # Obtener permisos existentes en lugar de crear nuevos
        for codename in permission_codenames:
            try:
                perm = Permission.objects.get(
                    codename=codename,
                    content_type=content_type,
                )
                permission_objects[codename] = perm
            except Permission.DoesNotExist:
                # Si el permiso no existe, opcionalmente créalo
                perm = Permission.objects.create(
                    codename=codename,
                    name=f'Can {codename.replace("_", " ")}',
                    content_type=content_type,
                )
                permission_objects[codename] = perm

    # Crear roles y asignar todos los permisos a todos los roles
    for role_name in ['Administrador', 'Moderador', 'Colaborador']:
        group, _ = Group.objects.get_or_create(name=role_name)
        group.permissions.set(permission_objects.values())

def remove_roles_and_permissions(apps, schema_editor):
    Group.objects.filter(name__in=['Administrador', 'Moderador', 'Colaborador']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_roles_and_permissions, remove_roles_and_permissions),
    ]