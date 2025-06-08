#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
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

# Test form submission
form_data = {
    'specialty': 'Test Cuisine',
    'min_guests': 10,
    'max_guests': 100,
    'service_area': 'Test City',
    'offers_buffet': True,
    'offers_plated': True,
    'offers_cocktail': False,
    'offers_food_stalls': False,
    'setup_policy': 'Test setup policy',
    'delivery_policy': 'Test delivery policy',
    'payment_policy': 'Test payment policy',
    'cancellation_policy': 'Test cancellation policy'
}

print("Submitting form...")
response = client.post('/caterers/create/', form_data)

print(f"Status code: {response.status_code}")
print(f"Response redirect: {response.get('Location', 'No redirect')}")

if response.status_code == 200:
    print("Form validation failed - checking for errors...")
    if hasattr(response, 'context') and response.context:
        form = response.context.get('form')
        if form and hasattr(form, 'errors'):
            print(f"Form errors: {form.errors}")
else:
    print("Form submitted successfully!")
