from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Unregister the original User admin
admin.site.unregister(User)

# Register User with custom admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
