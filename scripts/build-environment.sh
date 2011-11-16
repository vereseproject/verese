#!/bin/bash
#
# invoke as
# ~$ bash ./scripts/build-environment.sh
#
# use enviroment variable PIP to set the path to pip python package
# manager.
#
ENV="env"

if [ "$PIP" == "" ];
then
  PIP="pip"
fi

# if env exists activate it
if [ -d $ENV ];
then
  source $ENV/bin/activate || exit;
fi

$PIP -E $ENV install -r scripts/dependencies.txt

# activate environment
source $ENV/bin/activate

cd verese

# if no local_settings, create them
if [ ! -e local_settings.py ];
then
    cp local_settings.example.py local_settings.py
    echo "Demo local_settings.py installed, maybe you want to change them"
fi

# syncdb
echo "Syncing db"
python manage.py syncdb --noinput

echo "Migrating db"
python manage.py migrate

echo ""
echo "Installation complete"
echo ""
echo "Activate your environment with"
echo "~$ source env/bin/activate"
echo ""
echo "Run your server with"
echo "(env)~verese$ python manage.py runserver"
echo ""
echo "Load demo data with"
echo "(env)~verese$ python manage.py loaddata demo"
echo ""
