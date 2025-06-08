#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from caterers.views import caterer_create
from accounts.models import ProviderProfile

User = get_user_model()

# Get a user with provider profile
user = User.objects.filter(provider_profile__isnull=False).first()
if not user:
    print("No user with provider profile found")
    sys.exit(1)

print(f"Testing with user: {user.username}")

# Create a test client and login
client = Client()
client.force_login(user)

# Complete form data with all required fields
form_data = {
    'specialty': 'Filipino Cuisine',
    'min_guests': '20',
    'max_guests': '200', 
    'service_area': 'Roxas City, Capiz',
    'offers_buffet': 'on',  # HTML checkbox sends 'on' when checked
    'offers_plated': 'on',
    'setup_policy': 'We set up 2 hours before the event',
    'delivery_policy': 'Free delivery within 10km radius',
    'payment_policy': '50% down payment, 50% on event day',
    'cancellation_policy': '48 hours notice required for full refund'
}

print("Submitting complete form...")
response = client.post('/caterers/create/', form_data, follow=True)

print(f"Status code: {response.status_code}")
print(f"Final URL: {response.request['PATH_INFO']}")

if response.status_code == 200:
    if 'create' in response.request['PATH_INFO']:
        print("❌ Form submission failed - still on create page")
        if hasattr(response, 'context') and response.context:
            form = response.context.get('form')
            if form and hasattr(form, 'errors'):
                print(f"Form errors: {form.errors}")
            else:
                print("No form errors found in context")
    else:
        print("✅ Form redirected to different page - likely success!")
else:
    print(f"Unexpected status code: {response.status_code}")

# Check if caterer was created
from caterers.models import Caterer
try:
    caterer = Caterer.objects.get(provider=user.provider_profile)
    print(f"✅ Caterer created successfully: {caterer}")
    print(f"   - Specialty: {caterer.specialty}")
    print(f"   - Service Area: {caterer.service_area}")
    print(f"   - Min/Max Guests: {caterer.min_guests}-{caterer.max_guests}")
except Caterer.DoesNotExist:
    print("❌ No caterer found - creation failed")
