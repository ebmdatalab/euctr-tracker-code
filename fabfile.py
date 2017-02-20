from fabric.api import run, sudo
from fabric.api import prefix, warn, abort
from fabric.api import settings, task, env, shell_env
from fabric.context_managers import cd

from datetime import datetime
import json
import os
import requests

env.hosts = ['smallweb1.openprescribing.net']
env.forward_agent = True
env.colorize_errors = True
env.user = 'root'

environments = {
    'production': 'eutrialstracker_live',
    #'staging': 'eutrialstracker_staging'
}

def make_directory():
    run('mkdir -p %s' % (env.path))

def venv_init():
    run('[ -e venv ] || python3.5 -m venv venv')

def pip_install():
    if filter(lambda x: x.startswith('requirements'),
              [x for x in env.changed_files]):
        with prefix('source venv/bin/activate'):
            run('pip install -r requirements.txt')

#def run_migrations():
#    if env.environment == 'production':
#        with prefix('source .venv/bin/activate'):
#            run('cd openprescribing/ && python manage.py migrate '
#                '--settings=openprescribing.settings.production')
#    else:
#        warn("Refusing to run migrations in staging environment")

@task
def deploy(environment, branch='master'):
    if environment not in environments:
        abort("Specified environment must be one of %s" %
              ",".join(environments.keys()))
    env.app = environments[environment]
    env.environment = environment
    env.path = "/webapps/%s" % env.app
    env.branch = branch

    make_directory()
    with cd(env.path):
	venv_init()
        #pip_install()
        #run_migrations()
        #graceful_reload()




