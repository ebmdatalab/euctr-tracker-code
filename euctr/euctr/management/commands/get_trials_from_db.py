import subprocess
import os
import sys
import psycopg2
import csv
import datetime
import json
import collections
import hashlib

import sys
import pandas as pd
import numpy as np
import ast
from sqlalchemy import create_engine
from dateutil.relativedelta import relativedelta

from atomicwrites import atomic_write

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

def load_data_into_pandas(db, sufficiently_old):
    """load data from postgresql db"""
    engine = create_engine(db)
    cols = ['eudract_number',
            'eudract_number_with_country',
            'date_of_the_global_end_of_the_trial',
            'trial_is_part_of_a_paediatric_investigation_plan',
            'end_of_trial_status',
            'trial_status',
            'trial_human_pharmacology_phase_i',
            'trial_therapeutic_exploratory_phase_ii',
            'trial_therapeutic_confirmatory_phase_iii',
            'trial_therapeutic_use_phase_iv',
            'trial_bioequivalence_study',
            'subject_healthy_volunteers',
            'trial_condition_being_studied_is_a_rare_disease',
            'trial_single_blind',
            'full_title_of_the_trial',
            'name_or_abbreviated_title_of_the_trial_where_available',
            'trial_results',
            'sponsors' ]
    return pd.read_sql_query("SELECT {} FROM public.euctr WHERE meta_updated > '{}'".format(','.join(cols), sufficiently_old), con=engine)

def cleanup_dataset(euctr_cond):
    """cleaning up the condensed EUCTR dataset and adding the false conditions"""
    euctr_cond['date_of_the_global_end_of_the_trial'] = pd.to_datetime(euctr_cond['date_of_the_global_end_of_the_trial'])
    euctr_cond['trial_is_part_of_a_paediatric_investigation_plan'] = (euctr_cond['trial_is_part_of_a_paediatric_investigation_plan'] == True).astype(int)
    euctr_cond['trial_human_pharmacology_phase_i'] = (euctr_cond['trial_human_pharmacology_phase_i']== True).astype(int)
    euctr_cond['trial_therapeutic_exploratory_phase_ii'] = (euctr_cond['trial_therapeutic_exploratory_phase_ii']== True).astype(int)
    euctr_cond['trial_therapeutic_confirmatory_phase_iii'] = (euctr_cond['trial_therapeutic_confirmatory_phase_iii']== True).astype(int)
    euctr_cond['trial_therapeutic_use_phase_iv'] = (euctr_cond['trial_therapeutic_use_phase_iv']== True).astype(int)
    euctr_cond['not_bioequivalence_study'] = (euctr_cond['trial_bioequivalence_study']== False).astype(int)
    euctr_cond['trial_bioequivalence_study'] = (euctr_cond['trial_bioequivalence_study']== True).astype(int)
    euctr_cond['rare_disease_blank'] = (euctr_cond['trial_condition_being_studied_is_a_rare_disease'] == 'Information not present in EudraCT').astype(int)
    euctr_cond['not_rare_disease'] = (euctr_cond['trial_condition_being_studied_is_a_rare_disease'] == 'No').astype(int)
    euctr_cond['trial_condition_being_studied_is_a_rare_disease'] = (euctr_cond['trial_condition_being_studied_is_a_rare_disease'] == 'Yes').astype(int)
    euctr_cond['not_single_blind'] = (euctr_cond['trial_single_blind']== False).astype(int)
    euctr_cond['trial_single_blind'] = (euctr_cond['trial_single_blind']== True).astype(int)
    euctr_cond['not_healthy_volunteers'] = (euctr_cond['subject_healthy_volunteers']== False).astype(int)
    euctr_cond['subject_healthy_volunteers'] = (euctr_cond['subject_healthy_volunteers']== True).astype(int)

    # Nick's notebook used pandas.notna, we reimplement a simplified version
    # here for compatibility with pandas 0.19
    def euctr_notna(x):
        return not (x is None or x is np.nan)
    euctr_cond['trial_results'] = (euctr_cond['trial_results'].apply(euctr_notna)).astype(int)

    euctr_cond.rename(columns={'full_title_of_the_trial':'full_title', 'name_or_abbreviated_title_of_the_trial_where_available': 'abbreviated_title'}, inplace=True)
    euctr_cond['non_eu'] = euctr_cond.eudract_number_with_country.str.contains('-3rd').astype(int)   

def prepare_sponsor_data(euctr_cond):
    """prepare the sponsor data that we will join in later"""
    spon_cols = ['eudract_number', 'eudract_number_with_country', 'sponsors']
    euctr_spon = euctr_cond[spon_cols].reset_index(drop=True)

    s = euctr_spon['sponsors']
    # concat had sort=False in Nick's original version
    # doesn't seem to make any difference to the result
    s_exp = pd.concat([pd.DataFrame(x) for x in s], keys = s.index)
    return euctr_spon.drop('sponsors', 1).join(s_exp.reset_index(level=1, drop=True)).reset_index(drop=True)

def create_spon_status(spon_type):
    """create the spon_status table"""
    def sp(x):
        st = {}
        st['trial_count'] = x.eudract_number_with_country.count()
        st['commercial'] = np.where(x.status_of_the_sponsor == 'Commercial',1,0).sum()
        st['non_commercial'] = np.where(x.status_of_the_sponsor == 'Non-Commercial',1,0).sum()
        st['blank_status'] = np.where(pd.isnull(x.status_of_the_sponsor),1,0).sum()
        return pd.Series(st)

    spon_status = spon_type.groupby('eudract_number').apply(sp).reset_index()

    ss_cond = [
        (spon_status.non_commercial == spon_status.trial_count),
        (spon_status.commercial == spon_status.trial_count),
        (spon_status.blank_status == spon_status.trial_count)]
    ss_vals = [0,1,3]
    spon_status['sponsor_status'] = np.select(ss_cond, ss_vals, default = 2)

    return spon_status

def create_dataframe(euctr_cond):
    """Step 1 to the next dataframe"""
    def f(x):
        d = {}
        d['number_of_countries'] = x.eudract_number_with_country.nunique()
        d['min_end_date'] = x.date_of_the_global_end_of_the_trial.min()
        d['max_end_date'] = x.date_of_the_global_end_of_the_trial.max()
        d['comp_date'] = np.where(pd.notnull(x.date_of_the_global_end_of_the_trial),1,0).sum()
        d['has_results'] = x.trial_results.sum()
        d['includes_pip'] = x.trial_is_part_of_a_paediatric_investigation_plan.sum()
        d['single_blind'] = x.trial_single_blind.sum()
        d['not_single_blind'] = x.not_single_blind.sum()
        d['rare_disease'] = x.trial_condition_being_studied_is_a_rare_disease.sum()
        d['not_rare_disease'] = x.not_rare_disease.sum()
        d['rare_disease_blank'] = x.rare_disease_blank.sum()
        d['completed'] = np.where(x.end_of_trial_status == 'Completed', 1, 0).sum()
        d['ongoing'] =  np.where((x.end_of_trial_status == 'Ongoing') | (x.end_of_trial_status == 'Restarted'), 1, 0).sum()
        d['terminated'] = np.where(x.end_of_trial_status == 'Prematurely Ended', 1, 0).sum()
        d['suspended'] = np.where((x.end_of_trial_status == 'Temporarily Halted') | (x.end_of_trial_status == 'Suspended by CA'), 1, 0).sum()
        d['other_status'] = np.where((x.end_of_trial_status == 'Not Authorised') | (x.end_of_trial_status == 'Prohibited by CA'), 1, 0).sum()
        d['no_status'] = np.where(pd.isnull(x.end_of_trial_status),1,0).sum()
        d['phase_1'] = x.trial_human_pharmacology_phase_i.sum()
        d['phase_2'] = x.trial_therapeutic_exploratory_phase_ii.sum()
        d['phase_3'] = x.trial_therapeutic_confirmatory_phase_iii.sum()
        d['phase_4'] = x.trial_therapeutic_use_phase_iv.sum()
        d['bioequivalence'] = x.trial_bioequivalence_study.sum()
        d['not_bioequivalence'] = x.not_bioequivalence_study.sum()
        d['healthy_volunteers'] = x.subject_healthy_volunteers.sum()
        d['not_healthy_volunteers'] = x.not_healthy_volunteers.sum()
        d['full_title'] = x.full_title.astype('str').min()
        d['abbreviated_title'] = x.abbreviated_title.astype('str').max()
        d['non_eu'] = x.non_eu.sum()
        return pd.Series(d)

    return euctr_cond.groupby('eudract_number').apply(f).reset_index()

def clean_and_enhance_dataframe(grouped, due_date_cutoff, euctr_url):
    """some data cleaning & building most of the final dataframe"""
    grouped.replace('nan', np.nan, inplace=True)
    grouped['full_title'] = grouped.full_title.str.replace(r'\r','')
    grouped['full_title'] = grouped.full_title.str.replace(r'\n','')

    grouped.rename(columns={'eudract_number':'trial_id'}, inplace=True)
    grouped['min_end_date'] = pd.to_datetime(grouped['min_end_date'])
    grouped['max_end_date'] = pd.to_datetime(grouped['max_end_date'])
    grouped['has_results'] = (grouped.has_results == grouped.number_of_countries).astype(int)
    grouped['includes_pip'] = (grouped.includes_pip > 0).astype(int)
    grouped['exempt'] = ((grouped.includes_pip == 0) & (grouped.phase_1 == grouped.number_of_countries)).astype(int)

    sb_cond = [
        (grouped.single_blind == grouped.number_of_countries),
        (grouped.not_single_blind == grouped.number_of_countries)] 
    sb_vals = [1,0]
    grouped['single_blind'] = np.select(sb_cond,sb_vals, default = 2)

    rd_cond = [
        (grouped.rare_disease == grouped.number_of_countries),
        (grouped.not_rare_disease == grouped.number_of_countries),
        (grouped.rare_disease_blank == grouped.number_of_countries)]
    rd_vals = [1,0,3]
    grouped['rare_disease'] = np.select(rd_cond,rd_vals, default = 2)

    ph_cond = [
        (grouped.phase_1 == grouped.number_of_countries),
        (grouped.phase_2 == grouped.number_of_countries),
        (grouped.phase_3 == grouped.number_of_countries),
        (grouped.phase_4 == grouped.number_of_countries)]
    ph_vals = [1,2,3,4]
    grouped['phase'] = np.select(ph_cond,ph_vals, default = 0)

    be_cond = [
        (grouped.bioequivalence == grouped.number_of_countries),
        (grouped.not_bioequivalence == grouped.number_of_countries)]
    be_vals = [1,0]
    grouped['bioequivalence_study'] = np.select(be_cond,be_vals, default = 2)

    hv_cond = [
        (grouped.healthy_volunteers == grouped.number_of_countries),
        (grouped.not_healthy_volunteers == grouped.number_of_countries)]
    hv_vals = [1,0]
    grouped['health_volunteers'] = np.select(hv_cond,hv_vals, default = 2)

    ts_cond = [
        (grouped.ongoing == grouped.number_of_countries),
        ((grouped.completed) + (grouped.terminated) == grouped.number_of_countries),
        (((grouped.completed) + (grouped.terminated)) > 0) & (((grouped.completed) + (grouped.terminated)) < grouped.number_of_countries),
        (grouped.no_status == grouped.number_of_countries)]
    ts_vals = [0,1,2,4]
    grouped['trial_status'] = np.select(ts_cond,ts_vals, default = 3)

    grouped['any_terminated'] = (grouped.terminated > 0).astype(int)
    grouped['all_terminated'] = (grouped.terminated == grouped.number_of_countries).astype(int)
    grouped['results_expected'] = (((grouped.completed) + (grouped.terminated) == grouped.number_of_countries) & 
                                     (grouped.comp_date > 0) &
                                     (grouped.max_end_date < due_date_cutoff) &
                                     ~((grouped.includes_pip == 0) & (grouped.phase_1 == grouped.number_of_countries))).astype(int)
    grouped['all_completed_no_comp_date'] = (((grouped.completed) + (grouped.terminated) == grouped.number_of_countries) &
                                               (grouped.comp_date == 0)).astype(int)
    title_cond = [
        ((pd.isnull(grouped.full_title)) & (pd.notnull(grouped.abbreviated_title))),
        ((pd.isnull(grouped.full_title)) & (pd.isnull(grouped.abbreviated_title))),
        ((pd.notnull(grouped.full_title)) & (grouped.full_title.str.len() > 200))]
    title_vals = [grouped.abbreviated_title, 'No Title', grouped.full_title.str.slice(stop=200) + '...']
    grouped['trial_title'] = np.select(title_cond, title_vals, grouped.full_title)

    grouped['trial_url'] = euctr_url + grouped.trial_id
    grouped['comp_date_while_ongoing'] = ((grouped.comp_date > 0) & 
                                            (((grouped.completed) + (grouped.terminated)) > 0) & 
                                            (((grouped.completed) + (grouped.terminated)) < grouped.number_of_countries)).astype(int)
    grouped['contains_non_eu'] = (grouped.non_eu > 0).astype(int)
    grouped['only_non_eu'] = (grouped.non_eu == grouped.number_of_countries).astype(int)

class Command(BaseCommand):
    help = 'Fetches trials data from OpenTrials PostgreSQL database and saves to trials.csv'

    def add_arguments(self, parser):
        default_db = os.environ.get('EUCTR_OPENTRIALS_DB', None)
        parser.add_argument('--dburl',
                            type=str,
                            default=default_db)

    def handle(self, *args, **options):
        verbosity = int(options['verbosity'])

        opentrials_db = options['dburl']
        euctr_url = 'https://www.clinicaltrialsregister.eu/ctr-search/search?query='

        conn = psycopg2.connect(opentrials_db)
        cur = conn.cursor()
        # Find out the start date of current scrape.
        cur.execute(
            "select date(meta_updated) from euctr "
            "group by meta_updated "
            "order by meta_updated desc limit 60")
        scrape_dates = [x[0] for x in cur.fetchall()]
        # Default to the oldest of the last 60 runs
        sufficiently_old = scrape_dates[-1]
        last_scrape_date = scrape_dates.pop(0)
        if verbosity > 1:
            print("Late scrape start date:", last_scrape_date)

        # sufficiently_old: the date that is both more than 60 days
        # ago *and* more than 2 scrapes old. We assume such trials not
        # longer exist. The hand-waving around 60 days and 2 scrapes
        # is because some trials apparently reappear. See #66 for
        # discussion and analysis.
        scrape_index = 0
        scrape_window = 3
        for d in scrape_dates:
            scrape_index += 1
            if d > (last_scrape_date - datetime.timedelta(days=60)):
                # Disregard dates in the last 2 months
                continue
            if scrape_index >= scrape_window:
                sufficiently_old = d
                break
        if scrape_index < scrape_window \
           or last_scrape_date == sufficiently_old:
            # There's not been enough scrapes to expire anything, so
            # expire nothing
            sufficiently_old = sufficiently_old - datetime.timedelta(days=1)
        if verbosity > 1:
            print("Will skip trials older than:", sufficiently_old)

        # Date for reporting to be due has cutoff is 1 year (365 days) (by law,
        # trials must report a year after finishing) plus 4 weeks (28 days)
        # allowance (it takes that long for submissions to enter register)
        due_date_cutoff = pd.Timestamp(last_scrape_date - relativedelta(years=1) - datetime.timedelta(days=28))
        if verbosity > 1:
            print("Due date cutoff:", due_date_cutoff)

        euctr_cond = load_data_into_pandas(opentrials_db, sufficiently_old)

        cleanup_dataset(euctr_cond)

        spons = prepare_sponsor_data(euctr_cond)

        # deal with the name of the sponsor separately to the status
        spon_name = spons[['eudract_number', "name_of_sponsor"]].reset_index(drop=True)
        spon_type = spons[['eudract_number', 'eudract_number_with_country', 'status_of_the_sponsor']].reset_index(drop=True)
        spon_status = create_spon_status(spon_type)

        grouped = create_dataframe(euctr_cond)
        clean_and_enhance_dataframe(grouped, due_date_cutoff, euctr_url)
        
        final_cols = ['trial_id', 'number_of_countries', 'min_end_date', 'max_end_date', 'comp_date', 
                      'has_results', 'includes_pip', 'exempt', 'single_blind', 'rare_disease', 'phase', 
                      'bioequivalence_study', 'health_volunteers', 'trial_status', 'any_terminated', 'all_terminated', 
                      'results_expected', 'all_completed_no_comp_date', 'trial_title', 'trial_url', 
                      'comp_date_while_ongoing', 'contains_non_eu', 'only_non_eu']

        final_start = grouped[final_cols].reset_index(drop=True)

        # merge in the sponsor status field
        euctr_final = final_start.merge(spon_status[['eudract_number', 'sponsor_status']], left_on = 'trial_id', right_on = 'eudract_number')

        # finally merge in the sponsor names 
        # (which should double up where relevant)
        euctr_final = euctr_final.merge(spon_name, left_on = 'trial_id', right_on = 'eudract_number')

        # drop rows that are exact duplicates
        euctr_final = euctr_final.drop_duplicates().reset_index(drop=True)
        
        # get rid of repeated columns from joins and index resets
        euctr_final = euctr_final[euctr_final.columns[~((euctr_final.columns.str.contains('eudract_number')) | (euctr_final.columns.str.contains('index')))]]

        col_order = ['trial_id', 'number_of_countries', 'min_end_date', 'max_end_date', 'comp_date', 'has_results', 
                     'includes_pip', 'exempt', 'single_blind', 'rare_disease', 'phase', 'bioequivalence_study', 
                     'health_volunteers', 'trial_status', 'any_terminated', 'all_terminated', 'results_expected', 
                     'all_completed_no_comp_date', 'sponsor_status', 'name_of_sponsor', 'trial_title', 'trial_url', 
                     'comp_date_while_ongoing', 'contains_non_eu', 'only_non_eu']

        euctr_final = euctr_final[col_order].reset_index(drop=True)

        before_hash = hashlib.sha512(open(settings.SOURCE_CSV_FILE).read().encode("utf-8")).digest()
        euctr_final.to_csv(settings.SOURCE_CSV_FILE, index=False)
        after_hash = hashlib.sha512(open(settings.SOURCE_CSV_FILE).read().encode("utf-8")).digest()

        # Update "got_from_db" only if there were changes in database
        # (to stop git history being contaminated)
        if before_hash != after_hash:
            if verbosity > 1:
                print("Changes being recorded in meta file")
            with atomic_write(settings.SOURCE_META_FILE, overwrite=True) as f:
                out = collections.OrderedDict([
                    ('scrape_date', last_scrape_date.isoformat()),
                    ('due_date_cutoff', due_date_cutoff.isoformat()),
                    ('got_from_db', datetime.datetime.now().isoformat())
                ])
                f.write(json.dumps(out, indent=4, sort_keys=True))
        else:
            if verbosity > 1:
                print("No changes, not updating meta file")
