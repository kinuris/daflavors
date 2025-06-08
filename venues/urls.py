from django.urls import path
from . import views

app_name = 'venues'

urlpatterns = [
    path('', views.venue_list, name='venue_list'),
    path('', views.venue_list, name='list'),
    path('<int:venue_id>/', views.venue_detail, name='venue_detail'),
    path('<int:venue_id>/', views.venue_detail, name='detail'),
    path('create/', views.venue_create, name='venue_create'),
    path('create/', views.venue_create, name='create'),
    path('<int:venue_id>/update/', views.venue_update, name='venue_update'),
    path('<int:venue_id>/update/', views.venue_update, name='update'),
    path('<int:venue_id>/delete/', views.venue_delete, name='venue_delete'),
    path('<int:venue_id>/delete/', views.venue_delete, name='delete'),
]
