import django
import math

register = django.template.Library()

def default_if_nan(value, default):
    """Converts NaN (not a number) to string"""
    if math.isnan(value):
        return default
    return value

def default_if_invalid(value, default):
    """Converts None or NaN (not a number) to string"""
    if value is None or math.isnan(value):
        return default
    return value

def custom_percent(value):
    """Renders as a percent"""
    if math.isnan(value):
        return "-"
    return str(value) + "%"

register.filter('default_if_nan', default_if_nan)
register.filter('default_if_invalid', default_if_invalid)
register.filter('custom_percent', custom_percent)
