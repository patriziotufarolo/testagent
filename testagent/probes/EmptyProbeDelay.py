__author__ = 'Patrizio Tufarolo'
__email__ = 'patrizio.tufarolo@studenti.unimi.it'

from testagent.probe import Probe
from time import sleep


class EmptyProbe(Probe):
    def ciao0(self, inputs):
        print "ciao0"
        sleep(10)
        return True

    def ciao0r (self, inputs):
        return

    def appendAtomics(self):
        self.appendAtomic(self.ciao0, self.ciao0r)

probe = EmptyProbe()
