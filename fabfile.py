#
# Fabric script to manage verese
#

import os
from time import strftime

from fabric.api import env, run, sudo, local, \
     cd, hosts, runs_once, prompt, require

env.user = "verese"
env.hosts = ["dev.verese.net"]
env.backup_dir = "/home/verese/backup"

@runs_once
def master():
    """ The beta environment """
    env.remote_app_dir = "/home/verese/master"
    env.branch = "master"
    env.database = "master"

@runs_once
def dev():
    """ The beta environment """
    env.remote_app_dir = "/home/verese/dev"
    env.branch = "dev"
    env.database = "dev"

@runs_once
def experimental():
    """ The experimental environment """
    env.remote_app_dir = "/home/verese/experimental"
    env.branch = "experimental"
    env.database = None

def update_code():
    """
    Push code to github
    Pull code from server
    """
    require('remote_app_dir', provided_by=[dev, master, experimental])

    local("git push origin master dev experimental")

    with cd(env.remote_app_dir):
        run("git checkout %s" % env.branch)
        run("git pull origin %s" % env.branch)

def backup(files=True, database=True):
    """
    Backup
    """
    require('branch', provided_by=[dev, master, experimental])
    date = strftime("%Y%m%d%H%M")

    if files:
        run("tar czf %s/%s/verese-%s-%s.tar %s"
             % (env.backup_dir, env.branch, env.branch, date, env.remote_app_dir)
            )

    if database:
        run("pg_dump %s | gzip > %s/%s/verese-database-%s-%s.gz" %\
            (env.database, env.backup_dir, env.branch, env.branch, date)
            )

def deploy(do_backup=True, do_update=True):
    require('branch', provided_by=[dev, master, experimental])
    require('remote_app_dir', provided_by=[dev, master, experimental])

    if do_backup == True:
        backup()

    if do_update == True:
        update_code()

    if env.branch == "experimental":
        # delete database
        run("rm /home/verese/experimental/verese/verese.sqlite")

    with cd(env.remote_app_dir):
        run("bash ./scripts/build-environment.sh")

        if env.branch == "experimental":
            # load initial data
            run("./bin/python manage.py loaddata demo")

def list_backups():
    require('branch', provided_by=[dev, master, experimental])
    run("ls %s/%s" % (env.backup_dir, env.branch))

def restart():
    sudo("/usr/bin/supervisorctl restart %s" % env.branch, shell=False)
