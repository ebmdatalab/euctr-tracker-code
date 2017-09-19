import pandas

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Updates social sharing handles of sponsors from Google spreadsheet'

    def handle(self, *args, **options):
        trialstracker_csv_url = "https://docs.google.com/spreadsheets/d/1htoTrIFzHoqsj46KSFASa2paSwc7DfDVdHZhQO0Sv3U/export?format=csv"
        trialstracker_csv = pandas.read_csv(trialstracker_csv_url)
        #print(trialstracker_csv)
        a = pandas.DataFrame()
        a['name'] = trialstracker_csv['lead_sponsor']
        a['twitter'] = trialstracker_csv['twitter_handle']
        a = a.dropna(subset=['twitter'])

        eutrialstracker_csv_url = "https://docs.google.com/spreadsheets/d/1gRTGzmwE6uL_weA6zskZuUsM_CgMoMsHKTMZ9T2QVUU/export?format=csv"
        eutrialstracker_csv = pandas.read_csv(eutrialstracker_csv_url)
        b = pandas.DataFrame()
        #print(eutrialstracker_csv)
        b['name'] = eutrialstracker_csv['Sponsor name']
        b['twitter'] = eutrialstracker_csv['Twitter']
        b = b.dropna(subset=['twitter'])

        combined = pandas.concat([a, b], ignore_index=True)
        combined.to_csv("../../euctr-tracker-data/social_handles.csv", index=False)





