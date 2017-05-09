# euctr-tracker

Development
===========

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

Deployment
==========

We use fabric to deploy over SSH to a pet server. 

```
fab deploy:live
```

WARNING: Currently the code is copied from your local directory.
When the paper is published, we can perhaps make the github 
repository public, so the server can easily fetch the code 
directly.

The configuration is in `fabfile.py` and the `deploy` directory.

Environment settings live in `/etc/profile.d/eutrialstracker_live.sh`


Loading new data
================

The frontend application reads data from static JSON files 
in the `data/` directory. There's no local database.

1. Set the location of the OpenTrials PostgreSQL database.

```
export OPENTRIALS\_DB=postgres://username:password@hostname/dbname
```

2. Update `data/trials.csv` from the PostgreSQL database by running:

```
cd euctr
./manage.py get_trials_from_db
```

This assumes the table is called "euctr". It uses the SQL script
`opentrials-to-csv.sql` for the calculations and conversions needed.

3. Regenerate the JSON files from the CSV file by running:

```
./manage.py update_trials_json
```

4. Update the `DATA_SOURCE_DATE` in `euctr/settings.py`.

