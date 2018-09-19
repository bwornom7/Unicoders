from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .forms import UserForm, CheckForm, AccountForm
from .models import Check, Account
from django.core.paginator import Paginator

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
def check_edit(request, check_id):
  check = get_object_or_404(Check, pk=check_id)

@login_required
def check_new(request):
  messages.info(request, 'Please select an account to add a check.')
  return redirect(account_index)

@login_required
def account_index(request):
  accounts = Account.objects.all()
  return render(request, 'accounts/index.html', { 'accounts': accounts })

@login_required
def account_new(request):
  if request.method == 'POST':
    form = AccountForm(request.POST)
    if form.is_valid():
      form.save()
      messages.success(request, 'Successfully created new account!')
      return redirect('account_index')
  else:
    form = AccountForm()

  return render(request, 'accounts/new.html', { 'form': form })

@login_required
def account_edit(request, account_id):
  account = get_object_or_404(Account, pk=account_id)

@login_required
def account_check_index(request, account_id):
  account = get_object_or_404(Account, pk=account_id)
  return render(request, 'accounts/check_index.html', { 'account': account })

@login_required
def account_check_new(request, account_id): 
  account = get_object_or_404(Account, pk=account_id)
  if request.method == 'POST':
    form = CheckForm(request.POST)
    if form.is_valid():
      check = form.save(commit=False)
      check.user = request.user
      check.account = account
      check.save()
      messages.success(request, 'Successfully added new check!')
      return redirect(account_check_index, account.id)
  else:
    form = CheckForm()

  return render(request, 'checks/new.html', { 'form': form })