from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator

class Company(models.Model):
  name = models.CharField(max_length=50, null=True)
  wait_period = models.IntegerField(default=10)

  def __str__(self):
    return self.name

  class Meta:
    indexes = [
      models.Index(fields=['name'], name='company_name_idx')
    ]

class Bank(models.Model):
  name = models.CharField(max_length=50, null=True)

class Account(models.Model):
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
  address = models.CharField(max_length=150, null=True)
  date = models.DateField(auto_now_add=True, blank=True, null=True)

  def __str__(self):
    return self.name

  class Meta:
    ordering = ['-date']
    indexes = [
      models.Index(fields=['date'], name='account_date_idx')
    ]

class Check(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
  to = models.CharField(max_length=50, null=True)
  amount = models.DecimalField(decimal_places=2, max_digits=10, null=True)
  paid = models.DecimalField(decimal_places=2, max_digits=10, default=0, null=True)
  date = models.DateField(auto_now_add=True, blank=True, null=True)

  def __str__(self):
    return '{} --> {}: {}'.format(self.account.name, self.to, self.amount)

  class Meta:
    ordering = ['-date']
    indexes = [
      models.Index(fields=['date'], name='check_date_idx')
    ]

class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True)

  def __str__(self):
    return self.user.username

  def full_name(self):
    return '{} {}'.format(self.user.first_name, self.user.last_name)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
  instance.profile.save()