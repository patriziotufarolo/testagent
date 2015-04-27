from __future__ import absolute_import
from __future__ import print_function

__author__ = 'Patrizio Tufarolo'
__email__ = 'patrizio.tufarolo@studenti.unimi.it'
'''
Project: testagent
Author: Patrizio Tufarolo <patrizio.tufarolo@studenti.unimi.it>
Date: 20/04/15
'''

import os
import sys
import atexit
import signal
import logging
import threading

from tornado.options import options
from tornado.options import parse_command_line, parse_config_file
from tornado.log import enable_pretty_logging
from celery.bin.base import Command

from testagent import __version__
from testagent.app import TestAgent
from testagent.urls import settings
from testagent.utils import abs_path
import testagent.options as testagentoptions
from testagent.options import DEFAULT_CONFIG_FILE
from celery import Celery
logger = logging.getLogger(__name__)

class TestAgentCommand(Command):
    ENV_VAR_PREFIX = 'TESTAGENT_'

    def run_from_argv(self, prog_name, argv=None, command=None):
        env_options = filter(lambda x: x.startswith(self.ENV_VAR_PREFIX), os.environ)

        for env in env_options:
            name = env.lstrip(self.ENV_VAR_PREFIX).lower()
            value = os.environ(env)
            option = options._options[name]

            if option.multiple:
                value = map(option.type, value.split(','))
            else:
                value = option.type(value)
            setattr(options, name, value)

        argv = list(filter(self.testagent_option, argv))
        parse_command_line([prog_name] + argv)
        try:
            parse_config_file(options.conf, final=False)
            parse_command_line([prog_name] + argv)
        except IOError:
            if options.conf != DEFAULT_CONFIG_FILE:
                raise

        settings['debug'] = options.debug
        if options.debug and options.logging == 'info':
            options.logging = "debug"
            enable_pretty_logging()

        if options.certfile and options.keyfile:
            settings['ssl_options'] = dict(certfile=abs_path(options.certfile),
                                           keyfile=abs_path(options.keyfile))
            if options.ca_certs:
                settings['ssl_options']['ca_certs'] = abs_path(options.ca_certs)


        self.app.config_from_object(testagentoptions)

        self.app.connection = self.app.broker_connection

        self.app.loader.import_default_modules()

        testagent = TestAgent(capp=self.app, options=options, **settings)
        self.testagent = testagent
        atexit.register(testagent.stop)

        def sigterm_handler(signal, frame):
            logger.info('SIGTERM, shutting down')
            sys.exit(0)

        signal.signal(signal.SIGTERM, sigterm_handler)

        self.print_banner('ssl_options' in settings)

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
    @staticmethod
    def run_worker(capp):
        capp.worker_main()

    def print_banner(self, ssl):
        logger.info(
            "APIs available at http%s://%s:%s",
            's' if ssl else '',
            options.address or 'localhost',
            options.port
        )
