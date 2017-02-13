from django.shortcuts import render

from . import models


def index(request):
    headlines = models.get_headlines()
    table4 = models.get_table4()
    headlines['table4'] = table4

    return render(request, "index.html", context=headlines)
