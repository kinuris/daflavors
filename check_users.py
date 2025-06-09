#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daflavors.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
users = User.objects.filter(is_staff=True)
print(f'Staff users: {users.count()}')
for user in users:
    print(f'- {user.username} (superuser: {user.is_superuser})')

# If no staff users, let's create one for testing
if users.count() == 0:
    print("\nNo staff users found. Creating test admin user...")
    User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='admin123'
    )
    print("Created admin user: username='admin', password='admin123'")
