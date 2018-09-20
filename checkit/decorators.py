from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

def logout_required(function):
  def wrap(request, *args, **kwargs):
    if request.user.is_authenticated:
      messages.warning(request, 'You are already logged in.')
      return redirect('index')
    else:
      return function(request, *args, **kwargs)
  wrap.__doc__ = function.__doc__
  wrap.__name__ = function.__name__
  return wrap