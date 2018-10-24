from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .decorators import logout_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from .models import Check, Account, Company
from django.core.paginator import Paginator
from django.db.models import Q


def process_params(objects, params, filters):
    if params.get('search'):
        search = params.get('search')
        q = Q(**{filters[0]: search})
        for f in filters[1:]:
            q |= Q(**{f: search})
        objects = objects.filter(q)
    objects = objects.order_by(params.get('sort') if params.get('sort') else '-date_created')
    per = params.get('per') if params.get('per') else 10
    page = params.get('page') if params.get('page') else 1
    paginator = Paginator(objects, per)
    return paginator.get_page(page)


def process_context(request, vars):
    context = request.dict()
    context.update(vars)
    return context


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
    checks = process_params(checks, request.GET, ['account__name__icontains'])
    context = process_context(request.GET, {'checks': checks})
    return render(request, 'checks/index.html', context)


@login_required
def check_edit(request, check_id):
    check = get_object_or_404(Check, pk=check_id)
    if request.method == 'POST':
        form = CheckEditForm(request.POST, instance=check)
        if form.is_valid():
            form.save()
            messages.success(request, 'Check successfully updated!')
            return redirect('check_index')
    else:
        form = CheckEditForm(instance=check)
    return render(request, 'checks/edit.html', {'form': form, 'check': check})


@login_required
def check_new(request):
    messages.info(request, 'Please select an account to add a check.')
    return redirect(account_index)


@login_required
def check_delete(request, check_id):
    check = get_object_or_404(Check, pk=check_id)
    check.delete()
    messages.success(request, 'Check has been deleted.')
    return redirect('check_index')


@login_required
def account_index(request):
    accounts = Account.objects.filter(company=request.user.profile.company)
    accounts = process_params(accounts, request.GET, ['name__icontains', 'number__icontains'])
    context = process_context(request.GET, {'accounts': accounts})
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
    return render(request, 'accounts/new.html', {'form': form})


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
    return render(request, 'accounts/new.html', {'form': form, 'account': account})


@login_required
def account_delete(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    account.delete()
    messages.success(request, 'Account "{}" has been deleted.'.format(account.name))
    return redirect('account_index')


@login_required
def account_check_index(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    checks = account.check_set.all()
    checks = process_params(checks, request.GET, [''])
    context = process_context(request.GET, {'checks': checks, 'account': account})
    return render(request, 'checks/index.html', context)


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

    return render(request, 'checks/new.html', {'form': form})


@login_required
def company_index(request):
    companies = Company.objects.all()
    companies = process_params(companies, request.GET, ['name__icontains'])
    context = process_context(request.GET, {'companies': companies})
    return render(request, 'companies/index.html', context)


@logout_required
def company_choose(request):
    companies = Company.objects.all()
    companies = process_params(companies, request.GET, ['name__icontains'])
    context = process_context(request.GET, {'companies': companies})
    return render(request, 'companies/choose.html', context)


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

    return render(request, 'companies/new.html', {'form': form})


@login_required
def company_edit(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company "{}" successfully updated!'.format(company))
            return redirect('company_index')
    else:
        form = CompanyForm(instance=company)
    return render(request, 'companies/new.html', {'form': form, 'company': company})


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

    return render(request, 'register.html', {'form': form, 'company': company})
