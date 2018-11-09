from django.test import TestCase, RequestFactory, Client
from django.contrib.messages.storage.fallback import FallbackStorage
from django.urls import reverse, resolve
from .models import *
from .views import account_delete


def prepare(request):
    setattr(request, 'session', 'session')
    setattr(request, '_messages', FallbackStorage(request))


class AccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testadmin', email='testadmin@gmail.com', password='password', is_superuser=True)
        self.client = Client()
        self.client.login(username=self.user.username, password='password')
        self.fields = ['name', 'number', 'route', 'street', 'city', 'state', 'zip_code']
        self.values = ['Account', '20937520912209', '209375993', '123 Account Way', 'Greenville', 'SC', '29614']
        self.account = Account.objects.create(**{k: v for k, v in zip(self.fields, self.values)})

    def test_create(self):
        values = ['Test Name', '1234567890', '153920393', '123 Test', 'Greenville', 'SC', '29614']
        self.client.post(reverse('account_new'), {k: v for k, v in zip(self.fields, values)})

        account = Account.objects.last()
        self.assertEqual([getattr(account, k) for k in self.fields], values)

    def test_update(self):
        updates = {k: v for k, v in zip(self.fields, [getattr(self.account, x) for x in self.fields])}
        updates['route'] = '203949302'
        self.client.post(reverse('account_edit', args=[self.account.id]), updates)
        self.account.refresh_from_db()

        self.assertEqual([getattr(self.account, x) for x in self.fields], [updates[k] for k in self.fields])

    def test_delete(self):
        self.client.get(reverse('account_delete', args=[self.account.id]))

        accounts = Account.objects.filter(pk=self.account.id)
        self.assertEqual(accounts.count(), 0)


class CheckTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testadmin', email='testadmin@gmail.com', password='password', is_superuser=True)
        self.client = Client()
        self.client.login(username=self.user.username, password='password')
        self.fields = ['number', 'amount', 'date']
        self.values = ['3232', '55.22', '2018-11-08']
        self.account = Account.objects.create()
        self.check = Check.objects.create(**{**{k: v for k, v in zip(self.fields, self.values)}, **{'account': self.account, 'user': self.user}})

    def test_create(self):
        values = ['1234', '5233.22', '2018-10-05']
        self.client.post(reverse('account_check_new', args=[self.account.id]), {k: v for k, v in zip(self.fields, values)})

        check = Check.objects.last()
        self.assertEqual([str(getattr(check, k)) for k in self.fields], values)

    def test_update(self):
        updates = {k: v for k, v in zip(self.fields, [getattr(self.check, x) for x in self.fields])}
        updates['amount'] = '999.99'
        self.client.post(reverse('check_edit', args=[self.check.id]), updates)
        self.check.refresh_from_db()

        self.assertEqual([str(getattr(self.check, x)) for x in self.fields], [updates[k] for k in self.fields])

    def test_delete(self):
        self.client.get(reverse('check_delete', args=[self.check.id]))

        checks = Check.objects.filter(pk=self.check.id)
        self.assertEqual(checks.count(), 0)


class CompanyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testadmin', email='testadmin@gmail.com', password='password', is_superuser=True)
        self.client = Client()
        self.client.login(username=self.user.username, password='password')
        self.fields = ['name', 'desc', 'wait_period', 'late_fee', 'street', 'city', 'state', 'zip_code']
        self.values = ['Test Company', 'Coolio', '15', '55.50', '123 Company Way', 'Greenville', 'SC', '29302']
        self.company = Company.objects.create(**{k: v for k, v in zip(self.fields, self.values)})

    def test_create(self):
        values = ['Test 2', 'Another Desc', '20', '1.20', '10 Blah Road', 'McDonough', 'GA', '39320']
        self.client.post(reverse('company_new'), {k: v for k, v in zip(self.fields, values)})

        company = Company.objects.last()
        self.assertEqual([str(getattr(company, k)) for k in self.fields], values)

    def test_update(self):
        updates = {k: v for k, v in zip(self.fields, [getattr(self.company, x) for x in self.fields])}
        updates['name'] = 'Changed Name'
        self.client.post(reverse('company_edit', args=[self.company.id]), updates)
        self.company.refresh_from_db()

        self.assertEqual([str(getattr(self.company, x)) for x in self.fields], [updates[k] for k in self.fields])

    def test_delete(self):
        self.client.get(reverse('company_delete', args=[self.company.id]))

        companies = Company.objects.filter(pk=self.company.id)
        self.assertEqual(companies.count(), 0)
