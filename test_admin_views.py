#!/usr/bin/env python
"""
Test script for custom admin functionality
"""
import os
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from venues.models import Venue
from caterers.models import Caterer

def test_admin_functionality():
    print("=== Testing Custom Admin Interface ===\n")
    
    # Get admin user
    User = get_user_model()
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        print("❌ No admin user found!")
        return
    
    print(f"✅ Admin user found: {admin_user.username}")
    
    # Create test client and login
    client = Client()
    login_success = client.force_login(admin_user)
    print(f"✅ Admin user logged in")
    
    # Test admin dashboard
    print("\n--- Testing Admin Dashboard ---")
    response = client.get('/admin-panel/')
    print(f"Dashboard status: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    # Test venue regulation page
    print("\n--- Testing Venue Regulation ---")
    response = client.get('/admin-panel/venues/')
    print(f"Venue regulation status: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    # Test caterer regulation page
    print("\n--- Testing Caterer Regulation ---")
    response = client.get('/admin-panel/caterers/')
    print(f"Caterer regulation status: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    # Test data presence
    venues = Venue.objects.all()
    caterers = Caterer.objects.all()
    
    print(f"\n--- Data Summary ---")
    print(f"Total venues: {venues.count()}")
    print(f"Total caterers: {caterers.count()}")
    
    if venues.exists():
        venue = venues.first()
        print(f"Sample venue: {venue.business_name} (Active: {venue.is_active}, Suspended: {venue.is_suspended})")
        
        # Test venue detail page
        response = client.get(f'/admin-panel/venues/{venue.id}/')
        print(f"Venue detail status: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    if caterers.exists():
        caterer = caterers.first()
        print(f"Sample caterer: {caterer.business_name} (Active: {caterer.is_active}, Suspended: {caterer.is_suspended})")
        
        # Test caterer detail page
        response = client.get(f'/admin-panel/caterers/{caterer.id}/')
        print(f"Caterer detail status: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
        
        # Test AJAX suspension functionality
        print(f"\n--- Testing AJAX Functionality ---")
        original_status = caterer.is_suspended
        
        # Test suspend action
        response = client.post(f'/admin-panel/caterers/{caterer.id}/suspend/', {
            'reason': 'Testing suspension functionality'
        })
        print(f"Suspend AJAX status: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Suspend response: {data}")
            
            # Test unsuspend action
            response = client.post(f'/admin-panel/caterers/{caterer.id}/unsuspend/')
            print(f"Unsuspend AJAX status: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Unsuspend response: {data}")
    
    print(f"\n=== Admin Interface Testing Complete ===")

if __name__ == "__main__":
    test_admin_functionality()
