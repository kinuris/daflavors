#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/chrisdominicp.chan/Desktop/Programs/Python/django-projects/daflavors')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from bookings.forms import BookingForm
from venues.models import Venue
from caterers.models import Caterer

def test_booking_form_filtering():
    """Test that booking form only shows active, non-suspended venues and caterers"""
    
    print("Testing BookingForm filtering for suspended services...")
    
    # Get all venues and caterers
    all_venues = Venue.objects.all()
    all_caterers = Caterer.objects.all()
    
    print(f"Total venues in database: {all_venues.count()}")
    print(f"Total caterers in database: {all_caterers.count()}")
    
    # Check suspended venues
    suspended_venues = all_venues.filter(is_suspended=True)
    inactive_venues = all_venues.filter(is_active=False)
    
    print(f"Suspended venues: {suspended_venues.count()}")
    print(f"Inactive venues: {inactive_venues.count()}")
    
    # Check suspended caterers
    suspended_caterers = all_caterers.filter(is_suspended=True)
    inactive_caterers = all_caterers.filter(is_active=False)
    
    print(f"Suspended caterers: {suspended_caterers.count()}")
    print(f"Inactive caterers: {inactive_caterers.count()}")
    
    # Test the form
    form = BookingForm()
    
    available_venues = form.fields['venue'].queryset
    available_caterers = form.fields['caterer'].queryset
    
    print(f"\nVenues available in booking form: {available_venues.count()}")
    print(f"Caterers available in booking form: {available_caterers.count()}")
    
    # Verify that suspended/inactive services are excluded
    for venue in suspended_venues:
        if venue in available_venues:
            print(f"ERROR: Suspended venue '{venue.name}' is still available in form!")
        else:
            print(f"✓ Suspended venue '{venue.name}' correctly excluded from form")
    
    for venue in inactive_venues:
        if venue in available_venues:
            print(f"ERROR: Inactive venue '{venue.name}' is still available in form!")
        else:
            print(f"✓ Inactive venue '{venue.name}' correctly excluded from form")
    
    for caterer in suspended_caterers:
        if caterer in available_caterers:
            print(f"ERROR: Suspended caterer '{caterer.business_name}' is still available in form!")
        else:
            print(f"✓ Suspended caterer '{caterer.business_name}' correctly excluded from form")
    
    for caterer in inactive_caterers:
        if caterer in available_caterers:
            print(f"ERROR: Inactive caterer '{caterer.business_name}' is still available in form!")
        else:
            print(f"✓ Inactive caterer '{caterer.business_name}' correctly excluded from form")
    
    print("\nTest completed!")

if __name__ == '__main__':
    test_booking_form_filtering()
