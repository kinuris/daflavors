from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import formset_factory
from django.db import transaction
from django.http import Http404, JsonResponse
from django.core.exceptions import PermissionDenied
from accounts.models import CustomUser, ProviderProfile
from venues.models import Venue, VenueAvailability
from caterers.models import Caterer, MenuPackage, CourseCategory, MenuItem, CatererAvailability
from .models import Booking, MenuSelection, CourseSelection, Quote, Payment, Message
from .forms import (BookingForm, MenuSelectionForm, CourseSelectionForm, 
                  QuoteForm, PaymentForm, MessageForm)
import json
from decimal import Decimal
from datetime import date, timedelta

@login_required
def booking_list(request):
    """
    Display a list of bookings based on the user's role
    """
    # Different view for clients and providers
    if request.user.is_provider():
        try:
            provider_profile = request.user.provider_profile
            # Get venues and caterers operated by this provider
            venues = Venue.objects.filter(provider=provider_profile)
            caterers = Caterer.objects.filter(provider=provider_profile)
            
            # Get bookings for these venues and caterers
            venue_bookings = Booking.objects.filter(venue__in=venues)
            caterer_bookings = Booking.objects.filter(caterer__in=caterers)
            
            # Combine and remove duplicates
            bookings = (venue_bookings | caterer_bookings).distinct()
            
        except:
            messages.warning(request, "Please complete your provider profile to view bookings.")
            return redirect('accounts:profile')
    else:
        # For clients, show their own bookings
        bookings = Booking.objects.filter(client=request.user)
    
    # Filter by status if requested
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
        
    # Filter by date range if requested
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        bookings = bookings.filter(event_date__gte=start_date)
    if end_date:
        bookings = bookings.filter(event_date__lte=end_date)
        
    # Sort by event date
    bookings = bookings.order_by('event_date')
    
    context = {
        'bookings': bookings,
        'status': status,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'bookings/booking_list.html', context)

@login_required
def booking_detail(request, booking_id):
    """
    View details of a specific booking
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user has permission to view this booking
    if not has_booking_permission(request.user, booking):
        raise PermissionDenied("You don't have permission to view this booking.")
        
    # Get related data
    try:
        menu_selection = booking.menu_selection
        course_selections = menu_selection.course_selections.all().select_related('course_category')
    except:
        menu_selection = None
        course_selections = []
        
    # Get quotes and payments
    quotes = booking.quotes.all()
    payments = booking.payments.all()
    
    # Get messages
    messages_list = booking.messages.all().order_by('sent_at')
    
    # Check if the user can send messages
    can_send_message = False
    message_recipient = None
    
    if request.user == booking.client:
        can_send_message = True
        if booking.venue and booking.venue.provider:
            message_recipient = booking.venue.provider.user
        elif booking.caterer and booking.caterer.provider:
            message_recipient = booking.caterer.provider.user
    elif request.user.is_provider():
        if booking.venue and booking.venue.provider.user == request.user:
            can_send_message = True
            message_recipient = booking.client
        elif booking.caterer and booking.caterer.provider.user == request.user:
            can_send_message = True
            message_recipient = booking.client
    
    # Handle new message form
    if request.method == 'POST' and can_send_message and message_recipient:
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            new_message = message_form.save(commit=False)
            new_message.booking = booking
            new_message.sender = request.user
            new_message.recipient = message_recipient
            new_message.save()
            
            messages.success(request, "Your message has been sent.")
            return redirect('bookings:detail', booking_id=booking_id)
    else:
        message_form = MessageForm()
    
    context = {
        'booking': booking,
        'menu_selection': menu_selection,
        'course_selections': course_selections,
        'quotes': quotes,
        'payments': payments,
        'messages_list': messages_list,
        'can_send_message': can_send_message,
        'message_recipient': message_recipient,
        'message_form': message_form,
    }
    
    return render(request, 'bookings/booking_detail.html', context)

@login_required
def booking_create(request):
    """
    Create a new booking
    """
    # Get initial data from query parameters
    venue_id = request.GET.get('venue')
    caterer_id = request.GET.get('caterer')
    menu_id = request.GET.get('menu')
    
    if request.method == 'POST':
        form = BookingForm(request.POST, venue_id=venue_id)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.client = request.user
            booking.status = 'inquiry'
            booking.save()
            
            # Redirect to menu selection if caterer was selected
            if booking.caterer:
                return redirect('bookings:menu_select', booking_id=booking.id)
            else:
                messages.success(request, "Your booking inquiry has been submitted!")
                return redirect('bookings:detail', booking_id=booking.id)
    else:
        form = BookingForm(venue_id=venue_id)
        
        # Set initial values if provided in URL
        if venue_id:
            form.fields['venue'].initial = venue_id
        if caterer_id:
            form.fields['caterer'].initial = caterer_id
    
    context = {
        'form': form,
        'venue_id': venue_id,
        'caterer_id': caterer_id,
        'menu_id': menu_id,
    }
    
    return render(request, 'bookings/booking_form.html', context)

@login_required
def booking_update(request, booking_id):
    """
    Update an existing booking
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user has permission to edit this booking
    if not can_edit_booking(request.user, booking):
        messages.error(request, "You don't have permission to edit this booking.")
        return redirect('bookings:detail', booking_id=booking_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            booking = form.save()
            messages.success(request, "Booking has been updated successfully!")
            return redirect('bookings:detail', booking_id=booking.id)
    else:
        form = BookingForm(instance=booking)
    
    context = {
        'form': form,
        'booking': booking,
    }
    
    return render(request, 'bookings/booking_form.html', context)

@login_required
def booking_cancel(request, booking_id):
    """
    Cancel a booking
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user has permission to cancel this booking
    if not can_cancel_booking(request.user, booking):
        messages.error(request, "You don't have permission to cancel this booking.")
        return redirect('bookings:detail', booking_id=booking_id)
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Booking has been cancelled.")
        return redirect('bookings:detail', booking_id=booking_id)
    
    return render(request, 'bookings/booking_cancel.html', {'booking': booking})

@login_required
def menu_select(request, booking_id):
    """
    Select a menu package for a booking
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user has permission to edit this booking
    if not can_edit_booking(request.user, booking):
        messages.error(request, "You don't have permission to edit menu selections.")
        return redirect('bookings:detail', booking_id=booking_id)
    
    # Check if booking has a caterer
    if not booking.caterer:
        messages.error(request, "Please select a caterer for this booking first.")
        return redirect('bookings:update', booking_id=booking_id)
    
    # Get or create menu selection
    try:
        menu_selection = booking.menu_selection
    except MenuSelection.DoesNotExist:
        menu_selection = None
        
    # Get menu package ID from query params
    menu_id = request.GET.get('menu')
    
    if request.method == 'POST':
        form = MenuSelectionForm(request.POST, instance=menu_selection, caterer_id=booking.caterer.id)
        if form.is_valid():
            menu_selection = form.save(commit=False)
            menu_selection.booking = booking
            
            # Calculate menu price
            package = form.cleaned_data['menu_package']
            menu_selection.menu_total_price = package.base_price_per_person * booking.guest_count
            
            menu_selection.save()
            
            # Redirect to course selection if needed
            if package.requires_selections:
                return redirect('bookings:course_select', booking_id=booking_id)
            else:
                messages.success(request, "Menu package has been selected successfully!")
                return redirect('bookings:detail', booking_id=booking_id)
    else:
        form = MenuSelectionForm(instance=menu_selection, caterer_id=booking.caterer.id, menu_id=menu_id)
    
    context = {
        'form': form,
        'booking': booking,
        'menu_packages': MenuPackage.objects.filter(caterer=booking.caterer),
    }
    
    return render(request, 'bookings/menu_select.html', context)

@login_required
def course_select(request, booking_id):
    """
    Select menu items for each course category
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user has permission to edit this booking
    if not can_edit_booking(request.user, booking):
        messages.error(request, "You don't have permission to edit menu selections.")
        return redirect('bookings:detail', booking_id=booking_id)
    
    # Check if booking has a menu selection
    try:
        menu_selection = booking.menu_selection
    except:
        messages.error(request, "Please select a menu package first.")
        return redirect('bookings:menu_select', booking_id=booking_id)
    
    # Get course categories for this menu package
    course_categories = CourseCategory.objects.filter(
        menuitem__packageitem__package=menu_selection.menu_package
    ).distinct().order_by('display_order')
    
    if request.method == 'POST':
        forms_valid = True
        course_forms = []
        
        # Process each course category
        for category in course_categories:
            # Get or create course selection
            try:
                course_selection = CourseSelection.objects.get(
                    menu_selection=menu_selection,
                    course_category=category
                )
            except CourseSelection.DoesNotExist:
                course_selection = None
            
            # Get form data for this category
            form_prefix = f"course_{category.id}"
            form = CourseSelectionForm(
                request.POST,
                instance=course_selection,
                prefix=form_prefix,
                course_category=category,
                caterer_id=booking.caterer.id
            )
            
            if form.is_valid():
                course_forms.append((form, category))
            else:
                forms_valid = False
        
        if forms_valid:
            # Save all forms within a transaction
            with transaction.atomic():
                for form, category in course_forms:
                    # Only save if items are selected
                    if form.cleaned_data.get('selected_items'):
                        course_selection = form.save(commit=False)
                        course_selection.menu_selection = menu_selection
                        course_selection.save()
                        form.save_m2m()  # Save many-to-many relationships
            
            messages.success(request, "Menu items selected successfully!")
            return redirect('bookings:detail', booking_id=booking_id)
    
    # Prepare a form for each course category
    course_forms = []
    for category in course_categories:
        # Get or create course selection
        try:
            course_selection = CourseSelection.objects.get(
                menu_selection=menu_selection,
                course_category=category
            )
        except CourseSelection.DoesNotExist:
            course_selection = None
        
        form_prefix = f"course_{category.id}"
        form = CourseSelectionForm(
            instance=course_selection,
            prefix=form_prefix,
            course_category=category,
            caterer_id=booking.caterer.id
        )
        
        course_forms.append({
            'form': form,
            'category': category,
            'menu_items': MenuItem.objects.filter(
                caterer=booking.caterer,
                course_category=category
            )
        })
    
    context = {
        'booking': booking,
        'menu_selection': menu_selection,
        'course_forms': course_forms,
    }
    
    return render(request, 'bookings/course_select.html', context)

@login_required
def quote_create(request, booking_id):
    """
    Create a price quote for a booking (provider view)
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user has permission to create quotes
    if not is_booking_provider(request.user, booking):
        messages.error(request, "Only the venue or caterer provider can create quotes.")
        return redirect('bookings:detail', booking_id=booking_id)
    
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.booking = booking
            quote.status = 'draft'  # Start as draft
            quote.save()
            
            messages.success(request, "Quote created successfully!")
            return redirect('bookings:quote_detail', booking_id=booking_id, quote_id=quote.id)
    else:
        # Pre-fill with reasonable defaults
        initial = {}
        
        # Calculate suggested venue cost
        if booking.venue and booking.venue_room:
            suggested_venue_cost = booking.venue_room.base_price
            if booking.venue_room.price_per_hour:
                # Calculate hours (rounded up)
                hours = (booking.end_time.hour - booking.start_time.hour)
                if booking.end_time.minute > booking.start_time.minute:
                    hours += 1
                suggested_venue_cost += (booking.venue_room.price_per_hour * hours)
                
            initial['venue_cost'] = suggested_venue_cost
            
        # Calculate suggested catering cost
        if booking.caterer:
            try:
                menu_selection = booking.menu_selection
                suggested_catering_cost = menu_selection.menu_total_price
                initial['catering_cost'] = suggested_catering_cost
            except:
                pass
        
        # Set default validity to 30 days from now
        initial['valid_until'] = date.today() + timedelta(days=30)
        
        # Calculate suggested total
        suggested_total = initial.get('venue_cost', 0) + initial.get('catering_cost', 0)
        if suggested_total > 0:
            initial['total_amount'] = suggested_total
            
        form = QuoteForm(initial=initial)
    
    context = {
        'form': form,
        'booking': booking,
    }
    
    return render(request, 'bookings/quote_form.html', context)

@login_required
def quote_update(request, booking_id, quote_id):
    """
    Update an existing quote
    """
    booking = get_object_or_404(Booking, id=booking_id)
    quote = get_object_or_404(Quote, id=quote_id, booking=booking)
    
    # Check if user has permission to update quotes
    if not is_booking_provider(request.user, booking):
        messages.error(request, "Only the venue or caterer provider can update quotes.")
        return redirect('bookings:detail', booking_id=booking_id)
    
    # Don't allow updating quotes that have been accepted or rejected
    if quote.status in ['accepted', 'rejected']:
        messages.error(request, "This quote cannot be modified because it has already been accepted or rejected.")
        return redirect('bookings:quote_detail', booking_id=booking_id, quote_id=quote_id)
    
    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote)
        if form.is_valid():
            form.save()
            messages.success(request, "Quote updated successfully!")
            return redirect('bookings:quote_detail', booking_id=booking_id, quote_id=quote_id)
    else:
        form = QuoteForm(instance=quote)
    
    context = {
        'form': form,
        'booking': booking,
        'quote': quote,
        'is_update': True,
    }
    
    return render(request, 'bookings/quote_form.html', context)

@login_required
def quote_detail(request, booking_id, quote_id):
    """
    View details of a specific quote
    """
    booking = get_object_or_404(Booking, id=booking_id)
    quote = get_object_or_404(Quote, id=quote_id, booking=booking)
    
    # Check if user has permission to view quotes
    if not has_booking_permission(request.user, booking):
        raise PermissionDenied("You don't have permission to view this quote.")
    
    context = {
        'booking': booking,
        'quote': quote,
        'is_provider': is_booking_provider(request.user, booking),
        'is_client': (request.user == booking.client),
    }
    
    return render(request, 'bookings/quote_detail.html', context)

@login_required
def quote_send(request, booking_id, quote_id):
    """
    Send a quote to a client
    """
    booking = get_object_or_404(Booking, id=booking_id)
    quote = get_object_or_404(Quote, id=quote_id, booking=booking)
    
    # Check if user has permission to send quotes
    if not is_booking_provider(request.user, booking):
        messages.error(request, "Only the venue or caterer provider can send quotes.")
        return redirect('bookings:detail', booking_id=booking_id)
    
    # Don't allow sending quotes that have already been sent, accepted or rejected
    if quote.status != 'draft':
        messages.error(request, "This quote has already been sent, accepted or rejected.")
        return redirect('bookings:quote_detail', booking_id=booking_id, quote_id=quote_id)
    
    if request.method == 'POST':
        quote.status = 'sent'
        quote.save()
        
        # Update booking status
        booking.status = 'quote_provided'
        booking.save()
        
        messages.success(request, "Quote has been sent to the client.")
        return redirect('bookings:quote_detail', booking_id=booking_id, quote_id=quote_id)
    
    return render(request, 'bookings/quote_send.html', {'booking': booking, 'quote': quote})

@login_required
def quote_respond(request, booking_id, quote_id):
    """
    Client accepts or rejects a quote
    """
    booking = get_object_or_404(Booking, id=booking_id)
    quote = get_object_or_404(Quote, id=quote_id, booking=booking)
    
    # Check if user is the client
    if request.user != booking.client:
        messages.error(request, "Only the booking client can respond to quotes.")
        return redirect('bookings:detail', booking_id=booking_id)
    
    # Don't allow responding to quotes that haven't been sent, or have already been accepted/rejected
    if quote.status not in ['sent']:
        messages.error(request, "This quote cannot be responded to.")
        return redirect('bookings:quote_detail', booking_id=booking_id, quote_id=quote_id)
    
    if request.method == 'POST':
        response = request.POST.get('response')
        if response == 'accept':
            quote.status = 'accepted'
            quote.save()
            
            # Update booking status and financial details
            booking.status = 'pending_deposit'
            booking.total_amount = quote.total_amount
            
            # Set deposit amount to 50% of total by default
            booking.deposit_amount = Decimal(quote.total_amount) * Decimal('0.5')
            booking.save()
            
            messages.success(request, "You have accepted the quote. Please proceed with the deposit payment.")
        elif response == 'reject':
            quote.status = 'rejected'
            quote.save()
            messages.success(request, "You have rejected the quote.")
        
        return redirect('bookings:detail', booking_id=booking_id)
    
    return render(request, 'bookings/quote_respond.html', {'booking': booking, 'quote': quote})

@login_required
def payment_create(request, booking_id):
    """
    Record a new payment
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user has permission to create payments
    if not has_booking_permission(request.user, booking):
        messages.error(request, "You don't have permission to create payments for this booking.")
        return redirect('bookings:detail', booking_id=booking_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.save()
            
            messages.success(request, "Payment recorded successfully!")
            return redirect('bookings:detail', booking_id=booking_id)
    else:
        # Pre-fill with reasonable defaults
        initial = {
            'payment_date': date.today(),
            'payment_method': 'bank_transfer',
        }
        
        # If this is likely a deposit payment
        if not booking.deposit_paid and booking.deposit_amount:
            initial['amount'] = booking.deposit_amount
            initial['payment_type'] = 'deposit'
        # If this is likely a final payment
        elif booking.deposit_paid and not booking.final_payment_received and booking.total_amount:
            initial['amount'] = booking.total_amount - booking.deposit_amount
            initial['payment_type'] = 'final'
        
        form = PaymentForm(initial=initial)
    
    context = {
        'form': form,
        'booking': booking,
    }
    
    return render(request, 'bookings/payment_form.html', context)

@login_required
def payment_confirm(request, booking_id, payment_id):
    """
    Confirm a payment (provider only)
    """
    booking = get_object_or_404(Booking, id=booking_id)
    payment = get_object_or_404(Payment, id=payment_id, booking=booking)
    
    # Check if user is the provider
    if not is_booking_provider(request.user, booking):
        messages.error(request, "Only the provider can confirm payments.")
        return redirect('bookings:detail', booking_id=booking_id)
    
    if request.method == 'POST':
        payment.is_confirmed = True
        payment.save()
        
        # Update booking status based on payment type
        if payment.payment_type == 'deposit':
            booking.deposit_paid = True
            booking.status = 'confirmed'
            booking.save()
            messages.success(request, "Deposit payment confirmed. Booking is now confirmed!")
        elif payment.payment_type == 'final':
            booking.final_payment_received = True
            booking.status = 'completed'
            booking.save()
            messages.success(request, "Final payment confirmed. Booking is now complete!")
        else:
            messages.success(request, "Payment confirmed successfully!")
        
        return redirect('bookings:detail', booking_id=booking_id)
    
    return render(request, 'bookings/payment_confirm.html', {'booking': booking, 'payment': payment})



@login_required
def get_menu_packages(request):
    """
    Ajax endpoint to get menu packages for a selected caterer
    """
    caterer_id = request.GET.get('caterer_id')
    if caterer_id:
        packages = MenuPackage.objects.filter(caterer_id=caterer_id).values(
            'id', 'name', 'base_price_per_person', 'package_type', 
            'min_persons'
        )
        return JsonResponse({'packages': list(packages)})
    return JsonResponse({'packages': []})

# Helper functions for permission checks

def has_booking_permission(user, booking):
    """
    Check if a user has permission to view a booking
    """
    # Client can view their own booking
    if user == booking.client:
        return True
        
    # Check if user is provider of venue or caterer
    if user.is_provider():
        try:
            provider_profile = user.provider_profile
            
            # Venue provider
            if booking.venue and booking.venue.provider == provider_profile:
                return True
                
            # Caterer provider
            if booking.caterer and booking.caterer.provider == provider_profile:
                return True
        except:
            pass
    
    # Default: no permission
    return False

def can_edit_booking(user, booking):
    """
    Check if a user can edit a booking
    """
    # Only client can edit their booking, and only if not yet confirmed
    if user == booking.client and booking.status in ['inquiry', 'quote_provided']:
        return True
    
    return False

def can_cancel_booking(user, booking):
    """
    Check if a user can cancel a booking
    """
    # Client can cancel their booking if not yet completed
    if user == booking.client and booking.status not in ['completed', 'cancelled']:
        return True
        
    # Provider can cancel bookings that aren't completed
    if user.is_provider() and booking.status not in ['completed', 'cancelled']:
        try:
            provider_profile = user.provider_profile
            
            # Venue provider
            if booking.venue and booking.venue.provider == provider_profile:
                return True
                
            # Caterer provider
            if booking.caterer and booking.caterer.provider == provider_profile:
                return True
        except:
            pass
    
    return False

def is_booking_provider(user, booking):
    """
    Check if user is the provider of the venue or caterer for this booking
    """
    if user.is_provider():
        try:
            provider_profile = user.provider_profile
            
            # Venue provider
            if booking.venue and booking.venue.provider == provider_profile:
                return True
                
            # Caterer provider
            if booking.caterer and booking.caterer.provider == provider_profile:
                return True
        except:
            pass
    
    return False
