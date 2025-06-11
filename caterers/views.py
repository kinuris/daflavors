from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import inlineformset_factory
from django.db import transaction
from django.http import Http404
from accounts.models import ProviderProfile
from .models import Caterer, CatererImage, MenuPackage, CourseCategory, MenuItem, PackageItem, CatererAvailability, EventType
from .forms import (CatererForm, CatererImageForm, MenuPackageForm, CourseCategoryForm, 
                    MenuItemForm, PackageItemForm, CatererAvailabilityForm)

def caterer_list(request):
    """
    Display list of all caterers with search and filtering options
    """
    # Only show caterers that are available for booking (active and not suspended)
    caterers = Caterer.objects.filter(is_active=True, is_suspended=False)
    
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
    
    # Filter by event type if specified
    event_type = request.GET.get('event_type')
    if event_type:
        caterers = caterers.filter(event_types__id=event_type)
    
    # Filter by guest count if specified
    min_guests = request.GET.get('min_guests')
    max_guests = request.GET.get('max_guests')
    
    if min_guests:
        caterers = caterers.filter(min_guests__lte=min_guests)
    if max_guests:
        caterers = caterers.filter(max_guests__gte=max_guests)
    
    # Get all active event types for filter dropdown
    event_types = EventType.objects.filter(is_active=True)
    
    context = {
        'caterers': caterers,
        'specialty': specialty,
        'service_type': service_type,
        'event_type': event_type,
        'selected_event_type': event_type,
        'event_types': event_types,
        'min_guests': min_guests,
        'max_guests': max_guests
    }
    return render(request, 'caterers/caterer_list.html', context)

def caterer_detail(request, caterer_id):
    """
    Display detailed information about a specific caterer
    """
    caterer = get_object_or_404(Caterer, id=caterer_id)
    menu_packages = caterer.menu_packages.all()
    
    # Check if user owns this caterer profile
    is_owner = False
    if request.user.is_authenticated and hasattr(request.user, 'provider_profile'):
        is_owner = caterer.provider == request.user.provider_profile
    
    # If caterer is suspended or inactive, only show to owner and admin
    if not caterer.is_available_for_booking():
        if not is_owner and not request.user.is_staff:
            messages.error(request, "This caterer is currently not available for booking.")
            return redirect('caterers:list')
    
    context = {
        'caterer': caterer,
        'menu_packages': menu_packages,
        'is_owner': is_owner,
    }
    return render(request, 'caterers/caterer_detail.html', context)

@login_required
def caterer_create(request):
    """
    Create a new caterer profile
    """
    if not hasattr(request.user, 'provider_profile'):
        messages.error(request, "You must be registered as a provider to create a catering service.")
        return redirect('accounts:become_provider')
    
    if request.method == 'POST':
        form = CatererForm(request.POST)
        
        if form.is_valid():
            with transaction.atomic():
                caterer = form.save(commit=False)
                caterer.provider = request.user.provider_profile
                caterer.save()
            
            messages.success(request, "Catering service created successfully!")
            return redirect('caterers:detail', caterer_id=caterer.id)
        else:
            # Debug: print form errors
            print("Form errors:", form.errors)
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = CatererForm()
    
    context = {
        'form': form,
        'action': 'Create',
        'is_create': True,
        'form_title': 'Create Caterer Profile'
    }
    return render(request, 'caterers/caterer_form.html', context)

@login_required
def caterer_update(request, caterer_id):
    """
    Update an existing caterer profile
    """
    caterer = get_object_or_404(Caterer, id=caterer_id)
    
    # Check if user has permission to edit
    if not request.user.provider_profile == caterer.provider:
        messages.error(request, "You don't have permission to edit this catering service.")
        return redirect('caterers:caterer_detail', caterer_id=caterer.id)
    
    CatererImageFormSet = inlineformset_factory(Caterer, CatererImage, form=CatererImageForm, extra=1)
    
    if request.method == 'POST':
        form = CatererForm(request.POST, instance=caterer)
        image_formset = CatererImageFormSet(request.POST, request.FILES, instance=caterer)
        
        if form.is_valid() and image_formset.is_valid():
            with transaction.atomic():
                caterer = form.save()
                image_formset.save()
            
            messages.success(request, "Catering service updated successfully!")
            return redirect('caterers:caterer_detail', caterer_id=caterer.id)
    else:
        form = CatererForm(instance=caterer)
        image_formset = CatererImageFormSet(instance=caterer)
    
    context = {
        'form': form,
        'image_formset': image_formset,
        'caterer': caterer,
        'action': 'Update',
        'is_create': False,
        'form_title': 'Update Caterer Profile'
    }
    return render(request, 'caterers/caterer_form.html', context)

@login_required
def caterer_delete(request, caterer_id):
    """
    Delete a caterer profile
    """
    caterer = get_object_or_404(Caterer, id=caterer_id)
    
    # Check if user has permission to delete
    if not request.user.provider_profile == caterer.provider:
        messages.error(request, "You don't have permission to delete this catering service.")
        return redirect('caterers:caterer_detail', caterer_id=caterer.id)
    
    if request.method == 'POST':
        caterer.delete()
        messages.success(request, "Catering service deleted successfully!")
        return redirect('caterers:list')
    
    context = {
        'caterer': caterer
    }
    return render(request, 'caterers/caterer_confirm_delete.html', context)

# Menu Package Views
@login_required
def menu_list(request, caterer_id):
    """
    Display list of all menu packages for a caterer
    """
    caterer = get_object_or_404(Caterer, id=caterer_id)
    menu_packages = caterer.menu_packages.all()
    
    context = {
        'caterer': caterer,
        'menu_packages': menu_packages
    }
    return render(request, 'caterers/menu_list.html', context)

@login_required
def menu_create(request, caterer_id):
    """
    Create a new menu package
    """
    caterer = get_object_or_404(Caterer, id=caterer_id)
    
    # Check if user has permission to add menus
    if not request.user.provider_profile == caterer.provider:
        messages.error(request, "You don't have permission to add menus to this catering service.")
        return redirect('caterers:detail', caterer_id=caterer.id)
    
    PackageItemFormSet = inlineformset_factory(MenuPackage, PackageItem, form=PackageItemForm, extra=5)
    
    if request.method == 'POST':
        form = MenuPackageForm(request.POST)
        item_formset = PackageItemFormSet(request.POST)
        
        if form.is_valid() and item_formset.is_valid():
            with transaction.atomic():
                menu_package = form.save(commit=False)
                menu_package.caterer = caterer
                menu_package.save()
                
                item_formset.instance = menu_package
                item_formset.save()
            
            messages.success(request, "Menu package created successfully!")
            return redirect('caterers:menu', caterer_id=caterer.id, menu_id=menu_package.id)
    else:
        form = MenuPackageForm()
        item_formset = PackageItemFormSet()
    
    context = {
        'form': form,
        'item_formset': item_formset,
        'caterer': caterer,
        'action': 'Create'
    }
    return render(request, 'caterers/menu_form.html', context)

def menu_detail(request, caterer_id, menu_id):
    """
    Display details of a specific menu package
    """
    caterer = get_object_or_404(Caterer, id=caterer_id)
    menu_package = get_object_or_404(MenuPackage, id=menu_id, caterer=caterer)
    items = menu_package.items.all().order_by('course_category__display_order')
    
    context = {
        'caterer': caterer,
        'menu_package': menu_package,
        'items': items
    }
    return render(request, 'caterers/menu_detail.html', context)

@login_required
def menu_update(request, caterer_id, menu_id):
    """
    Update an existing menu package
    """
    caterer = get_object_or_404(Caterer, id=caterer_id)
    menu_package = get_object_or_404(MenuPackage, id=menu_id, caterer=caterer)
    
    # Check if user has permission to edit
    if not request.user.provider_profile == caterer.provider:
        messages.error(request, "You don't have permission to edit this menu package.")
        return redirect('caterers:menu', caterer_id=caterer.id, menu_id=menu_id)
    
    PackageItemFormSet = inlineformset_factory(MenuPackage, PackageItem, form=PackageItemForm, extra=1)
    
    if request.method == 'POST':
        form = MenuPackageForm(request.POST, instance=menu_package)
        item_formset = PackageItemFormSet(request.POST, instance=menu_package)
        
        if form.is_valid() and item_formset.is_valid():
            with transaction.atomic():
                menu_package = form.save()
                item_formset.save()
            
            messages.success(request, "Menu package updated successfully!")
            return redirect('caterers:menu', caterer_id=caterer.id, menu_id=menu_package.id)
    else:
        form = MenuPackageForm(instance=menu_package)
        item_formset = PackageItemFormSet(instance=menu_package)
    
    context = {
        'form': form,
        'item_formset': item_formset,
        'caterer': caterer,
        'menu_package': menu_package,
        'action': 'Update'
    }
    return render(request, 'caterers/menu_form.html', context)

@login_required
def menu_delete(request, caterer_id, menu_id):
    """
    Delete a menu package
    """
    caterer = get_object_or_404(Caterer, id=caterer_id)
    menu_package = get_object_or_404(MenuPackage, id=menu_id, caterer=caterer)
    
    # Check if user has permission to delete
    if not request.user.provider_profile == caterer.provider:
        messages.error(request, "You don't have permission to delete this menu package.")
        return redirect('caterers:menu_detail', caterer_id=caterer.id, menu_id=menu_id)
    
    if request.method == 'POST':
        menu_package.delete()
        messages.success(request, "Menu package deleted successfully!")
        return redirect('caterers:detail', caterer_id=caterer.id)
    
    context = {
        'caterer': caterer,
        'menu_package': menu_package
    }
    return render(request, 'caterers/menu_confirm_delete.html', context)
