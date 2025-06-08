#!/usr/bin/env python
"""
Test script to verify caterer form submission works correctly
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from accounts.models import ProviderProfile

User = get_user_model()

def test_caterer_form_submission():
    print("=" * 50)
    print("Testing Caterer Form Submission")
    print("=" * 50)
    
    # Create test client
    client = Client()
    
    # Get or create a test user and provider
    try:
        user = User.objects.get(email="test@example.com")
        print(f"✓ Using existing test user: {user.email}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            user_type="provider"
        )
        print(f"✓ Created test user: {user.email}")
    
    try:
        provider = ProviderProfile.objects.get(user=user)
        print(f"✓ Using existing provider: {provider}")
    except ProviderProfile.DoesNotExist:
        provider = ProviderProfile.objects.create(
            user=user,
            business_name="Test Catering Business",
            business_description="A test catering business",
            business_email="test@business.com",
            business_phone="123-456-7890",
            business_address="123 Test St, Test City",
            service_area="Test City"
        )
        print(f"✓ Created test provider: {provider}")
    
    # Login the user
    client.login(username="testuser", password="testpass123")
    print("✓ User logged in successfully")
    
    # Test form data with all required fields
    form_data = {
        'specialty': 'Filipino Cuisine',  # Required
        'min_guests': 20,                 # Required
        'max_guests': 200,               # Required
        'service_area': 'Roxas City, Panay Island',  # Required
        'offers_buffet': True,
        'offers_plated': True,
        'offers_cocktail': False,
        'offers_food_stalls': False,
        'setup_policy': 'We handle all setup and breakdown. Setup begins 2 hours before event.',
        'delivery_policy': 'Free delivery within 10km radius. Additional charges apply beyond.',
        'payment_policy': '50% deposit required upon booking. Balance due on event day.',
        'cancellation_policy': 'Full refund if cancelled 7+ days prior. 50% refund 3-7 days prior.'
    }
    
    print("\n" + "=" * 30)
    print("Submitting form with data:")
    print("=" * 30)
    for key, value in form_data.items():
        print(f"{key}: {value}")
    
    # Submit the form
    response = client.post('/caterers/create/', data=form_data, follow=True)
    
    print(f"\n✓ Form submitted. Response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Form submission successful!")
        
        # Check if caterer was created
        from caterers.models import Caterer
        try:
            caterer = Caterer.objects.get(provider=provider)
            print(f"✓ Caterer created successfully: {caterer.specialty}")
            print(f"  - Min guests: {caterer.min_guests}")
            print(f"  - Max guests: {caterer.max_guests}")
            print(f"  - Service area: {caterer.service_area}")
            return True
        except Caterer.DoesNotExist:
            print("✗ Caterer was not created in database")
            print("Response content:")
            print(response.content.decode()[:500] + "...")
            return False
    else:
        print(f"✗ Form submission failed with status {response.status_code}")
        print("Response content:")
        print(response.content.decode()[:500] + "...")
        return False

if __name__ == "__main__":
    success = test_caterer_form_submission()
    if success:
        print("\n🎉 TEST PASSED: Caterer form submission works correctly!")
    else:
        print("\n❌ TEST FAILED: Issues found with caterer form submission")
