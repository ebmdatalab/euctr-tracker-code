import pandas
import sys
import json
import numpy as np

from django.core.management.base import BaseCommand, CommandError

SOURCE_CSV_FILE = '../data/trials.csv'
NORMALIZE_FILE = '../data/normalized_sponsor_names_20FEB2017.xlsx'
OUTPUT_HEADLINE_FILE = '../data/headline.json'
OUTPUT_TABLE4_FILE = '../data/table4.json'
TABLE_4_THRESHOLD = 50

class Command(BaseCommand):
    help = 'Loads in data'

    def handle(self, *args, **options):
        headline = {}

        normalize = pandas.ExcelFile(NORMALIZE_FILE).parse("Sheet1")
        trials_input = pandas.read_csv(SOURCE_CSV_FILE)

        all_trials = pandas.merge(normalize, trials_input, on=['trial_id'])

        # This is used for the TABLE_4_THRESHOLD on whether to include
        # on the front page of the site / table 4 of the journal paper.
        all_trials['total_trials'] = all_trials.groupby(['normalized_name'])['trial_id'].transform('count')
#        print(all_trials)

        headline['total_trials'] = len(all_trials)


        due_trials = all_trials[all_trials.results_expected == 1]
        headline['due_trials'] = len(due_trials)

        due_with_results = due_trials[due_trials.has_results == 1]
        due_without_results = due_trials[due_trials.has_results == 0]
        headline['due_trials_with_results'] = len(due_with_results)
        headline['due_trials_without_results'] = len(due_without_results)
        headline['percent_without_results'] = round(len(due_without_results) / len(due_trials) * 100, 1)

        with open(OUTPUT_HEADLINE_FILE, 'w') as outfile:
            json.dump(headline, outfile)

        table4_trials = due_trials[due_trials['total_trials'] >= TABLE_4_THRESHOLD]
        table4_trials = table4_trials[
            ['normalized_name', 'has_results', 'results_expected', 'total_trials']
        ]
        by_sponsor = table4_trials.groupby('normalized_name')
        table4 = by_sponsor.agg({'has_results': 'sum', 'results_expected': 'sum', 'total_trials': 'max' })
        table4.reset_index(level=0, inplace=True)
        table4.rename(columns={
            'normalized_name': 'sponsor_name',
            'has_results': 'total_reported',
            'results_expected': 'total_due'
        }, inplace=True)
        table4['percent_reported'] = np.round(table4['total_reported'] / table4['total_due'] * 100, 1)

        #pandas.set_option('display.width', 200)
        #print(table4)
        table4.to_json(OUTPUT_TABLE4_FILE, orient='records')

