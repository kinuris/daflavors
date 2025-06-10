#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "daflavors.settings")
django.setup()

# Import models
from venues.models import Venue

def check_venues():
    print(f"Total venues in database: {Venue.objects.count()}")
    
    venues = Venue.objects.all()
    for venue in venues:
        print(f"- {venue.name} (ID: {venue.id})")
        print(f"  Active: {venue.is_active}")
        print(f"  Suspended: {venue.is_suspended}")
        print(f"  Available for booking: {venue.is_available_for_booking()}")
        print(f"  Provider: {venue.provider}")
        print()

if __name__ == "__main__":
    check_venues()
