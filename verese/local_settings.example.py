from settings import INSTALLED_APPS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'verese.sqlite',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        # when using mysql you need INNODB to enable transactions
        # 'OPTIONS': {
        #            'init_command': 'SET storage_engine=INNODB',
        #            }
    }
}

# locally installed apps
INSTALLED_APPS = INSTALLED_APPS + (
    )

DEBUG=True
LOCAL_DEVELOPMENT=True
SITE_EDITION="local"

VERESE_EMAIL_FROM = 'manager@verese.net'
