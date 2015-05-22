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
import signal
import tornado.log

from tornado.options import options
from tornado.options import parse_command_line, parse_config_file
from tornado.log import enable_pretty_logging
from tornado import ioloop
from celery.bin.base import Command
from testagent import __version__
from testagent.options import DEFAULT_CONFIG_FILE
from testagent.subscription_options import DEFAULT_SUBSCRIPTION_FILE
from testagent.services.SubscriptionService import TestAgentSubscription
from testagent.services.ApiService import TestAgentAPI
from testagent.services.WorkerService import WorkerService, WorkerServiceException
from testagent.services.LoggingService import LoggingService
from testagent.selfassessment import SelfAssessment
import daemon, daemon.pidfile


import time
class TestAgentCommand(Command):

    def run_from_argv(self, prog_name, argv=None, command=None):
        io_loop = ioloop.IOLoop.instance()
        LoggingService().setup_logger()
        LoggingService().configure(options)
        logger = LoggingService().get_generic_logger()

        def shutdown_http():
            logger.info('Will shutdown in %s seconds ...', 30)
            io_loop = ioloop.IOLoop.instance()

            deadline = time.time() + 30

            def stop_loop():
                now = time.time()
                if now < deadline and (io_loop._callbacks or io_loop._timeouts):
                    io_loop.add_timeout(now + 1, stop_loop)
                else:
                    io_loop.stop()
                    logger.info('Shutdown')
            stop_loop()

        def sigterm_handler(signal, frame):
            logger.info('SIGTERM detected, shutting down')
            ioloop.IOLoop.instance().add_callback(shutdown_http)
            sys.exit(0)
        signal.signal(signal.SIGTERM, sigterm_handler)
        signal.signal(signal.SIGINT, sigterm_handler)

        argv = list(filter(self.testagent_option, argv))

        try:
            parse_config_file(options.conf, final=False)
        except IOError:
            if options.conf != DEFAULT_CONFIG_FILE:
                raise
        try:
            parse_config_file(options.subscription_conf, final=False)
        except IOError:
            if options.subscription_conf != DEFAULT_SUBSCRIPTION_FILE:
                raise

        parse_command_line([prog_name] + argv)

        #
        # DEBUG MODE LOGGING
        #
        if options.debug and options.logging == 'info':
            options.logging = "debug"
            enable_pretty_logging()

        pidfile = daemon.pidfile.PIDLockFile("/var/run/testagent.pid")
        with daemon.DaemonContext(pidfile=pidfile, files_preserve=[LoggingService().get_file_handler().stream]):
            try:
                SelfAssessment().configure(options.selfassessment_dir)
                TestAgentSubscription().configure(options, logger)
                TestAgentAPI().configure(options, self.app, logger)
                TestAgentSubscription().start()
                TestAgentAPI().start()
                WorkerService().configure(self.app, options)
                try:
                    WorkerService().start_worker()
                except WorkerServiceException:
                    logger.warning("Worker not configured. Use Subscription APIs to configure it.")


                io_loop.start()
            except KeyboardInterrupt:
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