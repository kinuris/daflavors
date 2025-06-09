from django.urls import path
from . import views, admin_views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('search/', views.search, name='search'),
    path('faq/', views.faq, name='faq'),
    
    # Custom Admin Interface
    path('admin-panel/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/venues/', admin_views.venue_regulation, name='venue_regulation'),
    path('admin-panel/caterers/', admin_views.caterer_regulation, name='caterer_regulation'),
    path('admin-panel/venues/<int:venue_id>/', admin_views.venue_detail, name='venue_detail_admin'),
    path('admin-panel/caterers/<int:caterer_id>/', admin_views.caterer_detail, name='caterer_detail_admin'),
    
    # AJAX endpoints for regulation actions
    path('admin-panel/venues/<int:venue_id>/suspend/', admin_views.suspend_venue, name='suspend_venue'),
    path('admin-panel/venues/<int:venue_id>/unsuspend/', admin_views.unsuspend_venue, name='unsuspend_venue'),
    path('admin-panel/venues/<int:venue_id>/toggle-active/', admin_views.toggle_venue_active, name='toggle_venue_active'),
    path('admin-panel/caterers/<int:caterer_id>/suspend/', admin_views.suspend_caterer, name='suspend_caterer'),
    path('admin-panel/caterers/<int:caterer_id>/unsuspend/', admin_views.unsuspend_caterer, name='unsuspend_caterer'),
    path('admin-panel/caterers/<int:caterer_id>/toggle-active/', admin_views.toggle_caterer_active, name='toggle_caterer_active'),
]
