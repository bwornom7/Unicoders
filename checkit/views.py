from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import logout_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .forms import UserForm, CheckForm, AccountForm, CompanyForm
from .models import Check, Account, Company
from django.core.paginator import Paginator
from django.db.models import Q

def index(request):
  return render(request, 'index.html')

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
  accounts = Account.objects.filter(company=request.user.profile.company)
  search = request.GET.get('search')
  if search:
    accounts = accounts.filter(Q(name__icontains=search) | Q(number__icontains=search))
  context = request.GET.dict()
  context.update({ 'accounts': accounts })
  return render(request, 'accounts/index.html', context)

@login_required
def account_new(request):
  if request.method == 'POST':
    form = AccountForm(request.POST)
    if form.is_valid():
      account = form.save(commit=False)
      account.company = request.user.profile.company
      account.save()
      messages.success(request, 'Successfully created new account!')
      return redirect('account_index')
  else:
    form = AccountForm()

  return render(request, 'accounts/new.html', { 'form': form })

@login_required
def account_edit(request, account_id):
  account = get_object_or_404(Account, pk=account_id)
  if request.method == 'POST':
    form = AccountForm(request.POST, instance=account)
    if form.is_valid():
      form.save()
      messages.success(request, 'Account "{}" successfully updated!'.format(account.name))
      return redirect('account_index')
  else:
    form = AccountForm(instance=account)
  return render(request, 'accounts/new.html', { 'form': form, 'account': account })

@login_required
def account_delete(request, account_id):
  account = get_object_or_404(Account, pk=account_id)
  account.delete()
  messages.success(request, 'Account "{}" has been deleted.'.format(account.name))
  return redirect('account_index')

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

@login_required
def company_index(request):
  companies = Company.objects.all()
  return render(request, 'companies/index.html', { 'companies': companies })

@logout_required
def company_choose(request):
  companies = Company.objects.all()
  return render(request, 'companies/choose.html', { 'companies': companies })

@login_required
def company_new(request):
  if request.method == 'POST':
    form = CompanyForm(request.POST)
    if form.is_valid():
      form.save()
      messages.success(request, 'Successfully added company!')
      return redirect(company_index)
  else:
    form = CompanyForm()

  return render(request, 'companies/new.html', { 'form': form })

@login_required
def company_edit(request, company_id):
  company = get_object_or_404(Company, pk=company_id)

@logout_required
def register(request, company_id):
  company = get_object_or_404(Company, pk=company_id)

  if request.method == 'POST':
    form = UserForm(request.POST)
    if form.is_valid():
      user = form.save()
      user.profile.company = company
      user.save()

      login(request, user, backend='django.contrib.auth.backends.ModelBackend')
      
      messages.success(request, 'Account successfully created!')
      return redirect('index')
  else:
    form = UserForm()

  return render(request, 'register.html', { 'form': form, 'company': company })