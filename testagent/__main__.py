from __future__ import absolute_import
from __future__ import print_function


from testagent.services.SubscriptionService import TestAgentSubscription
from testagent.services.ApiService import TestAgentAPI
from testagent.services.WorkerService import WorkerService

__author__ = 'Patrizio Tufarolo'
__email__ = 'patrizio.tufarolo@studenti.unimi.it'
'''
Project: testagent
Author: Patrizio Tufarolo <patrizio.tufarolo@studenti.unimi.it>
Date: 20/04/15
'''

from testagent.command import TestAgentCommand
def main():
    TestAgentSubscription()
    TestAgentAPI()
    WorkerService()
    try:
        test_agent = TestAgentCommand()
        test_agent.execute_from_commandline()
    except:
        raise

if __name__ == "__main__":
    main()