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
DEFAULT_CONFIG_FILE = '/etc/testagent/testagent.conf'
DEFAULT_SELFASSESSMENT_DIR = '/etc/testagent/selfassessment'
subscription_settings = dict()
apis_settings = dict()

class CeleryConfiguration(object):
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_EVENT_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_IMPORTS = ('testagent.tasks',)



'''
configuration args
'''
define("conf", default=DEFAULT_CONFIG_FILE, help="Configuration file", group="main")


'''
subscription service settings
'''

define("subscription_port", default=8081,
       help="Subscription service listening port", type=int, group="subscription service")
define("subscription_address", default='',
       help="Subscription service listening address", type=str, group="subscription service")
define("subscription_server_cert", type=str, default=None,
       help="SSL certificate file for the subscription service", group="subscription service")
define("subscription_server_key", type=str, default=None,
       help="SSL key file for the subscription service", group="subscription service")
define("subscription_client_ca", type=str, default=None,
       help="SSL Certification Authority for TLS client authentication", group="subscription service")

'''
apis service settings
'''
define("apis_port", default=8080,
       help="APIs listening port", type=int, group="apis service")
define("apis_address", default='',
       help="APIs listening address", type=str, group="apis service")
define("apis_server_cert", type=str, default=None,
       help="SSL certificate file", group="apis service")
define("apis_server_key", type=str, default=None,
       help="SSL key file", group="apis service")
define("apis_client_ca", type=str, default=None,
       help="SSL Certification Authority for TLS client authentication", group="apis service")

'''
self assessment
'''
define("selfassessment_dir", default=DEFAULT_SELFASSESSMENT_DIR, help="Directory where to grab configurations from", group="self assessment")


'''
events management
'''
define("enable_events", type=bool, default=True,
       help="Periodically enable Celery events" , group="main")
define("persistent", type=bool, default=False,
       help="Enable persistent mode", group="events")
define("inspect_timeout", default=1000, type=float,
       help="Inspect timeout (in milliseconds)", group="events")
define("max_tasks", type=int, default=10000,
       help="Maximum number of tasks to keep in memory", group="main")
define("db", type=str, default='testagent',
       help="Database file", group="events")

'''
configuration for celery
'''
define("timezone", default="Europe/Rome", help="Timezone (default: Europe/Rome)", type=str, group="main")



'''
define("broker_url", default="amqp://guest:guest@localhost/",
       help="Broker URL - For now please use only AMQP if you are reporting to a TestManager" +
            " otherwise the software will crash. " +
            "(I don't know) (default: amqp://guest:guest@localhost/)", type=str)
define("backend_broker_url", default="", help="Backend broker URL", type=str)


define("results_exchange_name", default="collector_agents",
       help="Exchange name for reporting results (default: collector_agents)", type=str, group="subscription")
define("results_exchange_type", default="direct",
       help="Exchange type for reporting results (default: direct)", type=str, group="subscription")
define("results_queue_name", default="queue", group="subscription")
define("results_routing_key", default="key-test",
       help="Routing key for reporting results (default: key-test)", type=str, group="subscription")
'''

selfassessment = SelfAssessment("/etc/testagent")


define("debug", default=False,
       help="Run in debug mode", type=bool, group="main")

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_EVENT_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_IMPORTS = ('testagent.tasks',)

default_options = options
