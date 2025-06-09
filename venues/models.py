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
    
    # Admin monitoring fields
    is_active = models.BooleanField(default=True, help_text="Whether this venue is active and accepting bookings")
    is_suspended = models.BooleanField(default=False, help_text="Whether this venue has been suspended by admin")
    suspension_reason = models.TextField(blank=True, help_text="Reason for suspension (admin only)")
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspended_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='suspended_venues', limit_choices_to={'is_staff': True})
    
    # Datetime fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def is_available_for_booking(self):
        """Check if venue is available for new bookings"""
        return self.is_active and not self.is_suspended
    
    class Meta:
        ordering = ['name']

class VenueImage(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='venue_images/')
    caption = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.venue.name}"

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
