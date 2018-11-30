"""
This file contains the decorators for the views.
Decorators are mainly used for permissions, such
as admin, supervisor, and login access.
"""

from django.contrib import messages
from django.shortcuts import redirect


def logout_required(function):
    """
    The user must be logged out for the request to be processed.
    :param function: The view function
    :return: A redirect or the function return value
    """
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.warning(request, 'You are already logged in.')
            return redirect('index')
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def admin_required(function):
    """
    The user must be an admin for the request to be processed.
    :param function: The view function
    :return: A redirect or the function return value
    """
    def wrap(request, *args, **kwargs):
        if not request.user.profile.admin():
            messages.warning(request, 'You do not have permission to access this page.')
            return redirect('index')
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def supervisor_required(function):
    """
    The user must be a supervisor or admin for the request to be processed.
    :param function: The view function
    :return: A redirect or the function return value
    """
    def wrap(request, *args, **kwargs):
        if not (request.user.profile.admin() or request.user.profile.supervisor()):
            messages.warning(request, 'You do not have permission to access this page.')
            return redirect('index')
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap