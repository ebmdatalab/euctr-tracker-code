from django.shortcuts import render

from . import models


def index(request):
    headlines = models.get_headlines()
    return render(request, "index.html", context=headlines)
