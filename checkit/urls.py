from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('checks/', views.check_index, name='check_index'),
    path('checks/<int:check_id>/', views.check_edit, name='check_edit'),
    path('checks/<int:check_id>/delete/', views.check_delete, name='check_delete'),
    path('checks/<int:check_id>/letter1/', views.check_letter1, name='check_letter1'),
    path('checks/<int:check_id>/letter2/', views.check_letter2, name='check_letter2'),
    path('checks/<int:check_id>/letter3/', views.check_letter3, name='check_letter3'),
    path('checks/<int:check_id>/pay/', views.check_pay, name='check_pay'),
    path('accounts/', views.account_index, name='account_index'),
    path('accounts/new/', views.account_new, name='account_new'),
    path('accounts/<int:account_id>/', views.account_edit, name='account_edit'),
    path('accounts/<int:account_id>/delete/', views.account_delete, name='account_delete'),
    path('accounts/<int:account_id>/checks/', views.account_check_index, name='account_check_index'),
    path('accounts/<int:account_id>/checks/new/', views.account_check_new, name='account_check_new'),
    path('companies/', views.company_index, name='company_index'),
    path('companies/new/', views.company_new, name='company_new'),
    path('companies/choose/', views.company_choose, name='company_choose'),
    path('companies/<int:company_id>/', views.company_edit, name='company_edit'),
    path('companies/<int:company_id>/delete', views.company_delete, name='company_delete'),
    path('companies/<int:company_id>/register/', views.register, name='register'),
    path('letters/', views.letter, name='letter'),
    path('users/', views.user_index, name='user_index'),
    path('users/<int:user_id>/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete', views.user_delete, name='user_delete'),
    path('profile/', views.profile, name='profile')
]