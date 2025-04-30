from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'role']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'nombres', 'apellidos')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
