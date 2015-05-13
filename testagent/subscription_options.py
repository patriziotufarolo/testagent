from __future__ import absolute_import

__author__ = 'Patrizio Tufarolo'
__email__ = 'patrizio.tufarolo@studenti.unimi.it'
'''
Project: testagent
Author: Patrizio Tufarolo <patrizio.tufarolo@studenti.unimi.it>
Date: 13/05/15
'''

from tornado.options import define
from tornado.options import parse_config_file
from tornado.options import options

DEFAULT_SUBSCRIPTION_FILE = '/etc/testagent/subscription.conf'

define("subscription_conf", default=DEFAULT_SUBSCRIPTION_FILE, help="Subscription settings", callback=lambda file_path: parse_config_file(file_path), group="s")
define("broker_url", default="amqp://guest:guest@localhost/",
       help="Broker URL - For now please use only AMQP if you are reporting to a TestManager" +
            " otherwise the software will crash. " +
            "(I don't know) (default: amqp://guest:guest@localhost/)", type=str, group="subscription")
define("backend_broker_url", default="a", help="Backend broker URL", type=str, group="subscription")


define("results_exchange_name", default="collector_agents",
       help="Exchange name for reporting results (default: collector_agents)", type=str, group="subscription")
define("results_exchange_type", default="direct",
       help="Exchange type for reporting results (default: direct)", type=str, group="subscription")
define("results_queue_name", default="queue", group="subscription")
define("results_routing_key", default="key-test",
       help="Routing key for reporting results (default: key-test)", type=str, group="subscription")