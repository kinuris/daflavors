from django.db import models
from accounts.models import ProviderProfile

class Venue(models.Model):
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='venues')
    name = models.CharField(max_length=255)
    description = models.TextField()
    address = models.TextField()
    capacity = models.PositiveIntegerField(help_text="Maximum number of guests")
    
    # Venue type choices
    TYPE_CHOICES = (
        ('restaurant', 'Restaurant PDR'),
        ('hotel', 'Hotel'),
        ('event_hall', 'Event Hall'),
        ('garden', 'Garden'),
        ('beachside', 'Beachside'),
        ('heritage', 'Heritage House'),
        ('other', 'Other'),
    )
    venue_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    
    # Operating hours/availability
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    
    # Venue policies
    booking_policy = models.TextField(blank=True)
    cancellation_policy = models.TextField(blank=True)
    corkage_policy = models.TextField(blank=True, help_text="Policy for bringing outside food/drinks")
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base price for venue rental")
    
    # Datetime fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class VenueImage(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='venue_images/')
    caption = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.venue.name}"

class VenueFeature(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='features')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class VenueRoom(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    
    # Room features
    has_av_equipment = models.BooleanField(default=False)
    has_stage = models.BooleanField(default=False)
    
    # Layout options
    LAYOUT_CHOICES = (
        ('theater', 'Theater'),
        ('classroom', 'Classroom'),
        ('banquet', 'Banquet'),
        ('boardroom', 'Boardroom'),
        ('cocktail', 'Cocktail'),
        ('other', 'Other'),
    )
    available_layouts = models.CharField(max_length=255, help_text="Comma-separated list of available layouts")
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, 
                               help_text="Price for this room specifically (if different from venue base price)")
    
    def __str__(self):
        return f"{self.name} at {self.venue.name}"

class VenueAvailability(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    is_available = models.BooleanField(default=True)
    
    # If want to specify morning/afternoon/evening availability
    morning_available = models.BooleanField(default=True)
    afternoon_available = models.BooleanField(default=True)
    evening_available = models.BooleanField(default=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Venue Availabilities"
        unique_together = ('venue', 'date')
        
    def __str__(self):
        status = "available" if self.is_available else "unavailable"
        return f"{self.venue.name} - {self.date} - {status}"
