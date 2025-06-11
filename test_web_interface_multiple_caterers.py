#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from accounts.models import ProviderProfile
from caterers.models import Caterer

User = get_user_model()

def test_caterer_form_multiple_creation():
    print("=" * 60)
    print("TESTING CATERER FORM - MULTIPLE CREATION")
    print("=" * 60)
    
    # Get a user with provider profile (should exist from previous test)
    try:
        user = User.objects.get(username="multi_caterer_test")
        print(f"✓ Using test user: {user.username}")
    except User.DoesNotExist:
        print("❌ Test user not found. Run test_multiple_caterers.py first.")
        return False
    
    # Create a test client and login
    client = Client()
    client.force_login(user)
    print(f"✓ Logged in as {user.username}")
    
    # Get initial caterer count for this provider
    initial_count = user.provider_profile.caterers.count()
    print(f"✓ Provider currently has {initial_count} caterers")
    
    # Test creating another caterer via form
    form_data = {
        'specialty': 'Japanese Sushi',
        'min_guests': 25,
        'max_guests': 80,
        'service_area': 'Manila, Makati, BGC',
        'offers_buffet': False,
        'offers_plated': True,
        'offers_cocktail': True,
        'offers_food_stalls': False,
        'setup_policy': 'Traditional Japanese presentation with bamboo and ceramic serving ware.',
        'delivery_policy': 'Fresh sushi delivery with temperature-controlled transport.',
        'payment_policy': '70% deposit required for Japanese catering due to premium ingredients.',
        'cancellation_policy': '72-hour cancellation policy for Japanese sushi catering.'
    }
    
    # Test GET request to caterer create form
    print("\n--- Testing Caterer Create Form Access ---")
    response = client.get('/caterers/create/')
    if response.status_code == 200:
        print("✓ Caterer create form loads successfully")
    else:
        print(f"❌ Failed to load caterer create form: {response.status_code}")
        return False
    
    # Test POST request to create caterer
    print("\n--- Testing Caterer Creation via Form ---")
    response = client.post('/caterers/create/', data=form_data)
    
    if response.status_code == 302:  # Successful redirect
        print("✓ Caterer creation form submitted successfully")
        
        # Check if caterer was created
        final_count = user.provider_profile.caterers.count()
        if final_count == initial_count + 1:
            print(f"✓ Caterer count increased from {initial_count} to {final_count}")
            
            # Get the newly created caterer
            new_caterer = user.provider_profile.caterers.latest('created_at')
            print(f"✓ New caterer created: {new_caterer.specialty}")
            print(f"  - Guest range: {new_caterer.min_guests}-{new_caterer.max_guests}")
            print(f"  - Service area: {new_caterer.service_area}")
            
            # Test the redirect worked (should go to caterer detail)
            print(f"✓ Form redirected to: {response.url}")
            
            return True
        else:
            print(f"❌ Caterer count didn't increase: {initial_count} -> {final_count}")
            return False
    else:
        print(f"❌ Form submission failed: {response.status_code}")
        if hasattr(response, 'context') and response.context and 'form' in response.context:
            form = response.context['form']
            if form.errors:
                print(f"Form errors: {form.errors}")
        return False

def test_provider_dashboard():
    print("\n" + "=" * 60)
    print("TESTING PROVIDER DASHBOARD WITH MULTIPLE CATERERS")
    print("=" * 60)
    
    # Get the test user
    user = User.objects.get(username="multi_caterer_test")
    client = Client()
    client.force_login(user)
    
    # Test provider dashboard
    response = client.get('/accounts/provider-dashboard/')
    if response.status_code == 200:
        print("✓ Provider dashboard loads successfully")
        
        # Check that all caterers are displayed
        caterers = user.provider_profile.caterers.all()
        print(f"✓ Provider has {caterers.count()} caterers:")
        for caterer in caterers:
            print(f"  - {caterer.specialty}")
        
        # The dashboard should display all caterers
        content = response.content.decode()
        for caterer in caterers:
            if caterer.specialty in content:
                print(f"✓ '{caterer.specialty}' found in dashboard")
            else:
                print(f"❌ '{caterer.specialty}' not found in dashboard")
                return False
                
        return True
    else:
        print(f"❌ Provider dashboard failed to load: {response.status_code}")
        return False

if __name__ == "__main__":
    try:
        print("Testing caterer form with multiple caterers...")
        form_success = test_caterer_form_multiple_creation()
        
        print("\nTesting provider dashboard...")
        dashboard_success = test_provider_dashboard()
        
        if form_success and dashboard_success:
            print("\n🎉 All web interface tests passed!")
            print("✓ Multiple caterers can be created via web form")
            print("✓ Provider dashboard displays all caterers correctly")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
