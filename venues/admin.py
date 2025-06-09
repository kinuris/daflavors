from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Venue, VenueImage, VenueAvailability

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    """
    Admin interface for monitoring and managing venue status.
    Focused on suspension/activation rather than full CRUD operations.
    """
    list_display = ('name', 'provider_business_name', 'venue_type', 'capacity', 'status_indicator', 'created_at', 'suspension_info')
    list_filter = ('is_active', 'is_suspended', 'venue_type', 'created_at', 'suspended_at')
    search_fields = ('name', 'provider__business_name', 'provider__user__username', 'address')
    readonly_fields = ('provider', 'name', 'description', 'address', 'capacity', 'venue_type', 
                      'opening_time', 'closing_time', 'booking_policy', 'cancellation_policy', 
                      'corkage_policy', 'base_price', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Venue Information', {
            'fields': ('provider', 'name', 'description', 'address', 'capacity', 'venue_type', 
                      'opening_time', 'closing_time', 'base_price')
        }),
        ('Policies', {
            'fields': ('booking_policy', 'cancellation_policy', 'corkage_policy'),
            'classes': ('collapse',)
        }),
        ('Admin Controls', {
            'fields': ('is_active', 'is_suspended', 'suspension_reason', 'suspended_by', 'suspended_at'),
            'description': 'Use these controls to monitor and manage venue status.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def provider_business_name(self, obj):
        return obj.provider.business_name
    provider_business_name.short_description = 'Business Name'
    provider_business_name.admin_order_field = 'provider__business_name'
    
    def status_indicator(self, obj):
        if obj.is_suspended:
            return format_html('<span style="color: red; font-weight: bold;">🚫 SUSPENDED</span>')
        elif not obj.is_active:
            return format_html('<span style="color: orange; font-weight: bold;">⏸️ INACTIVE</span>')
        else:
            return format_html('<span style="color: green; font-weight: bold;">✅ ACTIVE</span>')
    status_indicator.short_description = 'Status'
    
    def suspension_info(self, obj):
        if obj.is_suspended and obj.suspended_at:
            return format_html('<span style="color: red;">Suspended: {}</span>', 
                             obj.suspended_at.strftime('%Y-%m-%d'))
        return '-'
    suspension_info.short_description = 'Suspension Date'
    
    def save_model(self, request, obj, form, change):
        # Auto-set suspension timestamp and admin when suspending
        if change and 'is_suspended' in form.changed_data:
            if obj.is_suspended and not obj.suspended_at:
                obj.suspended_at = timezone.now()
                obj.suspended_by = request.user
            elif not obj.is_suspended:
                obj.suspended_at = None
                obj.suspended_by = None
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        """Disable adding venues through admin - providers should create them"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting venues through admin - use suspension instead"""
        return False

# Remove the inline admin registrations to simplify the interface
# VenueImage and VenueAvailability will be managed through the main application

# Keep these for reference but with read-only access
@admin.register(VenueImage)
class VenueImageAdmin(admin.ModelAdmin):
    list_display = ('venue', 'caption', 'is_primary')
    list_filter = ('is_primary', 'venue__is_active', 'venue__is_suspended')
    search_fields = ('venue__name', 'caption')
    readonly_fields = ('venue', 'image', 'caption', 'is_primary')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(VenueAvailability)
class VenueAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('venue', 'date', 'is_available', 'morning_available', 'afternoon_available', 'evening_available')
    list_filter = ('is_available', 'date', 'venue__is_active', 'venue__is_suspended')
    search_fields = ('venue__name', 'notes')
    readonly_fields = ('venue', 'date', 'is_available', 'morning_available', 'afternoon_available', 
                      'evening_available', 'notes')
    date_hierarchy = 'date'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
