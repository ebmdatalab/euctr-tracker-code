import logging

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
