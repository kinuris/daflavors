"""
Custom admin views for service regulation
Separate from Django admin interface
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from venues.models import Venue
from caterers.models import Caterer
from accounts.models import CustomUser


@staff_member_required
def admin_dashboard(request):
    """Main dashboard for service regulation"""
    
    # Get statistics
    venue_stats = {
        'total': Venue.objects.count(),
        'active': Venue.objects.filter(is_active=True, is_suspended=False).count(),
        'inactive': Venue.objects.filter(is_active=False).count(),
        'suspended': Venue.objects.filter(is_suspended=True).count(),
    }
    
    caterer_stats = {
        'total': Caterer.objects.count(),
        'active': Caterer.objects.filter(is_active=True, is_suspended=False).count(),
        'inactive': Caterer.objects.filter(is_active=False).count(),
        'suspended': Caterer.objects.filter(is_suspended=True).count(),
    }
    
    # Recent suspensions (last 30 days)
    recent_venue_suspensions = Venue.objects.filter(
        is_suspended=True,
        suspended_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).order_by('-suspended_at')[:5]
    
    recent_caterer_suspensions = Caterer.objects.filter(
        is_suspended=True,
        suspended_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).order_by('-suspended_at')[:5]
    
    context = {
        'venue_stats': venue_stats,
        'caterer_stats': caterer_stats,
        'recent_venue_suspensions': recent_venue_suspensions,
        'recent_caterer_suspensions': recent_caterer_suspensions,
    }
    
    return render(request, 'core/admin_dashboard.html', context)


@staff_member_required
def venue_regulation(request):
    """Venue regulation page"""
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    venues = Venue.objects.select_related('provider__user', 'suspended_by')
    
    # Apply filters
    if status_filter == 'active':
        venues = venues.filter(is_active=True, is_suspended=False)
    elif status_filter == 'inactive':
        venues = venues.filter(is_active=False)
    elif status_filter == 'suspended':
        venues = venues.filter(is_suspended=True)
    
    # Apply search
    if search_query:
        venues = venues.filter(
            Q(name__icontains=search_query) |
            Q(provider__business_name__icontains=search_query) |
            Q(provider__user__username__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    venues = venues.order_by('-created_at')
    
    context = {
        'venues': venues,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_count': venues.count(),
    }
    
    return render(request, 'core/venue_regulation.html', context)


@staff_member_required
def caterer_regulation(request):
    """Caterer regulation page"""
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    caterers = Caterer.objects.select_related('provider__user', 'suspended_by')
    
    # Apply filters
    if status_filter == 'active':
        caterers = caterers.filter(is_active=True, is_suspended=False)
    elif status_filter == 'inactive':
        caterers = caterers.filter(is_active=False)
    elif status_filter == 'suspended':
        caterers = caterers.filter(is_suspended=True)
    
    # Apply search
    if search_query:
        caterers = caterers.filter(
            Q(provider__business_name__icontains=search_query) |
            Q(provider__user__username__icontains=search_query) |
            Q(specialty__icontains=search_query) |
            Q(service_area__icontains=search_query)
        )
    
    caterers = caterers.order_by('-created_at')
    
    context = {
        'caterers': caterers,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_count': caterers.count(),
    }
    
    return render(request, 'core/caterer_regulation.html', context)


@staff_member_required
def venue_detail(request, venue_id):
    """Detailed view of a venue for regulation"""
    venue = get_object_or_404(Venue, id=venue_id)
    
    # Get venue's booking history
    bookings = venue.bookings.all().order_by('-created_at')[:10]
    
    context = {
        'venue': venue,
        'bookings': bookings,
    }
    
    return render(request, 'core/venue_detail_admin.html', context)


@staff_member_required
def caterer_detail(request, caterer_id):
    """Detailed view of a caterer for regulation"""
    caterer = get_object_or_404(Caterer, id=caterer_id)
    
    # Get caterer's booking history
    bookings = caterer.bookings.all().order_by('-created_at')[:10]
    
    # Get menu packages and menu items
    packages = caterer.menu_packages.all().order_by('-created_at')[:5]
    menu_items = caterer.menu_items.select_related('course_category').order_by('-id')[:10]
    
    context = {
        'caterer': caterer,
        'bookings': bookings,
        'packages': packages,
        'menu_items': menu_items,
    }
    
    return render(request, 'core/caterer_detail_admin.html', context)


@staff_member_required
@require_POST
def suspend_venue(request, venue_id):
    """Suspend a venue"""
    venue = get_object_or_404(Venue, id=venue_id)
    
    try:
        data = json.loads(request.body)
        reason = data.get('reason', '').strip()
        
        if not reason:
            return JsonResponse({'success': False, 'error': 'Suspension reason is required'})
        
        venue.is_suspended = True
        venue.suspension_reason = reason
        venue.suspended_at = timezone.now()
        venue.suspended_by = request.user
        venue.save()
        
        messages.success(request, f'Venue "{venue.name}" has been suspended successfully.')
        
        return JsonResponse({
            'success': True,
            'message': f'Venue "{venue.name}" suspended successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@staff_member_required
@require_POST
def unsuspend_venue(request, venue_id):
    """Unsuspend a venue"""
    venue = get_object_or_404(Venue, id=venue_id)
    
    venue.is_suspended = False
    venue.suspension_reason = ''
    venue.suspended_at = None
    venue.suspended_by = None
    venue.save()
    
    messages.success(request, f'Venue "{venue.name}" has been unsuspended successfully.')
    
    return JsonResponse({
        'success': True,
        'message': f'Venue "{venue.name}" unsuspended successfully'
    })


@staff_member_required
@require_POST
def suspend_caterer(request, caterer_id):
    """Suspend a caterer"""
    caterer = get_object_or_404(Caterer, id=caterer_id)
    
    try:
        data = json.loads(request.body)
        reason = data.get('reason', '').strip()
        
        if not reason:
            return JsonResponse({'success': False, 'error': 'Suspension reason is required'})
        
        caterer.is_suspended = True
        caterer.suspension_reason = reason
        caterer.suspended_at = timezone.now()
        caterer.suspended_by = request.user
        caterer.save()
        
        messages.success(request, f'Caterer "{caterer.provider.business_name}" has been suspended successfully.')
        
        return JsonResponse({
            'success': True,
            'message': f'Caterer "{caterer.provider.business_name}" suspended successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@staff_member_required
@require_POST
def unsuspend_caterer(request, caterer_id):
    """Unsuspend a caterer"""
    caterer = get_object_or_404(Caterer, id=caterer_id)
    
    caterer.is_suspended = False
    caterer.suspension_reason = ''
    caterer.suspended_at = None
    caterer.suspended_by = None
    caterer.save()
    
    messages.success(request, f'Caterer "{caterer.provider.business_name}" has been unsuspended successfully.')
    
    return JsonResponse({
        'success': True,
        'message': f'Caterer "{caterer.provider.business_name}" unsuspended successfully'
    })


@staff_member_required
@require_POST  
def toggle_venue_active(request, venue_id):
    """Toggle venue active status"""
    venue = get_object_or_404(Venue, id=venue_id)
    
    venue.is_active = not venue.is_active
    venue.save()
    
    status = "activated" if venue.is_active else "deactivated"
    messages.success(request, f'Venue "{venue.name}" has been {status} successfully.')
    
    return JsonResponse({
        'success': True,
        'message': f'Venue "{venue.name}" {status} successfully',
        'is_active': venue.is_active
    })


@staff_member_required
@require_POST
def toggle_caterer_active(request, caterer_id):
    """Toggle caterer active status"""
    caterer = get_object_or_404(Caterer, id=caterer_id)
    
    caterer.is_active = not caterer.is_active
    caterer.save()
    
    status = "activated" if caterer.is_active else "deactivated"
    messages.success(request, f'Caterer "{caterer.provider.business_name}" has been {status} successfully.')
    
    return JsonResponse({
        'success': True,
        'message': f'Caterer "{caterer.provider.business_name}" {status} successfully',
        'is_active': caterer.is_active
    })
