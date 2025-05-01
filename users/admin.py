from django.contrib import admin

from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['nombres', 'apellidos', 'email', 'role', 'is_active']
    search_fields = ['nombres', 'apellidos', 'email']
    list_filter = ['role', 'is_active']
