from django.contrib import admin
from .models import SiteSettings, FAQ, Testimonial

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Basic Information', {
            'fields': ('site_name', 'site_tagline', 'contact_email', 'contact_phone', 'address')
        }),
        ('Social Media', {
            'fields': ('facebook', 'instagram', 'twitter')
        }),
        ('SEO Settings', {
            'fields': ('meta_description', 'meta_keywords')
        }),
        ('Site Assets', {
            'fields': ('logo', 'favicon')
        }),
        ('Business Settings', {
            'fields': ('commission_rate_venues', 'commission_rate_caterers')
        }),
        ('Footer', {
            'fields': ('footer_text',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance of SiteSettings
        return SiteSettings.objects.count() == 0

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order')
    list_filter = ('category',)
    search_fields = ('question', 'answer', 'category')
    list_editable = ('order', 'category')
    ordering = ['order', 'category', 'question']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'company', 'rating', 'is_approved', 'order')
    list_filter = ('is_approved', 'rating')
    search_fields = ('name', 'position', 'company', 'testimonial')
    list_editable = ('is_approved', 'order')
    ordering = ['order', '-created_at']
