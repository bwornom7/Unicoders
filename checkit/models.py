from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
import datetime


class Company(models.Model):
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
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='company_name_idx'),
            models.Index(fields=['date_created'], name='company_date_created_idx')
        ]
        verbose_name_plural = 'companies'


class Account(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50, null=True)
    number = models.CharField(max_length=32, null=True, validators=[
        RegexValidator(r'^[0-9a-zA-Z]*$',
                       message='Only alphanumeric characters are allowed.',
                       code='invalid_account_number')
    ])
    route = models.CharField(max_length=9, null=True, validators=[
        RegexValidator(r'^[0-9]{9}$',
                       message='Routing number must be 9 digits.',
                       code='invalid_routing_number')
    ])
    street = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=2, null=True)
    zip_code = models.CharField(max_length=5, null=True, validators=[
        RegexValidator(r'^[0-9]{5}$',
                       message='Zip code must be five digits.',
                       code='invalid_zip_code')
    ])
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['date_created'], name='account_date_created_idx'),
            models.Index(fields=['name'], name='account_name_idx'),
            models.Index(fields=['number'], name='account_number_idx')
        ]


class Check(models.Model):
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
        return '{}: {}'.format(self.account.name, self.amount)

    def current_letter(self):
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
        letter = self.current_letter()
        setattr(self, 'letter{}_date'.format(letter), datetime.datetime.now().date())
        self.save()
        return 'letters/letter{}.html'.format(letter)

    def row_status(self):
        letter = self.current_letter()
        if letter == 0:
            return 'row-success'
        if 1 <= letter <= 3:
            return 'row-warning'

    def amount_due(self):
        return self.account.company.late_fee + self.amount - self.amount_paid

    def pay(self, amount):
        ret = 'Successfully paid ${:.2f}'.format(amount)
        self.amount_paid += amount
        if self.amount_paid >= self.account.company.late_fee + self.amount:
            self.paid = True
            ret = 'Successfully paid off check!'
        self.save()
        return ret

    class Meta:
        indexes = [
            models.Index(fields=['date_created'], name='check_date_created_idx')
        ]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True)
    is_supervisor = models.BooleanField(default=False)
    records_per_page = models.IntegerField(default=10, validators=[
        MaxValueValidator(100),
        MinValueValidator(1)
    ])

    def __str__(self):
        return self.user.username

    def full_name(self):
        return '{} {}'.format(self.user.first_name, self.user.last_name)

    def admin(self):
        return self.user.is_superuser

    def supervisor(self):
        return self.is_supervisor

    def supervisor_up(self):
        return self.admin() or self.supervisor()

    def simulate(self, company):
        self.company = company
        self.save()

    def stop_simulate(self):
        self.company = None
        self.save()

    def admin_simulating(self):
        return self.admin() and self.company is not None

    def admin_not_simulating(self):
        return self.admin() and self.company is None

    def regular(self):
        return (not self.admin()) or self.admin_simulating()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
