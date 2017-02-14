import pandas
import sys
import json

from django.core.management.base import BaseCommand, CommandError

SOURCE_XLS_FILE = '../data/export-from-stata-2016-02-13.xls'
OUTPUT_HEADLINE_FILE = '../data/headline.json'


class Command(BaseCommand):
    help = 'Loads in data'

    def handle(self, *args, **options):
        headline = {}

        all_trials = pandas.ExcelFile(SOURCE_XLS_FILE).parse("Sheet1")
        headline['total_trials'] = len(all_trials)

        due_trials = all_trials[all_trials.are_results_due == 1]
        headline['due_trials'] = len(due_trials)

        due_with_results = due_trials[due_trials.results == "yes"]
        due_without_results = due_trials[due_trials.results == "no"]
        headline['due_trials_with_results'] = len(due_with_results)
        headline['due_trials_without_results'] = len(due_without_results)
        headline['percent_without_results'] = round(len(due_without_results) / len(due_trials) * 100, 1)

        with open(OUTPUT_HEADLINE_FILE, 'w') as outfile:
            json.dump(headline, outfile)

