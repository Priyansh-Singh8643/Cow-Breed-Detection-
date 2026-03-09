from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.user_dashboard_view, name='user_dashboard'),
    path('admin-dashboard/', views.custom_admin_view, name='custom_admin'),
    path('admin-dashboard/add/', views.add_breed_view, name='add_breed'),
    path('admin-dashboard/edit/<int:breed_id>/', views.edit_breed_view, name='edit_breed'),
    path('admin-dashboard/delete/<int:breed_id>/', views.delete_breed_view, name='delete_breed'),
]
