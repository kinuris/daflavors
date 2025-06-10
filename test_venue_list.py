#!/usr/bin/env python
import os
import django
import sys

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "daflavors.settings")
django.setup()

# Now import your models
from venues.models import Venue
from django.test import RequestFactory
from venues.views import venue_list
from django.template.loader import render_to_string

def test_venue_list_view():
    print("Testing venue_list view...")
    
    # Create a request factory
    factory = RequestFactory()
    request = factory.get('/venues/')
    
    # Get response from view
    response = venue_list(request)
    
    # Direct call to the view
    venues = Venue.objects.filter(is_active=True, is_suspended=False)
    print(f"Number of venues that should be visible: {venues.count()}")
    
    # Check context directly
    venues = response.context_data['venues'] if hasattr(response, 'context_data') else response.context['venues']
    
    print(f"Number of venues in response: {venues.count()}")
    print("Venues in response:")
    for venue in venues:
        print(f"- {venue.name}")
        print(f"  ID: {venue.id}")
        print(f"  Active: {venue.is_active}")
        print(f"  Suspended: {venue.is_suspended}")
        print("")
    
    # Check venues in database
    print("\nChecking venues in database:")
    all_venues = Venue.objects.all()
    print(f"Total venues: {all_venues.count()}")
    active_venues = Venue.objects.filter(is_active=True)
    print(f"Active venues: {active_venues.count()}")
    non_suspended = Venue.objects.filter(is_suspended=False)
    print(f"Non-suspended venues: {non_suspended.count()}")
    visible_venues = Venue.objects.filter(is_active=True, is_suspended=False)
    print(f"Visible venues (active & not suspended): {visible_venues.count()}")
    
    print("\nVenue details from database:")
    for venue in all_venues:
        print(f"- {venue.name}")
        print(f"  ID: {venue.id}")
        print(f"  Active: {venue.is_active}")
        print(f"  Suspended: {venue.is_suspended}")
        print(f"  Has images: {venue.images.exists()}")
        print(f"  Provider: {venue.provider}")
        print("")

if __name__ == "__main__":
    test_venue_list_view()
