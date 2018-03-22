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
OUTPUT_NEW_NORMALIZE_FILE = PREFIX + 'new_trials.csv'

pandas.set_option('display.max_columns', 500)
pandas.set_option('display.width', 1000)

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


def assert_no_grandparents(normalize_df):
    differing_parent = normalize_df[normalize_df['normalized_name_only'] != normalize_df["normalized_name"]]
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

def get_trials():
    trials = pandas.read_csv(
        SOURCE_CSV_FILE,
        keep_default_na=False, na_values=[]
    )
    trials['raw_slug'] = slugify_vec(trials['name_of_sponsor'])
    return trials

def get_normalized_sponsors():
    # XXX TODO: turn source into a google sheet, and rename columns
    #
    # Each row is a normalised sponsor name. Columns of interest are:
    #   name_of_sponsor: The name as a raw string which appears in a trial record
    #   normalized_name_only: A normalized version of this name
    #   normalized_name: ultimate parent company of the legal entity
    #   Proof: URL showing ownership implied by normalized_name
    #   Description: Description of what Proof shows
    #   Notes: further notes on the Proof
    #
    # We also add:
    #   raw_slug: slug of raw sponsor
    #   slug: slug of normalized name
    #   parent_slug: slug of normalized_name

    sponsors_full = pandas.read_excel(
        NORMALIZE_FILE, "Sheet1",
        keep_default_na=False, na_values=[]
    )
    sponsors = sponsors_full[['name_of_sponsor', 'normalized_name_only', 'normalized_name', 'Proof', 'Description', 'Notes']].copy()
    assert_no_grandparents(sponsors)
    sponsors['raw_slug'] = slugify_vec(sponsors['name_of_sponsor'])
    sponsors['slug'] = slugify_vec(sponsors['normalized_name_only'])
    sponsors['parent_slug'] = slugify_vec(sponsors['normalized_name'])
    if sponsors.duplicated('raw_slug').any():
        print("There were duplicates in raw names in the spreadsheet")
        sys.exit(1)
    return sponsors


def assert_all_trials_matched(all_trials, trials_and_sponsors):
    matched_trials = trials_and_sponsors[trials_and_sponsors['normalized_name_only'] != '']
    if len(matched_trials) != len(all_trials):
        # Write out list of new trials with matches we have, for manual
        # checking, fixing and adding to NORMALIZE_FILE
        print("Trials CSV: %d / %d entries matched" % (len(matched_trials), len(all_trials)))

        # ... first get a list of all the trials
        def join_it(x):
            return ",".join(map(str, x))
        trials_by_name = trials_and_sponsors.groupby('raw_slug').agg({
            'trial_id': join_it,
            'name_of_sponsor_orig': 'max',
            'normalized_name_only': 'max',
            'normalized_name': 'max',
            'Proof': 'max', # this throws away info if proofs vary for same name, but they don't seem to
            'Description': 'max',
            'Notes': 'max',
        })
        trials_by_name['name_of_sponsor'] = trials_by_name['name_of_sponsor_orig']
        trials_by_name['trials_ids'] = trials_by_name['trial_id']
        trials_by_name.sort_values(['normalized_name', 'normalized_name_only', 'name_of_sponsor', 'trials_ids'], inplace=True)
        trials_by_name_matched = trials_by_name[trials_by_name['normalized_name_only'] != '']
        print("Normalise CSV: %d / %d entries complete" % (len(trials_by_name_matched), len(trials_by_name)))
        # ... now output
        trials_by_name.to_csv(OUTPUT_NEW_NORMALIZE_FILE, columns=['trials_ids', 'name_of_sponsor', 'normalized_name_only', 'normalized_name', 'Proof', 'Description', 'Notes'], index=False)
        print("NOT GOING LIVE, until all trials are matched.")
        print("See {} for trials requiring normalisation".format(OUTPUT_NEW_NORMALIZE_FILE))
        sys.exit(1)

def merge_trials_and_sponsors(all_trials, sponsors):
    """Merge trials and normalised sponsors dataframes.

    If there are any unmatched trial sponsors, write a spreadsheet for
    a researcher to complete and return, and refuse to continue

    """
    trials_and_sponsors = pandas \
        .merge(
            sponsors, all_trials,
            on=['raw_slug'],
            how='right',
            suffixes=('', '_orig')) \
        .fillna('')
    # Did the join find everything?
    if False: # XXX
        assert_all_trials_matched(all_trials, trials_and_sponsors)
    else:
        trials_and_sponsors = trials_and_sponsors[trials_and_sponsors['normalized_name_only'] != '']
    return trials_and_sponsors

def make_trials_json(trials_with_sponsors):
    trials_with_sponsors.sort_values(['normalized_name_only', 'name_of_sponsor', 'trial_id'], inplace=True)
    trials_with_sponsors['total_trials'] = trials_with_sponsors.groupby(
        ['slug']
    )['trial_id'].transform('count') # XXX could just do ).size() ?
    # (check the group and count worked, e.g. all have a slug)
    null_counts = trials_with_sponsors[trials_with_sponsors['total_trials'].isnull()]
    assert len(null_counts) == 0
    trials_with_sponsors['total_trials'] = trials_with_sponsors['total_trials'].astype(int)
    # ... add various other fields
    trials_with_sponsors['overall_status'] = trials_with_sponsors.apply(work_out_status, axis=1)
    # ... write to a file
    trials_with_sponsors.sort_values('trial_id', inplace=True)
    json.dump(trials_with_sponsors.to_dict(orient='records'),
            open(OUTPUT_ALL_TRIALS_FILE, 'w'),
            indent=4, sort_keys=True
    )


def make_sponsors_json(df):
    # Sponsor list file, with all relevant counts
    sponsors = df[[
        'slug',
        'parent_slug',
        'normalized_name_only',
        'normalized_name',
        'has_results',
        'results_expected',
        'total_trials'
    ]]
    sponsor_grouped = sponsors.groupby('slug')
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
    # ... add count of total number of trials for the sponsor (this is used to
    # distinguish major sponsors so is a useful field to have at row level)
    sponsor_counts = sponsor_grouped.apply(do_counts)

    # Work out sponsors which are parents only and don't have own trials
    all_parents = pandas.DataFrame({
        # this is confusing, but needed for consistency with sponsor_counts.
        # effectively, these parents with no trials have a slug
        # the same as their parent_slug
        'slug': sponsors['parent_slug'],
        'sponsor_name': sponsors['normalized_name']
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
                full_parent["children"].append({
                    "slug": child_slug,
                    "name": child["sponsor_name"]
                })
    # ... count number of trials with inconsistent data
    inconsistent_trials = df[
        (df['overall_status'] == 'error-completed-no-comp-date') |
        (df['overall_status'] == 'error-ongoing-has-comp-date') |
        (df['overall_status'] == 'no-trial-status')
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
    return all_sponsors, int(inconsistent_trials_count.sum())


def make_headline_json(df, all_sponsors, inconsistent_trials_count):
    trials_meta = json.load(open(SOURCE_META_FILE))
    # Headline counts file, used for things like front page large numbers
    headline = {}
    headline['scrape_date'] = trials_meta['scrape_date']
    headline['due_date_cutoff'] = trials_meta['due_date_cutoff']
    headline['total_trials'] = len(df)
    # ... trials which have declared completed everywhere with a date, and a
    # year has passed
    due_trials = df[df.results_expected == 1]
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
    headline['inconsistent_trials'] = inconsistent_trials_count
    assert len(df) == headline['total_trials']
    headline['percent_inconsistent'] = round(
        headline['inconsistent_trials'] / headline['total_trials'] * 100, 1
    )

    # ... sponsors counts
    headline["all_sponsors_count"] = len(df)

    #headline["major_sponsors_count"] = np.count_nonzero(df['major'])
    # ... write to a file
    with open(OUTPUT_HEADLINE_FILE, 'w') as outfile:
        json.dump(headline, outfile, indent=4, sort_keys=True)

    # Update headline history file
    headline_history = json.load(open(OUTPUT_HEADLINE_HISTORY, 'r'))
    headline_history[headline['scrape_date']] = headline
    with open(OUTPUT_HEADLINE_HISTORY, 'w') as outfile:
        json.dump(headline_history, outfile, indent=4, sort_keys=True)

class Command(BaseCommand):
    help = 'Converts euctr-tracker-data/trials.csv into various JSON files that the Django app needs'

    def handle(self, *args, **options):
        # All trials metadata file
        all_trials = get_trials()
        sponsors = get_normalized_sponsors()
        trials_with_sponsors = merge_trials_and_sponsors(all_trials, sponsors)
        # At this stage, we now have one row per trial,
        make_trials_json(trials_with_sponsors)

        all_sponsors, inconsistent_trials_count = make_sponsors_json(trials_with_sponsors)
        make_headline_json(trials_with_sponsors, all_sponsors, inconsistent_trials_count)
