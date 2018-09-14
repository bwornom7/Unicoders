from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)

  def __str__(self):
    return self.user.username

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
  instance.profile.save()

class Check(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=50)
  date = models.DateField(auto_now_add=True)