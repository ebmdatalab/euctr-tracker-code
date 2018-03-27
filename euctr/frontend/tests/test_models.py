import json
import os


from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import Mock


from django.test import SimpleTestCase
from django.test import Client

from frontend.models import get_trials
from frontend.models import get_sponsor
from frontend.models import get_major_sponsors
from django.conf import settings



def fixture_path(filename):
    return os.path.join(settings.BASE_DIR, 'frontend/tests/fixtures/', filename)


def all_trials():
    return json.load(open(fixture_path('all_trials.json')))


def all_sponsors():
    return json.load(open(fixture_path('all_sponsors.json')))


class TrialsTestCase(SimpleTestCase):
    @patch('frontend.models.get_all_trials', all_trials)
    def test_trial_in_several_countries_by_one_parent_appears_once(self):
        slug = 'glaxosmithkline'
        trials = get_trials(slug)
        self.assertEqual(len(trials), 1)
        self.assertEqual(trials[0]['slug'], slug)
        self.assertEqual(trials[0]['total_trials'], 4)


@patch('frontend.models.get_all_sponsors', all_sponsors)
class SponsorsTestCase(SimpleTestCase):
    def test_sponsors(self):
        slug = 'glaxosmithkline'
        sponsor = get_sponsor(slug)
        self.assertEqual(sponsor['slug'], slug)
        self.assertEqual(sponsor['sponsor_name'], 'GlaxoSmithKline')

    def test_major_sponsors(self):
        sponsors = get_major_sponsors()
        # XXX change fixtures so there are values here
        self.assertEqual(len(sponsors), 0)
