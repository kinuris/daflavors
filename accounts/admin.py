from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, ProviderProfile

class ProviderProfileInline(admin.StackedInline):
    model = ProviderProfile
    can_delete = False
    verbose_name = 'Provider Profile'
    verbose_name_plural = 'Provider Profiles'
    readonly_fields = ('business_name', 'business_description', 'business_email', 'business_phone', 
                      'business_address', 'service_area', 'business_logo')

class CustomUserAdmin(UserAdmin):
    """
    Enhanced user admin with focus on monitoring and user management.
    Providers and their profiles are read-only to prevent admin interference.
    """
    list_display = ('username', 'email', 'full_name', 'user_type_display', 'provider_status', 'account_status', 'date_joined')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'provider_profile__business_name')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address', 'profile_picture')}),
        ('Account Status', {'fields': ('is_active', 'user_type')}),
        ('Admin Permissions', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
            'description': 'Only modify these for admin users. Provider permissions are managed automatically.'
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('username',)
    inlines = [ProviderProfileInline]
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or "-"
    full_name.short_description = 'Name'
    
    def user_type_display(self, obj):
        colors = {
            'client': 'blue',
            'provider': 'green', 
            'admin': 'red'
        }
        color = colors.get(obj.user_type, 'gray')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                         color, obj.get_user_type_display())
    user_type_display.short_description = 'User Type'
    
    def provider_status(self, obj):
        if obj.user_type == 'provider':
            try:
                profile = obj.provider_profile
                if profile.verified:
                    return format_html('<span style="color: green;">✅ Verified</span>')
                else:
                    return format_html('<span style="color: orange;">⏳ Pending</span>')
            except ProviderProfile.DoesNotExist:
                return format_html('<span style="color: red;">❌ No Profile</span>')
        return '-'
    provider_status.short_description = 'Provider Status'
    
    def account_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✅ Active</span>')
        else:
            return format_html('<span style="color: red;">❌ Inactive</span>')
    account_status.short_description = 'Account Status'
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        
        # Make provider user details mostly read-only to prevent admin interference
        if obj and obj.user_type == 'provider':
            readonly.extend(['username', 'first_name', 'last_name', 'email', 'phone_number', 'address'])
        
        return readonly

@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    """
    Read-only admin interface for monitoring provider profiles.
    Verification can be controlled by admin.
    """
    list_display = ('business_name', 'user', 'business_email', 'service_area', 'verification_status', 'has_venues', 'has_caterers')
    list_filter = ('verified', 'user__date_joined')
    search_fields = ('business_name', 'user__username', 'user__email', 'business_email', 'service_area')
    readonly_fields = ('user', 'business_name', 'business_description', 'business_email', 'business_phone', 
                      'business_address', 'service_area', 'business_logo')
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Business Information', {
            'fields': ('business_name', 'business_description', 'business_email', 'business_phone', 
                      'business_address', 'service_area', 'business_logo')
        }),
        ('Admin Controls', {
            'fields': ('verified',),
            'description': 'Control provider verification status.'
        }),
    )
    
    def verification_status(self, obj):
        if obj.verified:
            return format_html('<span style="color: green;">✅ Verified</span>')
        else:
            return format_html('<span style="color: orange;">⏳ Pending Verification</span>')
    verification_status.short_description = 'Status'
    
    def has_venues(self, obj):
        venue_count = obj.venues.count()
        if venue_count > 0:
            active_count = obj.venues.filter(is_active=True, is_suspended=False).count()
            return f"{active_count}/{venue_count} active"
        return "No venues"
    has_venues.short_description = 'Venues'
    
    def has_caterers(self, obj):
        try:
            caterer = obj.caterer
            if caterer.is_active and not caterer.is_suspended:
                return format_html('<span style="color: green;">✅ Active</span>')
            elif caterer.is_suspended:
                return format_html('<span style="color: red;">🚫 Suspended</span>')
            else:
                return format_html('<span style="color: orange;">⏸️ Inactive</span>')
        except:
            return "No caterer"
    has_caterers.short_description = 'Caterer'
    
    def has_add_permission(self, request):
        """Provider profiles should be created when users register as providers"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Provider profiles should not be deleted independently"""
        return False

admin.site.register(CustomUser, CustomUserAdmin)
