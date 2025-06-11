#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def test_url_patterns():
    print("TESTING URL PATTERNS WITH MULTIPLE CATERERS")
    print("=" * 50)
    
    # Get test user
    user = User.objects.get(username="multi_caterer_test")
    provider = user.provider_profile
    caterers = provider.caterers.all()
    
    client = Client()
    client.force_login(user)
    
    # Test caterer list
    print("Testing caterer list...")
    response = client.get('/caterers/')
    if response.status_code == 200:
        print("✓ Caterer list loads successfully")
    else:
        print(f"❌ Caterer list failed: {response.status_code}")
        return False
    
    # Test caterer detail for each caterer
    print("Testing caterer detail pages...")
    for caterer in caterers:
        url = f'/caterers/{caterer.id}/'
        response = client.get(url)
        if response.status_code == 200:
            print(f"✓ Caterer detail loads for {caterer.specialty}")
        else:
            print(f"❌ Caterer detail failed for {caterer.specialty}: {response.status_code}")
            return False
    
    # Test caterer create (should work multiple times)
    print("Testing caterer create form...")
    response = client.get('/caterers/create/')
    if response.status_code == 200:
        print("✓ Caterer create form loads successfully")
    else:
        print(f"❌ Caterer create form failed: {response.status_code}")
        return False
    
    # Test provider dashboard
    print("Testing provider dashboard...")
    response = client.get('/accounts/provider-dashboard/')
    if response.status_code == 200:
        print("✓ Provider dashboard loads successfully")
        
        # Check that all caterers appear in dashboard
        content = response.content.decode()
        for caterer in caterers:
            if caterer.specialty in content:
                print(f"✓ '{caterer.specialty}' appears in dashboard")
            else:
                print(f"❌ '{caterer.specialty}' missing from dashboard")
                return False
    else:
        print(f"❌ Provider dashboard failed: {response.status_code}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = test_url_patterns()
        if success:
            print(f"\n🎉 All URL pattern tests passed!")
            print("✅ All caterer views work correctly with multiple caterers")
        else:
            print(f"\n❌ URL pattern tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
