"""
This file includes all of the data for how the database stores
its information. It includes the models, relationships, and fields
as Python classes. To generate a database migration when a model
has been changed or added, run

    python manage.py makemigrations

To actually migrate the data into the database, run

    python manage.py migrate

Models also have helpful fields that may be used in templates, or
methods that change data on them.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
import datetime


class Company(models.Model):
    """
    The company model. It includes all necessary attributes, and it
    is the main/top model for the whole system.
    """
    name = models.CharField(max_length=50, null=True)
    desc = models.CharField(max_length=1000, null=True)
    wait_period = models.IntegerField(default=10)
    street = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=2, null=True)
    zip_code = models.CharField(max_length=5, null=True, validators=[
        RegexValidator(r'^[0-9]{5}$',
                       message='Zip code must be five digits.',
                       code='invalid_zip_code')
    ])
    late_fee = models.DecimalField(decimal_places=2, max_digits=10, default=50, null=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        """Returns a textual representation of the company"""
        return self.name

    class Meta:
        indexes = [  # Create indexes on fields that are searched.
            models.Index(fields=['name'], name='company_name_idx'),
            models.Index(fields=['date_created'], name='company_date_created_idx')
        ]
        verbose_name_plural = 'companies'


class Account(models.Model):
    """
    The account model includes a foreign key to a company. It
    also includes all of the data for an account, including number,
    routing number, and address.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50, null=True)
    number = models.CharField(max_length=32, null=True, validators=[
        RegexValidator(r'^[0-9a-zA-Z]*$',  # Only alphanumeric characters
                       message='Only alphanumeric characters are allowed.',
                       code='invalid_account_number')
    ])
    route = models.CharField(max_length=9, null=True, validators=[
        RegexValidator(r'^[0-9]{9}$',  # 9 digits is a routing number in US
                       message='Routing number must be 9 digits.',
                       code='invalid_routing_number')
    ])
    street = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=2, null=True)
    zip_code = models.CharField(max_length=5, null=True, validators=[
        RegexValidator(r'^[0-9]{5}$',  # Zip code is just 5 digits, not worrying about rest
                       message='Zip code must be five digits.',
                       code='invalid_zip_code')
    ])
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        """Return a textual representation of the account - the name"""
        return self.name

    class Meta:
        indexes = [  # Create indexes on fields that are searched.
            models.Index(fields=['date_created'], name='account_date_created_idx'),
            models.Index(fields=['name'], name='account_name_idx'),
            models.Index(fields=['number'], name='account_number_idx'),
            models.Index(fields=['route'], name='account_route_idx'),
            models.Index(fields=['street'], name='account_street_idx')
        ]


class Check(models.Model):
    """
    The check model. It includes a foreign key to the user who created it,
    a foreign key to the account it's associated with, and all other necessary
    fields. The standard fields are check number, amount, and date.
    Other fields:
        paid: Whether or not the check has been paid, manually or actually
        amount_paid: The amount currently paid on the check
        letter1_date: The date that letter 1 was generated
        letter2_date: The date that letter 2 was generated
        letter3_date: The date that letter 3 was generated
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    number = models.IntegerField(default=0, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    paid = models.BooleanField(default=False)
    amount_paid = models.DecimalField(decimal_places=2, max_digits=10, default=0, null=True)
    date = models.DateField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    letter1_date = models.DateField(null=True)
    letter2_date = models.DateField(null=True)
    letter3_date = models.DateField(null=True)

    def __str__(self):
        """Returns a textual representation of the check"""
        return '{}: {}'.format(self.account.name, self.amount)

    def current_letter(self):
        """
        Determins which letter should be generated for the check.
        :return:
            0 if already paid
            1 if letter 1
            2 if letter 2
            3 if letter 3
            -1 if no letter needs to be generated
        """
        delta = (datetime.datetime.now().date() - self.date_created.date()).days
        wait_period = self.account.company.wait_period
        if self.paid:
            return 0
        if not self.letter1_date:
            return 1
        elif not self.letter2_date and delta >= wait_period:
            return 2
        elif not self.letter3_date and delta >= wait_period * 2:
            return 3
        return -1

    def current_letter_template(self):
        """
        Gets the current template that needs to be generated for a letter
        :return: The string of the current letter template
        """
        letter = self.current_letter()
        setattr(self, 'letter{}_date'.format(letter), datetime.datetime.now().date())
        self.save()
        return 'letters/letter{}.html'.format(letter)

    def row_status(self):
        """
        How should the check display in a table?
        :return:
            'row-success' if check has been paid
            'row-warning' if letter needs to be generated
        """
        letter = self.current_letter()
        if letter == 0:
            return 'row-success'
        if 1 <= letter <= 3:
            return 'row-warning'

    def amount_due(self):
        """How much is due for this check?"""
        return self.account.company.late_fee + self.amount - self.amount_paid

    def pay(self, amount):
        """
        Pays a certain amount on the check
        :param amount: The amount to pay
        :return: A string for how much or whether the check was fully paid
        """
        ret = 'Successfully paid ${:.2f}'.format(amount)
        self.amount_paid += amount
        if self.amount_paid >= self.account.company.late_fee + self.amount:
            self.paid = True
            ret = 'Successfully paid off check!'
        self.save()
        return ret

    class Meta:
        indexes = [  # Create indexes on fields that are searched.
            models.Index(fields=['date_created'], name='check_date_created_idx')
        ]


class Profile(models.Model):
    """
    The profile model, which contains extra data besides the
    Django defaults for a user.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True)
    is_supervisor = models.BooleanField(default=False)
    records_per_page = models.IntegerField(default=10, validators=[
        MaxValueValidator(100),  # No more than 100 records per page
        MinValueValidator(1)  # No less than 1 record per page
    ])

    def __str__(self):
        """Returns a textual representation of the user, the username"""
        return self.user.username

    def full_name(self):
        """Returns the user's full name, first + last"""
        return '{} {}'.format(self.user.first_name, self.user.last_name)

    def admin(self):
        """Whether or not the user is an administrator"""
        return self.user.is_superuser

    def supervisor(self):
        """Whether or not the user is a supervisor"""
        return self.is_supervisor

    def supervisor_up(self):
        """Whether or not the user is a supervisor or admin"""
        return self.admin() or self.supervisor()

    def simulate(self, company):
        """Makes an administrator start simulating a company"""
        self.company = company
        self.save()

    def stop_simulate(self):
        """Stops an administrator's simulation"""
        self.company = None
        self.save()

    def admin_simulating(self):
        """Whether or not an admin is simulating a company"""
        return self.admin() and self.company is not None

    def admin_not_simulating(self):
        """Whether or not the user is an admin and not simulating"""
        return self.admin() and self.company is None

    def regular(self):
        """
        Whether or not the user is a supervisor or regular user,
        which includes a simulated admin user
        """
        return (not self.admin()) or self.admin_simulating()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Creates the user profile whenever a user is created"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Saves the user profile whenever the user is saved"""
    instance.profile.save()
