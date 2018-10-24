from django import template

register = template.Library()


@register.filter
def sort_to_field(value):
    return value.replace('-', '')
