from __future__ import absolute_import
from __future__ import print_function
from daemon import runner

from testagent.services.SubscriptionService import TestAgentSubscription
from testagent.services.ApiService import TestAgentAPI
from testagent.services.WorkerService import WorkerService
from testagent.services.LoggingService import LoggingService
from testagent.selfassessment import SelfAssessment

__author__ = 'Patrizio Tufarolo'
__email__ = 'patrizio.tufarolo@studenti.unimi.it'
'''
Project: testagent
Author: Patrizio Tufarolo <patrizio.tufarolo@studenti.unimi.it>
Date: 20/04/15
'''

from testagent.command import TestAgentCommand

LoggingService()


class TestAgent(object):
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = '/var/run/testagent/testagent.pid'
        self.pidfile_timeout = 5

    def run(self):
        TestAgentSubscription()
        TestAgentAPI()
        WorkerService()
        SelfAssessment()
        try:
            test_agent = TestAgentCommand()
            test_agent.execute_from_commandline()
        except:
            raise


def main():
    daemon_runner = runner.DaemonRunner(TestAgent)
    daemon_runner.daemon_context.files_preserve = [LoggingService().get_file_handler()]
    daemon_runner.do_action()

if __name__ == "__main__":
    main()