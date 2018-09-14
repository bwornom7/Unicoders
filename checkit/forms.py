from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError

class RegistrationForm(forms.Form):
  first_name = forms.CharField(max_length=50, label='First Name')
  last_name = forms.CharField(max_length=50, label='Last Name')
  username = forms.CharField(max_length=50, help_text='e.g. foo_bar97')
  email = forms.EmailField(help_text='e.g. foobar97@gmail.com')
  password = forms.CharField(max_length=32, widget=forms.PasswordInput)
  confirm = forms.CharField(max_length=32, widget=forms.PasswordInput)

  def clean(self):
    cleaned_data = super().clean()
    password = cleaned_data.get('password')
    confirm = cleaned_data.get('confirm')
    if password != confirm:
      self.add_error('confirm', 'Passwords do not match.')
      self.add_error('password', 'Passwords do not match.')