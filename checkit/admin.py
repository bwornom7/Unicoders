"""
This file specifies how the default Django
admin pages will look.
"""

from django.contrib import admin
from .models import Check, Account, Company

# Register our models to the admin pages
admin.site.register(Check)
admin.site.register(Account)
admin.site.register(Company)