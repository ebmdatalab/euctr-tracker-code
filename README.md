# euctr-tracker

Installation
============

Using Python 3, create and enter a virtualenv, as [described
here](https://docs.djangoproject.com/en/1.10/intro/contributing/).

Install required packages.

```
pip install -r requirements.txt
```

Then run the application.

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


