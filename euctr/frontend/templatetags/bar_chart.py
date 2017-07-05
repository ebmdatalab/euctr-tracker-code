import django
import math

register = django.template.Library()

def calc_bar(value, *args):
    """Calculate percentage of value out of the maximum
    of three values, for making a bar chart."""

    top = max(args + (value,))
    percent = value / top * 100
    return percent

register.simple_tag(calc_bar)
