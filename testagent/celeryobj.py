from __future__ import absolute_import

__author__ = 'Patrizio Tufarolo'
__email__ = 'patrizio.tufarolo@studenti.unimi.it'
'''
Project: testagent
Author: Patrizio Tufarolo <patrizio.tufarolo@studenti.unimi.it>
Date: 21/04/15
'''

from celery import Celery
from celery.apps import worker
import testagent.options
RED = "\033[1;31m"
GRAY = "\033[1;30m"
WHITE = "\033[1;37m"
LGRAY = "\033[0;37m"
RESET_SEQ = "\033[1;36m"

app = Celery('cumulus_testagent')
app.config_from_object(testagent.options.CeleryConfiguration)