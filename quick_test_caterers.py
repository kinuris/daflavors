#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import ProviderProfile
from caterers.models import Caterer

User = get_user_model()

def quick_test_multiple_caterers():
    print("QUICK TEST: Multiple Caterers Functionality")
    print("=" * 50)
    
    # Check existing test user
    try:
        user = User.objects.get(username="multi_caterer_test")
        provider = user.provider_profile
        caterers = provider.caterers.all()
        
        print(f"✓ Provider: {provider.business_name}")
        print(f"✓ Total caterers: {caterers.count()}")
        
        for i, caterer in enumerate(caterers, 1):
            print(f"  {i}. {caterer.specialty}")
            print(f"     - Active: {caterer.is_active}")
            print(f"     - Available for booking: {caterer.is_available_for_booking()}")
        
        # Test that we can still access the old-style methods if any templates use them
        print(f"\n✓ Reverse relationship works:")
        for caterer in caterers:
            assert caterer.provider == provider
        print(f"  All caterers correctly reference their provider")
        
        # Test filtering
        active_caterers = provider.caterers.filter(is_active=True)
        print(f"\n✓ Filtering works: {active_caterers.count()} active caterers")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = quick_test_multiple_caterers()
    if success:
        print("\n🎉 Multiple caterers functionality is working correctly!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)
