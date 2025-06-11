from django.core.management.base import BaseCommand
from caterers.models import EventType

class Command(BaseCommand):
    help = 'Creates default event types for caterers'

    def handle(self, *args, **options):
        default_event_types = [
            {
                'name': 'Wedding',
                'description': 'Wedding ceremonies and receptions',
                'icon': '💒',
                'display_order': 1,
            },
            {
                'name': 'Corporate Event',
                'description': 'Business meetings, conferences, and corporate gatherings',
                'icon': '🏢',
                'display_order': 2,
            },
            {
                'name': 'Birthday Party',
                'description': 'Birthday celebrations for all ages',
                'icon': '🎂',
                'display_order': 3,
            },
            {
                'name': 'Baby Shower',
                'description': 'Baby shower celebrations',
                'icon': '👶',
                'display_order': 4,
            },
            {
                'name': 'Graduation',
                'description': 'Graduation ceremonies and parties',
                'icon': '🎓',
                'display_order': 5,
            },
            {
                'name': 'Anniversary',
                'description': 'Wedding and business anniversaries',
                'icon': '💕',
                'display_order': 6,
            },
            {
                'name': 'Holiday Party',
                'description': 'Christmas, New Year, and other holiday celebrations',
                'icon': '🎄',
                'display_order': 7,
            },
            {
                'name': 'Baptism/Christening',
                'description': 'Religious ceremonies and celebrations',
                'icon': '⛪',
                'display_order': 8,
            },
            {
                'name': 'Quinceañera',
                'description': '15th birthday celebrations',
                'icon': '👸',
                'display_order': 9,
            },
            {
                'name': 'Debut (18th Birthday)',
                'description': '18th birthday celebrations and debutante parties',
                'icon': '🌟',
                'display_order': 10,
            },
            {
                'name': 'Engagement Party',
                'description': 'Engagement celebrations',
                'icon': '💍',
                'display_order': 11,
            },
            {
                'name': 'Funeral/Memorial',
                'description': 'Memorial services and funeral receptions',
                'icon': '🕊️',
                'display_order': 12,
            },
            {
                'name': 'Family Reunion',
                'description': 'Family gatherings and reunions',
                'icon': '👨‍👩‍👧‍👦',
                'display_order': 13,
            },
            {
                'name': 'School Event',
                'description': 'School functions, proms, and educational events',
                'icon': '🏫',
                'display_order': 14,
            },
            {
                'name': 'Sports Event',
                'description': 'Sports banquets and athletic celebrations',
                'icon': '🏆',
                'display_order': 15,
            },
            {
                'name': 'Charity Event',
                'description': 'Fundraisers and charity functions',
                'icon': '❤️',
                'display_order': 16,
            },
            {
                'name': 'Cultural Event',
                'description': 'Cultural festivals and traditional celebrations',
                'icon': '🎭',
                'display_order': 17,
            },
            {
                'name': 'Retirement Party',
                'description': 'Retirement celebrations',
                'icon': '🎣',
                'display_order': 18,
            },
            {
                'name': 'Housewarming',
                'description': 'New home celebrations',
                'icon': '🏠',
                'display_order': 19,
            },
            {
                'name': 'Other',
                'description': 'Other special events and occasions',
                'icon': '🎉',
                'display_order': 20,
            },
        ]

        created_count = 0
        updated_count = 0

        for event_data in default_event_types:
            event_type, created = EventType.objects.get_or_create(
                name=event_data['name'],
                defaults={
                    'description': event_data['description'],
                    'icon': event_data['icon'],
                    'display_order': event_data['display_order'],
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created event type: {event_type.name}')
                )
            else:
                # Update existing event type if needed
                if (event_type.description != event_data['description'] or 
                    event_type.icon != event_data['icon'] or 
                    event_type.display_order != event_data['display_order']):
                    
                    event_type.description = event_data['description']
                    event_type.icon = event_data['icon']
                    event_type.display_order = event_data['display_order']
                    event_type.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Updated event type: {event_type.name}')
                    )

        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(default_event_types)} event types:\n'
                f'  - Created: {created_count} new event types\n'
                f'  - Updated: {updated_count} existing event types\n'
                f'  - Total: {EventType.objects.count()} event types in database'
            )
        )
        self.stdout.write('='*50)
