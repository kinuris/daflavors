from django.contrib import admin
from .models import Booking, MenuSelection, CourseSelection, Quote, Payment, Message

class MenuSelectionInline(admin.StackedInline):
    model = MenuSelection
    can_delete = False
    verbose_name = 'Menu Selection'
    verbose_name_plural = 'Menu Selections'

class CourseSelectionInline(admin.TabularInline):
    model = CourseSelection
    extra = 1
    
class QuoteInline(admin.TabularInline):
    model = Quote
    extra = 0
    max_num = 3
    fields = ('total_amount', 'status', 'valid_until')
    readonly_fields = ('total_amount', 'status')

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('payment_date', 'payment_type', 'amount', 'payment_method', 'is_confirmed')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'event_type', 'venue', 'caterer', 'event_date', 'status', 'total_amount', 'deposit_paid')
    list_filter = ('status', 'event_date', 'created_at', 'deposit_paid', 'final_payment_received')
    search_fields = ('client__username', 'client__email', 'venue__name', 'caterer__provider__business_name', 'special_requests')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'event_date'
    inlines = [MenuSelectionInline, QuoteInline, PaymentInline]

@admin.register(MenuSelection)
class MenuSelectionAdmin(admin.ModelAdmin):
    list_display = ('booking', 'menu_package', 'vegetarian_count', 'gluten_free_count', 'menu_total_price')
    search_fields = ('booking__client__username', 'menu_package__name')
    inlines = [CourseSelectionInline]

@admin.register(CourseSelection)
class CourseSelectionAdmin(admin.ModelAdmin):
    list_display = ('menu_selection', 'course_category')
    search_fields = ('menu_selection__booking__client__username', 'course_category__name')
    filter_horizontal = ('selected_items',)

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'total_amount', 'status', 'valid_until')
    list_filter = ('status', 'valid_until', 'created_at')
    search_fields = ('booking__client__username', 'booking__venue__name', 'client_notes', 'provider_notes')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'valid_until'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'amount', 'payment_type', 'payment_method', 'payment_date', 'is_confirmed')
    list_filter = ('payment_type', 'payment_method', 'is_confirmed', 'payment_date')
    search_fields = ('booking__client__username', 'reference_number')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'payment_date'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'booking', 'is_read', 'sent_at')
    list_filter = ('is_read', 'sent_at')
    search_fields = ('sender__username', 'recipient__username', 'subject', 'content')
    readonly_fields = ('sent_at',)
