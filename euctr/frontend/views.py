from django.shortcuts import render
from django.conf import settings

from . import models


def index(request):
    context = models.get_headlines()

    table4 = models.get_table4()
    context['table4'] = table4
    context['load_js_at_start'] = True

    return render(request, "index.html", context=context)


def sponsors(request):
    context = {}
    context['all_sponsors'] = models.get_all_sponsors()
    context['load_js_at_start'] = True

    return render(request, "sponsors.html", context=context)


def about(request):
    context = {}
    context['data_source_date'] = getattr(settings, "DATA_SOURCE_DATE", None)

    return render(request, "about.html", context=context)
