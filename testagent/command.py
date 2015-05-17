from __future__ import absolute_import
from __future__ import print_function

__author__ = 'Patrizio Tufarolo'
__email__ = 'patrizio.tufarolo@studenti.unimi.it'
'''
Project: testagent
Author: Patrizio Tufarolo <patrizio.tufarolo@studenti.unimi.it>
Date: 20/04/15
'''

import sys
import atexit
import signal
import logging
import threading
from ssl import CERT_REQUIRED

from tornado.options import options
from tornado.options import parse_command_line, parse_config_file
from tornado.log import enable_pretty_logging
from tornado import ioloop
from celery.bin.base import Command

from testagent import __version__
from testagent.app import TestAgent
from testagent.app_subscription import TestAgentSubscription
from testagent.options import subscription_settings
from testagent.options import apis_settings
from testagent.options import CeleryConfiguration
from testagent.utils import abs_path
from testagent.options import DEFAULT_CONFIG_FILE
from testagent.subscription_options import DEFAULT_SUBSCRIPTION_FILE
import testagent.options as testagentoptions
from testagent.selfassessment import SelfAssessment
logger = logging.getLogger(__name__)

class TestAgentCommand(Command):

    def run_from_argv(self, prog_name, argv=None, command=None):

        # PARSE COMMAND LINE AND CONFIG
        argv = list(filter(self.testagent_option, argv))
        parse_command_line([prog_name] + argv)
        try:
            parse_config_file(options.conf, final=False)
            parse_command_line([prog_name] + argv)
        except IOError:
            if options.conf != DEFAULT_CONFIG_FILE:
                raise
        try:
            parse_config_file('subscription.conf', final=False)
            parse_command_line([prog_name] + argv)
        except IOError:
            if options.subscription_conf != DEFAULT_SUBSCRIPTION_FILE:
                raise


        #
        # DEBUG MODE LOGGING
        #

        if options.debug and options.logging == 'info':
            options.logging = "debug"
            enable_pretty_logging()

        testagentoptions.SelfAssessment = SelfAssessment(options.selfassessment_dir)
        try:
            io_loop = ioloop.IOLoop.instance()
            self.subscription_start()

            if (True
                and options.broker_url
                and options.results_exchange_name
                and options.results_exchange_type
                and options.results_queue_name
                and options.results_routing_key
                and options.tasks_exchange_name
                and options.tasks_exchange_name
                and options.tasks_exchange_type
                and options.tasks_queue_name):
                self.testagent_start()

            io_loop.start()
        except KeyboardInterrupt:
            sys.exit()

    def subscription_start(self):
        #
        # SERVICE START
        #
        #
        # SUBSCRIPTION SERVICE SETTINGS
        #

        subscription_settings["debug"] = options.debug

        if options.subscription_server_cert and options.subscription_server_key:
            subscription_settings["ssl"] = dict(
                certfile=abs_path(options.subscription_server_cert),
                keyfile=abs_path(options.subscription_server_key)
            )
            if options.subscription_client_ca:
                subscription_settings["ssl"]["ca_certs"] = abs_path(options.subscription_client_ca)
                subscription_settings["ssl"]["cert_reqs"] = CERT_REQUIRED

        self.subscription_service = TestAgentSubscription(options=options, **subscription_settings)

        atexit.register(self.subscription_service.stop)

        self.print_subscription_banner('ssl' in subscription_settings)
        self.subscription_service.start()

    def testagent_start(self):

        apis_settings['debug'] = options.debug

        if options.apis_server_cert and options.apis_server_key:
            apis_settings["ssl"] = dict(
                certfile=abs_path(options.apis_server_cert),
                keyfile=abs_path(options.apis_server_key)
            )
            if options.subscription_client_ca:
                apis_settings["ssl"]["ca_certs"] = abs_path(options.apis_client_ca)
                apis_settings["ssl"]["cert_reqs"] = CERT_REQUIRED
        if options.broker_url[:4] != "amqp":
            raise Exception("Only AMQP is supported")
        CeleryConfiguration.BROKER_URL = options.broker_url
        CeleryConfiguration.CELERY_TIMEZONE = options.timezone
        CeleryConfiguration.CELERY_RESULT_BACKEND = options.backend_broker_url
        from kombu import Queue, Exchange
        CeleryConfiguration.CELERY_DEFAULT_QUEUE = options.tasks_queue_name
        CeleryConfiguration.CELERY_QUEUES = [
            Queue(options.tasks_queue_name,
                  exchange=Exchange(options.tasks_exchange_name, type=options.tasks_exchange_type),
                  routing_key=options.tasks_routing_key
                  )
        ]

        CeleryConfiguration.BROKER_USE_SSL = False
        if options.broker_ssl_enable and options.broker_ssl_ca:
            CeleryConfiguration.BROKER_USE_SSL = {
                "ca_certs": options.broker_ssl_cacerts
            }
            if options.broker_ssl_verifycert and options.broker_ssl_keyfile and options.broker_ssl_certfile:
                CeleryConfiguration.BROKER_USE_SSL["keyfile"] = options.broker_ssl_keyfile,
                CeleryConfiguration.BROKER_USE_SSL["certfile"] = options.broker_ssl_certfile,
                CeleryConfiguration.BROKER_USE_SSL["cert_reqs"] = CERT_REQUIRED,

        self.app.config_from_object(CeleryConfiguration)

        self.app.connection = self.app.broker_connection

        self.app.loader.import_default_modules()

        testagent = TestAgent(capp=self.app, options=options, **apis_settings)
        self.testagent = testagent
        testagentoptions.testagent = testagent
        atexit.register(testagent.stop)

        def sigterm_handler(signal, frame):
            logger.info('SIGTERM, shutting down')
            sys.exit(0)

        signal.signal(signal.SIGTERM, sigterm_handler)

        self.print_banner('ssl' in apis_settings)

        testagent.start()


    def handle_argv(self, prog_name, argv, command=None):
        return self.run_from_argv(prog_name, argv)

    def early_version(self, argv):
        if '--version' in argv:
            print(__version__, file=self.stdout)
            super(TestAgentCommand, self).early_version(argv)

    @staticmethod
    def testagent_option(arg):
        name, _, value = arg.lstrip('-').partition("=")
        name = name.replace('-', '_')
        return hasattr(options, name)

    def print_banner(self, ssl):
        logger.info(
            "APIs available at http%s://%s:%s",
            's' if ssl else '',
            options.apis_address or 'localhost',
            options.apis_port
        )

    def print_subscription_banner(self, ssl):
        logger.info(
            "Subscription service available at http%s://%s:%s",
            's' if ssl else '',
            options.subscription_address or 'localhost',
            options.subscription_port
        )