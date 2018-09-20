from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import Check, Account, Company

class UserForm(UserCreationForm):
  username = forms.CharField(help_text='e.g. foobar97')
  first_name = forms.CharField()
  last_name=forms.CharField()
  email=forms.EmailField(help_text='e.g. foobar97@gmail.com')
  password1=forms.CharField(widget=forms.PasswordInput(), label='Password', help_text='Enter your password')
  password2=forms.CharField(widget=forms.PasswordInput(), label='Confirm Password', help_text='Re-enter your password')

  class Meta(UserCreationForm.Meta):
    model = User
    fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

class AccountForm(forms.ModelForm):
  name = forms.CharField(label='Account Name', help_text='Enter account name')
  number = forms.CharField(label='Account Number', help_text='Enter account number')
  route = forms.CharField(label='Routing Number', help_text='Enter routing number')
  address = forms.CharField(help_text='Enter full address')

  class Meta(forms.ModelForm):
    model = Account
    fields = ('name', 'number', 'route', 'address')

class CheckForm(forms.ModelForm):
  to = forms.CharField(label='Pay To', help_text='Enter who this check was paid out to')
  amount = forms.CharField(help_text='Enter the dollar amount')

  class Meta:
    model = Check
    fields = ['to', 'amount']

class CompanyForm(forms.ModelForm):
  name = forms.CharField(help_text='Enter the company\'s name')
  desc = forms.CharField(label='Description', help_text='Enter a brief description for this company', widget=forms.Textarea)

  class Meta:
    model = Company
    fields = ['name', 'desc']