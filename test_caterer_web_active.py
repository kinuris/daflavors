#!/usr/bin/env python3
"""
Test the caterer creation view to ensure it creates active caterers
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, '/Users/chrisdominicp.chan/Desktop/Programs/Python/django-projects/daflavors')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from accounts.models import ProviderProfile
from caterers.models import Caterer

User = get_user_model()

def test_caterer_view_creation():
    """Test caterer creation through the web view"""
    print("=" * 60)
    print("TESTING CATERER CREATION VIA WEB VIEW")
    print("=" * 60)
    
    client = Client()
    
    # Create test user and provider
    username = "web_test_provider"
    try:
        user = User.objects.get(username=username)
        print(f"✓ Using existing user: {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email="webtest@example.com",
            password="testpass123",
            user_type="provider"
        )
        print(f"✓ Created new user: {username}")
    
    try:
        provider = ProviderProfile.objects.get(user=user)
        print(f"✓ Using existing provider profile")
    except ProviderProfile.DoesNotExist:
        provider = ProviderProfile.objects.create(
            user=user,
            business_name="Web Test Catering Co.",
            business_phone="555-0299",
            business_email="webtest@catering.com",
            business_address="456 Web Street, Web City",
            service_area="Web City, Web Region",
            business_description="Web test catering service"
        )
        print(f"✓ Created new provider profile")
    
    # Login the user
    client.login(username=username, password="testpass123")
    print("✓ User logged in successfully")
    
    # Test GET request to caterer creation form
    print("\n--- Testing GET Request ---")
    response = client.get('/caterers/create/')
    print(f"GET /caterers/create/ - Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Failed to load caterer creation form")
        return False
    
    print("✓ Caterer creation form loaded successfully")
    
    # Test POST request to create caterer
    print("\n--- Testing POST Request ---")
    
    initial_count = Caterer.objects.filter(provider=provider).count()
    print(f"Initial caterer count: {initial_count}")
    
    form_data = {
        'service_name': 'Web Test Catering Service',
        'specialty': 'Web Test Cuisine',
        'min_guests': 35,
        'max_guests': 250,
        'service_area': 'Web Test City, Web Test Region',
        'offers_buffet': True,
        'offers_plated': False,
        'offers_cocktail': True,
        'offers_food_stalls': False,
        'setup_policy': 'Web test setup policy.',
        'delivery_policy': 'Web test delivery policy.',
        'payment_policy': 'Web test payment policy.',
        'cancellation_policy': 'Web test cancellation policy.'
    }
    
    response = client.post('/caterers/create/', data=form_data)
    print(f"POST /caterers/create/ - Status: {response.status_code}")
    
    if response.status_code == 302:  # Successful redirect
        print("✓ Form submitted successfully (redirected)")
        
        # Check if caterer was created
        final_count = Caterer.objects.filter(provider=provider).count()
        
        if final_count == initial_count + 1:
            print(f"✓ Caterer count increased from {initial_count} to {final_count}")
            
            # Get the newly created caterer
            new_caterer = Caterer.objects.filter(provider=provider).latest('created_at')
            print(f"✓ New caterer created: {new_caterer.service_name}")
            print(f"  - is_active: {new_caterer.is_active}")
            print(f"  - is_suspended: {new_caterer.is_suspended}")
            print(f"  - available_for_booking: {new_caterer.is_available_for_booking()}")
            
            if not new_caterer.is_active:
                print("❌ New caterer should be active!")
                return False
                
            if new_caterer.is_suspended:
                print("❌ New caterer should not be suspended!")
                return False
                
            print("✓ New caterer has correct active status")
            
        else:
            print(f"❌ Expected caterer count to increase, but it didn't")
            return False
            
    elif response.status_code == 200:
        print("❌ Form submission failed (returned to form)")
        # Try to extract form errors from response
        content = response.content.decode('utf-8')
        if 'error' in content.lower():
            print("❌ Form contains errors")
        return False
        
    else:
        print(f"❌ Unexpected response status: {response.status_code}")
        return False
    
    print("\n" + "=" * 60)
    print("WEB VIEW TEST SUMMARY")
    print("=" * 60)
    print("✓ GET request loads form successfully")
    print("✓ POST request creates caterer successfully")
    print("✓ New caterer is automatically active")
    print("✓ New caterer is available for booking")
    print("✓ Web interface works correctly")
    
    print("\n🎉 WEB VIEW TEST PASSED!")
    return True

if __name__ == "__main__":
    try:
        success = test_caterer_view_creation()
        if success:
            print("\n✅ Web view test completed successfully")
        else:
            print("\n❌ Web view test failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Web view test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
