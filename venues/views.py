from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import inlineformset_factory
from django.db import transaction
from django.http import Http404
from .models import Venue, VenueImage, VenueFeature, VenueRoom, VenueAvailability
from .forms import VenueForm, VenueImageForm, VenueFeatureForm, VenueRoomForm, VenueAvailabilityForm
from accounts.models import ProviderProfile

def venue_list(request):
    """
    Display list of all venues with search and filtering options
    """
    venues = Venue.objects.all()
    venue_types = Venue.TYPE_CHOICES
    
    # Filter by venue type if specified
    venue_type = request.GET.get('venue_type')
    if venue_type:
        venues = venues.filter(venue_type=venue_type)
    
    # Filter by capacity if specified
    min_capacity = request.GET.get('min_capacity')
    if min_capacity:
        venues = venues.filter(capacity__gte=min_capacity)

    # Filter by price range if specified
    max_price = request.GET.get('max_price')
    if max_price:
        venues = venues.filter(base_price__lte=max_price)
    
    context = {
        'venues': venues,
        'venue_types': venue_types,
        'selected_type': venue_type,
        'min_capacity': min_capacity,
        'max_price': max_price
    }
    return render(request, 'venues/venue_list.html', context)

def venue_detail(request, venue_id):
    """
    Display detailed information for a specific venue
    """
    venue = get_object_or_404(Venue, id=venue_id)
    
    # Get all venue rooms and features
    rooms = venue.rooms.all()
    features = venue.features.all()
    
    # Check if the current user is the owner of this venue
    is_owner = False
    if request.user.is_authenticated and hasattr(request.user, 'provider_profile'):
        is_owner = venue.provider == request.user.provider_profile
    
    context = {
        'venue': venue,
        'rooms': rooms,
        'features': features,
        'is_owner': is_owner,
    }
    return render(request, 'venues/venue_detail.html', context)

@login_required
def venue_create(request):
    """
    Create a new venue
    """
    if not hasattr(request.user, 'provider_profile'):
        messages.error(request, "You must be registered as a provider to create venues.")
        return redirect('accounts:become_provider')
    
    VenueImageFormSet = inlineformset_factory(Venue, VenueImage, form=VenueImageForm, extra=3, can_delete=True)
    VenueRoomFormSet = inlineformset_factory(Venue, VenueRoom, form=VenueRoomForm, extra=2, can_delete=True)
    VenueFeatureFormSet = inlineformset_factory(Venue, VenueFeature, form=VenueFeatureForm, extra=3, can_delete=True)
    
    if request.method == 'POST':
        form = VenueForm(request.POST)
        image_formset = VenueImageFormSet(request.POST, request.FILES)
        room_formset = VenueRoomFormSet(request.POST)
        feature_formset = VenueFeatureFormSet(request.POST)
        
        if form.is_valid() and image_formset.is_valid() and room_formset.is_valid() and feature_formset.is_valid():
            with transaction.atomic():
                venue = form.save(commit=False)
                venue.provider = request.user.provider_profile
                venue.save()
                
                image_formset.instance = venue
                image_formset.save()
                
                room_formset.instance = venue
                room_formset.save()
                
                feature_formset.instance = venue
                feature_formset.save()
                
            messages.success(request, "Venue created successfully!")
            return redirect('venues:venue_detail', venue_id=venue.id)
    else:
        form = VenueForm()
        image_formset = VenueImageFormSet()
        room_formset = VenueRoomFormSet()
        feature_formset = VenueFeatureFormSet()
    
    context = {
        'form': form,
        'image_formset': image_formset,
        'room_formset': room_formset,
        'feature_formset': feature_formset,
        'action': 'Create'
    }
    return render(request, 'venues/venue_form.html', context)

@login_required
def venue_update(request, venue_id):
    """
    Update an existing venue
    """
    venue = get_object_or_404(Venue, id=venue_id)
    
    # Check if user has permission to edit this venue
    if not request.user.provider_profile == venue.provider:
        messages.error(request, "You don't have permission to edit this venue.")
        return redirect('venues:venue_detail', venue_id=venue.id)
    
    VenueImageFormSet = inlineformset_factory(Venue, VenueImage, form=VenueImageForm, extra=1, can_delete=True)
    VenueRoomFormSet = inlineformset_factory(Venue, VenueRoom, form=VenueRoomForm, extra=1, can_delete=True)
    VenueFeatureFormSet = inlineformset_factory(Venue, VenueFeature, form=VenueFeatureForm, extra=1, can_delete=True)
    
    if request.method == 'POST':
        form = VenueForm(request.POST, instance=venue)
        image_formset = VenueImageFormSet(request.POST, request.FILES, instance=venue)
        room_formset = VenueRoomFormSet(request.POST, instance=venue)
        feature_formset = VenueFeatureFormSet(request.POST, instance=venue)
        
        if form.is_valid() and image_formset.is_valid() and room_formset.is_valid() and feature_formset.is_valid():
            with transaction.atomic():
                venue = form.save()
                image_formset.save()
                room_formset.save()
                feature_formset.save()
                
            messages.success(request, "Venue updated successfully!")
            return redirect('venues:venue_detail', venue_id=venue.id)
    else:
        form = VenueForm(instance=venue)
        image_formset = VenueImageFormSet(instance=venue)
        room_formset = VenueRoomFormSet(instance=venue)
        feature_formset = VenueFeatureFormSet(instance=venue)
    
    context = {
        'form': form,
        'image_formset': image_formset,
        'room_formset': room_formset,
        'feature_formset': feature_formset,
        'venue': venue,
        'action': 'Update'
    }
    return render(request, 'venues/venue_form.html', context)

@login_required
def venue_delete(request, venue_id):
    """
    Delete a venue
    """
    venue = get_object_or_404(Venue, id=venue_id)
    
    # Check if user has permission to delete this venue
    if not request.user.provider_profile == venue.provider:
        messages.error(request, "You don't have permission to delete this venue.")
        return redirect('venues:detail', venue_id=venue.id)
    
    if request.method == 'POST':
        venue.delete()
        messages.success(request, "Venue deleted successfully!")
        return redirect('venues:list')
    
    context = {
        'venue': venue
    }
    return render(request, 'venues/venue_confirm_delete.html', context)

@login_required
def venue_create(request):
    """
    Create a new venue with associated metadata
    """
    # Check if the user is a provider
    if not request.user.is_provider():
        messages.error(request, "Only providers can create venues.")
        return redirect('accounts:profile')
    
    # Get or create provider profile
    try:
        provider_profile = request.user.provider_profile
    except:
        messages.error(request, "Please complete your provider profile first.")
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.provider = provider_profile
            venue.save()
            
            # Add success message
            messages.success(request, f"Venue '{venue.name}' created successfully!")
            
            # Redirect to update page to add images, features, and rooms
            return redirect('venues:venue_update', venue_id=venue.id)
    else:
        form = VenueForm()
    
    return render(request, 'venues/venue_form.html', {
        'form': form, 
        'form_title': 'Add New Venue',
        'is_create': True
    })

@login_required
def venue_update(request, venue_id):
    """
    Update an existing venue and its associated data
    """
    venue = get_object_or_404(Venue, id=venue_id)
    
    # Security check: ensure the user owns this venue
    try:
        provider_profile = request.user.provider_profile
        if venue.provider != provider_profile:
            messages.error(request, "You don't have permission to edit this venue.")
            return redirect('venues:venue_detail', venue_id=venue_id)
    except:
        messages.error(request, "You don't have permission to edit this venue.")
        return redirect('venues:venue_detail', venue_id=venue_id)
    
    # Create formsets for related objects
    ImageFormSet = inlineformset_factory(
        Venue, VenueImage, form=VenueImageForm,
        extra=1, can_delete=True
    )
    
    FeatureFormSet = inlineformset_factory(
        Venue, VenueFeature, form=VenueFeatureForm,
        extra=1, can_delete=True
    )
    
    RoomFormSet = inlineformset_factory(
        Venue, VenueRoom, form=VenueRoomForm,
        extra=1, can_delete=True
    )
    
    if request.method == 'POST':
        form = VenueForm(request.POST, instance=venue)
        image_formset = ImageFormSet(request.POST, request.FILES, instance=venue)
        feature_formset = FeatureFormSet(request.POST, instance=venue)
        room_formset = RoomFormSet(request.POST, instance=venue)
        
        # Create availability records for selected dates
        new_dates = request.POST.getlist('new_availability_date')
        
        if form.is_valid() and image_formset.is_valid() and feature_formset.is_valid() and room_formset.is_valid():
            with transaction.atomic():
                # Save the main form and formsets
                form.save()
                image_formset.save()
                feature_formset.save()
                room_formset.save()
                
                # Handle availability dates
                for date_str in new_dates:
                    if date_str:  # Only process non-empty dates
                        VenueAvailability.objects.create(
                            venue=venue,
                            date=date_str,
                            is_available=True
                        )
            
            messages.success(request, f"Venue '{venue.name}' updated successfully!")
            return redirect('venues:venue_detail', venue_id=venue_id)
    else:
        form = VenueForm(instance=venue)
        image_formset = ImageFormSet(instance=venue)
        feature_formset = FeatureFormSet(instance=venue)
        room_formset = RoomFormSet(instance=venue)
    
    # Get existing availability dates
    availability_dates = VenueAvailability.objects.filter(venue=venue)
    
    context = {
        'form': form,
        'image_formset': image_formset,
        'feature_formset': feature_formset,
        'room_formset': room_formset,
        'availability_dates': availability_dates,
        'venue': venue,
        'form_title': f'Edit Venue: {venue.name}',
        'is_create': False
    }
    
    return render(request, 'venues/venue_form.html', context)

@login_required
def venue_delete(request, venue_id):
    """
    Delete a venue and all associated data
    """
    venue = get_object_or_404(Venue, id=venue_id)
    
    # Security check: ensure the user owns this venue
    try:
        provider_profile = request.user.provider_profile
        if venue.provider != provider_profile:
            messages.error(request, "You don't have permission to delete this venue.")
            return redirect('venues:venue_detail', venue_id=venue_id)
    except:
        messages.error(request, "You don't have permission to delete this venue.")
        return redirect('venues:venue_detail', venue_id=venue_id)
    
    venue_name = venue.name
    
    if request.method == 'POST':
        venue.delete()
        messages.success(request, f"Venue '{venue_name}' has been deleted.")
        return redirect('accounts:provider_dashboard')
    
    return render(request, 'venues/venue_confirm_delete.html', {'venue': venue})
