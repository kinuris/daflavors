#!/usr/bin/env python
"""
Test script to verify the service_name field implementation
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from caterers.models import Caterer
from accounts.models import ProviderProfile, CustomUser
from django.contrib.auth import get_user_model

def test_service_name_field():
    print("🧪 Testing service_name field implementation...")
    
    # Test 1: Check if field exists in model
    print("\n1. Checking if service_name field exists in Caterer model...")
    try:
        # Check if the field exists
        field = Caterer._meta.get_field('service_name')
        print(f"   ✅ service_name field found: {field.__class__.__name__}")
        print(f"   ✅ Max length: {field.max_length}")
        print(f"   ✅ Blank allowed: {field.blank}")
        print(f"   ✅ Help text: {field.help_text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Check __str__ method
    print("\n2. Testing __str__ method...")
    try:
        caterers = Caterer.objects.all()[:3]
        for caterer in caterers:
            str_result = str(caterer)
            print(f"   ✅ Caterer {caterer.id}: '{str_result}'")
            # Should use service_name if available, otherwise business_name
            expected = caterer.service_name or caterer.provider.business_name
            if str_result == expected:
                print(f"      ✅ Correct: Uses {'service_name' if caterer.service_name else 'business_name'}")
            else:
                print(f"      ❌ Incorrect: Expected '{expected}', got '{str_result}'")
    except Exception as e:
        print(f"   ❌ Error testing __str__: {e}")
    
    # Test 3: Create a test caterer with service_name
    print("\n3. Testing caterer creation with service_name...")
    try:
        # Find an existing provider or skip this test
        provider = ProviderProfile.objects.filter(caterers__isnull=True).first()
        if provider:
            caterer = Caterer.objects.create(
                provider=provider,
                service_name="Test Catering Service",
                specialty="Test Cuisine",
                min_guests=10,
                max_guests=100,
                service_area="Test Area"
            )
            print(f"   ✅ Created caterer with service_name: '{caterer.service_name}'")
            print(f"   ✅ __str__ result: '{str(caterer)}'")
            
            # Test without service_name
            caterer.service_name = ""
            caterer.save()
            print(f"   ✅ Cleared service_name, __str__ now: '{str(caterer)}'")
            
            # Clean up
            caterer.delete()
            print("   ✅ Test caterer cleaned up")
        else:
            print("   ⚠️  No available provider for testing, skipping creation test")
    except Exception as e:
        print(f"   ❌ Error creating test caterer: {e}")
    
    # Test 4: Check migration status
    print("\n4. Checking database migration status...")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(caterers_caterer)")
            columns = cursor.fetchall()
            service_name_found = any(col[1] == 'service_name' for col in columns)
            if service_name_found:
                print("   ✅ service_name column exists in database")
            else:
                print("   ❌ service_name column not found in database")
    except Exception as e:
        print(f"   ❌ Error checking database: {e}")
    
    print("\n✅ Service name field testing completed!")
    return True

if __name__ == "__main__":
    test_service_name_field()
