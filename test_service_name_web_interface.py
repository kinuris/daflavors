#!/usr/bin/env python
"""
Test the web interface for service_name functionality
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import ProviderProfile
from caterers.models import Caterer

def test_caterer_web_interface():
    print("🌐 Testing caterer web interface with service_name...")
    
    # Test 1: Check caterer list view
    print("\n1. Testing caterer list view...")
    try:
        client = Client()
        response = client.get('/caterers/')
        print(f"   ✅ Caterer list response: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            # Check if service names are being displayed
            caterers_with_service_names = Caterer.objects.exclude(service_name='')[:3]
            for caterer in caterers_with_service_names:
                if caterer.service_name in content:
                    print(f"   ✅ Found service name '{caterer.service_name}' in list")
                else:
                    print(f"   ⚠️  Service name '{caterer.service_name}' not found in list")
        
    except Exception as e:
        print(f"   ❌ Error testing caterer list: {e}")
    
    # Test 2: Check caterer detail view
    print("\n2. Testing caterer detail view...")
    try:
        caterer = Caterer.objects.first()
        if caterer:
            response = client.get(f'/caterers/{caterer.id}/')
            print(f"   ✅ Caterer detail response: {response.status_code}")
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                expected_name = caterer.service_name or caterer.provider.business_name
                if expected_name in content:
                    print(f"   ✅ Found expected name '{expected_name}' in detail view")
                else:
                    print(f"   ⚠️  Expected name '{expected_name}' not found in detail view")
        
    except Exception as e:
        print(f"   ❌ Error testing caterer detail: {e}")
    
    # Test 3: Check form rendering (requires authentication)
    print("\n3. Testing caterer form rendering...")
    try:
        # Find a provider user
        provider_user = None
        for profile in ProviderProfile.objects.all()[:5]:
            if profile.user:
                provider_user = profile.user
                break
        
        if provider_user:
            client.force_login(provider_user)
            
            # Test caterer creation form
            response = client.get('/caterers/create/')
            print(f"   ✅ Caterer create form response: {response.status_code}")
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                if 'service_name' in content.lower():
                    print("   ✅ service_name field found in create form")
                else:
                    print("   ⚠️  service_name field not found in create form")
            
            # Test caterer edit form if user has caterers
            caterer = Caterer.objects.filter(provider__user=provider_user).first()
            if caterer:
                response = client.get(f'/caterers/{caterer.id}/edit/')
                print(f"   ✅ Caterer edit form response: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.content.decode('utf-8')
                    if caterer.service_name and caterer.service_name in content:
                        print(f"   ✅ Found existing service name '{caterer.service_name}' in edit form")
                    elif 'service_name' in content.lower():
                        print("   ✅ service_name field found in edit form")
        else:
            print("   ⚠️  No provider user found for form testing")
        
    except Exception as e:
        print(f"   ❌ Error testing caterer forms: {e}")
    
    # Test 4: Test form submission
    print("\n4. Testing form submission...")
    try:
        if provider_user:
            provider_profile = ProviderProfile.objects.filter(user=provider_user).first()
            if provider_profile and not provider_profile.caterers.exists():
                # Test creating a caterer with service_name
                form_data = {
                    'service_name': 'Test Service Name',
                    'specialty': 'Test Cuisine',
                    'min_guests': '10',
                    'max_guests': '100',
                    'service_area': 'Test Area',
                    'offers_buffet': 'on',
                    'setup_policy': 'Test setup policy',
                    'delivery_policy': 'Test delivery policy',
                    'payment_policy': 'Test payment policy',
                    'cancellation_policy': 'Test cancellation policy',
                }
                
                response = client.post('/caterers/create/', form_data)
                print(f"   ✅ Form submission response: {response.status_code}")
                
                if response.status_code == 302:  # Redirect on success
                    # Check if caterer was created
                    new_caterer = Caterer.objects.filter(
                        provider=provider_profile,
                        service_name='Test Service Name'
                    ).first()
                    
                    if new_caterer:
                        print(f"   ✅ Caterer created with service_name: '{new_caterer.service_name}'")
                        print(f"   ✅ String representation: '{str(new_caterer)}'")
                        
                        # Clean up
                        new_caterer.delete()
                        print("   ✅ Test caterer cleaned up")
                    else:
                        print("   ⚠️  Caterer not found after submission")
            else:
                print("   ⚠️  Cannot test creation - provider already has caterer or no provider found")
        
    except Exception as e:
        print(f"   ❌ Error testing form submission: {e}")
    
    print("\n✅ Web interface testing completed!")

if __name__ == "__main__":
    test_caterer_web_interface()
