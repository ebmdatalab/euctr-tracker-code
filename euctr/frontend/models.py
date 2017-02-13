from django.db import models

import json

def get_headlines():
    data = json.load(open('data/headline.json'))
    return data

