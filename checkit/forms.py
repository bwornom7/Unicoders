"""
All the forms used in the project. Forms include things like
creating, updating, basic interaction forms, and more.
"""

from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Check, Account, Company, Profile
import datetime


# All the state choices for a state dropdown input
STATE_CHOICES = (('AL', 'Alabama'), ('AK', 'Alaska'), ('AS', 'American Samoa'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('DC', 'District Of Columbia'), ('FM', 'Federated States Of Micronesia'), ('FL', 'Florida'), ('GA', 'Georgia'), ('GU', 'Guam'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MH', 'Marshall Islands'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('MP', 'Northern Mariana Islands'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PW', 'Palau'), ('PA', 'Pennsylvania'), ('PR', 'Puerto Rico'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VI', 'Virgin Islands'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming'))


class UserForm(UserCreationForm):
    """
    The form for creating a user (registering). It extends
    Django's default registration form by adding first name,
    last name, and email.
    """
    username = forms.CharField(help_text='e.g. foobar97')
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField(help_text='e.g. foobar97@gmail.com')
    password1 = forms.CharField(widget=forms.PasswordInput(), label='Password', help_text='Enter your password')
    password2 = forms.CharField(widget=forms.PasswordInput(), label='Confirm Password', help_text='Re-enter your password')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')


class UserEditForm(forms.ModelForm):
    """
    The form for editing a user. Using this form, we can make the user
    an admin. Only supervisor/admin users have access to this form through the user
    edit page.
    """
    username = forms.CharField(help_text='e.g. foobar97')
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField(help_text='e.g. foobar97@gmail.com')
    is_superuser = forms.BooleanField(label='Admin?', required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_superuser')


class ProfileForm(forms.ModelForm):
    """
    The form for editing a user profile. Using this form, we can make the user
    a supervisor. Only supervisor/admin users have access to this form through
    the user edit page.
    """
    is_supervisor = forms.BooleanField(label='Supervisor?', required=False)
    records_per_page = forms.IntegerField(label='Items per page')

    class Meta:
        model = Profile
        fields = ['is_supervisor', 'records_per_page']


class ProfileUserForm(forms.ModelForm):
    """
    The user edit form. A user can edit their profile details using this
    form on the profile page.
    """
    username = forms.CharField(help_text='e.g. foobar97')
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField(help_text='e.g. foobar97@gmail.com')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    """
    The profile edit form. A user can edit their profile details,
    specifically records per page, using this form.
    """
    records_per_page = forms.IntegerField(label='Items per page')

    class Meta:
        model = Profile
        fields = ['records_per_page']


class AccountForm(forms.ModelForm):
    """
    The form to create an account. It includes all necessary fields, including
    name, number, routing number, and address.
    """
    name = forms.CharField(label='Account Name', help_text='Enter account name')
    number = forms.CharField(label='Account Number', help_text='Enter account number')
    route = forms.CharField(label='Routing Number', help_text='Enter routing number')
    street = forms.CharField(label='Street Name', help_text='Enter street address')
    city = forms.CharField(label='City', help_text='Enter city address')
    state = forms.ChoiceField(choices=STATE_CHOICES)
    zip_code = forms.CharField(label='Zip Code', help_text='Enter zip code')

    class Meta:
        model = Account
        fields = ('name', 'number', 'route', 'street', 'city', 'state', 'zip_code')


class CheckForm(forms.ModelForm):
    """
    The form for creating a check. The check is created under an account.
    It includes all necessary fields, and the date field shows a date
    picker when displayed in the browser for easy input.
    """
    number = forms.CharField(help_text='Enter the check number')
    amount = forms.CharField(help_text='Enter the dollar amount')
    date = forms.DateField(initial=datetime.date.today,
                           input_formats=['%m/%d/%Y'],
                           widget=forms.DateInput(format='%m/%d/%Y', attrs={'class': 'date-field'}))

    class Meta:
        model = Check
        fields = ['number', 'amount', 'date']


class CheckEditForm(forms.ModelForm):
    """
    The form to edit a check. A supervisor/admin can override the "paid"
    attribute in the case the company decides to pay off a user's
    bounced check for free.
    """
    number = forms.CharField(help_text='Enter the check number')
    amount = forms.CharField(help_text='Enter the dollar amount')
    date = forms.DateField(input_formats=['%m/%d/%Y'],
                           widget=forms.DateInput(format='%m/%d/%Y', attrs={'class': 'date-field'}))
    paid = forms.BooleanField(required=False)

    class Meta:
        model = Check
        fields = ['number', 'amount', 'date', 'paid']


class CheckPayForm(forms.Form):
    """
    Allows any user to pay of a certain amount of a check.
    """
    amount = forms.DecimalField(help_text='Enter the amount paid')


class CompanyForm(forms.ModelForm):
    """
    The company creation form. It includes all necessary fields, including
    name, description, address, wait period time, and late fee.
    """
    name = forms.CharField(help_text='Enter the company\'s name')
    desc = forms.CharField(label='Description', help_text='Enter a brief description for this company',
                           widget=forms.Textarea, required=False)
    street = forms.CharField(label='Street Name', help_text='Enter street address')
    city = forms.CharField(label='City', help_text='Enter city address')
    state = forms.ChoiceField(choices=STATE_CHOICES)
    zip_code = forms.CharField(label='Zip Code', help_text='Enter zip code')
    wait_period = forms.CharField(label='Wait Period', initial='10', help_text='Enter wait period between letters')
    late_fee = forms.CharField(label='Late Fee', initial='50', help_text='Enter the late fee for bounced checks')

    class Meta:
        model = Company
        fields = ['name', 'desc', 'street', 'city', 'state', 'zip_code', 'wait_period', 'late_fee']


class ReportForm(forms.Form):
    """
    This form allows a user to enter a date range when generating visual
    reports on the reports page. It includes a start and end date.
    """
    start_date = forms.DateField(initial=datetime.datetime.now().date() - datetime.timedelta(days=7),
                                 input_formats=['%m/%d/%Y'],
                                 widget=forms.DateInput(format='%m/%d/%Y', attrs={'class': 'date-field'}))
    end_date = forms.DateField(initial=datetime.datetime.now().date(),
                               input_formats=['%m/%d/%Y'],
                               widget=forms.DateInput(format='%m/%d/%Y', attrs={'class': 'date-field'}))