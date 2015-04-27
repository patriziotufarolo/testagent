from __future__ import absolute_import

__author__ = 'Patrizio Tufarolo'
__email__ = 'patrizio.tufarolo@studenti.unimi.it'
'''
Project: testagent
Author: Patrizio Tufarolo <patrizio.tufarolo@studenti.unimi.it>
Date: 20/04/15
'''
import types
from tornado.options import define
from tornado.options import options
from testagent.selfassessment import SelfAssessment
DEFAULT_CONFIG_FILE = 'testagentconfig.py'
BROKER_URL = 'amqp://guest:guest@localhost//'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_EVENT_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
#CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend'
CELERY_TIMEZONE = 'Europe/London'
CELERY_IMPORTS = ('testagent.tasks',)
selfassessment = SelfAssessment("/etc/cumulus")



define("port", default=8080,
       help="Run on the given port", type=int)

define("address", default='',
       help="Run on the given address", type=str)

define("debug", default=False,
       help="Run in debug mode", type=bool)
define("inspect_timeout", default=1000, type=float,
       help="Inspect timeout (in milliseconds)")
define("max_tasks", type=int, default=10000,
       help="Maximum number of tasks to keep in memory")
define("db", type=str, default='testagent',
       help="Database file")
define("persistent", type=bool, default=False,
       help="Enable persistent mode")
define("broker_api", type=str, default=None,
       help="Inspect broker e.g. http://guest:guest@localhost:15672/api/")
define("certfile", type=str, default=None,
       help="SSL certificate file")
define("keyfile", type=str, default=None,
       help="SSL key file")
define("xheaders", type=bool, default=False,
       help="Enable support for the 'X-Real-Ip' and 'X-Scheme' headers.")

define("conf", default=DEFAULT_CONFIG_FILE,
       help="Configuration file")
define("enable_events", type=bool, default=True,
       help="Periodically enable Celery events")
define("format_task", type=types.FunctionType, default=None,
       help="Use custom task formatter")
define("natural_time", type=bool, default=True,
       help="Show time in relative format")

default_options = options
