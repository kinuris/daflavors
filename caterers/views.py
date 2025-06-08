from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import inlineformset_factory
from django.db import transaction
from django.http import Http404
from accounts.models import ProviderProfile
from .models import Caterer, CatererImage, MenuPackage, CourseCategory, MenuItem, PackageItem, CatererAvailability
from .forms import (CatererForm, CatererImageForm, MenuPackageForm, CourseCategoryForm, 
                    MenuItemForm, PackageItemForm, CatererAvailabilityForm)

def caterer_list(request):
    """
    Display list of all caterers with search and filtering options
    """
    caterers = Caterer.objects.all()
    
    # Filter by specialty if specified
    specialty = request.GET.get('specialty')
    if specialty:
        caterers = caterers.filter(specialty__icontains=specialty)
    
    # Filter by service type if specified
    service_type = request.GET.get('service_type')
    if service_type == 'buffet':
        caterers = caterers.filter(offers_buffet=True)
    elif service_type == 'plated':
        caterers = caterers.filter(offers_plated=True)
    elif service_type == 'cocktail':
        caterers = caterers.filter(offers_cocktail=True)
    elif service_type == 'food_stalls':
        caterers = caterers.filter(offers_food_stalls=True)
    
    # Filter by guest count if specified
    min_guests = request.GET.get('min_guests')
    max_guests = request.GET.get('max_guests')
    
    if min_guests:
        caterers = caterers.filter(min_guests__lte=min_guests)
    if max_guests:
        caterers = caterers.filter(max_guests__gte=max_guests)
    
    context = {
        'caterers': caterers,
        'specialty': specialty,
        'service_type': service_type,
        'min_guests': min_guests,
        'max_guests': max_guests
    }
    return render(request, 'caterers/caterer_list.html', context)

def caterer_detail(request, caterer_id):
    """
    Display detailed information for a specific caterer
    """
    caterer = get_object_or_404(Caterer, id=caterer_id)
    
    # Check if the current user is the owner of this caterer
    is_owner = False
    if request.user.is_authenticated:
        try:
            provider_profile = request.user.provider_profile
            is_owner = (caterer.provider == provider_profile)
        except:
            pass
    
    # Get menu packages offered by this caterer
    menu_packages = caterer.menu_packages.all()
    
    context = {
        'caterer': caterer,
        'is_owner': is_owner,
        'menu_packages': menu_packages
    }
    return render(request, 'caterers/caterer_detail.html', context)

@login_required
def caterer_create(request):
    """
    Create a new caterer with associated metadata
    """
    # Check if the user is a provider
    if not request.user.is_provider():
        messages.error(request, "Only providers can create caterer profiles.")
        return redirect('accounts:profile')
    
    # Get or create provider profile
    try:
        provider_profile = request.user.provider_profile
    except:
        messages.error(request, "Please complete your provider profile first.")
        return redirect('accounts:profile')
    
    # Check if the provider already has a caterer profile
    try:
        existing_caterer = Caterer.objects.get(provider=provider_profile)
        messages.warning(request, "You already have a caterer profile. You can edit your existing profile.")
        return redirect('caterers:caterer_update', caterer_id=existing_caterer.id)
    except Caterer.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = CatererForm(request.POST)
        if form.is_valid():
            caterer = form.save(commit=False)
            caterer.provider = provider_profile
            caterer.save()
            
            # Add success message
            messages.success(request, "Caterer profile created successfully!")
            
            # Redirect to update page to add images and other details
            return redirect('caterers:caterer_update', caterer_id=caterer.id)
    else:
        form = CatererForm()
    
    return render(request, 'caterers/caterer_form.html', {
        'form': form, 
        'form_title': 'Create Caterer Profile',
        'is_create': True
    })

@login_required
def caterer_update(request, caterer_id):
    """
    Update an existing caterer profile and its associated data
    """
    caterer = get_object_or_404(Caterer, id=caterer_id)
    
    # Security check: ensure the user owns this caterer profile
    try:
        provider_profile = request.user.provider_profile
        if caterer.provider != provider_profile:
            messages.error(request, "You don't have permission to edit this caterer profile.")
            return redirect('caterers:caterer_detail', caterer_id=caterer_id)
    except:
        messages.error(request, "You don't have permission to edit this caterer profile.")
        return redirect('caterers:caterer_detail', caterer_id=caterer_id)
    
    # Create formset for caterer images
    ImageFormSet = inlineformset_factory(
        Caterer, CatererImage, form=CatererImageForm,
        extra=1, can_delete=True
    )
    
    if request.method == 'POST':
        form = CatererForm(request.POST, instance=caterer)
        image_formset = ImageFormSet(request.POST, request.FILES, instance=caterer)
        
        # Create availability records for selected dates
        new_dates = request.POST.getlist('new_availability_date')
        
        if form.is_valid() and image_formset.is_valid():
            with transaction.atomic():
                # Save the main form and formset
                form.save()
                image_formset.save()
                
                # Handle availability dates
                for date_str in new_dates:
                    if date_str:  # Only process non-empty dates
                        CatererAvailability.objects.create(
                            caterer=caterer,
                            date=date_str,
                            is_available=True
                        )
            
            messages.success(request, "Caterer profile updated successfully!")
            return redirect('caterers:caterer_detail', caterer_id=caterer_id)
    else:
        form = CatererForm(instance=caterer)
        image_formset = ImageFormSet(instance=caterer)
    
    # Get existing availability dates
    availability_dates = CatererAvailability.objects.filter(caterer=caterer)
    
    context = {
        'form': form,
        'image_formset': image_formset,
        'availability_dates': availability_dates,
        'caterer': caterer,
        'form_title': 'Edit Caterer Profile',
        'is_create': False
    }
    
    return render(request, 'caterers/caterer_form.html', context)

@login_required
def caterer_delete(request, caterer_id):
    """
    Delete a caterer profile and all associated data
    """
    caterer = get_object_or_404(Caterer, id=caterer_id)
    
    # Security check: ensure the user owns this caterer profile
    try:
        provider_profile = request.user.provider_profile
        if caterer.provider != provider_profile:
            messages.error(request, "You don't have permission to delete this caterer profile.")
            return redirect('caterers:caterer_detail', caterer_id=caterer_id)
    except:
        messages.error(request, "You don't have permission to delete this caterer profile.")
        return redirect('caterers:caterer_detail', caterer_id=caterer_id)
    
    if request.method == 'POST':
        caterer.delete()
        messages.success(request, "Caterer profile has been deleted.")
        return redirect('accounts:provider_dashboard')
    
    return render(request, 'caterers/caterer_confirm_delete.html', {'caterer': caterer})

@login_required
def menu_list(request, caterer_id):
    """
    List all menu packages for a specific caterer
    """
    caterer = get_object_or_404(Caterer, id=caterer_id)
    
    # Check if the current user is the owner of this caterer
    is_owner = False
    if request.user.is_authenticated:
        try:
            provider_profile = request.user.provider_profile
            is_owner = (caterer.provider == provider_profile)
        except:
            pass
    
    menu_packages = caterer.menu_packages.all()
    
    context = {
        'caterer': caterer,
        'menu_packages': menu_packages,
        'is_owner': is_owner
    }
    return render(request, 'caterers/menu_list.html', context)

@login_required
def menu_create(request, caterer_id):
    """
    Create a new menu package for a caterer
    """
    caterer = get_object_or_404(Caterer, id=caterer_id)
    
    # Security check: ensure the user owns this caterer profile
    try:
        provider_profile = request.user.provider_profile
        if caterer.provider != provider_profile:
            messages.error(request, "You don't have permission to create menu packages for this caterer.")
            return redirect('caterers:caterer_detail', caterer_id=caterer_id)
    except:
        messages.error(request, "You don't have permission to create menu packages for this caterer.")
        return redirect('caterers:caterer_detail', caterer_id=caterer_id)
    
    if request.method == 'POST':
        form = MenuPackageForm(request.POST)
        if form.is_valid():
            menu_package = form.save(commit=False)
            menu_package.caterer = caterer
            menu_package.save()
            
            messages.success(request, f"Menu package '{menu_package.name}' created successfully!")
            return redirect('caterers:menu_update', caterer_id=caterer_id, menu_id=menu_package.id)
    else:
        form = MenuPackageForm()
    
    context = {
        'form': form,
        'caterer': caterer,
        'form_title': 'Create Menu Package',
        'is_create': True
    }
    
    return render(request, 'caterers/menu_form.html', context)

@login_required
def menu_detail(request, caterer_id, menu_id):
    """
    View details of a specific menu package
    """
    caterer = get_object_or_404(Caterer, id=caterer_id)
    menu_package = get_object_or_404(MenuPackage, id=menu_id, caterer=caterer)
    
    # Check if the current user is the owner of this caterer
    is_owner = False
    if request.user.is_authenticated:
        try:
            provider_profile = request.user.provider_profile
            is_owner = (caterer.provider == provider_profile)
        except:
            pass
    
    # Get package items grouped by course category
    package_items = PackageItem.objects.filter(package=menu_package).order_by('course_category__display_order')
    
    context = {
        'caterer': caterer,
        'menu_package': menu_package,
        'package_items': package_items,
        'is_owner': is_owner
    }
    
    return render(request, 'caterers/menu_detail.html', context)

@login_required
def menu_update(request, caterer_id, menu_id):
    """
    Update an existing menu package
    """
    caterer = get_object_or_404(Caterer, id=caterer_id)
    menu_package = get_object_or_404(MenuPackage, id=menu_id, caterer=caterer)
    
    # Security check: ensure the user owns this caterer profile
    try:
        provider_profile = request.user.provider_profile
        if caterer.provider != provider_profile:
            messages.error(request, "You don't have permission to update menu packages for this caterer.")
            return redirect('caterers:menu_detail', caterer_id=caterer_id, menu_id=menu_id)
    except:
        messages.error(request, "You don't have permission to update menu packages for this caterer.")
        return redirect('caterers:menu_detail', caterer_id=caterer_id, menu_id=menu_id)
    
    # Use inline formset for package items
    PackageItemFormSet = inlineformset_factory(
        MenuPackage, PackageItem, form=PackageItemForm,
        extra=1, can_delete=True
    )
    
    if request.method == 'POST':
        form = MenuPackageForm(request.POST, instance=menu_package)
        formset = PackageItemFormSet(request.POST, instance=menu_package)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            
            messages.success(request, f"Menu package '{menu_package.name}' updated successfully!")
            return redirect('caterers:menu_detail', caterer_id=caterer_id, menu_id=menu_id)
    else:
        form = MenuPackageForm(instance=menu_package)
        formset = PackageItemFormSet(instance=menu_package)
    
    # Get all menu items for this caterer, for easy selection in the formset
    menu_items = MenuItem.objects.filter(caterer=caterer)
    
    context = {
        'form': form,
        'formset': formset,
        'caterer': caterer,
        'menu_package': menu_package,
        'menu_items': menu_items,
        'form_title': f'Edit "{menu_package.name}" Menu Package',
        'is_create': False
    }
    
    return render(request, 'caterers/menu_form.html', context)

@login_required
def menu_delete(request, caterer_id, menu_id):
    """
    Delete a menu package
    """
    caterer = get_object_or_404(Caterer, id=caterer_id)
    menu_package = get_object_or_404(MenuPackage, id=menu_id, caterer=caterer)
    
    # Security check: ensure the user owns this caterer profile
    try:
        provider_profile = request.user.provider_profile
        if caterer.provider != provider_profile:
            messages.error(request, "You don't have permission to delete menu packages for this caterer.")
            return redirect('caterers:menu_detail', caterer_id=caterer_id, menu_id=menu_id)
    except:
        messages.error(request, "You don't have permission to delete menu packages for this caterer.")
        return redirect('caterers:menu_detail', caterer_id=caterer_id, menu_id=menu_id)
    
    if request.method == 'POST':
        menu_package.delete()
        messages.success(request, f"Menu package '{menu_package.name}' has been deleted.")
        return redirect('caterers:menu_list', caterer_id=caterer_id)
    
    return render(request, 'caterers/menu_confirm_delete.html', {
        'caterer': caterer,
        'menu_package': menu_package
    })
