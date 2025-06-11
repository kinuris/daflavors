from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import time, timedelta, datetime
from decimal import Decimal

from accounts.models import ProviderProfile
from venues.models import Venue
from caterers.models import Caterer, MenuPackage, CourseCategory, MenuItem

# Get the user model at runtime to ensure we get the correct custom user model
User = get_user_model()

class Command(BaseCommand):
    help = 'Creates sample data for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete all existing data before creating samples',
        )

    def handle(self, *args, **kwargs):
        if kwargs['flush']:
            self.stdout.write('Deleting existing data...')
            MenuItem.objects.all().delete()
            MenuPackage.objects.all().delete()
            CourseCategory.objects.all().delete()
            Caterer.objects.all().delete()
            Venue.objects.all().delete()
            ProviderProfile.objects.all().delete()
            User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully deleted existing data'))

        self.stdout.write('Creating sample data...')
        
        # Create admin user
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@daflavors.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True
        )
        admin_user.user_type = 'admin'
        admin_user.save()
        self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_user.username}'))
        
        # Create sample clients
        clients = []
        client_data = [
            {
                'username': 'maria.santos',
                'email': 'maria@example.com',
                'password': 'client123',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'phone_number': '+63 917 123 4567',
                'address': 'Makati City, Metro Manila'
            },
            {
                'username': 'john.dela.cruz',
                'email': 'john@example.com',
                'password': 'client123',
                'first_name': 'John',
                'last_name': 'Dela Cruz',
                'phone_number': '+63 918 765 4321',
                'address': 'Quezon City, Metro Manila'
            }
        ]
        
        for data in client_data:
            client = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            client.user_type = 'client'
            client.phone_number = data['phone_number']
            client.address = data['address']
            client.save()
            clients.append(client)
            self.stdout.write(self.style.SUCCESS(f'Created client: {client.username}'))
        
        # Create sample providers
        provider_data = [
            {
                'user': {
                    'username': 'grand.palace',
                    'email': 'info@grandpalace.com',
                    'password': 'provider123',
                    'first_name': 'Grand',
                    'last_name': 'Palace',
                    'phone_number': '+63 2 8888 9999',
                    'address': 'BGC, Taguig City'
                },
                'profile': {
                    'business_name': 'Grand Palace Events Place',
                    'business_description': 'Luxurious events venue in the heart of BGC',
                    'business_email': 'events@grandpalace.com',
                    'business_phone': '+63 2 8888 9999',
                    'business_address': 'BGC, Taguig City',
                    'service_area': 'Metro Manila',
                    'verified': True
                }
            }
        ]
        
        providers = []
        for data in provider_data:
            # Create user
            provider_user = User.objects.create_user(
                username=data['user']['username'],
                email=data['user']['email'],
                password=data['user']['password'],
                first_name=data['user']['first_name'],
                last_name=data['user']['last_name']
            )
            provider_user.user_type = 'provider'
            provider_user.phone_number = data['user']['phone_number'] 
            provider_user.address = data['user']['address']
            provider_user.save()
            
            # Create provider profile
            provider_profile = ProviderProfile.objects.create(
                user=provider_user,
                **data['profile']
            )
            providers.append(provider_profile)
            self.stdout.write(self.style.SUCCESS(f'Created provider: {provider_user.username}'))
        
        # Create a venue for the provider
        venue = Venue.objects.create(
            provider=providers[0],
            name='Grand Palace Main Hall',
            description='Our flagship venue perfect for weddings and corporate events',
            address='123 High Street, BGC, Taguig City',
            capacity=500,
            venue_type='event_hall',
            opening_time=time(8, 0),  # 8:00 AM
            closing_time=time(23, 0),  # 11:00 PM
            booking_policy='50% down payment required',
            cancellation_policy='Full refund if cancelled 30 days before the event',
            base_price=Decimal('50000.00')
        )
        self.stdout.write(self.style.SUCCESS(f'Created venue: {venue.name}'))
        
        # Create a caterer for the same provider (Grand Palace also offers catering)
        caterer = Caterer.objects.create(
            provider=providers[0],
            service_name='Grand Palace Catering',
            specialty='International Cuisine',
            min_guests=50,
            max_guests=1000,
            offers_buffet=True,
            offers_plated=True,
            offers_cocktail=True,
            offers_food_stalls=True,
            service_area='Metro Manila',
            setup_policy='Setup starts 4 hours before event',
            delivery_policy='Free delivery within Metro Manila',
            payment_policy='50% down payment required',
            cancellation_policy='Full refund if cancelled 30 days before'
        )
        self.stdout.write(self.style.SUCCESS(f'Created caterer: {caterer.service_name}'))
        
        # Create course categories
        categories = [
            {'name': 'Appetizers', 'display_order': 1},
            {'name': 'Soups', 'display_order': 2},
            {'name': 'Main Course', 'display_order': 3},
            {'name': 'Desserts', 'display_order': 4}
        ]
        
        created_categories = {}
        for cat in categories:
            category = CourseCategory.objects.create(**cat)
            created_categories[cat['name']] = category
            self.stdout.write(self.style.SUCCESS(f'Created course category: {category.name}'))
        
        # Create menu items
        menu_items = [
            {
                'name': 'Shrimp Cocktail',
                'description': 'Fresh shrimp with cocktail sauce',
                'course_category': created_categories['Appetizers'],
                'is_gluten_free': True,
                'individual_price': Decimal('250.00')
            },
            {
                'name': 'Mushroom Soup',
                'description': 'Creamy mushroom soup',
                'course_category': created_categories['Soups'],
                'is_vegetarian': True,
                'individual_price': Decimal('200.00')
            },
            {
                'name': 'Beef Wellington',
                'description': 'Classic beef wellington with mushroom duxelles',
                'course_category': created_categories['Main Course'],
                'individual_price': Decimal('850.00')
            },
            {
                'name': 'Chocolate Lava Cake',
                'description': 'Warm chocolate cake with molten center',
                'course_category': created_categories['Desserts'],
                'is_vegetarian': True,
                'individual_price': Decimal('300.00')
            }
        ]
        
        for item in menu_items:
            menu_item = MenuItem.objects.create(caterer=caterer, **item)
            self.stdout.write(self.style.SUCCESS(f'Created menu item: {menu_item.name}'))
        
        # Create menu packages
        packages = [
            MenuPackage.objects.create(
                caterer=caterer,
                name='Premium Wedding Package',
                description='Complete wedding package including appetizers, soup, main course, and dessert',
                package_type='plated',
                base_price_per_person=Decimal('2500.00'),
                min_persons=100,
                is_customizable=True
            ),
            MenuPackage.objects.create(
                caterer=caterer,
                name='Corporate Lunch Buffet',
                description='Perfect for business meetings and corporate events',
                package_type='buffet',
                base_price_per_person=Decimal('1200.00'),
                min_persons=50,
                is_customizable=True
            )
        ]
        for package in packages:
            self.stdout.write(self.style.SUCCESS(f'Created menu package: {package.name}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully created all sample data'))
