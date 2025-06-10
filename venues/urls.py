from django.urls import path
from . import views

app_name = 'venues'

urlpatterns = [
    path('', views.venue_list, name='list'),
    path('<int:venue_id>/', views.venue_detail, name='detail'),
    path('create/', views.venue_create, name='create'),
    path('<int:venue_id>/update/', views.venue_update, name='update'),
    path('<int:venue_id>/delete/', views.venue_delete, name='delete'),
]
