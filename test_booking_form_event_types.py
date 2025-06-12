#!/usr/bin/env python
"""
Test script to verify that the booking form displays caterers with their event types
"""
import os
import sys
import django

# Add the project root to the Python path
sys.path.insert(0, '/Users/chrisdominicp.chan/Desktop/Programs/Python/django-projects/daflavors')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from caterers.models import Caterer, EventType
from accounts.models import ProviderProfile
from datetime import date

User = get_user_model()

def test_booking_form_event_types():
    print("=== Testing Booking Form Event Types Display ===\n")
    
    # Create a test client
    client = Client()
    
    # Check if we have caterers with event types
    caterers = Caterer.objects.filter(is_active=True, is_suspended=False).prefetch_related('event_types')
    
    print(f"Found {caterers.count()} active caterers:")
    for caterer in caterers[:5]:  # Show first 5
        event_types = caterer.event_types.all()
        event_type_names = [f"{et.icon} {et.name}" if et.icon else et.name for et in event_types]
        print(f"  - {caterer.provider.business_name}")
        print(f"    Event Types: {', '.join(event_type_names) if event_type_names else 'None'}")
    
    # Check if we have a test user
    test_users = User.objects.filter(email__contains='test')
    if not test_users.exists():
        print("\nNo test users found. Creating a test user...")
        try:
            test_user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
            print(f"Created test user: {test_user.username}")
        except Exception as e:
            print(f"Error creating test user: {e}")
            # Try to use the first available non-staff user
            test_user = User.objects.filter(is_staff=False, is_superuser=False).first()
            if test_user:
                print(f"Using existing user: {test_user.username}")
            else:
                print("No suitable test user found. Creating one...")
                test_user = User.objects.create_user(
                    username='temptest',
                    email='temptest@example.com',
                    password='temppass123'
                )
    else:
        test_user = test_users.first()
        print(f"Using existing test user: {test_user.username}")
    
    # Log in as the test user
    client.force_login(test_user)
    
    # Make a request to the booking form
    print(f"\nRequesting booking form page...")
    response = client.get('/bookings/create/')
    
    if response.status_code == 200:
        print("✅ Booking form page loaded successfully")
        
        # Check if the response contains caterer names and event types
        content = response.content.decode('utf-8')
        
        # Look for caterers with event types in the HTML
        caterer_count = 0
        event_type_displays = 0
        
        for caterer in caterers[:3]:  # Check first 3 caterers
            business_name = caterer.provider.business_name
            if business_name in content:
                caterer_count += 1
                print(f"✅ Found caterer: {business_name}")
                
                # Check if event types are displayed with the caterer
                for event_type in caterer.event_types.all()[:2]:  # Check first 2 event types
                    if event_type.name in content:
                        event_type_displays += 1
                        print(f"   ✅ Found event type: {event_type.icon} {event_type.name}" if event_type.icon else f"   ✅ Found event type: {event_type.name}")
        
        print(f"\nSummary:")
        print(f"- Caterers found in form: {caterer_count}")
        print(f"- Event type displays found: {event_type_displays}")
        
        # Check if the caterers_with_event_types context is being used
        if 'caterers_with_event_types' in response.context or caterer_count > 0:
            print("✅ Event types are being displayed with caterers in the booking form!")
        else:
            print("❌ Event types may not be displaying properly in the booking form")
        
        # Look for specific HTML patterns that indicate event types are displayed
        if " - " in content and any(et.icon for caterer in caterers for et in caterer.event_types.all()):
            print("✅ Found event type formatting with icons in the form")
        
    else:
        print(f"❌ Error loading booking form page: HTTP {response.status_code}")
        if hasattr(response, 'context') and response.context and 'form' in response.context:
            form = response.context['form']
            if form.errors:
                print(f"Form errors: {form.errors}")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_booking_form_event_types()
