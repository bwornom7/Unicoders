from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from .decorators import logout_required, admin_required, supervisor_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from .models import Check, Account, Company
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse

from io import StringIO, BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template

from functools import reduce
from operator import ior
from chartit import DataPool, Chart
import logging
import leather

logger = logging.getLogger(__name__)


def get_per(user):
    return user.profile.records_per_page if user.is_authenticated else 10


def process_params(user, objects, params, filters, default_sort='-date_created'):
    if params.get('search'):
        search = params.get('search')
        q = reduce(ior, [Q(**{x: search}) for x in filters])
        objects = objects.filter(q)
    objects = objects.order_by(params.get('sort') if params.get('sort') else default_sort)
    per = params.get('per') if params.get('per') else get_per(user)
    page = params.get('page') if params.get('page') else 1
    paginator = Paginator(objects, per)
    return paginator.get_page(page)


def process_context(request, vars, default_sort='-date_created'):
    context = request.dict()
    context.update(vars)
    if 'sort' not in context: context['sort'] = default_sort
    return context


def pdf_from_html(request, html, error_redirect, error_args):
    result = BytesIO()
    pdf = pisa.pisaDocument(StringIO(html), dest=result)
    if not pdf.err:
        logger.info('Letter PDF generated')
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    else:
        messages.warning(request, 'Error generating letter PDF.')
        return redirect(error_redirect, **error_args)


def generate_letter_chart(id, checks, start_date, end_date):
    letter = 'letter{}_date'.format(id)
    ds = DataPool(
        series=[{
            'options': {
                'source': checks
                          .filter(**{'{}__range'.format(letter): (start_date, end_date)})
                          .values(letter)
                          .annotate(count=Count(letter))
                          .exclude(**{'{}__isnull'.format(letter): True})
                          .order_by(letter),
            },
            'terms': [letter, 'count']
        }]
    )

    return Chart(
        datasource=ds,
        series_options=[{
            'options': {
                'type': 'column',
                'stacking': False
            },
            'terms': {
                letter: ['count']
            }
        }],
        chart_options={
            'title': {
                'text': 'Generated Warning Letter {}'.format(id)
            },
            'xAxis': {
                'title': {
                    'text': 'Date'
                }
            }
        }
    )


def handler404(request, exception, template_name='404.html'):
    response = render(request, template_name)
    response.status_code = 404
    return response


def handler500(request, template_name='500.html'):
    response = render(request, template_name)
    response.status_code = 500
    return response


def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    logger.info('User {} successfully logged out'.format(request.user))
    return redirect('index')


@login_required
def check_index(request):
    if request.user.profile.admin_not_simulating():
        checks = Check.objects.all()
        heading = 'All Checks'
    elif request.user.profile.supervisor_up():
        checks = Check.objects.filter(user__profile__company=request.user.profile.company)
        heading = 'Checks for Company: {}'.format(request.user.profile.company)
    else:
        checks = Check.objects.filter(user=request.user)
        heading = 'Your Checks'
    checks = process_params(request.user, checks, request.GET, ['account__name__icontains'])
    context = process_context(request.GET, {'checks': checks, 'heading': heading})
    return render(request, 'checks/index.html', context)


@login_required
def check_edit(request, check_id):
    check = get_object_or_404(Check, pk=check_id)
    if request.method == 'POST':
        form = CheckEditForm(request.POST, instance=check)
        if form.is_valid():
            form.save()
            logger.info('Check #{} has been edited'.format(check.number))
            messages.success(request, 'Check successfully updated!')
            return redirect('check_index')
    else:
        form = CheckEditForm(instance=check)
    return render(request, 'checks/edit.html', {'form': form, 'check': check})


@login_required
def check_pay(request, check_id):
    check = get_object_or_404(Check, pk=check_id)
    if request.method == 'POST':
        form = CheckPayForm(request.POST)
        if form.is_valid():
            message = check.pay(form.cleaned_data['amount'])
            messages.success(request, message)
            return redirect('check_index')
    else:
        form = CheckPayForm()
    return render(request, 'checks/pay.html', {'form': form, 'check': check})


@login_required
@supervisor_required
def check_delete(request, check_id):
    check = get_object_or_404(Check, pk=check_id)
    check.delete()
    logger.info('Check #{} has been deleted'.format(check.number))
    messages.success(request, 'Check has been deleted.')
    return redirect('check_index')


@login_required
def account_index(request):
    if request.user.profile.admin_not_simulating():
        accounts = Account.objects.all()
        heading = 'All Accounts'
    else:
        accounts = Account.objects.filter(company=request.user.profile.company)
        heading = 'Accounts for Company: {}'.format(request.user.profile.company)
    accounts = process_params(request.user, accounts, request.GET, ['name__icontains', 'number__icontains', 'route__icontains', 'street__icontains'])
    context = process_context(request.GET, {'accounts': accounts, 'heading': heading})
    return render(request, 'accounts/index.html', context)


@login_required
def account_new(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.company = request.user.profile.company
            account.save()
            logger.info('Successfully created new account')
            messages.success(request, 'Successfully created new account!')
            if request.POST.get('again'):
                return redirect('account_new')
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
            logger.info('Account "{}" successfully updated'.format(account.name))
            messages.success(request, 'Account "{}" successfully updated!'.format(account.name))
            return redirect('account_index')
    else:
        form = AccountForm(instance=account)
    return render(request, 'accounts/new.html', {'form': form, 'account': account})


@login_required
@supervisor_required
def account_delete(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    account.delete()
    logger.info('Account "{}" has been deleted.'.format(account.name))
    messages.success(request, 'Account "{}" has been deleted.'.format(account.name))
    return redirect('account_index')


@login_required
@supervisor_required
def account_check_index(request, account_id):
    account = get_object_or_404(Account, pk=account_id)
    checks = account.check_set.all()
    checks = process_params(request.user, checks, request.GET, [''])
    heading = 'Checks for Account: {}'.format(account)
    context = process_context(request.GET, {'checks': checks,
                                            'heading': heading,
                                            'back_link': 'account_index',
                                            'back_name': 'All Accounts'})
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
            logger.info('Successfully added check #{}'.format(check.number))
            messages.success(request, 'Successfully added new check!')
            if request.POST.get('again'):
                return redirect(account_check_new, account_id)
            return redirect(account_index)
    else:
        form = CheckForm()

    return render(request, 'checks/new.html', {'form': form, 'account': account})


@login_required
@admin_required
def company_index(request):
    companies = Company.objects.all()
    companies = process_params(request.user, companies, request.GET, ['name__icontains'])
    context = process_context(request.GET, {'companies': companies, 'heading': 'All Companies'})
    return render(request, 'companies/index.html', context)


@logout_required
def company_choose(request):
    companies = Company.objects.all()
    companies = process_params(request.user, companies, request.GET, ['name__icontains'])
    context = process_context(request.GET, {'companies': companies})
    return render(request, 'companies/choose.html', context)


@login_required
@admin_required
def company_new(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info('Successfully added company: {}'.format(form.cleaned_data['name']))
            messages.success(request, 'Successfully added company!')
            return redirect(company_index)
    else:
        form = CompanyForm()

    return render(request, 'companies/new.html', {'form': form})


@login_required
@admin_required
def company_edit(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            logger.info('Company "{}" successfully updated'.format(company))
            messages.success(request, 'Company "{}" successfully updated!'.format(company))
            return redirect('company_index')
    else:
        form = CompanyForm(instance=company)
    return render(request, 'companies/new.html', {'form': form, 'company': company})


@login_required
@admin_required
def company_delete(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    company.delete()
    logger.info('Company {} has been deleted.'.format(company))
    messages.success(request, 'Company {} has been deleted.'.format(company))
    return redirect('company_index')


@login_required
@admin_required
def company_simulate(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    request.user.profile.simulate(company)
    return redirect('company_index')


@login_required
@admin_required
def company_stop_simulate(request):
    request.user.profile.stop_simulate()
    return redirect('company_index')


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

            logger.info('Account {} created'.format(user.profile.full_name()))
            messages.success(request, 'Account successfully created!')
            return redirect('index')
    else:
        form = UserForm()

    return render(request, 'register.html', {'form': form, 'company': company})


@login_required
def letter(request):
    checks = Check.objects.filter(user=request.user)
    company = request.user.profile.company

    if not len([x.current_letter() for x in checks if x.current_letter() >= 1]):
        messages.info(request, 'No letters to generate.')
        return redirect('check_index')

    template = get_template('letters/letters.html')
    context = {'checks': checks, 'company': company, 'user': request.user}
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(StringIO(html), dest=result)
    if not pdf.err:
        logger.info('Letters generated')
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    else:
        messages.error(request, 'Error generating letters PDF.')
        return redirect('check_index')


@login_required
def check_letter1(request, check_id):
    check = get_object_or_404(Check, pk=check_id)
    company = request.user.profile.company
    template = get_template('letters/letter1.html')
    context = {'check': check, 'company': company, 'user': request.user}
    html = template.render(context)
    return pdf_from_html(request, html, check_edit, {'check_id': check_id})


@login_required
def check_letter2(request, check_id):
    check = get_object_or_404(Check, pk=check_id)
    company = request.user.profile.company
    template = get_template('letters/letter2.html')
    context = {'check': check, 'company': company, 'user': request.user}
    html = template.render(context)
    return pdf_from_html(request, html, check_edit, {'check_id': check_id})


@login_required
def check_letter3(request, check_id):
    check = get_object_or_404(Check, pk=check_id)
    company = request.user.profile.company
    template = get_template('letters/letter3.html')
    context = {'check': check, 'company': company, 'user': request.user}
    html = template.render(context)
    return pdf_from_html(request, html, check_edit, {'check_id': check_id})


@login_required
@supervisor_required
def user_index(request):
    if request.user.profile.admin_not_simulating():
        users = User.objects.all()
        heading = 'All Users'
    else:
        users = User.objects.filter(profile__company=request.user.profile.company)
        heading = 'Users for Company: {}'.format(request.user.profile.company)
    users = process_params(request.user, users, request.GET, ['first_name__icontains', 'last_name__icontains', 'email__icontains', 'username__icontains'], '-date_joined')
    context = process_context(request.GET, {'users': users, 'heading': heading}, '-date_joined')
    return render(request, 'users/index.html', context)


@login_required
@supervisor_required
def user_check_index(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    checks = user.check_set.all()
    checks = process_params(request.user, checks, request.GET, [''])
    heading = 'Checks for User: {}'.format(user.profile.full_name())
    context = process_context(request.GET, {'checks': checks,
                                            'heading': heading,
                                            'back_link': 'user_index',
                                            'back_name': 'All Users'})
    return render(request, 'checks/index.html', context)


@login_required
@supervisor_required
def user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            logger.info('User "{}" successfully updated'.format(user))
            messages.success(request, 'User "{}" successfully updated!'.format(user))
            return redirect('user_index')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileForm(instance=user.profile)
    return render(request, 'users/edit.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
@admin_required
def user_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    logger.info('User "{}" has been deleted.'.format(user))
    messages.success(request, 'User "{}" has been deleted.'.format(user))
    return redirect('user_index')


@login_required
def report(request):
    if request.user.profile.admin_not_simulating():
        checks = Check.objects.all()
        heading = 'Reports for All Checks'
    elif request.user.profile.supervisor_up():
        checks = Check.objects.filter(user__profile__company=request.user.profile.company)
        heading = 'Reports for Company: {}'.format(request.user.profile.company)
    else:
        checks = Check.objects.filter(user=request.user)
        heading = 'Reports for Your Checks'

    end_date = datetime.datetime.now().date()
    start_date = end_date - datetime.timedelta(days=7)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
    else:
        form = ReportForm()
    logger.info(start_date)

    copy = checks.filter(date_created__date__range=(start_date, end_date))
    paid = len([c for c in copy if c.paid])
    not_paid = len(copy) - paid
    data = [
        (paid, 'Checks Paid'),
        (not_paid, 'Checks Not Paid')
    ]
    chart = leather.Chart('Checks Processed by CheckIt')
    chart.add_bars(data)
    chart.to_svg('checkit/static/img/bars.svg')

    letter_charts = []
    for i in range(3):
        letter_charts.append(generate_letter_chart(i + 1, checks, start_date, end_date))

    return render(request, 'report/report.html', {'letter_charts': letter_charts, 'form': form, 'heading': heading})


@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        user_form = ProfileUserForm(request.POST, instance=user)
        profile_form = ProfileEditForm(request.POST, instance=user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            logger.info('Profile "{}" successfully updated'.format(user))
            messages.success(request, 'Profile successfully updated!')
            return redirect('index')
    else:
        user_form = ProfileUserForm(instance=user)
        profile_form = ProfileEditForm(instance=user.profile)
    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})