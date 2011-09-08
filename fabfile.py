#
# Fabric script to manage verese
#

import os
from time import strftime

from fabric.api import env, run, sudo, local, \
     cd, hosts, runs_once, prompt, require

env.user = "verese"
env.hosts = ["beta.verese.net:2222"]
env.backup_dir = "/home/verese/backup"

@runs_once
def beta():
    """ The beta environment """
    env.remote_app_dir = "/home/verese/domains/beta.verese.net/verese/"
    env.branch = "dev"
    env.database = "beta"

def update_code():
    """
    Push code to github
    Pull code from server
    """
    require('remote_app_dir', provided_by=[beta])

    local("git push origin master dev")

    with cd(env.remote_app_dir):
        run("git checkout %s" % env.branch)
        run("git pull origin %s" % env.branch)

def backup(files=True, database=True):
    """
    Backup
    """
    require('branch', provided_by=[beta])
    date = strftime("%Y%m%d%H%M")

    if files:
        with cd(os.path.join(env.remote_app_dir, '..')):
            run("tar czf %s/%s/verese-%s-%s.tar "
                "verese" % (env.backup_dir, env.branch, env.branch, date)
                )

    if database:
        with cd(os.path.join(env.remote_app_dir, '..')):
            run("mysqldump %s | gzip > %s/%s/verese-database-%s-%s.gz" %\
                (env.database, env.backup_dir, env.branch, env.branch, date)
                )

def deploy(do_backup=True, do_update=True):
    require('branch', provided_by=[beta])
    require('remote_app_dir', provided_by=[beta])

    if do_backup == True:
        backup()

    if do_update == True:
        update_code()

    with cd(env.remote_app_dir):
        run("bash ./scripts/build-environment.sh")

def list_backups():
    require('branch', provided_by=[beta])
    run("ls %s/%s" % (env.backup_dir, env.branch))

def restart():
    sudo("/etc/init.d/apache2 graceful", shell=False)
