from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .forms import LoginForm, RegistrationForm, ProviderProfileForm, UserProfileUpdateForm
from .models import CustomUser, ProviderProfile
from venues.models import Venue
from caterers.models import Caterer
from bookings.models import Booking

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                
                # If 'remember_me' is not checked, set session to expire when browser closes
                if not remember_me:
                    request.session.set_expiry(0)
                
                # Redirect to appropriate dashboard
                if user.is_provider():
                    return redirect('accounts:provider_dashboard')
                else:
                    return redirect('core:home')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('core:home')

@transaction.atomic
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        provider_form = None
        
        # If registering as provider, also validate provider form
        if 'user_type' in request.POST and request.POST['user_type'] == 'provider':
            provider_form = ProviderProfileForm(request.POST, request.FILES)
            if form.is_valid() and provider_form.is_valid():
                user = form.save()
                provider_profile = provider_form.save(commit=False)
                provider_profile.user = user
                provider_profile.save()
                
                login(request, user)
                messages.success(request, "Account created successfully! Please complete your provider profile.")
                return redirect('accounts:provider_dashboard')
        else:
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, "Account created successfully!")
                return redirect('core:home')
    else:
        form = RegistrationForm()
        provider_form = ProviderProfileForm()
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'provider_form': provider_form
    })

@login_required
def profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        user_form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
        provider_form = None
        
        if user.is_provider():
            provider_profile = user.provider_profile
            provider_form = ProviderProfileForm(request.POST, request.FILES, instance=provider_profile)
            
            if user_form.is_valid() and provider_form.is_valid():
                user_form.save()
                provider_form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('accounts:profile')
        else:
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('accounts:profile')
    else:
        user_form = UserProfileUpdateForm(instance=user)
        provider_form = None
        
        if user.is_provider():
            provider_profile, created = ProviderProfile.objects.get_or_create(user=user)
            provider_form = ProviderProfileForm(instance=provider_profile)
    
    # Get bookings if user is client
    bookings = None
    if user.is_client():
        bookings = Booking.objects.filter(client=user)
    
    context = {
        'user_form': user_form,
        'provider_form': provider_form,
        'bookings': bookings
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def provider_dashboard(request):
    user = request.user
    
    if not user.is_provider():
        messages.error(request, "Access denied. Provider account required.")
        return redirect('core:home')
    
    # Get venues and caterers owned by this provider
    venues = Venue.objects.filter(owner=user)
    caterers = Caterer.objects.filter(owner=user)
    
    # Get bookings for this provider's venues and caterers
    venue_bookings = Booking.objects.filter(venue__in=venues)
    catering_bookings = Booking.objects.filter(caterer__in=caterers)
    
    context = {
        'venues': venues,
        'caterers': caterers,
        'venue_bookings': venue_bookings,
        'catering_bookings': catering_bookings,
    }
    
    return render(request, 'accounts/provider_dashboard.html', context)
