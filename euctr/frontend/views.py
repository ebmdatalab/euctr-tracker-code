import logging
import math

from django.shortcuts import render
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse

import selenium.webdriver

from . import models


def index(request):
    context = models.get_headlines()

    all_sponsors = models.get_all_sponsors()
    context['all_sponsors'] = all_sponsors
    context['load_js_at_start'] = True

    return render(request, "index.html", context=context)

def sponsor(request, slug):
    return _sponsor(request, slug, "sponsor.html", False)

def sponsor_screenshot(request, slug):
    return _sponsor(request, slug, "sponsor_screenshot.html", True)

def _sponsor(request, slug, template_name, taking_screenshot):
    context = models.get_sponsor(slug)

    EXTRA_MARGIN=8
    if (context['inconsistent_trials'] > context['total_due']):
        context['late_reporting_height'] = 200 * math.sqrt(context['total_due'] / context['inconsistent_trials'])
        context['bad_data_height'] = 200
        context['late_reporting_margin'] = (context['bad_data_height'] - context['late_reporting_height']) / 2 + EXTRA_MARGIN
        context['bad_data_margin'] = 0 + EXTRA_MARGIN
    else:
        context['late_reporting_height'] = 200
        context['bad_data_height'] = 200 * math.sqrt(context['inconsistent_trials'] / context['total_due'])
        context['late_reporting_margin'] = 0 + EXTRA_MARGIN
        context['bad_data_margin'] = (context['late_reporting_height'] - context['bad_data_height']) / 2 + EXTRA_MARGIN

    context['trials'] = models.get_trials(slug)
    context['load_js_at_start'] = True
    context['taking_screenshot'] = taking_screenshot

    return render(request, template_name, context=context)

driver = selenium.webdriver.PhantomJS()
driver.set_window_size(1280, 100)
def sponsor_screenshot_png(request, slug):
    url = request.build_absolute_uri(reverse("sponsor_screenshot", kwargs={"slug": slug}))
    driver.get(url)
    png_binary = driver.get_screenshot_as_png()

    return HttpResponse(png_binary, 'image/png')

def about(request):
    context = {}
    context['data_source_date'] = getattr(settings, "DATA_SOURCE_DATE", None)

    return render(request, "about.html", context=context)
