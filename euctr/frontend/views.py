from django.shortcuts import render
from django.conf import settings

from . import models


def index(request):
    headlines = models.get_headlines()
    table4 = models.get_table4()
    headlines['table4'] = table4

    return render(request, "index.html", context=headlines)


def sponsors(request):
    context = {}
    context['all_sponsors'] = models.get_all_sponsors()

    return render(request, "sponsors.html", context=context)


def about(request):
    context = {}
    context['data_source_date'] = getattr(settings, "DATA_SOURCE_DATE", None)

    return render(request, "about.html", context=context)
