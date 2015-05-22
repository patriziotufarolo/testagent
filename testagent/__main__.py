from __future__ import absolute_import
from __future__ import print_function
import daemon

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
def main():
    with daemon.DaemonContext(stdout=sys.stdout):
            daem = MainDaemon()
            daem.run()

class MainDaemon(object):
    def __init__(self):
        pass

    def run(self):
        TestAgentSubscription()
        TestAgentAPI()
        WorkerService()
        SelfAssessment()
        LoggingService()
        try:
            test_agent = TestAgentCommand()
            test_agent.execute_from_commandline()
        except:
            raise
import sys
if __name__ == "__main__":
    main()