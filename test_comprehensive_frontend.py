#!/usr/bin/env python
"""
Comprehensive test script for frontend suspension status indicators
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
from django.utils import timezone
from venues.models import Venue
from caterers.models import Caterer

User = get_user_model()

def test_comprehensive_frontend():
    """Comprehensive test of frontend suspension indicators"""
    print("=== Comprehensive Frontend Suspension Status Test ===\n")
    
    # Get admin user
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            username='testadmin',
            email='admin@test.com',
            password='testpass123'
        )
        print(f"✅ Created admin user: {admin_user.username}")
    
    # Get test data
    venue = Venue.objects.first()
    caterer = Caterer.objects.first()
    
    if not venue or not caterer:
        print("❌ No test data found. Please run create_sample_data.py first")
        return
    
    print(f"Testing with:")
    print(f"  - Venue: {venue.name} (Owner: {venue.provider.user.username})")
    print(f"  - Caterer: {caterer.provider.business_name} (Owner: {caterer.provider.user.username})")
    
    # Store original states
    venue_orig = {
        'is_suspended': venue.is_suspended,
        'is_active': venue.is_active,
        'suspension_reason': venue.suspension_reason,
        'suspended_at': venue.suspended_at,
        'suspended_by': venue.suspended_by
    }
    
    caterer_orig = {
        'is_suspended': caterer.is_suspended,
        'is_active': caterer.is_active,
        'suspension_reason': caterer.suspension_reason,
        'suspended_at': caterer.suspended_at,
        'suspended_by': caterer.suspended_by
    }
    
    try:
        print(f"\n🔄 Setting up test scenarios...")
        
        # Scenario 1: Suspend venue
        venue.is_suspended = True
        venue.suspension_reason = "Testing comprehensive frontend indicators"
        venue.suspended_at = timezone.now()
        venue.suspended_by = admin_user
        venue.save()
        
        # Scenario 2: Make caterer inactive
        caterer.is_active = False
        caterer.save()
        
        print(f"✅ Test scenarios configured")
        
        # Generate test URLs and instructions
        print(f"\n🎯 FRONTEND TEST INSTRUCTIONS:")
        print(f"{'='*60}")
        
        print(f"\n1. 🏠 VENUE SUSPENSION INDICATORS:")
        print(f"   URL: http://127.0.0.1:8001/venues/{venue.id}/")
        print(f"   Login as: {venue.provider.user.username}")
        print(f"   Expected: Red suspension banner in owner actions section")
        print(f"   Status: 🚫 SUSPENDED - {venue.suspension_reason}")
        
        print(f"\n2. 🍽️ CATERER INACTIVE INDICATORS:")
        print(f"   URL: http://127.0.0.1:8001/caterers/{caterer.id}/")
        print(f"   Login as: {caterer.provider.user.username}")
        print(f"   Expected: Orange inactive banner in owner actions section")
        print(f"   Status: ⏸️ INACTIVE - Not visible to clients")
        
        print(f"\n3. 📊 PROVIDER DASHBOARD:")
        print(f"   URL: http://127.0.0.1:8001/accounts/provider_dashboard/")
        print(f"   Login as: {venue.provider.user.username} or {caterer.provider.user.username}")
        print(f"   Expected: Status badges on service cards")
        print(f"   - Venue: 🚫 Suspended badge")
        print(f"   - Caterer: ⏸️ Inactive badge")
        
        print(f"\n4. 🔍 PUBLIC LISTINGS (should NOT show suspended/inactive services):")
        print(f"   Venues List: http://127.0.0.1:8001/venues/")
        print(f"   Caterers List: http://127.0.0.1:8001/caterers/")
        print(f"   Expected: Suspended venue and inactive caterer should NOT appear")
        
        print(f"\n5. 📋 BOOKING FORMS (should NOT include suspended/inactive services):")
        print(f"   Create Booking: http://127.0.0.1:8001/bookings/create/")
        print(f"   Expected: Suspended venue and inactive caterer should NOT be in dropdowns")
        
        print(f"\n6. 🛡️ ADMIN INTERFACE:")
        print(f"   Admin: http://127.0.0.1:8001/admin/")
        print(f"   Expected: Status indicators with colors in venue/caterer lists")
        print(f"   - 🚫 SUSPENDED (red)")
        print(f"   - ⏸️ INACTIVE (orange)")
        
        print(f"\n{'='*60}")
        print(f"💡 TIP: Open multiple browser tabs to test different scenarios")
        print(f"🔑 Use these credentials:")
        print(f"   - Venue Owner: {venue.provider.user.username}")
        print(f"   - Caterer Owner: {caterer.provider.user.username}")
        print(f"   - Admin: {admin_user.username}")
        print(f"{'='*60}")
        
        # Wait for user to test
        input("\n⏸️  Press Enter after testing all scenarios to restore original states...")
        
        # Now test active scenario
        print(f"\n🔄 Testing ACTIVE status indicators...")
        venue.is_suspended = False
        venue.is_active = True
        venue.suspension_reason = ""
        venue.suspended_at = None
        venue.suspended_by = None
        venue.save()
        
        caterer.is_suspended = False
        caterer.is_active = True
        caterer.save()
        
        print(f"\n✅ ACTIVE STATUS TEST:")
        print(f"   Venue: http://127.0.0.1:8001/venues/{venue.id}/")
        print(f"   Caterer: http://127.0.0.1:8001/caterers/{caterer.id}/")
        print(f"   Expected: Green ✅ ACTIVE status banners")
        
        input("\n⏸️  Press Enter to restore original states and finish...")
        
    finally:
        # Restore original states
        print(f"\n🔄 Restoring original states...")
        
        venue.is_suspended = venue_orig['is_suspended']
        venue.is_active = venue_orig['is_active']
        venue.suspension_reason = venue_orig['suspension_reason']
        venue.suspended_at = venue_orig['suspended_at']
        venue.suspended_by = venue_orig['suspended_by']
        venue.save()
        
        caterer.is_suspended = caterer_orig['is_suspended']
        caterer.is_active = caterer_orig['is_active']
        caterer.suspension_reason = caterer_orig['suspension_reason']
        caterer.suspended_at = caterer_orig['suspended_at']
        caterer.suspended_by = caterer_orig['suspended_by']
        caterer.save()
        
        print(f"✅ All services restored to original states")
        print(f"\n🎉 Frontend suspension indicators testing complete!")

if __name__ == '__main__':
    test_comprehensive_frontend()
