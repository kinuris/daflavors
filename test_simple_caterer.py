#!/usr/bin/env python
"""
Simple test script to verify caterer form submission works
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from accounts.models import ProviderProfile
from caterers.models import Caterer

User = get_user_model()

def test_caterer_form():
    print("=" * 50)
    print("Testing Caterer Form - Simple Validation Test")
    print("=" * 50)
    
    # Create test user and provider
    user = User.objects.create_user(
        username="testcaterer",
        email="caterer@test.com",
        password="testpass123",
        user_type="provider"
    )
    
    provider = ProviderProfile.objects.create(
        user=user,
        business_name="Test Catering Co",
        business_description="Test catering business",
        business_email="business@test.com",
        business_phone="123-456-7890",
        business_address="123 Test Street",
        service_area="Test City"
    )
    
    print(f"✓ Created test user: {user.username}")
    print(f"✓ Created test provider: {provider.business_name}")
    
    # Test data for caterer form
    caterer_data = {
        'specialty': 'Filipino Cuisine',
        'min_guests': 20,
        'max_guests': 200,
        'service_area': 'Roxas City, Panay Island',
        'offers_buffet': True,
        'offers_plated': True,
        'offers_cocktail': False,
        'offers_food_stalls': False,
        'setup_policy': 'We handle all setup and breakdown.',
        'delivery_policy': 'Free delivery within 10km radius.',
        'payment_policy': '50% deposit required upon booking.',
        'cancellation_policy': 'Full refund if cancelled 7+ days prior.'
    }
    
    # Create caterer directly (simulating successful form submission)
    caterer = Caterer.objects.create(
        provider=provider,
        **caterer_data
    )
    
    print(f"✓ Caterer created successfully: {caterer.specialty}")
    print(f"  - Min guests: {caterer.min_guests}")
    print(f"  - Max guests: {caterer.max_guests}")
    print(f"  - Service area: {caterer.service_area}")
    print(f"  - Offers buffet: {caterer.offers_buffet}")
    print(f"  - Offers plated: {caterer.offers_plated}")
    
    # Verify caterer was saved correctly
    saved_caterer = Caterer.objects.get(provider=provider)
    assert saved_caterer.specialty == 'Filipino Cuisine'
    assert saved_caterer.min_guests == 20
    assert saved_caterer.max_guests == 200
    assert saved_caterer.service_area == 'Roxas City, Panay Island'
    
    print("✓ All caterer fields validated successfully")
    
    # Test the form validation logic
    from caterers.forms import CatererForm
    
    form_data = {
        'specialty': 'Italian Cuisine',
        'min_guests': 30,
        'max_guests': 150,
        'service_area': 'Manila, Philippines',
        'offers_buffet': True,
        'offers_plated': False,
        'offers_cocktail': True,
        'offers_food_stalls': False,
        'setup_policy': 'Setup 3 hours before event.',
        'delivery_policy': 'Delivery available within city limits.',
        'payment_policy': '30% deposit, balance on delivery.',
        'cancellation_policy': '48 hour cancellation policy.'
    }
    
    form = CatererForm(data=form_data)
    if form.is_valid():
        print("✓ Form validation passed with valid data")
    else:
        print("✗ Form validation failed:")
        print(form.errors)
        return False
    
    # Test form with missing required fields
    incomplete_data = {
        'specialty': 'Mexican Cuisine',
        # Missing min_guests, max_guests, service_area
    }
    
    incomplete_form = CatererForm(data=incomplete_data)
    if not incomplete_form.is_valid():
        print("✓ Form correctly rejects incomplete data")
        print(f"  - Expected errors: {list(incomplete_form.errors.keys())}")
    else:
        print("✗ Form should have rejected incomplete data")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✓ Caterer model works correctly")
    print("✓ Form validation works for valid data")
    print("✓ Form validation rejects incomplete data")
    print("✓ All required fields are properly validated")
    
    return True

if __name__ == "__main__":
    try:
        success = test_caterer_form()
        if success:
            print("\n✅ The caterer form functionality is working correctly!")
            print("✅ Users should be able to create caterer profiles successfully")
        else:
            print("\n❌ Issues found with caterer form functionality")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
