from django.db import models
from accounts.models import ProviderProfile

class EventType(models.Model):
    """Predefined event types that caterers can serve"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, help_text="Description of this event type")
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class or emoji")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0, help_text="Order for displaying event types")
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Event Type"
        verbose_name_plural = "Event Types"
    
    def __str__(self):
        return self.name

class Caterer(models.Model):
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='caterers')
    
    # Additional caterer-specific fields
    specialty = models.CharField(max_length=255, help_text="Main cuisine specialty")
    min_guests = models.PositiveIntegerField(default=10, help_text="Minimum number of guests for catering")
    max_guests = models.PositiveIntegerField(default=500, help_text="Maximum number of guests for catering")
    
    # Event types this caterer serves
    event_types = models.ManyToManyField(EventType, blank=True, related_name='caterers', 
                                       help_text="Types of events this caterer specializes in")
    
    # Service types offered
    offers_buffet = models.BooleanField(default=True)
    offers_plated = models.BooleanField(default=True)
    offers_cocktail = models.BooleanField(default=True)
    offers_food_stalls = models.BooleanField(default=False)
    
    # Service areas
    service_area = models.CharField(max_length=255, help_text="List of areas/cities served, comma separated")
    
    # Service policies
    setup_policy = models.TextField(blank=True)
    delivery_policy = models.TextField(blank=True)
    payment_policy = models.TextField(blank=True)
    cancellation_policy = models.TextField(blank=True)
    
    # Admin monitoring fields
    is_active = models.BooleanField(default=True, help_text="Whether this caterer is active and accepting bookings")
    is_suspended = models.BooleanField(default=False, help_text="Whether this caterer has been suspended by admin")
    suspension_reason = models.TextField(blank=True, help_text="Reason for suspension (admin only)")
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspended_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='suspended_caterers', limit_choices_to={'is_staff': True})
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.provider.business_name
    
    def is_available_for_booking(self):
        """Check if caterer is available for new bookings"""
        return self.is_active and not self.is_suspended
    
    def get_event_types_display(self):
        """Get comma-separated list of event types for display"""
        return ", ".join([event_type.name for event_type in self.event_types.all()])

class CatererImage(models.Model):
    caterer = models.ForeignKey(Caterer, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='caterer_images/')
    caption = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.caterer}"

class MenuPackage(models.Model):
    caterer = models.ForeignKey(Caterer, on_delete=models.CASCADE, related_name='menu_packages')
    name = models.CharField(max_length=255, help_text="E.g., 'Wedding Package A', 'Corporate Lunch Set'")
    description = models.TextField()
    
    # Package type
    PACKAGE_TYPE_CHOICES = (
        ('buffet', 'Buffet'),
        ('plated', 'Plated'),
        ('cocktail', 'Cocktail Reception'),
        ('food_stalls', 'Food Stalls'),
        ('mixed', 'Mixed Service'),
    )
    package_type = models.CharField(max_length=15, choices=PACKAGE_TYPE_CHOICES)
    
    # Pricing
    base_price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    min_persons = models.PositiveIntegerField(default=10)
    
    # Settings
    is_customizable = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def price_per_person(self):
        """Alias for base_price_per_person for template compatibility"""
        return self.base_price_per_person
    
    def __str__(self):
        return f"{self.name} - {self.caterer}"

class CourseCategory(models.Model):
    name = models.CharField(max_length=50)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Course Categories"
        ordering = ['display_order']
    
    def __str__(self):
        return self.name

class MenuItem(models.Model):
    caterer = models.ForeignKey(Caterer, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Categorization
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='menu_items')
    
    # Dietary info
    is_vegetarian = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    is_nut_free = models.BooleanField(default=False)
    is_halal = models.BooleanField(default=False)
    
    # Individual pricing if available outside packages
    individual_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Image
    image = models.ImageField(upload_to='menu_item_images/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class PackageItem(models.Model):
    package = models.ForeignKey(MenuPackage, on_delete=models.CASCADE, related_name='package_items')
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    items = models.ManyToManyField(MenuItem, related_name='in_packages')
    
    # How many items from this category can be selected
    selection_limit = models.PositiveIntegerField(default=1, 
        help_text="Number of items the customer can select from this category")
    
    # Is this course required or optional?
    is_required = models.BooleanField(default=True)
    
    # Additional price per person if this is a premium option
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        unique_together = ('package', 'course_category')
    
    def __str__(self):
        return f"{self.course_category.name} options for {self.package.name}"

class CatererAvailability(models.Model):
    caterer = models.ForeignKey(Caterer, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    is_available = models.BooleanField(default=True)
    
    # If want to specify morning/afternoon/evening availability
    morning_available = models.BooleanField(default=True)
    afternoon_available = models.BooleanField(default=True)
    evening_available = models.BooleanField(default=True)
    
    max_bookings_per_day = models.PositiveIntegerField(default=1)
    current_bookings = models.PositiveIntegerField(default=0)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Caterer Availabilities"
        unique_together = ('caterer', 'date')
        
    def __str__(self):
        status = "available" if self.is_available else "unavailable"
        return f"{self.caterer} - {self.date} - {status}"
