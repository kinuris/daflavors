from django.contrib import admin
from .models import Caterer, CatererImage, MenuPackage, CourseCategory, MenuItem, PackageItem, CatererAvailability

class CatererImageInline(admin.TabularInline):
    model = CatererImage
    extra = 3

@admin.register(Caterer)
class CatererAdmin(admin.ModelAdmin):
    list_display = ('provider', 'specialty', 'min_guests', 'max_guests')
    list_filter = ('offers_buffet', 'offers_plated', 'offers_cocktail', 'offers_food_stalls')
    search_fields = ('provider__business_name', 'specialty', 'service_area')
    inlines = [CatererImageInline]

@admin.register(CatererImage)
class CatererImageAdmin(admin.ModelAdmin):
    list_display = ('caterer', 'caption', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('caterer__provider__business_name', 'caption')

class PackageItemInline(admin.TabularInline):
    model = PackageItem
    extra = 1

@admin.register(MenuPackage)
class MenuPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'caterer', 'package_type', 'base_price_per_person', 'min_persons', 'is_customizable')
    list_filter = ('package_type', 'is_customizable', 'created_at')
    search_fields = ('name', 'description', 'caterer__provider__business_name')
    inlines = [PackageItemInline]

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_order')
    ordering = ['display_order', 'name']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'caterer', 'course_category', 'is_vegetarian', 'is_gluten_free', 'is_nut_free', 'is_halal', 'individual_price')
    list_filter = ('course_category', 'is_vegetarian', 'is_gluten_free', 'is_nut_free', 'is_halal')
    search_fields = ('name', 'description', 'caterer__provider__business_name')

@admin.register(PackageItem)
class PackageItemAdmin(admin.ModelAdmin):
    list_display = ('package', 'course_category', 'selection_limit', 'is_required', 'additional_price')
    list_filter = ('course_category', 'is_required')
    search_fields = ('package__name', 'course_category__name')
    filter_horizontal = ('items',)

@admin.register(CatererAvailability)
class CatererAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('caterer', 'date', 'is_available', 'morning_available', 'afternoon_available', 'evening_available', 'max_bookings_per_day', 'current_bookings')
    list_filter = ('is_available', 'morning_available', 'afternoon_available', 'evening_available', 'date')
    search_fields = ('caterer__provider__business_name', 'notes')
    date_hierarchy = 'date'
