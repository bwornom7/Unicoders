from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .forms import RegistrationForm

def index(request):
  return render(request, 'index.html')

def register(request):
  if request.method == 'POST':
    f = RegistrationForm(request.POST)
    if f.is_valid():
      
      messages.success(request, 'Account successfully created!')
      return redirect('/')
  else:
    f = RegistrationForm()
  return render(request, 'register.html', { 'form': f })