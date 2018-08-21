# euctr-tracker

## How it works

### Code and data layout

There are two repos which should be checked out in a common directory.
One is `euctr-tracker-code`, and the other is `euctr-tracker-data`.

The latter contains JSON files which are loaded into memory by the
`frontend` Django app in `euctr-tracker-code` loads the contents of
the JSON files into memory.

Thus we avoid using a database. Originally this design made sense as
the data structure was simple, and the source data was in a third
party database over which we had no control.  This makes less sense
now as we run our own database for the source data, and the model has
become more complex; we do, however, maintain the advantage of
maintaining all the historic data in git.

### Service operation

Once a month, we run a shell script
`crawl-and-dump-eutrialstracker_live.sh` that does two things:

1. It executes command that uses `scrapy` to scrape the EUCTR
register, via cron.  This writes to a local postgres database,
`euctr`.  It takes up to 4 days to run - it must do a full scrape each
time, due to the design of the website we are scraping.
2. It runs the Djano management command `get_trials_from_db`, which
creates a CSV based on this data, and writes it to the
`euctr-tracker-data` directory.

Every 30 minutes, `loaddata-eutrialstracker_live.sh` is also run. If
any uncommitted changes are found in the `euctr-tracker-data`
directory, it executes the django management command
`update_trials_json`, to create the set of JSON files which drive the
website.

However, this second shell script will often fail to run to the end,
because there's a sponsors CSV file (see *Terminology* section, below)
which requires manual normalisation every time new sponsors are added
to it. If this happens, the `update_trials_json` script exits early
with a message (which is also emailed to a recipient specified in the
django settings file).

The recipient should exit the CSV and update it directly in the
`euctr-tracker-data` repo; `loaddata-eutrialstracker_live.sh` should
pick this up on the next run.  At this stage, all the latest generated
files are committed to the `euctr-tracker-data` repostory.


## Development

Install these Python development packages before you begin. For
example, on a Debian-based system:

```
apt install python3 python3-venv build-essential python3-dev phantomjs
```

Using Python 3, create and enter a virtualenv, as [described
here](https://docs.djangoproject.com/en/1.10/intro/contributing/).
For example:

```
python3.5 -m venv venv
. venv/bin/activate
```

Install required Python packages.

```
pip install -r requirements.txt
```

Set environment variables required.

```
export EUCTR_SECRET_KEY= # random longish string for sessions
export EUCTR_DEBUG= # yes or no
export EUCTR_OPENTRIALS_DB=postgres://<account_name>:<password>@<servername>/warehouse

export EUCTR_GOOGLE_TRACKING_ID= # optional Analytics id, e.g. UA-nnnnnnnn-n
export EUCTR_CRAWLERA_APIKEY= # for crawler proxying
```

Checkout the data respository.

```
cd ..
git clone git@github.com:ebmdatalab/euctr-tracker-data.git
cd -
```
Run the application.

```
cd euctr
./manage.py runserver
```

There are a few tests.

```
./manage.py test
```

## Deployment

We use fabric to deploy over SSH to a pet server.

```
fab deploy:live
```

The code and data are updated via git from the master branch
of their repositories.

The configuration is in `fabfile.py` and the `deploy` directory.

When settings up a new server:
* Put environment settings live in `/etc/profile.d/eutrialstracker_live.sh`
* Put SSH keys for the git repositories in `/var/www/eutrialstracker_live/ssh-keys`


## Loading new data

The frontend application reads data from static JSON files in
the `../euctr-tracker-data/` directory.

1. Set the location of a PostgreSQL database. This is only used as
an intermediate store for the crawler to keep data in. The live website
doesn't use it.

```
export EUCTR\_OPENTRIALS\_DB=postgres://username:password@hostname/dbname
```

If you need the schema, look in `euctr/crawl/schema.sql`.

2. Run the EUCTR crawler to populate the PostgreSQL database by running
with a date range:

```
cd euctr
./manage.py run_crawler 2004-01-01 2017-09-19
```

Or update results from a particular query, e.g. a specific trial id:

```
./manage.py run_crawler --query=2004-000012-13
```

3. Update `../euctr-tracker-data/trials.csv` from the PostgreSQL
database by running:

```
./manage.py get_trials_from_db
```

This assumes the table is called "euctr". It uses the SQL script
`opentrials-to-csv.sql` for the calculations and conversions needed.

4. Regenerate the JSON files from the CSV file by running:

```
./manage.py update_trials_json
```


## Terminology

The spreadsheet `../euctr-tracker-data/normalized_sponsor_names.xlsx` contains
normalized versions of the names for trials that are listed in the register.

`normalized_name_only`: This column represents normalization based only on
sponsor name or very simple research. Different spelling/abbreviations of a
sponsor name and divisions/subsidiaries of the same sponsor will be normalized
to the same parent sponsor name (ex: DrugCompany Inc., DrugCompany Incorporated
and DrugCompany Generics would all be normalized to the generic DrugCompany
Inc.). This also includes, where possible, instances in which a sponsor name is
implemented in different languages and also attempts to consolidate hospital
systems under a single normalized name (ex: Putting hospitals in the Copenhagen
University hospital system together or matching an old NHS Trust name to the
new name). If a sponsor is identified in their sponsor name as part of another
company (ex: “doing business as” or “a wholly owned subsidiary of” ) then that
company will be normalized to the parent company identified (ex:
“GenericCompany Inc, a wholly owned subsidiary of Drugs Inc.” would normalize
to “Drugs Inc.“). Attempts are also made to make sponsor names more uniform and
readable with the removal of extraneous text or names in all capital letters.

`normalized_name`: This column represents an effort to normalize based on more in
depth research into mergers, acquisitions and name changes for corporate
entities. Proof is sought to account changes in corporate ownership and where
it is believed responsibility for reporting would ultimately be vested. Proof
of notable acquisitions is given in the spreadsheet for changes made in this
column.
