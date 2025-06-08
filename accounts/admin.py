from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ProviderProfile

class ProviderProfileInline(admin.StackedInline):
    model = ProviderProfile
    can_delete = False
    verbose_name = 'Provider Profile'
    verbose_name_plural = 'Provider Profiles'

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_type', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    inlines = [ProviderProfileInline]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ProviderProfile)
