#!/usr/bin/env python3
"""
Final verification that caterers are created as active by default
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

def verify_caterer_active_status():
    """Final verification that caterers are created as active"""
    print("=" * 70)
    print("FINAL VERIFICATION: CATERER ACTIVE STATUS DEFAULT")
    print("=" * 70)
    
    # Check existing caterers in the database
    print("\n--- Checking Existing Caterers ---")
    
    all_caterers = Caterer.objects.all()
    total_caterers = all_caterers.count()
    active_caterers = all_caterers.filter(is_active=True).count()
    inactive_caterers = all_caterers.filter(is_active=False).count()
    
    print(f"Total caterers in database: {total_caterers}")
    print(f"Active caterers: {active_caterers}")
    print(f"Inactive caterers: {inactive_caterers}")
    
    if inactive_caterers > 0:
        print(f"\n⚠️  Found {inactive_caterers} inactive caterers:")
        for caterer in all_caterers.filter(is_active=False):
            print(f"  - {caterer.service_name or caterer.provider.business_name} (ID: {caterer.id})")
            print(f"    Created: {caterer.created_at}")
            print(f"    Provider: {caterer.provider.business_name}")
    
    # Test model default
    print(f"\n--- Testing Model Field Default ---")
    model_field = Caterer._meta.get_field('is_active')
    print(f"Model field 'is_active' default: {model_field.default}")
    
    if model_field.default != True:
        print("❌ Model field default is not True!")
        return False
    else:
        print("✓ Model field default is correctly set to True")
    
    # Test form exclusions
    print(f"\n--- Testing Form Field Exclusions ---")
    form = CatererForm()
    excluded_admin_fields = ['is_active', 'is_suspended', 'suspension_reason', 'suspended_at', 'suspended_by']
    
    for field in excluded_admin_fields:
        if field in form.fields:
            print(f"❌ Admin field '{field}' should not be in form!")
            return False
        else:
            print(f"✓ Admin field '{field}' correctly excluded from form")
    
    # Test fresh caterer creation
    print(f"\n--- Testing Fresh Caterer Creation ---")
    
    # Get or create a test provider
    username = "final_test_provider"
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email="finaltest@example.com",
            password="testpass123",
            user_type="provider"
        )
    
    try:
        provider = ProviderProfile.objects.get(user=user)
    except ProviderProfile.DoesNotExist:
        provider = ProviderProfile.objects.create(
            user=user,
            business_name="Final Test Catering Co.",
            business_phone="555-0399",
            business_email="finaltest@catering.com",
            business_address="789 Final Street, Final City",
            service_area="Final City, Final Region",
            business_description="Final test catering service"
        )
    
    # Create a fresh caterer
    test_caterer = Caterer.objects.create(
        provider=provider,
        service_name="Final Verification Catering",
        specialty="Final Test Cuisine",
        min_guests=40,
        max_guests=300,
        service_area="Final Test Area",
        offers_buffet=True,
        offers_plated=True,
        setup_policy="Final test setup",
        delivery_policy="Final test delivery",
        payment_policy="Final test payment",
        cancellation_policy="Final test cancellation"
    )
    
    print(f"✓ Created fresh caterer: {test_caterer.service_name}")
    print(f"  - ID: {test_caterer.id}")
    print(f"  - is_active: {test_caterer.is_active}")
    print(f"  - is_suspended: {test_caterer.is_suspended}")
    print(f"  - available_for_booking: {test_caterer.is_available_for_booking()}")
    
    if not test_caterer.is_active:
        print("❌ Fresh caterer is not active!")
        return False
    
    if test_caterer.is_suspended:
        print("❌ Fresh caterer should not be suspended!")
        return False
    
    if not test_caterer.is_available_for_booking():
        print("❌ Fresh caterer should be available for booking!")
        return False
    
    print("✓ Fresh caterer has all correct status values")
    
    # Summary
    print("\n" + "=" * 70)
    print("FINAL VERIFICATION SUMMARY")
    print("=" * 70)
    print("✅ Model field 'is_active' defaults to True")
    print("✅ Form correctly excludes admin-only fields")
    print("✅ New caterers are created as active by default")
    print("✅ New caterers are available for booking")
    print("✅ System is working correctly")
    
    if inactive_caterers == 0:
        print("✅ No inactive caterers found in database")
    else:
        print(f"⚠️  Found {inactive_caterers} inactive caterers (may be intentionally deactivated)")
    
    print("\n🎉 FINAL VERIFICATION PASSED!")
    print("Caterers are automatically active when created!")
    
    return True

if __name__ == "__main__":
    try:
        success = verify_caterer_active_status()
        if success:
            print("\n✅ Final verification completed successfully")
        else:
            print("\n❌ Final verification failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Final verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
