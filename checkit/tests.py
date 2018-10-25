from django.test import TestCase, RequestFactory
from .models import *
from .views import account_delete
from django.contrib.messages.storage.fallback import FallbackStorage

class AccountTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='testuser@gmail.com', password='password')
        self.account = Account.objects.create(
            name='Account',
            number='209375',
            route='209375993',
            street='123 Account Way',
            city='Greenville',
            state='SC',
            zip_code='29614')

    def test_delete(self):
        request = self.factory.get('accounts/delete')
        request.user = self.user
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))

        account_delete(request, self.account.id)
        accounts = Account.objects.filter(pk=self.account.id)
        self.assertEqual(accounts.count(), 0)