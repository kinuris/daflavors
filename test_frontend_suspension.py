#!/usr/bin/env python
"""
Test script to temporarily suspend services to test frontend suspension indicators
"""
import os
import sys
import django
from datetime import datetime

# Add the project directory to Python path
sys.path.append('/Users/chrisdominicp.chan/Desktop/Programs/Python/django-projects/daflavors')

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')

# Setup Django
django.setup()

from django.contrib.auth import get_user_model
from venues.models import Venue
from caterers.models import Caterer

User = get_user_model()

def test_suspension_indicators():
    """Test suspension status indicators in frontend"""
    print("=== Testing Frontend Suspension Status Indicators ===\n")
    
    # Get first venue and caterer to test with
    venues = Venue.objects.all()
    caterers = Caterer.objects.all()
    
    if not venues.exists() or not caterers.exists():
        print("❌ No venues or caterers found. Please create some test data first.")
        return
    
    # Get admin user for suspension tracking
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        print("❌ No admin user found. Creating one...")
        admin_user = User.objects.create_superuser(
            username='testadmin',
            email='admin@test.com',
            password='testpass123'
        )
        print(f"✅ Created admin user: {admin_user.username}")
    
    test_venue = venues.first()
    test_caterer = caterers.first()
    
    print(f"Testing with:")
    print(f"  - Venue: {test_venue.name}")
    print(f"  - Caterer: {test_caterer.provider.business_name}")
    
    # Store original states
    venue_original_suspended = test_venue.is_suspended
    venue_original_active = test_venue.is_active
    caterer_original_suspended = test_caterer.is_suspended
    caterer_original_active = test_caterer.is_active
    
    try:
        # Test Case 1: Suspend the venue
        print(f"\n🔍 Test Case 1: Suspending venue '{test_venue.name}'")
        test_venue.is_suspended = True
        test_venue.suspension_reason = "Testing frontend suspension indicators"
        test_venue.suspended_at = datetime.now()
        test_venue.suspended_by = admin_user
        test_venue.save()
        print(f"   ✅ Venue suspended. Check venue detail page and provider dashboard")
        
        # Test Case 2: Make caterer inactive
        print(f"\n🔍 Test Case 2: Making caterer '{test_caterer.provider.business_name}' inactive")
        test_caterer.is_active = False
        test_caterer.save()
        print(f"   ✅ Caterer made inactive. Check caterer detail page and provider dashboard")
        
        # Test Case 3: Suspend the caterer as well
        print(f"\n🔍 Test Case 3: Suspending caterer '{test_caterer.provider.business_name}'")
        test_caterer.is_suspended = True
        test_caterer.suspension_reason = "Testing frontend suspension indicators for caterers"
        test_caterer.suspended_at = datetime.now()
        test_caterer.suspended_by = admin_user
        test_caterer.save()
        print(f"   ✅ Caterer suspended. Check caterer detail page and provider dashboard")
        
        print(f"\n🎯 Frontend Testing Instructions:")
        print(f"1. Visit venue detail page: http://127.0.0.1:8001/venues/{test_venue.id}/")
        print(f"2. Visit caterer detail page: http://127.0.0.1:8001/caterers/{test_caterer.id}/")
        print(f"3. Login as the venue/caterer owner to see suspension status in owner actions")
        print(f"4. Visit provider dashboard to see status badges in service listings")
        print(f"5. Verify suspended services don't appear in public listings")
        
        input("\n⏸️  Press Enter after testing to restore original states...")
        
    finally:
        # Restore original states
        print(f"\n🔄 Restoring original states...")
        test_venue.is_suspended = venue_original_suspended
        test_venue.is_active = venue_original_active
        if not venue_original_suspended:
            test_venue.suspension_reason = ""
            test_venue.suspended_at = None
            test_venue.suspended_by = None
        test_venue.save()
        print(f"   ✅ Venue '{test_venue.name}' restored")
        
        test_caterer.is_suspended = caterer_original_suspended
        test_caterer.is_active = caterer_original_active
        if not caterer_original_suspended:
            test_caterer.suspension_reason = ""
            test_caterer.suspended_at = None
            test_caterer.suspended_by = None
        test_caterer.save()
        print(f"   ✅ Caterer '{test_caterer.provider.business_name}' restored")
        
        print(f"\n✅ All services restored to original states")

if __name__ == '__main__':
    test_suspension_indicators()
