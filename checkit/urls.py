from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('checks/', views.check_index, name='check_index'),
    path('checks/new/', views.check_new, name='check_new'),
    path('checks/<int:check_id>/', views.check_edit, name='check_edit'),
    path('accounts/', views.account_index, name='account_index'),
    path('accounts/new/', views.account_new, name='account_new'),
    path('accounts/<int:account_id>/', views.account_edit, name='account_edit'),
    path('accounts/<int:account_id>/checks/', views.account_check_index, name='account_check_index'),
    path('accounts/<int:account_id>/checks/new/', views.account_check_new, name='account_check_new'),
]