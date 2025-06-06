from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_owner', 'is_staff', 'is_active'] 

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_owner',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_owner',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

