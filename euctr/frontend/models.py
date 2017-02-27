from django.db import models

import json


headings_data = json.load(open('../data/headline.json'))
all_sponsors_data = json.load(open('../data/all_sponsors.json'))
sponsor_by_slug = { x["slug"]: x for x in all_sponsors_data }


def get_headlines():
    return headings_data


def get_all_sponsors():
    return all_sponsors_data


def get_sponsor(slug):
    return sponsor_by_slug[slug]

