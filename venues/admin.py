from django.contrib import admin
from .models import Venue, VenueImage, VenueAvailability

class VenueImageInline(admin.TabularInline):
    model = VenueImage
    extra = 3

class VenueAvailabilityInline(admin.TabularInline):
    model = VenueAvailability
    extra = 1

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'venue_type', 'capacity', 'base_price')
    list_filter = ('venue_type', 'created_at')
    search_fields = ('name', 'description', 'address')
    inlines = [VenueImageInline, VenueAvailabilityInline]

@admin.register(VenueImage)
class VenueImageAdmin(admin.ModelAdmin):
    list_display = ('venue', 'caption', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('venue__name', 'caption')

@admin.register(VenueAvailability)
class VenueAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('venue', 'date', 'is_available', 'morning_available', 'afternoon_available', 'evening_available')
    list_filter = ('is_available', 'morning_available', 'afternoon_available', 'evening_available', 'date')
    search_fields = ('venue__name', 'notes')
    date_hierarchy = 'date'
