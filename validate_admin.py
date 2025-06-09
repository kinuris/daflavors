#!/usr/bin/env python
"""
Final validation of custom admin interface
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from django.contrib.auth import get_user_model
from venues.models import Venue
from caterers.models import Caterer
from django.urls import reverse
from django.conf import settings

def validate_admin_interface():
    print("🔍 VALIDATING CUSTOM ADMIN INTERFACE")
    print("=" * 50)
    
    # Check models and data
    print("\n📊 DATA VALIDATION:")
    venues = Venue.objects.all()
    caterers = Caterer.objects.all()
    User = get_user_model()
    admins = User.objects.filter(is_staff=True)
    
    print(f"   ✅ Venues: {venues.count()}")
    print(f"   ✅ Caterers: {caterers.count()}")
    print(f"   ✅ Admin users: {admins.count()}")
    
    # Check URL configuration
    print("\n🌐 URL VALIDATION:")
    urls_to_check = [
        ('core:admin_dashboard', '/admin-panel/'),
        ('core:venue_regulation', '/admin-panel/venues/'),
        ('core:caterer_regulation', '/admin-panel/caterers/'),
    ]
    
    for url_name, expected_url in urls_to_check:
        try:
            url = reverse(url_name)
            print(f"   ✅ {url_name}: {url}")
        except Exception as e:
            print(f"   ❌ {url_name}: {e}")
            print(f"      Expected: {expected_url}")
    
    # Check templates exist
    print("\n📄 TEMPLATE VALIDATION:")
    template_files = [
        'templates/core/admin_dashboard.html',
        'templates/core/venue_regulation.html',
        'templates/core/caterer_regulation.html',
        'templates/core/venue_detail_admin.html',
        'templates/core/caterer_detail_admin.html',
    ]
    
    for template in template_files:
        full_path = os.path.join(settings.BASE_DIR, template)
        if os.path.exists(full_path):
            print(f"   ✅ {template}")
        else:
            print(f"   ❌ {template}")
    
    # Check view functions
    print("\n🎯 VIEW VALIDATION:")
    try:
        from core.admin_views import (
            admin_dashboard,
            venue_regulation,
            caterer_regulation,
            venue_detail,
            caterer_detail,
            suspend_venue,
            unsuspend_venue,
            toggle_venue_active,
            suspend_caterer,
            unsuspend_caterer,
            toggle_caterer_active
        )
        
        views = [
            'admin_dashboard', 'venue_regulation', 'caterer_regulation',
            'venue_detail', 'caterer_detail',
            'suspend_venue', 'unsuspend_venue', 'toggle_venue_active',
            'suspend_caterer', 'unsuspend_caterer', 'toggle_caterer_active'
        ]
        
        for view_name in views:
            print(f"   ✅ {view_name}")
            
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
    
    # Sample data check
    if venues.exists():
        print(f"\n🏢 SAMPLE VENUE:")
        venue = venues.first()
        print(f"   Name: {venue.name}")
        print(f"   Active: {venue.is_active}")
        print(f"   Suspended: {venue.is_suspended}")
        print(f"   Available for booking: {venue.is_available_for_booking()}")
    
    if caterers.exists():
        print(f"\n🍽️ SAMPLE CATERER:")
        caterer = caterers.first()
        print(f"   Name: {caterer.provider.business_name}")
        print(f"   Active: {caterer.is_active}")
        print(f"   Suspended: {caterer.is_suspended}")
        print(f"   Available for booking: {caterer.is_available_for_booking()}")
        
        services = []
        if caterer.offers_buffet: services.append("Buffet")
        if caterer.offers_plated: services.append("Plated")
        if caterer.offers_cocktail: services.append("Cocktail")
        if caterer.offers_food_stalls: services.append("Food Stalls")
        print(f"   Services: {', '.join(services)}")
    
    print(f"\n🎉 VALIDATION COMPLETE!")
    print(f"💡 Access the admin interface at: http://127.0.0.1:8000/admin-panel/")
    print(f"🔐 Login required: Use admin credentials to access staff-only features")
    
    return True

if __name__ == "__main__":
    validate_admin_interface()
