from django.shortcuts import render
from django.conf import settings

from . import models


def index(request):
    context = models.get_headlines()

    all_sponsors = models.get_all_sponsors()
    context['all_sponsors'] = all_sponsors
    context['load_js_at_start'] = True

    return render(request, "index.html", context=context)


def about(request):
    context = {}
    context['data_source_date'] = getattr(settings, "DATA_SOURCE_DATE", None)

    return render(request, "about.html", context=context)
