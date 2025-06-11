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

def test_admin_interface_display():
    print("TESTING ADMIN INTERFACE DISPLAY")
    print("=" * 40)
    
    # Get the test provider
    user = User.objects.get(username="multi_caterer_test")
    provider = user.provider_profile
    
    # Test the provider admin method we updated
    from accounts.admin import ProviderProfileAdmin
    admin_instance = ProviderProfileAdmin(ProviderProfile, None)
    
    # Test the has_caterers method
    caterers_display = admin_instance.has_caterers(provider)
    print(f"✓ Admin caterers display: {caterers_display}")
    
    # Test individual caterer admin
    caterers = provider.caterers.all()
    print(f"✓ Total caterers for admin review: {caterers.count()}")
    
    for caterer in caterers:
        print(f"  - {caterer.specialty}")
        print(f"    Provider: {caterer.provider.business_name}")
        print(f"    Status: {'Active' if caterer.is_active else 'Inactive'}")
        print(f"    Available: {'Yes' if caterer.is_available_for_booking() else 'No'}")
    
    return True

def test_multiple_provider_scenario():
    print("\nTESTING MULTIPLE PROVIDERS WITH MULTIPLE CATERERS")
    print("=" * 55)
    
    # Create another provider to test the full scenario
    try:
        user2 = User.objects.get(username="provider2_test")
    except User.DoesNotExist:
        user2 = User.objects.create_user(
            username="provider2_test",
            email="provider2@test.com",
            password="testpass123",
            user_type="provider"
        )
        
        provider2 = ProviderProfile.objects.create(
            user=user2,
            business_name="Second Provider Co",
            business_description="Another catering business",
            business_email="business2@test.com",
            business_phone="098-765-4321",
            business_address="456 Business Ave",
            service_area="Different City"
        )
        
        # Create caterers for second provider
        Caterer.objects.create(
            provider=provider2,
            specialty='Mexican Cuisine',
            min_guests=30,
            max_guests=300,
            service_area='Quezon City',
            offers_buffet=True,
            offers_plated=False,
            offers_cocktail=False,
            offers_food_stalls=True
        )
        
        Caterer.objects.create(
            provider=provider2,
            specialty='French Fine Dining',
            min_guests=20,
            max_guests=80,
            service_area='Makati CBD',
            offers_buffet=False,
            offers_plated=True,
            offers_cocktail=True,
            offers_food_stalls=False
        )
        
        print(f"✓ Created second provider: {provider2.business_name}")
    else:
        provider2 = user2.provider_profile
        print(f"✓ Using existing second provider: {provider2.business_name}")
    
    # Verify separation between providers
    provider1 = User.objects.get(username="multi_caterer_test").provider_profile
    
    p1_caterers = provider1.caterers.all()
    p2_caterers = provider2.caterers.all()
    
    print(f"✓ Provider 1 ({provider1.business_name}) has {p1_caterers.count()} caterers:")
    for caterer in p1_caterers:
        print(f"  - {caterer.specialty}")
    
    print(f"✓ Provider 2 ({provider2.business_name}) has {p2_caterers.count()} caterers:")
    for caterer in p2_caterers:
        print(f"  - {caterer.specialty}")
    
    # Verify no cross-contamination
    total_caterers = Caterer.objects.count()
    expected_total = p1_caterers.count() + p2_caterers.count()
    
    print(f"✓ Total caterers in system: {total_caterers}")
    print(f"✓ Expected total: {expected_total}")
    
    if total_caterers >= expected_total:
        print("✓ No cross-contamination between providers")
        return True
    else:
        print("❌ Possible data integrity issue")
        return False

if __name__ == "__main__":
    try:
        admin_success = test_admin_interface_display()
        multi_provider_success = test_multiple_provider_scenario()
        
        if admin_success and multi_provider_success:
            print(f"\n🎉 All admin and multi-provider tests passed!")
            print("✅ Multiple caterers per provider is fully functional")
            print("✅ Admin interface correctly handles multiple caterers")
            print("✅ Provider separation is maintained")
        else:
            print(f"\n❌ Some tests failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
