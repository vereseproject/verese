import os
import sys

os.chdir("/home/verese.net/domains/beta.verese.net/public_html")
execfile('env/bin/activate_this.py', dict(__file__='env/bin/activate_this.py'))
sys.path.insert(0, 'verese')

os.environ['DJANGO_SETTINGS_MODULE'] = "verese.settings"

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
