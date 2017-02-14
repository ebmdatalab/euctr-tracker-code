import pandas
import sys
import json
import numpy as np

from django.core.management.base import BaseCommand, CommandError

SOURCE_XLS_FILE = '../data/export-from-stata-2016-02-13.xls'
OUTPUT_HEADLINE_FILE = '../data/headline.json'
OUTPUT_TABLE4_FILE = '../data/table4.json'
TABLE_4_THRESHOLD = 50

def yes_no_to_number(x):
    if x == 'yes':
        return 1
    if x == 'no':
        return 0
    assert False

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

        table4_trials = due_trials[due_trials['count'] >= TABLE_4_THRESHOLD]
        table4_trials = table4_trials[
            ['normalized_name_of_sponsor', 'results', 'are_results_due']
        ]
        table4_trials['results'] = table4_trials['results'].map(yes_no_to_number)
        by_sponsor = table4_trials.groupby('normalized_name_of_sponsor')
        table4 = by_sponsor.sum()
        table4.reset_index(level=0, inplace=True)
        table4.rename(columns={
            'normalized_name_of_sponsor': 'sponsor_name',
            'results': 'total_reported',
            'are_results_due': 'total_due'
        }, inplace=True)
        table4['percent_reported'] = np.round(table4['total_reported'] / table4['total_due'] * 100, 1)

        #pandas.set_option('display.width', 200)
        #print(table4)
        table4.to_json(OUTPUT_TABLE4_FILE, orient='records')

