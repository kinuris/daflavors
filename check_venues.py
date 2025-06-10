#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "daflavors.settings")
django.setup()

# Now import your models
from venues.models import Venue

def check_venues():
    print(f"Total venues in database: {Venue.objects.count()}")
    
    # Check for active venues
    active_venues = Venue.objects.filter(is_active=True)
    print(f"Active venues: {active_venues.count()}")
    
    # Check for non-suspended venues
    non_suspended = Venue.objects.filter(is_suspended=False)
    print(f"Non-suspended venues: {non_suspended.count()}")
    
    # Check for venues that should be visible (active and not suspended)
    visible_venues = Venue.objects.filter(is_active=True, is_suspended=False)
    print(f"Venues that should be visible (active & not suspended): {visible_venues.count()}")
    
    # Print details about each venue
    print("\nVenue details:")
    for venue in Venue.objects.all():
        print(f"- {venue.name}")
        print(f"  ID: {venue.id}")
        print(f"  Active: {venue.is_active}")
        print(f"  Suspended: {venue.is_suspended}")
        print(f"  Has images: {venue.images.exists()}")
        print(f"  Provider: {venue.provider}")
        print("")
    
if __name__ == "__main__":
    check_venues()
