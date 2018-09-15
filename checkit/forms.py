from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Check

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

class ProfileForm(forms.ModelForm):
  class Meta:
    model = Profile
    fields = []

class CheckForm(forms.ModelForm):
  class Meta:
    model = Check
    fields = ['name', 'bank', 'route']