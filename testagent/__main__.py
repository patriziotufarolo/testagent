from __future__ import absolute_import
from __future__ import print_function
import pdb
__author__ = 'Patrizio Tufarolo'
__email__ = 'patrizio.tufarolo@studenti.unimi.it'
'''
Project: testagent
Author: Patrizio Tufarolo <patrizio.tufarolo@studenti.unimi.it>
Date: 20/04/15
'''

from testagent.command import TestAgentCommand
def main():
    try:
        test_agent = TestAgentCommand()
        test_agent.execute_from_commandline()
    except:
        raise

if __name__ == "__main__":
    main()