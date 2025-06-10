#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "daflavors.settings")
django.setup()

from venues.models import Venue

def fix_venues():
    print(f"Total venues in database: {Venue.objects.count()}")
    venues = Venue.objects.all()
    
    for venue in venues:
        print(f"Venue: {venue.name}")
        print(f"  ID: {venue.id}")
        print(f"  Active: {venue.is_active}")
        print(f"  Suspended: {venue.is_suspended}")
        
        # If the venue is suspended, unsuspend it
        if venue.is_suspended:
            print(f"  Unsuspending venue: {venue.name}")
            venue.is_suspended = False
            venue.save()
            print(f"  Venue now suspended: {venue.is_suspended}")
            
        # If the venue is not active, activate it
        if not venue.is_active:
            print(f"  Activating venue: {venue.name}")
            venue.is_active = True
            venue.save()
            print(f"  Venue now active: {venue.is_active}")
    
    print("\nAfter fixes:")
    for venue in Venue.objects.all():
        print(f"- {venue.name}: Active={venue.is_active}, Suspended={venue.is_suspended}")
    
    # Count venues that should now be visible
    visible_venues = Venue.objects.filter(is_active=True, is_suspended=False)
    print(f"\nVenues that should be visible now: {visible_venues.count()}")

if __name__ == "__main__":
    fix_venues()
