#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "daflavors.settings")
django.setup()

# Import required modules
from django.test import RequestFactory
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from venues.models import Venue
from venues.views import venue_update

# Get the User model
User = get_user_model()

def test_venue_url_patterns():
    """Test that URL patterns for venues app are correctly configured"""
    
    print("Testing venue URL patterns...")
    
    # Get the first venue from the database
    try:
        venue = Venue.objects.first()
        venue_id = venue.id
        print(f"Found venue: {venue.name} (ID: {venue_id})")
    except:
        print("No venues found in database. Please create a venue first.")
        return
    
    # Test various URL patterns
    urls_to_test = [
        ('venues:list', [], {}),
        ('venues:detail', [], {'venue_id': venue_id}),
        ('venues:update', [], {'venue_id': venue_id}),
        ('venues:delete', [], {'venue_id': venue_id})
    ]
    
    for url_name, args, kwargs in urls_to_test:
        try:
            url = reverse(url_name, args=args, kwargs=kwargs)
            resolver = resolve(url)
            print(f"URL pattern '{url_name}' resolves to: {url}")
            print(f"  View function: {resolver.func.__name__}")
            print(f"  App name: {resolver.app_name}")
            print(f"  URL name: {resolver.url_name}")
            print()
        except Exception as e:
            print(f"Error resolving URL pattern '{url_name}': {e}")
            print()

if __name__ == "__main__":
    test_venue_url_patterns()
