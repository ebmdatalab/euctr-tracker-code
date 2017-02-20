# euctr-tracker

Installation
============

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

Run the application.

```
cd euctr
./manage.py runserver
```


Loading new data
================

There's no database yet. Data is read from static files in
the `data/` directory.

You can regenerate the JSON files in there from the XLS source
file with this command.

```
./manage.py loadtrialsdata
```


