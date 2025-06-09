from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Caterer, CatererImage, MenuPackage, CourseCategory, MenuItem, PackageItem, CatererAvailability

@admin.register(Caterer)
class CatererAdmin(admin.ModelAdmin):
    """
    Admin interface for monitoring and managing caterer status.
    Focused on suspension/activation rather than full CRUD operations.
    """
    list_display = ('provider_business_name', 'specialty', 'service_area', 'guest_capacity', 'status_indicator', 'created_at', 'suspension_info')
    list_filter = ('is_active', 'is_suspended', 'offers_buffet', 'offers_plated', 'offers_cocktail', 'offers_food_stalls', 'created_at', 'suspended_at')
    search_fields = ('provider__business_name', 'provider__user__username', 'specialty', 'service_area')
    readonly_fields = ('provider', 'specialty', 'min_guests', 'max_guests', 'offers_buffet', 'offers_plated', 
                      'offers_cocktail', 'offers_food_stalls', 'service_area', 'setup_policy', 'delivery_policy', 
                      'payment_policy', 'cancellation_policy', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Caterer Information', {
            'fields': ('provider', 'specialty', 'service_area', 'min_guests', 'max_guests')
        }),
        ('Services Offered', {
            'fields': ('offers_buffet', 'offers_plated', 'offers_cocktail', 'offers_food_stalls'),
        }),
        ('Policies', {
            'fields': ('setup_policy', 'delivery_policy', 'payment_policy', 'cancellation_policy'),
            'classes': ('collapse',)
        }),
        ('Admin Controls', {
            'fields': ('is_active', 'is_suspended', 'suspension_reason', 'suspended_by', 'suspended_at'),
            'description': 'Use these controls to monitor and manage caterer status.'
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
    
    def guest_capacity(self, obj):
        return f"{obj.min_guests} - {obj.max_guests} guests"
    guest_capacity.short_description = 'Guest Capacity'
    
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
        """Disable adding caterers through admin - providers should create them"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting caterers through admin - use suspension instead"""
        return False

# Keep related models for monitoring but with read-only access
@admin.register(CatererImage)
class CatererImageAdmin(admin.ModelAdmin):
    list_display = ('caterer', 'caption', 'is_primary')
    list_filter = ('is_primary', 'caterer__is_active', 'caterer__is_suspended')
    search_fields = ('caterer__provider__business_name', 'caption')
    readonly_fields = ('caterer', 'image', 'caption', 'is_primary')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(MenuPackage)
class MenuPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'caterer', 'package_type', 'base_price_per_person', 'min_persons', 'is_customizable')
    list_filter = ('package_type', 'is_customizable', 'created_at', 'caterer__is_active', 'caterer__is_suspended')
    search_fields = ('name', 'description', 'caterer__provider__business_name')
    readonly_fields = ('caterer', 'name', 'description', 'package_type', 'base_price_per_person', 
                      'min_persons', 'is_customizable', 'created_at', 'updated_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_order')
    ordering = ['display_order', 'name']
    readonly_fields = ('name', 'display_order')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'caterer', 'course_category', 'is_vegetarian', 'is_gluten_free', 'is_nut_free', 'is_halal', 'individual_price')
    list_filter = ('course_category', 'is_vegetarian', 'is_gluten_free', 'is_nut_free', 'is_halal', 'caterer__is_active', 'caterer__is_suspended')
    search_fields = ('name', 'description', 'caterer__provider__business_name')
    readonly_fields = ('caterer', 'course_category', 'name', 'description', 'individual_price', 
                      'is_vegetarian', 'is_gluten_free', 'is_nut_free', 'is_halal')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(PackageItem)
class PackageItemAdmin(admin.ModelAdmin):
    list_display = ('package', 'course_category', 'selection_limit', 'is_required', 'additional_price')
    list_filter = ('course_category', 'is_required', 'package__caterer__is_active', 'package__caterer__is_suspended')
    search_fields = ('package__name', 'course_category__name')
    readonly_fields = ('package', 'course_category', 'selection_limit', 'is_required', 'additional_price', 'items')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(CatererAvailability)
class CatererAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('caterer', 'date', 'is_available', 'morning_available', 'afternoon_available', 'evening_available', 'max_bookings_per_day', 'current_bookings')
    list_filter = ('is_available', 'morning_available', 'afternoon_available', 'evening_available', 'date', 'caterer__is_active', 'caterer__is_suspended')
    search_fields = ('caterer__provider__business_name', 'notes')
    readonly_fields = ('caterer', 'date', 'is_available', 'morning_available', 'afternoon_available', 
                      'evening_available', 'max_bookings_per_day', 'current_bookings', 'notes')
    date_hierarchy = 'date'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
