from fabric.api import run, sudo, put
from fabric.api import prefix, warn, abort
from fabric.api import settings, task, env, shell_env
from fabric.contrib.project import rsync_project
from fabric.context_managers import cd

from datetime import datetime
import json
import os
import requests
import sys

env.hosts = ['smallweb1.openprescribing.net']
env.forward_agent = True
env.colorize_errors = True
env.user = 'root'

environments = {
    'live': 'eutrialstracker_live',
    #'staging': 'eutrialstracker_staging'
}

def make_directory():
    run('mkdir -p %s' % (env.path))

def venv_init():
    run('[ -e venv ] || python3.5 -m venv venv')

def pip_install():
    with prefix('source venv/bin/activate'):
	run('pip install -q -r requirements.txt')

def upload_files():
    put("requirements.txt", ".")
    rsync_project(env.path, "euctr", extra_opts="--quiet")
    rsync_project(env.path, "data", extra_opts="--quiet")
    rsync_project(env.path, "deploy", extra_opts="--quiet")

def setup_nginx():
    run('ln -sf %s/deploy/supervisor-%s.conf /etc/supervisor/conf.d/%s.conf' % (env.path, env.app, env.app))
    run('ln -sf %s/deploy/nginx-%s /etc/nginx/sites-enabled/%s' % (env.path, env.app, env.app))
    run('chown -R www-data:www-data /var/www/%s' % (env.app))
    run('service supervisor restart')
    run('nginx -t && service nginx restart')

#def run_migrations():
#    if env.environment == 'live':
#        with prefix('source .venv/bin/activate'):
#            run('cd openprescribing/ && python manage.py migrate '
#                '--settings=openprescribing.settings.live')
#    else:
#        warn("Refusing to run migrations in staging environment")

@task
def deploy(environment, branch='master'):
    if environment not in environments:
        abort("Specified environment must be one of %s" %
              ",".join(environments.keys()))
    env.app = environments[environment]
    env.environment = environment
    env.path = "/var/www/%s" % env.app
    env.branch = branch

    make_directory()
    with cd(env.path):
	venv_init()
	upload_files()
        pip_install()
	setup_nginx()
        #run_migrations()




