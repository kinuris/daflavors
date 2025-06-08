from django.db import models
from accounts.models import CustomUser
from venues.models import Venue
from caterers.models import Caterer, MenuPackage, MenuItem, CourseCategory

class Booking(models.Model):
    # Basic booking information
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    
    # Event can be at a venue, with a caterer, or both
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    caterer = models.ForeignKey(Caterer, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    
    # Event details
    event_type = models.CharField(max_length=100, help_text="Type of event (Wedding, Corporate, Birthday, etc.)")
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    guest_count = models.PositiveIntegerField()
    
    # Special requests and notes
    special_requests = models.TextField(blank=True)
    
    # Status tracking
    STATUS_CHOICES = (
        ('inquiry', 'Inquiry'),
        ('quote_provided', 'Quote Provided'),
        ('pending_deposit', 'Pending Deposit'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inquiry')
    
    # Financial tracking
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deposit_paid = models.BooleanField(default=False)
    final_payment_received = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        event_location = self.venue.name if self.venue else "No venue specified"
        return f"{self.client.username}'s {self.event_type} at {event_location} on {self.event_date}"

class MenuSelection(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='menu_selection')
    menu_package = models.ForeignKey(MenuPackage, on_delete=models.CASCADE)
    
    # Special dietary requirements
    vegetarian_count = models.PositiveIntegerField(default=0)
    gluten_free_count = models.PositiveIntegerField(default=0)
    nut_free_count = models.PositiveIntegerField(default=0)
    halal_count = models.PositiveIntegerField(default=0)
    other_dietary_requirements = models.TextField(blank=True)
    
    # Menu notes
    notes = models.TextField(blank=True)
    
    # Financial
    menu_total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Menu for {self.booking}"

class CourseSelection(models.Model):
    menu_selection = models.ForeignKey(MenuSelection, on_delete=models.CASCADE, related_name='course_selections')
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    selected_items = models.ManyToManyField(MenuItem)
    
    def __str__(self):
        return f"{self.course_category.name} selections for {self.menu_selection.booking}"

class Quote(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='quotes')
    
    # Quote details
    venue_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    catering_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    service_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    additional_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    additional_charges_description = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Quote status
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent to Client'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    # Validity
    valid_until = models.DateField()
    
    # Notes
    provider_notes = models.TextField(blank=True, help_text="Notes from provider, not visible to client")
    client_notes = models.TextField(blank=True, help_text="Notes visible to client")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Quote #{self.id} for {self.booking}"

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    PAYMENT_TYPE_CHOICES = (
        ('deposit', 'Deposit'),
        ('final', 'Final Payment'),
        ('additional', 'Additional Payment'),
    )
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES)
    
    PAYMENT_METHOD_CHOICES = (
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('gcash', 'GCash'),
        ('maya', 'Maya'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    )
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES)
    
    # For reference/tracking
    reference_number = models.CharField(max_length=100, blank=True)
    
    # Status
    is_confirmed = models.BooleanField(default=False)
    
    # Timestamps
    payment_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.payment_type} payment of ₱{self.amount} for {self.booking}"

class Message(models.Model):
    # Who is involved
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    
    # Message content
    subject = models.CharField(max_length=255)
    content = models.TextField()
    
    # Status
    is_read = models.BooleanField(default=False)
    
    # Timestamps
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}: {self.subject}"
