from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Booking Routes
    path('', views.booking_list, name='list'),
    path('create/', views.booking_create, name='create'),
    path('<int:booking_id>/', views.booking_detail, name='detail'),
    path('<int:booking_id>/update/', views.booking_update, name='update'),
    path('<int:booking_id>/cancel/', views.booking_cancel, name='cancel'),
    
    # Menu Selection Routes
    path('<int:booking_id>/menu-select/', views.menu_select, name='menu_select'),
    path('<int:booking_id>/course-select/', views.course_select, name='course_select'),
    
    # Quote Routes
    path('<int:booking_id>/quote/create/', views.quote_create, name='quote_create'),
    path('<int:booking_id>/quote/<int:quote_id>/', views.quote_detail, name='quote_detail'),
    path('<int:booking_id>/quote/<int:quote_id>/update/', views.quote_update, name='quote_update'),
    path('<int:booking_id>/quote/<int:quote_id>/send/', views.quote_send, name='quote_send'),
    path('<int:booking_id>/quote/<int:quote_id>/respond/', views.quote_respond, name='quote_respond'),
    
    # Payment Routes
    path('<int:booking_id>/payment/create/', views.payment_create, name='payment_create'),
    path('<int:booking_id>/payment/<int:payment_id>/confirm/', views.payment_confirm, name='payment_confirm'),
    
    # AJAX endpoints
    path('ajax/menu-packages/', views.get_menu_packages, name='get_menu_packages'),
]
