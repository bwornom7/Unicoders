from django.contrib import admin
from .models import Check, Profile, Account, Company

admin.site.register(Check)
admin.site.register(Account)
admin.site.register(Company)