from django.urls import path
from . import views

app_name = 'caterers'

urlpatterns = [
    path('', views.caterer_list, name='caterer_list'),
    path('', views.caterer_list, name='list'),
    path('<int:caterer_id>/', views.caterer_detail, name='caterer_detail'),
    path('<int:caterer_id>/', views.caterer_detail, name='detail'),
    path('create/', views.caterer_create, name='caterer_create'),
    path('create/', views.caterer_create, name='create'),
    path('<int:caterer_id>/update/', views.caterer_update, name='caterer_update'),
    path('<int:caterer_id>/update/', views.caterer_update, name='update'),
    path('<int:caterer_id>/delete/', views.caterer_delete, name='caterer_delete'),
    path('<int:caterer_id>/delete/', views.caterer_delete, name='delete'),
    path('<int:caterer_id>/menus/', views.menu_list, name='menu_list'),
    path('<int:caterer_id>/menus/', views.menu_list, name='menus'),
    path('<int:caterer_id>/menus/create/', views.menu_create, name='menu_create'),
    path('<int:caterer_id>/menus/create/', views.menu_create, name='menu_add'),
    path('<int:caterer_id>/menus/<int:menu_id>/', views.menu_detail, name='menu_detail'),
    path('<int:caterer_id>/menus/<int:menu_id>/', views.menu_detail, name='menu'),
    path('<int:caterer_id>/menus/<int:menu_id>/update/', views.menu_update, name='menu_update'),
    path('<int:caterer_id>/menus/<int:menu_id>/update/', views.menu_update, name='menu_edit'),
    path('<int:caterer_id>/menus/<int:menu_id>/delete/', views.menu_delete, name='menu_delete'),
    path('<int:caterer_id>/menus/<int:menu_id>/delete/', views.menu_delete, name='menu_remove'),
]
