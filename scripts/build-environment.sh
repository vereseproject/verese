#!/bin/bash
#
# invoke as
# ~$ bash ./scripts/build-environment.sh

# install django
pip -E env install django

# activate environment
source env/bin/activate

# install the rest
pip install south
# pip install piston
# pip install tastypie
pip install django_extensions
pip install ipython
pip install django-taggit
pip install werkzeug


pip -E env install -e git://github.com/mozilla/django-piston.git
