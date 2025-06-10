#!/usr/bin/env python
import os
import django
import datetime

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "daflavors.settings")
django.setup()

# Now import your models
from venues.models import Venue, VenueImage
from accounts.models import CustomUser, ProviderProfile
from django.utils import timezone

def create_test_venue():
    # First check if we have any users
    if not CustomUser.objects.filter(is_staff=True).exists():
        print("Creating admin user...")
        admin_user = CustomUser.objects.create_superuser(
            username="testadmin",
            email="testadmin@daflavors.example.com",
            password="testpassword123"
        )
        print(f"Created admin user: {admin_user}")
    else:
        admin_user = CustomUser.objects.filter(is_staff=True).first()
        print(f"Using existing admin user: {admin_user}")
    
    # Check if we have any provider profiles
    if not hasattr(admin_user, 'provider_profile'):
        print("Creating provider profile...")
        provider = ProviderProfile.objects.create(
            user=admin_user,
            business_name="Test Provider Business",
            business_address="Test Address",
            business_phone="123456789",
            verified=True
        )
        print(f"Created provider profile: {provider}")
    else:
        provider = admin_user.provider_profile
        print(f"Using existing provider profile: {provider}")
    
    # Create a test venue
    venue_name = f"Test Venue {timezone.now().strftime('%Y%m%d%H%M%S')}"
    print(f"Creating venue: {venue_name}")
    
    venue = Venue.objects.create(
        provider=provider,
        name=venue_name,
        description="This is a test venue created for debugging",
        address="123 Test Street, Test City",
        capacity=100,
        venue_type="restaurant",
        opening_time=datetime.time(9, 0),
        closing_time=datetime.time(22, 0),
        booking_policy="Test booking policy",
        cancellation_policy="Test cancellation policy",
        base_price=5000.00,
        is_active=True,
        is_suspended=False
    )
    
    print(f"Created venue: {venue}")
    print(f"Venue is_active: {venue.is_active}")
    print(f"Venue is_suspended: {venue.is_suspended}")
    
    # Now check all venues
    print("\nAll venues:")
    for v in Venue.objects.all():
        print(f"- {v.name}")
        print(f"  ID: {v.id}")
        print(f"  Active: {v.is_active}")
        print(f"  Suspended: {v.is_suspended}")
        print(f"  Is available for booking: {v.is_available_for_booking()}")
        print(f"  Provider: {v.provider}")
        print("")
    
    return venue

if __name__ == "__main__":
    create_test_venue()
