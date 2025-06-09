"""
Management command to demonstrate custom admin functionality
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from venues.models import Venue
from caterers.models import Caterer
from django.utils import timezone


class Command(BaseCommand):
    help = 'Demonstrate custom admin functionality'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Custom Admin Interface Demo ===\n'))
        
        # Check data availability
        venue_count = Venue.objects.count()
        caterer_count = Caterer.objects.count()
        
        self.stdout.write(f"📊 Data Summary:")
        self.stdout.write(f"   • Venues: {venue_count}")
        self.stdout.write(f"   • Caterers: {caterer_count}")
        
        if venue_count == 0 and caterer_count == 0:
            self.stdout.write(self.style.WARNING("No venues or caterers found. Please add some data first."))
            return
        
        # Demo venue functionality
        if venue_count > 0:
            self.stdout.write(f"\n🏢 Venue Management Demo:")
            venue = Venue.objects.first()
            self.stdout.write(f"   Sample venue: {venue.name}")
            self.stdout.write(f"   Status: {'✅ Active' if venue.is_active else '❌ Inactive'}")
            self.stdout.write(f"   Suspended: {'🔴 Yes' if venue.is_suspended else '🟢 No'}")
            
            # Demo suspension
            if not venue.is_suspended:
                self.stdout.write(f"\n   📝 Testing suspension functionality...")
                venue.is_suspended = True
                venue.suspension_reason = "Demo: Testing admin functionality"
                venue.suspended_at = timezone.now()
                venue.save()
                self.stdout.write(f"   ✅ Venue suspended successfully")
                
                # Restore status
                venue.is_suspended = False
                venue.suspension_reason = ""
                venue.suspended_at = None
                venue.save()
                self.stdout.write(f"   ✅ Venue unsuspended successfully")
        
        # Demo caterer functionality
        if caterer_count > 0:
            self.stdout.write(f"\n🍽️ Caterer Management Demo:")
            caterer = Caterer.objects.first()
            self.stdout.write(f"   Sample caterer: {caterer.provider.business_name}")
            self.stdout.write(f"   Status: {'✅ Active' if caterer.is_active else '❌ Inactive'}")
            self.stdout.write(f"   Suspended: {'🔴 Yes' if caterer.is_suspended else '🟢 No'}")
            
            # Show service offerings
            services = []
            if caterer.offers_buffet:
                services.append("Buffet")
            if caterer.offers_plated:
                services.append("Plated")
            if caterer.offers_cocktail:
                services.append("Cocktail")
            if caterer.offers_food_stalls:
                services.append("Food Stalls")
            
            self.stdout.write(f"   Services: {', '.join(services) if services else 'None specified'}")
            
            # Demo suspension
            if not caterer.is_suspended:
                self.stdout.write(f"\n   📝 Testing suspension functionality...")
                caterer.is_suspended = True
                caterer.suspension_reason = "Demo: Testing admin functionality"
                caterer.suspended_at = timezone.now()
                caterer.save()
                self.stdout.write(f"   ✅ Caterer suspended successfully")
                
                # Restore status
                caterer.is_suspended = False
                caterer.suspension_reason = ""
                caterer.suspended_at = None
                caterer.save()
                self.stdout.write(f"   ✅ Caterer unsuspended successfully")
        
        # Check admin users
        User = get_user_model()
        admin_count = User.objects.filter(is_staff=True).count()
        self.stdout.write(f"\n👤 Admin Users: {admin_count}")
        
        # Show interface URLs
        self.stdout.write(f"\n🌐 Custom Admin Interface URLs:")
        self.stdout.write(f"   • Dashboard: http://127.0.0.1:8000/admin-panel/")
        self.stdout.write(f"   • Venue Regulation: http://127.0.0.1:8000/admin-panel/venues/")
        self.stdout.write(f"   • Caterer Regulation: http://127.0.0.1:8000/admin-panel/caterers/")
        
        if venue_count > 0:
            venue = Venue.objects.first()
            self.stdout.write(f"   • Venue Detail: http://127.0.0.1:8000/admin-panel/venues/{venue.id}/")
        
        if caterer_count > 0:
            caterer = Caterer.objects.first()
            self.stdout.write(f"   • Caterer Detail: http://127.0.0.1:8000/admin-panel/caterers/{caterer.id}/")
        
        self.stdout.write(f"\n📋 Features Implemented:")
        self.stdout.write(f"   ✅ Staff-only access control")
        self.stdout.write(f"   ✅ Dashboard with statistics")
        self.stdout.write(f"   ✅ Venue and caterer regulation pages")
        self.stdout.write(f"   ✅ Search and filtering functionality")
        self.stdout.write(f"   ✅ AJAX-powered suspension actions")
        self.stdout.write(f"   ✅ Detailed individual service views")
        self.stdout.write(f"   ✅ Responsive design with status indicators")
        self.stdout.write(f"   ✅ Modal-based suspension workflow")
        self.stdout.write(f"   ✅ Auto-refresh dashboard")
        
        self.stdout.write(self.style.SUCCESS('\n=== Custom Admin Interface Ready! ==='))
        self.stdout.write(f"💡 Login with admin credentials to access the interface.")
