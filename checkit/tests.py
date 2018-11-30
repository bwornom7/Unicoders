"""
This file contains all of the tests for the system.
Tests include creating, updating, and deleting.
"""


from django.test import TestCase, RequestFactory, Client
from django.contrib.messages.storage.fallback import FallbackStorage
from django.urls import reverse, resolve
from .models import *
from .views import account_delete


class AccountTests(TestCase):
    """
    Account tests for the system. Tests to make sure
    fields are working correctly, and actions like
    create, update, and delete perform correctly.
    """

    def setUp(self):
        """Runs the setup before every other test in the AccountTests"""
        self.user = User.objects.create_user(username='testadmin', email='testadmin@gmail.com', password='password', is_superuser=True)
        self.client = Client()
        self.client.login(username=self.user.username, password='password')
        self.fields = ['name', 'number', 'route', 'street', 'city', 'state', 'zip_code']
        self.values = ['Account', '20937520912209', '209375993', '123 Account Way', 'Greenville', 'SC', '29614']
        self.account = Account.objects.create(**{k: v for k, v in zip(self.fields, self.values)})

    def test_create(self):
        """Tests the creation of an account, and makes sure fields are correct"""
        # Start values, and send a post request to the new account page
        values = ['Test Name', '1234567890', '153920393', '123 Test', 'Greenville', 'SC', '29614']
        self.client.post(reverse('account_new'), {k: v for k, v in zip(self.fields, values)})

        # Make sure the most recent account has the posted values
        account = Account.objects.last()
        self.assertEqual([getattr(account, k) for k in self.fields], values)

    def test_update(self):
        """Tests the update of an account, making sure fields are correct"""
        # Send the updates to the account edit page
        updates = {k: v for k, v in zip(self.fields, [getattr(self.account, x) for x in self.fields])}
        updates['route'] = '203949302'
        self.client.post(reverse('account_edit', args=[self.account.id]), updates)

        # Make sure updates have been applied
        self.account.refresh_from_db()
        self.assertEqual([getattr(self.account, x) for x in self.fields], [updates[k] for k in self.fields])

    def test_delete(self):
        """Tests the delete of an account"""
        # Send a request to delete
        self.client.get(reverse('account_delete', args=[self.account.id]))

        # Make sure the account doesn't show up
        accounts = Account.objects.filter(pk=self.account.id)
        self.assertEqual(accounts.count(), 0)


class CheckTests(TestCase):
    """
    Check tests for the system. Tests to make sure
    fields are working correctly, and actions like
    create, update, and delete perform correctly.
    """

    def setUp(self):
        """Runs the setup before every other test in the CheckTests"""
        self.user = User.objects.create_user(username='testadmin', email='testadmin@gmail.com', password='password', is_superuser=True)
        self.client = Client()
        self.client.login(username=self.user.username, password='password')
        self.fields = ['number', 'amount', 'date']
        self.values = ['3232', '55.22', '2018-11-08']
        self.account = Account.objects.create(name='Test Account')
        self.check = Check.objects.create(**{**{k: v for k, v in zip(self.fields, self.values)}, **{'account': self.account, 'user': self.user}})

    def test_create(self):
        """Tests the creation of a check, and makes sure fields are correct"""
        # Send a post request to the new check page
        values = ['1234', '5233.22', '10/05/2018']
        self.client.post(reverse('account_check_new', args=[self.account.id]), {k: v for k, v in zip(self.fields, values)})
        values[2] = '2018-10-05'  # Adjust for the form tweaked date format

        # Make sure the check is there and that fields are correct
        check = Check.objects.last()
        self.assertEqual([str(getattr(check, k)) for k in self.fields], values)

    def test_update(self):
        """Tests the update of a check, and makes sure updated fields are correct"""
        # Send a request to update amount field
        updates = {k: v for k, v in zip(self.fields, [getattr(self.check, x) for x in self.fields])}
        updates['amount'] = '999.99'
        updates['date'] = '11/08/2018'
        self.client.post(reverse('check_edit', args=[self.check.id]), updates)
        updates['date'] = '2018-11-08'

        # Make sure the update has been applied
        self.check.refresh_from_db()
        self.assertEqual([str(getattr(self.check, x)) for x in self.fields], [updates[k] for k in self.fields])

    def test_delete(self):
        """Tests the delete of a check"""
        # Send a request to delete
        self.client.get(reverse('check_delete', args=[self.check.id]))

        # Make sure the check has been deleted
        checks = Check.objects.filter(pk=self.check.id)
        self.assertEqual(checks.count(), 0)


class CompanyTests(TestCase):
    """
    Company tests for the system. Tests to make sure
    fields are working correctly, and actions like
    create, update, and delete perform correctly.
    """

    def setUp(self):
        """Runs the setup before every other test in the CompanyTests"""
        self.user = User.objects.create_user(username='testadmin', email='testadmin@gmail.com', password='password', is_superuser=True)
        self.client = Client()
        self.client.login(username=self.user.username, password='password')
        self.fields = ['name', 'desc', 'wait_period', 'late_fee', 'street', 'city', 'state', 'zip_code']
        self.values = ['Test Company', 'Coolio', '15', '55.50', '123 Company Way', 'Greenville', 'SC', '29302']
        self.company = Company.objects.create(**{k: v for k, v in zip(self.fields, self.values)})

    def test_create(self):
        """Tests the creation of a company, and makes sure fields are correct"""
        # Send a post request to the new company page
        values = ['Test 2', 'Another Desc', '20', '1.20', '10 Blah Road', 'McDonough', 'GA', '39320']
        self.client.post(reverse('company_new'), {k: v for k, v in zip(self.fields, values)})

        # Make sure new company has been created
        company = Company.objects.last()
        self.assertEqual([str(getattr(company, k)) for k in self.fields], values)

    def test_update(self):
        """Tests the update of a company, and makes sure updated fields are correct"""
        # Send a request to update name field
        updates = {k: v for k, v in zip(self.fields, [getattr(self.company, x) for x in self.fields])}
        updates['name'] = 'Changed Name'
        self.client.post(reverse('company_edit', args=[self.company.id]), updates)

        # Make sure updated has been applied
        self.company.refresh_from_db()
        self.assertEqual([str(getattr(self.company, x)) for x in self.fields], [updates[k] for k in self.fields])

    def test_delete(self):
        """Tests the delete of a company"""
        # Send a request to delete
        self.client.get(reverse('company_delete', args=[self.company.id]))

        # Make sure the company has been deleted
        companies = Company.objects.filter(pk=self.company.id)
        self.assertEqual(companies.count(), 0)
