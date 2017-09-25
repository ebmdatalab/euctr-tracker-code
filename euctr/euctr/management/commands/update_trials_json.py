import pandas
import sys
import json
import numpy as np
import json

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify
slugify_vec = np.vectorize(slugify)

PREFIX = '../../euctr-tracker-data/'
SOURCE_CSV_FILE = PREFIX + 'trials.csv'
SOURCE_META_FILE = PREFIX + 'trials.csv.json'
NORMALIZE_FILE = PREFIX + 'normalized_sponsor_names.xlsx'
OUTPUT_HEADLINE_FILE = PREFIX + 'headline.json'
OUTPUT_HEADLINE_HISTORY = PREFIX + 'headline-history.json'
OUTPUT_ALL_SPONSORS_FILE = PREFIX + 'all_sponsors.json'
MAJOR_SPONSORS_THRESHOLD = 50
OUTPUT_ALL_TRIALS_FILE = PREFIX + 'all_trials.json'
OUTPUT_NEW_TRIALS_FILE = PREFIX + 'new_trials.csv'

# For given row of trial data, work out the overall status for display in the
# user interface in rows of the table.
def work_out_status(t):
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

    return overall_status


class Command(BaseCommand):
    help = 'Converts euctr-tracker-data/trials.csv into various JSON files that the Django app needs'

    def handle(self, *args, **options):
        # All trials metadata file
        trials_meta = json.load(open(SOURCE_META_FILE))

        # Load in list of trials, list of normalized names, and join together
        trials_input = pandas.read_csv(SOURCE_CSV_FILE)
        normalize_full = pandas.read_excel(
            NORMALIZE_FILE, "Sheet1",
            keep_default_na=False, na_values=[]
        )
        normalize = normalize_full[['trial_id', 'normalized_name_only', 'normalized_name']]
        # ... do a consistency check (see README.md for definitions of these columns) - find items
        # which have a sponsor name ('normalized_name_only') that is also a parent name
        # (another sponsor's 'normalized_name') but not this sponsor's parent name
        differing_parent = normalize_full[normalize['normalized_name_only'] != normalize["normalized_name"]]
        a1 = set(differing_parent['normalized_name_only'])
        a2 = set(differing_parent['normalized_name'])
        incorrect_parents = a1.intersection(a2)
        if len(incorrect_parents) > 0:
            print("Inconsistent parents: %r" % incorrect_parents)
            print("For these sponsors:")
            for p in incorrect_parents:
                print("Names of these:", set(differing_parent[differing_parent['normalized_name_only'] == p]['name_of_sponsor']))
                print("Conflict with parent names of these:", set(differing_parent[differing_parent['normalized_name'] == p]['name_of_sponsor']))
            sys.exit(1)
        # ... first join on trial_id
        all_trials = pandas.merge(normalize, trials_input, on=['trial_id'])

        # Did the join find everything?
        if len(trials_input) != len(all_trials):
            # Work out which trials are new
            new_trials = trials_input.set_index('trial_id')
            new_trials.drop(normalize['trial_id'], inplace=True, errors="ignore") # TODO: put errosr back
            new_trials.reset_index(inplace=True)
            new_trials['slug'] = slugify_vec(new_trials['name_of_sponsor'])
            new_trials.sort_values('trial_id', inplace=True)

            # Merge based on slug
            normalize_by_slug = normalize_full[['name_of_sponsor', 'normalized_name_only', 'normalized_name']].copy()
            normalize_by_slug['slug'] = slugify_vec(normalize_by_slug['name_of_sponsor'])
            del normalize_by_slug['name_of_sponsor']
            normalize_by_slug = normalize_by_slug.drop_duplicates('slug')

            new_trials_merged = pandas.merge(normalize_by_slug, new_trials, on=['slug'], how='right')
            new_trials_merged.sort_values(['normalized_name_only', 'name_of_sponsor'], inplace=True)

            # Write out list of new trials with matches we have, for manual
            # checking, fixing and adding to NORMALIZE_FILE
            new_trials_merged.to_csv(OUTPUT_NEW_TRIALS_FILE, columns=['trial_id', 'name_of_sponsor', 'normalized_name_only', 'normalized_name'], index=False)
            print("Trials CSV: %d entries  After merge with normalization: %d entries\n\nSee new_trials.csv : %d for list" % (len(trials_input), len(all_trials), len(new_trials)))

            # Assume remaining are new sponsors for now
            unmatched = pandas.isnull(new_trials_merged['normalized_name_only'])
            new_trials_merged.loc[unmatched, 'normalized_name_only'] = new_trials_merged.loc[unmatched, 'name_of_sponsor']
            new_trials_merged.loc[unmatched, 'normalized_name'] = new_trials_merged.loc[unmatched, 'name_of_sponsor']
            #new_trials_merged.to_csv(PREFIX + 'n.csv', columns=['trial_id', 'name_of_sponsor', 'normalized_name_only', 'normalized_name'], index=False) # debugging

            # Add our merge guesses to the main list
            all_trials = all_trials.append(new_trials_merged)
            assert(len(trials_input) == len(all_trials))
        else:
            # Everything matched, erase new trials file
            cols = ['trial_id', 'name_of_sponsor', 'normalized_name_only', 'normalized_name']
            new_trials_merged = pandas.DataFrame(columns=cols)
            new_trials_merged.to_csv(OUTPUT_NEW_TRIALS_FILE, columns=cols, index=False)

        # All trials list
        # ... add slug fields
        all_trials['slug'] = slugify_vec(all_trials['normalized_name_only'])
        all_trials['parent_slug'] = slugify_vec(all_trials['normalized_name'])
        # ... add count of total number of trials for the sponsor (this is used to
        # distinguish major sponsors so is a useful field to have at row level)
        all_trials['total_trials'] = all_trials.groupby(
            ['slug']
        )['trial_id'].transform('count') # XXX could just do ).size() ?
        # (check the group and count worked, e.g. all have a slug)
        null_counts = all_trials[all_trials['total_trials'].isnull()]
        assert len(null_counts) == 0
        all_trials['total_trials'] = all_trials['total_trials'].astype(int)
        # ... add various other fields
        all_trials['overall_status'] = all_trials.apply(work_out_status, axis=1)
        # ... write to a file
        all_trials.sort_values('trial_id', inplace=True)
        json.dump(all_trials.to_dict(orient='records'),
                open(OUTPUT_ALL_TRIALS_FILE, 'w'),
                indent=4, sort_keys=True
        )

        # Sponsor list file, with all relevant counts
        all_trials_less_fields = all_trials[[
            'slug',
            'parent_slug',
            'normalized_name_only',
            'normalized_name',
            'has_results',
            'results_expected',
            'total_trials'
        ]]
        sponsor_grouped = all_trials_less_fields.groupby('slug')
        # ... count up totals
        def do_counts(g):
            due = g[g['results_expected'] == 1]

            # These should be the same for all trials of a sponsor
            assert len(g['slug'].value_counts()) == 1
            assert len(g['total_trials'].value_counts()) == 1

            slug = g['slug'].max()
            sponsor_name = g['normalized_name_only'].max()
            parent_slugs = list(g['parent_slug'].unique())
            parent_names = list(g['normalized_name'].unique())
            if slug in parent_slugs:
                if slug not in parent_slugs:
                    print("Unexpected parent slug not found", slug)
                parent_slugs.remove(slug)
                if sponsor_name not in parent_names:
                    print("Unexpected parent name not found", sponsor_name)
                parent_names.remove(sponsor_name)
            parents = [ { 'slug': a[0], 'name': a[1]} for a in zip(parent_slugs, parent_names) ]

            ret = pandas.Series({
                'sponsor_name': sponsor_name,
                'parents': parents,
                'children': [],
                'total_due': due['results_expected'].sum(),
                'total_reported': due['has_results'].sum(),
                'total_trials': g['total_trials'].max(),
            })
            return ret
        sponsor_counts = sponsor_grouped.apply(do_counts)
        #import pdb; pdb.set_trace()
        #sponsor_counts.index.rename('name_for_index', inplace=True)

        # Work out sponsors which are parents only and don't have own trials
        all_parents = pandas.DataFrame({
            # this is confusing, but needed for consistency with sponsor_counts.
            # effectively, these parents with no trials have a slug
            # the same as their parent_slug
            'slug': all_trials_less_fields['parent_slug'],
            'sponsor_name': all_trials_less_fields['normalized_name']
        })
        all_parents = all_parents.set_index('slug')
        all_parents = all_parents.drop_duplicates()
        all_parents['children'] = [ list() for x in range(len(all_parents)) ]
        all_parents['parents'] = [ list() for x in range(len(all_parents)) ]
        all_parents['total_due'] = 0
        all_parents['total_reported'] = 0
        all_parents['total_trials'] = 0
        all_parents = all_parents.drop(sponsor_counts.index, errors='ignore')

        # Combine list of ones with trials with list of ones without trials
        all_sponsors = pandas.concat([sponsor_counts, all_parents])

        # ... add in relationships between orgs in other direction
        for child_slug, child in all_sponsors.iterrows():
            for parent in child["parents"]:
                full_parent = all_sponsors.loc[parent["slug"]]
                if full_parent.empty:
                    print("Failed to find parent %s of child %s" % (parent["slug"], child_slug))
                else:
                    #import pdb; pdb.set_trace()
                    full_parent["children"].append({
                        "slug": child_slug,
                        "name": child["sponsor_name"]
                    })
        # ... count number of trials with inconsistent data
        inconsistent_trials = all_trials[
            (all_trials['overall_status'] == 'error-completed-no-comp-date') |
            (all_trials['overall_status'] == 'error-ongoing-has-comp-date') |
            (all_trials['overall_status'] == 'no-trial-status')
        ]
        inconsistent_trials_count = inconsistent_trials.groupby('slug').size()
        all_sponsors['inconsistent_trials'] = inconsistent_trials_count
        all_sponsors['inconsistent_trials'].fillna(0.0, inplace=True)
        all_sponsors['inconsistent_trials'] = all_sponsors['inconsistent_trials'].astype(int)
        # ... move slug from being index to being column
        all_sponsors.reset_index(level=0, inplace=True)
        # ... count number not yet due
        all_sponsors['not_yet_due_trials'] = all_sponsors['total_trials'] - all_sponsors['total_due'] - all_sponsors['inconsistent_trials']
        # ... work out percentages
        all_sponsors['percent_reported'] = np.round(
            all_sponsors['total_reported'] /
            all_sponsors['total_due'] * 100, 1
        )
        all_sponsors['total_unreported'] = all_sponsors['total_due'] - all_sponsors['total_reported']
        all_sponsors['percent_unreported'] = np.round(
            all_sponsors['total_unreported'] /
            all_sponsors['total_due'] * 100, 1
        )
        all_sponsors['percent_bad_data'] = np.round(
            all_sponsors['inconsistent_trials'] /
            all_sponsors['total_trials'] * 100, 1
        )
        all_sponsors['major'] = np.where(
            (all_sponsors['total_trials'] >= MAJOR_SPONSORS_THRESHOLD) &
            (all_sponsors['total_due'] > 0) &
            (all_sponsors['sponsor_name'] != "Unknown Sponsor")
        , 1, 0)
        # ... write to a file
        all_sponsors.sort_values('slug', inplace=True)
        json.dump(all_sponsors.to_dict(orient='records'),
                open(OUTPUT_ALL_SPONSORS_FILE, 'w'),
                indent=4, sort_keys=True
        )

        # Headline counts file, used for things like front page large numbers
        headline = {}
        headline['scrape_date'] = trials_meta['scrape_date']
        headline['due_date_cutoff'] = trials_meta['due_date_cutoff']
        headline['total_trials'] = len(all_trials)
        # ... trials which have declared completed everywhere with a date, and a
        # year has passed
        due_trials = all_trials[all_trials.results_expected == 1]
        headline['due_trials'] = len(due_trials)
        # ... trials which have or have not posted results
        due_with_results = due_trials[due_trials.has_results == 1]
        due_without_results = due_trials[due_trials.has_results == 0]
        headline['due_trials_with_results'] = len(due_with_results)
        headline['due_trials_without_results'] = len(due_without_results)
        headline['percent_without_results'] = round(
                len(due_without_results) / len(due_trials) * 100, 1
        )
        # .. trials with inconsistent data
        headline['inconsistent_trials'] = int(inconsistent_trials_count.sum())
        assert len(all_trials) == headline['total_trials']
        headline['percent_inconsistent'] = round(
            headline['inconsistent_trials'] / headline['total_trials'] * 100, 1
        )

        # ... sponsors counts
        headline["all_sponsors_count"] = len(all_sponsors)
        headline["major_sponsors_count"] = np.count_nonzero(all_sponsors['major'])
        # ... write to a file
        with open(OUTPUT_HEADLINE_FILE, 'w') as outfile:
            json.dump(headline, outfile, indent=4, sort_keys=True)

        # Update headline history file
        headline_history = json.load(open(OUTPUT_HEADLINE_HISTORY, 'r'))
        headline_history[headline['scrape_date']] = headline
        with open(OUTPUT_HEADLINE_HISTORY, 'w') as outfile:
            json.dump(headline_history, outfile, indent=4, sort_keys=True)


