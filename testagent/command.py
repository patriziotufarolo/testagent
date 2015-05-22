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
import logging, time
logger = logging.getLogger("main")

class TestAgentCommand(Command):

    def run_from_argv(self, prog_name, argv=None, command=None):
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

        try:
            SelfAssessment().configure(options.selfassessment_dir)
            TestAgentSubscription().configure(options)
            LoggingService().configure(options)
            TestAgentAPI().configure(options, self.app)
            TestAgentSubscription().start()
            TestAgentAPI().start()
            WorkerService().configure(self.app, options)
            try:
                WorkerService().start_worker()
            except WorkerServiceException:
                logger.warning("Worker not configured. Use Subscription APIs to configure it.")
            from multiprocessing import Process
            time.sleep(10)
            Process(target=self.test_empty_probe).start()
            Process(target=self.test_empty_probe).start()
            Process(target=self.test_empty_probe).start()
            Process(target=self.test_empty_probe).start()
            io_loop = ioloop.IOLoop.instance()
            io_loop.start()
        except KeyboardInterrupt:
            sys.exit()

    def handle_argv(self, prog_name, argv, command=None):
        return self.run_from_argv(prog_name, argv)


    def test_empty_probe(self):
        print("parto tra 10s")
        import time ; time.sleep(10)
        print("ok sto per partire")
        from testagent.tasks import start_certification
        start_certification.delay('''
        <collector id="1" cmid="1" probe_driver="EmptyProbeDelay">
                <TestCases>
                    <TestCase>
                        <ID>1</ID>
                        <Description>TestCase1</Description>
                        <TestInstance Operation="1">
                            <Preconditions/>
                            <HiddenCommunications/>
                            <Input>
                                <Item key="Input1" value="Value1" />
                                <Item key="Input2" value="Value2" />
                            </Input>
                            <ExpectedOutput/>
                            <PostConditions/>
                        </TestInstance>
                        <TestInstance Operation="3">
                            <Preconditions/>
                            <HiddenCommunications/>
                            <Input>
                                <Item key="Input6" value="Value6" />
                            </Input>
                            <ExpectedOutput/>
                            <PostConditions/>
                        </TestInstance>
                        <TestInstance Operation="2">
                            <Preconditions/>
                            <HiddenCommunications/>
                            <Input>
                                <Item key="Input8" value="Value8" />
                                <Item key="Input5" value="Value9" />
                            </Input>
                            <ExpectedOutput/>
                            <PostConditions/>
                        </TestInstance>
                    </TestCase>
                </TestCases>
                </collector>
        ''')

    def early_version(self, argv):
        if '--version' in argv:
            print(__version__, file=self.stdout)
            super(TestAgentCommand, self).early_version(argv)

    @staticmethod
    def testagent_option(arg):
        name, _, value = arg.lstrip('-').partition("=")
        name = name.replace('-', '_')
        return hasattr(options, name)