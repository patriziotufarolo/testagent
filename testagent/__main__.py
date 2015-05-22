from __future__ import absolute_import
from __future__ import print_function
import daemon, daemon.pidfile

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
LoggingService().setup_logger()

def main():
    pidfile = daemon.pidfile.PIDLockFile("/var/run/testagent.pid")
    with daemon.DaemonContext(pidfile=pidfile, files_preserve=LoggingService().get_file_handler().stream):
        TestAgentSubscription()
        TestAgentAPI()
        WorkerService()
        SelfAssessment()
        try:
            test_agent = TestAgentCommand()
            test_agent.execute_from_commandline()
        except:
            raise
if __name__ == "__main__":
    main()