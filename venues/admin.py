from django.contrib import admin
from .models import Venue, VenueImage, VenueFeature, VenueRoom, VenueAvailability

class VenueImageInline(admin.TabularInline):
    model = VenueImage
    extra = 3

class VenueFeatureInline(admin.TabularInline):
    model = VenueFeature
    extra = 2

class VenueRoomInline(admin.TabularInline):
    model = VenueRoom
    extra = 1

class VenueAvailabilityInline(admin.TabularInline):
    model = VenueAvailability
    extra = 1

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'venue_type', 'capacity', 'base_price')
    list_filter = ('venue_type', 'created_at')
    search_fields = ('name', 'description', 'address')
    inlines = [VenueImageInline, VenueFeatureInline, VenueRoomInline, VenueAvailabilityInline]

@admin.register(VenueImage)
class VenueImageAdmin(admin.ModelAdmin):
    list_display = ('venue', 'caption', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('venue__name', 'caption')

@admin.register(VenueFeature)
class VenueFeatureAdmin(admin.ModelAdmin):
    list_display = ('venue', 'name')
    search_fields = ('venue__name', 'name', 'description')

@admin.register(VenueRoom)
class VenueRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'venue', 'capacity', 'has_av_equipment', 'has_stage')
    list_filter = ('has_av_equipment', 'has_stage')
    search_fields = ('name', 'venue__name', 'description')

@admin.register(VenueAvailability)
class VenueAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('venue', 'date', 'is_available', 'morning_available', 'afternoon_available', 'evening_available')
    list_filter = ('is_available', 'morning_available', 'afternoon_available', 'evening_available', 'date')
    search_fields = ('venue__name', 'notes')
    date_hierarchy = 'date'
