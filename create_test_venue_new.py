#!/usr/bin/env python
import os
import django
import datetime
from decimal import Decimal

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "daflavors.settings")
django.setup()

# Import models
from django.contrib.auth import get_user_model
from accounts.models import ProviderProfile
from venues.models import Venue

User = get_user_model()

def create_test_venue():
    # Create a test user and provider
    try:
        user = User.objects.get(username='test_provider')
        print(f"Using existing provider user: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='test_provider',
            email='test@example.com',
            password='test123',
            first_name='Test',
            last_name='Provider',
        )
        user.user_type = 'provider'
        user.save()
        print(f"Created provider user: {user.username}")

    try:
        provider = ProviderProfile.objects.get(user=user)
        print(f"Using existing provider profile: {provider}")
    except ProviderProfile.DoesNotExist:
        provider = ProviderProfile.objects.create(
            user=user,
            business_name='Test Venue Provider',
            business_email='venue@test.com',
            business_phone='+1234567890',
            business_address='123 Test St',
            service_area='Test Area',
            verified=True
        )
        print(f"Created provider profile: {provider}")

    # Create a test venue
    venue = Venue.objects.create(
        provider=provider,
        name='Test Exhibition Hall',
        description='A test venue for exhibitions and events',
        address='456 Test Ave, Test City',
        capacity=300,
        venue_type='event_hall',
        opening_time=datetime.time(9, 0),  # 9:00 AM
        closing_time=datetime.time(21, 0),  # 9:00 PM
        booking_policy='Test booking policy',
        cancellation_policy='Test cancellation policy',
        base_price=Decimal('25000.00'),
        is_active=True,
        is_suspended=False
    )
    print(f"Created venue: {venue.name} (ID: {venue.id})")
    print(f"Active: {venue.is_active}")
    print(f"Suspended: {venue.is_suspended}")
    
    # Check all venues
    print("\nAll venues after creation:")
    for v in Venue.objects.all():
        print(f"- {v.name} (ID: {v.id})")
        print(f"  Active: {v.is_active}")
        print(f"  Suspended: {v.is_suspended}")
        print(f"  Available for booking: {v.is_available_for_booking()}")
        print(f"  Provider: {v.provider}")
        print()

if __name__ == "__main__":
    create_test_venue()
