from django.db import models

import json


def get_headlines():
    data = json.load(open('../data/headline.json'))
    return data


def get_table4():
    data = json.load(open('../data/table4.json'))
    return data


def get_all_sponsors():
    data = json.load(open('../data/all_sponsors.json'))
    return data
