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

def test_multiple_caterers():
    print("=" * 60)
    print("TESTING MULTIPLE CATERERS PER PROVIDER")
    print("=" * 60)
    
    # Create a test user and provider if they don't exist
    username = "multi_caterer_test"
    try:
        user = User.objects.get(username=username)
        print(f"✓ Using existing user: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email="multicaterer@test.com",
            password="testpass123",
            user_type="provider"
        )
        print(f"✓ Created new user: {user.username}")
    
    # Get or create provider profile
    try:
        provider = user.provider_profile
        print(f"✓ Using existing provider: {provider.business_name}")
    except:
        provider = ProviderProfile.objects.create(
            user=user,
            business_name="Multi Caterer Business Co",
            business_description="A business with multiple catering services",
            business_email="business@multicaterer.com",
            business_phone="123-456-7890",
            business_address="123 Business Street",
            service_area="Test City, Test State"
        )
        print(f"✓ Created new provider: {provider.business_name}")
    
    # Check existing caterers for this provider
    existing_caterers = provider.caterers.all()
    print(f"✓ Provider currently has {existing_caterers.count()} caterer(s)")
    
    # Test data for multiple caterers
    caterer_data_list = [
        {
            'specialty': 'Filipino Cuisine',
            'min_guests': 20,
            'max_guests': 200,
            'service_area': 'Metro Manila',
            'offers_buffet': True,
            'offers_plated': True,
            'offers_cocktail': False,
            'offers_food_stalls': False,
            'setup_policy': 'We handle all Filipino buffet setup and breakdown.',
            'delivery_policy': 'Free delivery within 15km radius for Filipino catering.',
            'payment_policy': '50% deposit required upon booking Filipino catering.',
            'cancellation_policy': 'Full refund if cancelled 7+ days prior for Filipino events.'
        },
        {
            'specialty': 'Italian Cuisine',
            'min_guests': 15,
            'max_guests': 150,
            'service_area': 'Makati, BGC, Ortigas',
            'offers_buffet': False,
            'offers_plated': True,
            'offers_cocktail': True,
            'offers_food_stalls': False,
            'setup_policy': 'Elegant plated Italian dining setup with white linens.',
            'delivery_policy': 'Premium delivery service for Italian cuisine within Metro Manila.',
            'payment_policy': '60% deposit required for Italian fine dining events.',
            'cancellation_policy': '48-hour cancellation policy for Italian catering.'
        },
        {
            'specialty': 'Korean BBQ',
            'min_guests': 10,
            'max_guests': 100,
            'service_area': 'Quezon City, Makati',
            'offers_buffet': True,
            'offers_plated': False,
            'offers_cocktail': False,
            'offers_food_stalls': True,
            'setup_policy': 'Interactive Korean BBQ stations with grills and side dishes.',
            'delivery_policy': 'Special handling for Korean BBQ equipment and ingredients.',
            'payment_policy': '40% deposit for Korean BBQ catering.',
            'cancellation_policy': 'Flexible cancellation up to 5 days before Korean BBQ events.'
        }
    ]
    
    created_caterers = []
    
    # Create multiple caterers for the same provider
    for i, caterer_data in enumerate(caterer_data_list, 1):
        print(f"\n--- Creating Caterer {i}: {caterer_data['specialty']} ---")
        
        try:
            caterer = Caterer.objects.create(
                provider=provider,
                **caterer_data
            )
            created_caterers.append(caterer)
            print(f"✓ Successfully created caterer: {caterer.specialty}")
            print(f"  - Guest range: {caterer.min_guests}-{caterer.max_guests}")
            print(f"  - Service area: {caterer.service_area}")
            print(f"  - Offers buffet: {caterer.offers_buffet}")
            print(f"  - Offers plated: {caterer.offers_plated}")
            print(f"  - Offers cocktail: {caterer.offers_cocktail}")
            print(f"  - Offers food stalls: {caterer.offers_food_stalls}")
            
        except Exception as e:
            print(f"✗ Failed to create caterer {i}: {e}")
            return False
    
    # Verify the relationship works
    print(f"\n--- Verification ---")
    updated_caterers = provider.caterers.all()
    print(f"✓ Provider now has {updated_caterers.count()} total caterer(s)")
    
    print(f"\nAll caterers for {provider.business_name}:")
    for caterer in updated_caterers:
        print(f"  - {caterer.specialty} (ID: {caterer.id})")
        print(f"    Guest capacity: {caterer.min_guests}-{caterer.max_guests}")
        print(f"    Service area: {caterer.service_area}")
        
        # Test that the reverse relationship works
        assert caterer.provider == provider, "Reverse relationship not working!"
    
    print(f"\n--- Testing Queries ---")
    
    # Test filtering caterers by provider
    filipino_caterers = Caterer.objects.filter(provider=provider, specialty__icontains='Filipino')
    print(f"✓ Filipino caterers for this provider: {filipino_caterers.count()}")
    
    # Test filtering by service offerings
    buffet_caterers = provider.caterers.filter(offers_buffet=True)
    print(f"✓ Buffet-offering caterers: {buffet_caterers.count()}")
    
    plated_caterers = provider.caterers.filter(offers_plated=True)
    print(f"✓ Plated-service caterers: {plated_caterers.count()}")
    
    # Test active status filtering
    active_caterers = provider.caterers.filter(is_active=True, is_suspended=False)
    print(f"✓ Active caterers: {active_caterers.count()}")
    
    print(f"\n--- SUCCESS! ---")
    print(f"Multiple caterers per provider functionality is working correctly!")
    print(f"Provider '{provider.business_name}' now has {updated_caterers.count()} different catering services:")
    for caterer in updated_caterers:
        print(f"  • {caterer.specialty}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_multiple_caterers()
        if success:
            print("\n🎉 All tests passed! Multiple caterers per provider is working!")
        else:
            print("\n❌ Tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
