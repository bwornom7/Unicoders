from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('checks/', views.check_index, name='check_index'),
    path('checks/new', views.check_new, name='check_new'),
    path('checks/<int:id>/', views.check_edit, name='check_edit'),
]