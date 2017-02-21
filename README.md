# euctr-tracker

Development
===========

Install these Python development packages before you begin. For
example, on a Debian-based system:

```
apt install python3 python3-venv build-essential python3-dev
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
```

Run the application.

```
cd euctr
./manage.py runserver
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

1. Get hold of a dump from OpenTrials EUCTR SQL databsae. 
It'll be called something like:

```
opentrials-warehouse-euctr-20170123.dump
```

Restore that into a PostgreSQL database.

2. Export that to `data/trials.csv` using the SQL script
`data/opentrials-to-csv.sql`.

```
psql euctr --quiet -f opentrials-to-csv.sql -o trials.csv
```

3. The frontend application reads data from static JSON files 
in the `data/` directory. There's no database yet.

Then regenerate the JSON files from the CSV file by running it:

```
./manage.py loadtrialsdata
```

Update the `DATA_SOURCE_DATE` in `euctr/settings.py`.





