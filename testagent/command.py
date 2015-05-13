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
from ssl import CERT_REQUIRED

from tornado.options import options
from tornado.options import parse_command_line, parse_config_file
from tornado.log import enable_pretty_logging
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
            if options.conf != DEFAULT_CONFIG_FILE or options.subscription_conf != DEFAULT_SUBSCRIPTION_FILE:
                raise

        #
        # DEBUG MODE LOGGING
        #

        if options.debug and options.logging == 'info':
            options.logging = "debug"
            enable_pretty_logging()

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

        subscription_service = TestAgentSubscription(options=options, **subscription_settings)
        atexit.register(subscription_service.stop)

        #
        # SUBSCRIPTION SERVICE START
        #
        self.print_subscription_banner('ssl' in apis_settings)
        try:
            subscription_service.start()
        except (KeyboardInterrupt, SystemExit):
            sys.exit()

        #
        # APIs SERVICE SETTINGS
        #

        apis_settings['debug'] = options.debug

        if options.apis_server_cert and options.apis_server_key:
            apis_settings["ssl"] = dict(
                certfile=abs_path(options.apis_server_cert),
                keyfile=abs_path(options.apis_server_key)
            )
            if options.subscription_client_ca:
                apis_settings["ssl"]["ca_certs"] = abs_path(options.apis_client_ca)
                apis_settings["ssl"]["cert_reqs"] = CERT_REQUIRED


        CeleryConfiguration.BROKER_URL = options.broker_url
        CeleryConfiguration.CELERY_TIMEZONE = options.timezone
        CeleryConfiguration.CELERY_RESULT_BACKEND = options.backend_broker_url

        self.app.config_from_object(CeleryConfiguration)

        self.app.connection = self.app.broker_connection

        self.app.loader.import_default_modules()

        testagent = TestAgent(capp=self.app, options=options, **apis_settings)
        self.testagent = testagent
        atexit.register(testagent.stop)

        def sigterm_handler(signal, frame):
            logger.info('SIGTERM, shutting down')
            sys.exit(0)

        signal.signal(signal.SIGTERM, sigterm_handler)

        self.print_banner('ssl' in apis_settings)

        try:
            testagent.start()
        except (KeyboardInterrupt, SystemExit):
            sys.exit()

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