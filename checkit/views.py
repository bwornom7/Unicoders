from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .forms import ProfileForm, UserForm, CheckForm
from .models import Check

def index(request):
  return render(request, 'index.html')

def register(request):
  if request.user.is_authenticated:
    messages.warning(request, 'You are already logged in.')
    return redirect('index')

  if request.method == 'POST':
    user_form = UserForm(request.POST)
    if user_form.is_valid():
      user = user_form.save()

      login(request, user, backend='django.contrib.auth.backends.ModelBackend')
      
      messages.success(request, 'Account successfully created!')
      return redirect('index')
    else:
      messages.warning(request, 'Please correct the error(s) below.')
  else:
    user_form = UserForm()

  return render(request, 'register.html', { 'user_form': user_form })

@login_required
def logout_user(request):
  logout(request)
  messages.success(request, 'You have successfully logged out.')
  return redirect('index')

@login_required
def check_index(request):
  checks = Check.objects.filter(user=request.user)
  return render(request, 'checks/index.html', { 'checks': checks })

@login_required
def check_new(request):
  if request.method == 'POST':
    form = CheckForm(request.POST)
    if form.is_valid():
      check = form.save(commit=False)
      check.user = request.user
      check.save()
      messages.success(request, 'Successfully added new check!')
      return redirect('check_index')
  else:
    form = CheckForm()

  return render(request, 'checks/new.html', { 'form': form })

@login_required
def check_edit(request):
  pass