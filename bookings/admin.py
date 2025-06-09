from django.contrib import admin
from django.utils.html import format_html
from .models import Booking, MenuSelection, CourseSelection, Quote, Payment, Message

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Read-only admin interface for monitoring bookings.
    Admins can view booking details but cannot modify them.
    """
    list_display = ('id', 'client', 'event_type', 'venue', 'caterer', 'event_date', 'status_indicator', 'total_amount', 'deposit_status')
    list_filter = ('status', 'event_date', 'created_at', 'deposit_paid', 'final_payment_received', 
                   'venue__is_suspended', 'caterer__is_suspended')
    search_fields = ('client__username', 'client__email', 'venue__name', 'caterer__provider__business_name', 'special_requests')
    readonly_fields = ('client', 'venue', 'caterer', 'event_type', 'event_date', 'start_time', 'end_time', 
                      'guest_count', 'special_requests', 'status', 'total_amount', 'deposit_amount', 
                      'deposit_paid', 'final_payment_received', 'created_at', 'updated_at')
    date_hierarchy = 'event_date'
    
    fieldsets = (
        ('Event Information', {
            'fields': ('client', 'event_type', 'event_date', 'start_time', 'end_time', 'guest_count')
        }),
        ('Services', {
            'fields': ('venue', 'caterer')
        }),
        ('Special Requests', {
            'fields': ('special_requests',),
            'classes': ('collapse',)
        }),
        ('Status & Financial', {
            'fields': ('status', 'total_amount', 'deposit_amount', 'deposit_paid', 'final_payment_received')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_indicator(self, obj):
        status_colors = {
            'inquiry': 'blue',
            'quote_provided': 'orange',
            'pending_deposit': 'purple',
            'confirmed': 'green',
            'in_progress': 'teal',
            'completed': 'darkgreen',
            'cancelled': 'red'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                         color, obj.get_status_display())
    status_indicator.short_description = 'Status'
    
    def deposit_status(self, obj):
        if obj.deposit_paid:
            return format_html('<span style="color: green;">✅ Paid</span>')
        elif obj.deposit_amount:
            return format_html('<span style="color: red;">❌ Pending</span>')
        return '-'
    deposit_status.short_description = 'Deposit'
    
    def has_add_permission(self, request):
        """Bookings should be created by clients through the frontend"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Bookings should not be deleted by admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make bookings read-only for admin"""
        return False

@admin.register(MenuSelection)
class MenuSelectionAdmin(admin.ModelAdmin):
    list_display = ('booking', 'menu_package', 'vegetarian_count', 'gluten_free_count', 'menu_total_price')
    search_fields = ('booking__client__username', 'menu_package__name')
    readonly_fields = ('booking', 'menu_package', 'vegetarian_count', 'gluten_free_count', 
                      'nut_free_count', 'halal_count', 'other_dietary_requirements', 'notes', 
                      'menu_total_price', 'created_at', 'updated_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(CourseSelection)
class CourseSelectionAdmin(admin.ModelAdmin):
    list_display = ('menu_selection', 'course_category')
    search_fields = ('menu_selection__booking__client__username', 'course_category__name')
    readonly_fields = ('menu_selection', 'course_category', 'selected_items')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'total_amount', 'status_indicator', 'valid_until')
    list_filter = ('status', 'valid_until', 'created_at')
    search_fields = ('booking__client__username', 'booking__venue__name', 'client_notes', 'provider_notes')
    readonly_fields = ('booking', 'venue_cost', 'catering_cost', 'service_charges', 'additional_charges', 
                      'additional_charges_description', 'total_amount', 'status', 'valid_until', 
                      'provider_notes', 'client_notes', 'created_at', 'updated_at')
    date_hierarchy = 'valid_until'
    
    def status_indicator(self, obj):
        status_colors = {
            'draft': 'gray',
            'sent': 'blue',
            'accepted': 'green',
            'rejected': 'red',
            'expired': 'orange'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                         color, obj.get_status_display())
    status_indicator.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'amount', 'payment_type', 'payment_method', 'payment_date', 'confirmation_status')
    list_filter = ('payment_type', 'payment_method', 'is_confirmed', 'payment_date')
    search_fields = ('booking__client__username', 'reference_number')
    readonly_fields = ('booking', 'amount', 'payment_type', 'payment_method', 'reference_number', 
                      'is_confirmed', 'payment_date', 'created_at', 'updated_at')
    date_hierarchy = 'payment_date'
    
    def confirmation_status(self, obj):
        if obj.is_confirmed:
            return format_html('<span style="color: green;">✅ Confirmed</span>')
        else:
            return format_html('<span style="color: red;">❌ Pending</span>')
    confirmation_status.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'booking', 'read_status', 'sent_at')
    list_filter = ('is_read', 'sent_at')
    search_fields = ('sender__username', 'recipient__username', 'subject', 'content')
    readonly_fields = ('booking', 'sender', 'recipient', 'subject', 'content', 'is_read', 'sent_at')
    
    def read_status(self, obj):
        if obj.is_read:
            return format_html('<span style="color: green;">✅ Read</span>')
        else:
            return format_html('<span style="color: blue;">📧 Unread</span>')
    read_status.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
