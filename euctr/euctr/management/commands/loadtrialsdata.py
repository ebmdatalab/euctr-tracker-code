import pandas
import sys
import json
import numpy as np

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

SOURCE_CSV_FILE = '../data/trials.csv'
NORMALIZE_FILE = '../data/normalized_sponsor_names_21FEB2017.xlsx'
OUTPUT_HEADLINE_FILE = '../data/headline.json'
OUTPUT_ALL_SPONSORS_FILE = '../data/all_sponsors.json'
TABLE_4_THRESHOLD = 50
OUTPUT_ALL_TRIALS_FILE = '../data/all_trials.json'

# For given row of trial data, work out the overall status for display in the
# user interface in rows of the table.
def work_out_status(t):
    #print("-------------")
    #print(t)

    status = None

    assert t.results_expected in (0, 1)
    assert t.trial_status in (0, 1, 2, 3, 4)
    assert t.comp_date_while_ongoing == 0 or (t.trial_status in (0, 2))
    assert t.all_completed_no_comp_date == 0 or t.trial_status == 1

    if t.trial_status == 0 or t.trial_status == 2: # 0 means none done, 2 means some protocols are done
        if t.comp_date_while_ongoing:
            overall_status = "error-ongoing-has-comp-date"
        else:
            if t.has_results == 1:
                overall_status = "ongoing-reported-early"
            else:
                overall_status = "ongoing"
    elif t.trial_status == 1:
        if t.all_completed_no_comp_date:
            overall_status = "error-completed-no-comp-date"
        elif t.results_expected == 0:
            if t.has_results == 1:
                overall_status = "completed-reported-early"
            else:
                overall_status = "completed-not-due"
        else:
            if t.has_results == 1:
                overall_status = "reported"
            else:
                overall_status = "completed-due"
    elif t.trial_status == 3:
        overall_status = "other" # suspended, withdrawn, not authorised, prohibited by CA
    elif t.trial_status == 4:
        overall_status = "no-trial-status" # a blank trial status usually indicated a paediatric trial taking place wholly outside of the EU/EEA

    #print("NEW STATUS", overall_status)

    return overall_status


class Command(BaseCommand):
    help = 'Loads in data'

    def handle(self, *args, **options):
        headline = {}

        # Load in list of trials, list of normalized names, and join together
        trials_input = pandas.read_csv(SOURCE_CSV_FILE)
        normalize = pandas.read_excel(
            NORMALIZE_FILE, "Sheet1",
            keep_default_na=False, na_values=[]
        )
        all_trials = pandas.merge(normalize, trials_input, on=['trial_id'])
        headline['total_trials'] = len(all_trials)

        # Add count of number of trials. Used for the TABLE_4_THRESHOLD below
        # on whether to include on the front page of the site / table 4 of the
        # journal paper.
        all_trials['total_trials'] = all_trials.groupby(
            ['normalized_name']
        )['trial_id'].transform('count') # XXX could just do ).size() ?
        # ... check the group and count worked, eg all have a normalized_name
        null_counts = all_trials[all_trials['total_trials'].isnull()]
        assert len(null_counts) == 0

        # Add various other fields
        all_trials['total_trials'] = all_trials['total_trials'].astype(int)
        all_trials['slug'] = np.vectorize(slugify)(all_trials['normalized_name'])
        all_trials['overall_status'] = all_trials.apply(work_out_status, axis=1)

        # Output all trials to file for sponsors page
        all_trials.sort_values('trial_id', inplace=True)
        json.dump(all_trials.to_dict(orient='records'),
                open(OUTPUT_ALL_TRIALS_FILE, 'w'),
                indent=4, sort_keys=True
        )

        # Trials which have declared completed everywhere with a date, and a
        # year has passed
        due_trials = all_trials[all_trials.results_expected == 1]
        headline['due_trials'] = len(due_trials)

        # Trials which have or have not posted results
        due_with_results = due_trials[due_trials.has_results == 1]
        due_without_results = due_trials[due_trials.has_results == 0]
        headline['due_trials_with_results'] = len(due_with_results)
        headline['due_trials_without_results'] = len(due_without_results)
        headline['percent_without_results'] = round(
                len(due_without_results) / len(due_trials) * 100, 1
        )

        sponsor_trials = due_trials[[
            'slug',
            'normalized_name',
            'has_results',
            'results_expected',
            'total_trials'
        ]]
        # ... count up totals
        sponsor_grouped = sponsor_trials.groupby('normalized_name')
        def do_counts(g):
            print("======================")
            print(g)
            print("----------------------")
            ret = pandas.Series({
                'slug': g['slug'].max(),
                'sponsor_name': g['normalized_name'].max(),
                'total_due': (g['results_expected'] == 1).count(),
                'total_reported': g[g['results_expected'] == 1]['has_results'].sum(),
                'total_trials': g['total_trials'].max(),
            })
            print(ret)
            print("----------------------")
            return ret
        sponsor_counts = sponsor_grouped.apply(do_counts)
        print(sponsor_counts)
        # ... count number of trials with inconsistent data
        inconsistent_trials = all_trials[
            (all_trials['overall_status'] == 'error-completed-no-comp-date') |
            (all_trials['overall_status'] == 'error-ongoing-has-comp-date') |
            (all_trials['overall_status'] == 'no-trial-status')
        ]
        inconsistent_trials_count = inconsistent_trials.groupby('normalized_name').size()
        sponsor_counts['inconsistent_trials'] = inconsistent_trials_count
        sponsor_counts['inconsistent_trials'].fillna(0.0, inplace=True)
        sponsor_counts['inconsistent_trials'] = sponsor_counts['inconsistent_trials'].astype(int)
        # ... reform it
        sponsor_counts.reset_index(level=0, inplace=True)
        # ... count number not yet due
        sponsor_counts['not_yet_due_trials'] = sponsor_counts['total_trials'] - sponsor_counts['total_due'] - sponsor_counts['inconsistent_trials']
        # ... work out percentages
        sponsor_counts['percent_reported'] = np.round(
            sponsor_counts['total_reported'] /
            sponsor_counts['total_due'] * 100, 1
        )
        sponsor_counts['total_unreported'] = sponsor_counts['total_due'] - sponsor_counts['total_reported']
        sponsor_counts['percent_unreported'] = np.round(
            sponsor_counts['total_unreported'] /
            sponsor_counts['total_due'] * 100, 1
        )
        sponsor_counts['percent_bad_data'] = np.round(
            sponsor_counts['inconsistent_trials'] /
            sponsor_counts['total_trials'] * 100, 1
        )
        del sponsor_counts['normalized_name']
        # ... write them to a file
        sponsor_counts.sort_values('slug', inplace=True)
        json.dump(sponsor_counts.to_dict(orient='records'),
                open(OUTPUT_ALL_SPONSORS_FILE, 'w'),
                indent=4, sort_keys=True
        )

        # To get size of the default front page table
        table4 = sponsor_counts[
            sponsor_counts['total_trials'] >= TABLE_4_THRESHOLD
        ]

        # More total counts
        headline["all_sponsors_count"] = len(sponsor_counts)
        headline["major_sponsors_count"] = len(table4)

        # Write out file of totals, e.g. for front page large numbers
        with open(OUTPUT_HEADLINE_FILE, 'w') as outfile:
            json.dump(headline, outfile, indent=4, sort_keys=True)


