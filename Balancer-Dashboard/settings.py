import os
# Settings file for the gateway gui
VERSION = "0.1"

HOSTS_ALLOW = "0.0.0.0"
PORT = '80'

DEBUG = True

TIMEOUT = 5

SECRET_KEY = "dhfsufghfbshfoiajnvojds<adwasojos"

DATABASE_HOST = 'localhost'
DATABASE_PORT = '5432'

POSTGRES_DB = 'balancer'
POSTGRES_USER = 'user'
POSTGRES_PASSWORD = 'password'

SQLALCHEMY_DATABASE_URI = ('postgresql://%s:%s@%s:%s/%s' % (POSTGRES_USER, POSTGRES_PASSWORD, DATABASE_HOST,
                                                            DATABASE_PORT, POSTGRES_DB))
SQLALCHEMY_TRACK_MODIFICATIONS = True

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Default log file names for developing and production
if DEBUG:
    LOG_FILE = BASE_PATH + "/log/development.log"
else:
    LOG_FILE = BASE_PATH + "/log/production.log"

# Client app Config

