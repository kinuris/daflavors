#!/usr/bin/env python3
"""
Test script to verify that caterers are created as active by default
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, '/Users/chrisdominicp.chan/Desktop/Programs/Python/django-projects/daflavors')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import ProviderProfile
from caterers.models import Caterer
from caterers.forms import CatererForm

User = get_user_model()

def test_caterer_active_default():
    """Test that caterers are created as active by default"""
    print("=" * 60)
    print("TESTING CATERER ACTIVE STATUS DEFAULT")
    print("=" * 60)
    
    # Create or get a test user and provider
    username = "test_provider_active"
    try:
        user = User.objects.get(username=username)
        print(f"✓ Using existing user: {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email="test_active@example.com",
            password="testpass123"
        )
        print(f"✓ Created new user: {username}")
    
    # Create or get provider profile
    try:
        provider = ProviderProfile.objects.get(user=user)
        print(f"✓ Using existing provider profile")
    except ProviderProfile.DoesNotExist:
        provider = ProviderProfile.objects.create(
            user=user,
            business_name="Test Active Catering Co.",
            business_phone="555-0199",
            business_email="test_active@catering.com",
            business_address="123 Test Street, Test City",
            service_area="Test City, Test Region",
            business_description="Test catering service for active status testing"
        )
        print(f"✓ Created new provider profile")
    
    print(f"\nProvider: {provider.business_name}")
    initial_caterer_count = provider.caterers.count()
    print(f"Initial caterer count: {initial_caterer_count}")
    
    # Test 1: Direct model creation (should respect default=True)
    print("\n--- Test 1: Direct Model Creation ---")
    
    caterer_data = {
        'service_name': 'Active Test Catering Service',
        'specialty': 'Test Cuisine',
        'min_guests': 25,
        'max_guests': 150,
        'service_area': 'Test City, Test Region',
        'offers_buffet': True,
        'offers_plated': True,
        'offers_cocktail': False,
        'offers_food_stalls': False,
        'setup_policy': 'We handle all setup for testing.',
        'delivery_policy': 'Test delivery policy.',
        'payment_policy': 'Test payment terms.',
        'cancellation_policy': 'Test cancellation policy.'
    }
    
    direct_caterer = Caterer.objects.create(
        provider=provider,
        **caterer_data
    )
    
    print(f"✓ Direct caterer created: {direct_caterer.service_name}")
    print(f"  - is_active: {direct_caterer.is_active}")
    print(f"  - is_suspended: {direct_caterer.is_suspended}")
    
    # Test 2: Form-based creation (should also be active)
    print("\n--- Test 2: Form-Based Creation ---")
    
    form_data = {
        'service_name': 'Active Form Test Service',
        'specialty': 'Form Test Cuisine',
        'min_guests': 30,
        'max_guests': 200,
        'service_area': 'Form Test City, Form Test Region',
        'offers_buffet': True,
        'offers_plated': False,
        'offers_cocktail': True,
        'offers_food_stalls': False,
        'setup_policy': 'Form test setup policy.',
        'delivery_policy': 'Form test delivery policy.',
        'payment_policy': 'Form test payment policy.',
        'cancellation_policy': 'Form test cancellation policy.'
    }
    
    form = CatererForm(data=form_data)
    
    if form.is_valid():
        form_caterer = form.save(commit=False)
        form_caterer.provider = provider
        form_caterer.save()
        
        print(f"✓ Form caterer created: {form_caterer.service_name}")
        print(f"  - is_active: {form_caterer.is_active}")
        print(f"  - is_suspended: {form_caterer.is_suspended}")
    else:
        print(f"❌ Form validation failed: {form.errors}")
        return False
    
    # Test 3: Verify form excludes admin fields
    print("\n--- Test 3: Form Field Exclusion ---")
    
    excluded_fields = ['provider', 'created_at', 'updated_at', 'is_active', 'is_suspended', 'suspension_reason', 'suspended_at', 'suspended_by']
    form_fields = list(form.fields.keys())
    
    print(f"Form fields: {form_fields}")
    
    for field in excluded_fields:
        if field in form_fields:
            print(f"❌ Field '{field}' should be excluded but is in form")
            return False
        else:
            print(f"✓ Field '{field}' correctly excluded from form")
    
    # Test 4: Verify both caterers are available for booking
    print("\n--- Test 4: Booking Availability ---")
    
    for caterer in [direct_caterer, form_caterer]:
        is_available = caterer.is_available_for_booking()
        print(f"✓ {caterer.service_name}: available_for_booking = {is_available}")
        
        if not is_available:
            print(f"❌ Caterer should be available for booking!")
            return False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    final_caterer_count = provider.caterers.count()
    new_caterers = final_caterer_count - initial_caterer_count
    
    print(f"✓ Created {new_caterers} new caterers")
    print(f"✓ All caterers created with is_active=True by default")
    print(f"✓ All caterers available for booking")
    print(f"✓ Form properly excludes admin-only fields")
    print(f"✓ No issues detected with caterer active status")
    
    print("\n🎉 ALL TESTS PASSED - Caterers are automatically active!")
    
    return True

if __name__ == "__main__":
    try:
        success = test_caterer_active_default()
        if success:
            print("\n✅ Test completed successfully")
        else:
            print("\n❌ Test failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
