from django.shortcuts import render, redirect
from django.db.models import Q, Count, Avg
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from venues.models import Venue
from caterers.models import Caterer
from .models import FAQ, Testimonial, SiteSettings

def home(request):
    """Home page view"""
    try:
        # Featured venues (just get 4 random ones for now)
        featured_venues = Venue.objects.all().order_by('?')[:4]
        
        # Featured caterers (just get 4 random ones for now)
        featured_caterers = Caterer.objects.all().order_by('?')[:4]
        
        # Testimonials
        testimonials = Testimonial.objects.filter(is_approved=True).order_by('order', '-created_at')[:6]
    except:
        # In case models don't exist yet
        featured_venues = []
        featured_caterers = []
        testimonials = []
    
    context = {
        'featured_venues': featured_venues,
        'featured_caterers': featured_caterers,
        'testimonials': testimonials,
    }
    
    return render(request, 'core/home.html', context)

def about(request):
    """About page view"""
    context = {}
    
    return render(request, 'core/about.html', context)

def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # Simple validation
        if not all([name, email, subject, message]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'core/contact.html', {
                'name': name,
                'email': email,
                'phone': phone,
                'subject': subject,
                'message': message,
            })
        
        # Get site settings for contact email
        try:
            site_settings = SiteSettings.objects.first()
            recipient_email = site_settings.contact_email if site_settings else 'info@daflavors.com'
        except:
            recipient_email = 'info@daflavors.com'
        
        # Email details
        email_subject = f"DaFlavors Contact: {subject}"
        email_message = f"""
        Name: {name}
        Email: {email}
        Phone: {phone}
        
        Message:
        {message}
        """
        
        try:
            # Attempt to send email
            # Note: For actual production, you should configure email settings in settings.py
            # send_mail(
            #     email_subject,
            #     email_message,
            #     email,  # From email
            #     [recipient_email],  # To email
            #     fail_silently=False,
            # )
            
            # For now, just show success message
            messages.success(request, 'Your message has been sent! We will get back to you soon.')
            return redirect('core:contact')
        except Exception as e:
            messages.error(request, f'There was an error sending your message. Please try again later.')
    
    context = {}
    
    return render(request, 'core/contact.html', context)

def search(request):
    """Global search functionality"""
    query = request.GET.get('query', '')
    event_type = request.GET.get('event_type', '')
    location = request.GET.get('location', '')
    capacity = request.GET.get('capacity', '')
    try:
        capacity = int(capacity) if capacity else 0
    except (ValueError, TypeError):
        capacity = 0
    
    try:
        # Venues search
        venue_results = Venue.objects.all()
        if query:
            venue_results = venue_results.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(address__icontains=query)
            )
        
        if location:
            venue_results = venue_results.filter(address__icontains=location)
        
        if capacity > 0:
            venue_results = venue_results.filter(capacity__gte=capacity)
        
        # Caterers search
        caterer_results = Caterer.objects.all()
        if query:
            caterer_results = caterer_results.filter(
                Q(provider__business_name__icontains=query) | 
                Q(provider__business_description__icontains=query) |
                Q(specialty__icontains=query)
            )
        
        if location:
            caterer_results = caterer_results.filter(service_area__icontains=location)
        
        if capacity > 0:
            caterer_results = caterer_results.filter(max_guests__gte=capacity)
    except:
        # In case models don't exist yet
        venue_results = []
        caterer_results = []
    
    context = {
        'query': query,
        'event_type': event_type,
        'location': location,
        'capacity': capacity,
        'venue_results': venue_results,
        'caterer_results': caterer_results,
    }
    
    return render(request, 'core/search_results.html', context)

def faq(request):
    """FAQ page view"""
    faqs = FAQ.objects.all().order_by('order', 'category', 'question')
    
    # Group FAQs by category
    categories = {}
    for faq in faqs:
        category = faq.category or 'General'
        if category not in categories:
            categories[category] = []
        categories[category].append(faq)
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'core/faq.html', context)
