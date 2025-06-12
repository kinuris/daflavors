#!/usr/bin/env python
"""
Simple test to verify booking form template context
"""
import os
import sys
import django

# Add the project root to the Python path
sys.path.insert(0, '/Users/chrisdominicp.chan/Desktop/Programs/Python/django-projects/daflavors')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from django.template import Template, Context
from caterers.models import Caterer
from bookings.forms import BookingForm

def test_caterer_display():
    print("=== Testing Caterer Display in Booking Form ===\n")
    
    # Get caterers with event types (same as in the view)
    caterers_with_event_types = Caterer.objects.filter(
        is_active=True, 
        is_suspended=False
    ).prefetch_related('event_types').select_related('provider')
    
    print(f"Found {caterers_with_event_types.count()} active caterers:")
    
    for caterer in caterers_with_event_types:
        event_types = caterer.event_types.all()
        print(f"\nCaterer: {caterer.provider.business_name}")
        print(f"Event Types ({event_types.count()}):")
        
        for i, event_type in enumerate(event_types):
            icon_display = f"{event_type.icon} " if event_type.icon else ""
            print(f"  {i+1}. {icon_display}{event_type.name}")
        
        # Simulate the template rendering for this caterer
        event_type_list = []
        for event_type in event_types[:3]:  # First 3 as in template
            if event_type.icon:
                event_type_list.append(f"{event_type.icon} {event_type.name}")
            else:
                event_type_list.append(event_type.name)
        
        event_type_display = ", ".join(event_type_list)
        if event_types.count() > 3:
            event_type_display += f" (+{event_types.count() - 3} more)"
        
        full_display = f"{caterer.provider.business_name}"
        if event_type_display:
            full_display += f" - {event_type_display}"
        
        print(f"Template Display: {full_display}")
    
    # Test the form initialization
    print(f"\n=== Testing Form ===")
    form = BookingForm()
    caterer_field = form.fields['caterer']
    queryset = caterer_field.queryset
    
    print(f"Form caterer queryset count: {queryset.count()}")
    for caterer in queryset:
        print(f"  - {caterer.provider.business_name}")

if __name__ == "__main__":
    test_caterer_display()
