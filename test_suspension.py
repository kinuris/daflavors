#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/Users/chrisdominicp.chan/Desktop/Programs/Python/django-projects/daflavors')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from bookings.forms import BookingForm, MenuSelectionForm
from venues.models import Venue
from caterers.models import Caterer
from accounts.models import CustomUser
from django.contrib.auth import get_user_model

def test_suspended_services():
    """Test booking form validation with suspended services"""
    
    print("Testing booking form with suspended services...")
    
    # Get a venue and caterer to test with
    venue = Venue.objects.first()
    caterer = Caterer.objects.first()
    
    if not venue or not caterer:
        print("No venue or caterer found for testing")
        return
    
    print(f"Testing with venue: {venue.name}")
    print(f"Testing with caterer: {caterer.provider.business_name}")
    
    # Test form before suspension
    form = BookingForm()
    print(f"\nBefore suspension:")
    print(f"Venue available in form: {venue in form.fields['venue'].queryset}")
    print(f"Caterer available in form: {caterer in form.fields['caterer'].queryset}")
    
    # Test venue availability method
    print(f"Venue is_available_for_booking(): {venue.is_available_for_booking()}")
    print(f"Caterer is_available_for_booking(): {caterer.is_available_for_booking()}")
    
    # Suspend the venue
    print(f"\nSuspending venue '{venue.name}'...")
    admin_user = CustomUser.objects.filter(is_superuser=True).first()
    venue.is_suspended = True
    venue.suspension_reason = "Testing suspension functionality"
    venue.suspended_by = admin_user
    venue.save()
    
    # Suspend the caterer
    print(f"Suspending caterer '{caterer.provider.business_name}'...")
    caterer.is_suspended = True
    caterer.suspension_reason = "Testing suspension functionality"
    caterer.suspended_by = admin_user
    caterer.save()
    
    # Test form after suspension
    form = BookingForm()
    print(f"\nAfter suspension:")
    print(f"Venue available in form: {venue in form.fields['venue'].queryset}")
    print(f"Caterer available in form: {caterer in form.fields['caterer'].queryset}")
    
    # Test availability methods
    venue.refresh_from_db()
    caterer.refresh_from_db()
    print(f"Venue is_available_for_booking(): {venue.is_available_for_booking()}")
    print(f"Caterer is_available_for_booking(): {caterer.is_available_for_booking()}")
    
    # Test form validation
    print(f"\nTesting form validation...")
    form_data = {
        'event_type': 'Test Event',
        'event_date': '2025-01-30',
        'start_time': '18:00',
        'end_time': '22:00',
        'guest_count': 50,
        'venue': venue.id,
        'caterer': caterer.id,
        'special_requests': 'Test booking with suspended services'
    }
    
    form = BookingForm(data=form_data)
    is_valid = form.is_valid()
    print(f"Form is valid: {is_valid}")
    
    if not is_valid:
        print("Form errors:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
    
    # Test MenuSelectionForm filtering
    print(f"\nTesting MenuSelectionForm filtering...")
    menu_form = MenuSelectionForm(caterer_id=caterer.id)
    print(f"Menu packages available: {menu_form.fields['menu_package'].queryset.count()}")
    
    # Unsuspend for cleanup
    print(f"\nUnsuspending services for cleanup...")
    venue.is_suspended = False
    venue.suspension_reason = ""
    venue.suspended_by = None
    venue.save()
    
    caterer.is_suspended = False
    caterer.suspension_reason = ""
    caterer.suspended_by = None
    caterer.save()
    
    print("Test completed and cleanup done!")

if __name__ == '__main__':
    test_suspended_services()
