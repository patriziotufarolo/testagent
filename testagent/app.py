from __future__ import absolute_import

__author__ = 'Patrizio Tufarolo'
__email__ = 'patrizio.tufarolo@studenti.unimi.it'
'''
Project: testagent
Author: Patrizio Tufarolo <patrizio.tufarolo@studenti.unimi.it>
Date: 20/04/15
'''

import logging

from functools import partial
from concurrent.futures import ThreadPoolExecutor

from celery import Celery
from celery.apps import worker

import tornado.web
import threading
from multiprocessing import Process
from tornado import ioloop

from celery.signals import worker_shutdown
from testagent.urls import handlers
from testagent.events import Events
from testagent.options import default_options
import testagent.options

process = Process()

RED = "\033[1;31m"
GRAY = "\033[1;30m"
WHITE = "\033[1;37m"
LGRAY = "\033[0;37m"
RESET_SEQ = "\033[1;37m"

worker.BANNER = """\n
\t\t\tCelery Version {version}

Welcome\t\t\t\t\t""" + RED + """{hostname}"""+RESET_SEQ+"""

=> Test Agent ID:\t\t\t"""+RED+"""{app}"""+RESET_SEQ+"""
=> Broker:\t\t\t\t"""+RED+"""{conninfo}"""+RESET_SEQ+"""
=> Results backend broker:\t\t"""+RED+"""{results}"""+RESET_SEQ+"""
=> Concurrency\t\t\t\t"""+RED+"""{concurrency}"""+RESET_SEQ+"""

=> Active queues
{queues}
"""
worker.ARTLINES = []


ARTLINES = [
RED+'''                                                             .lkKWMWNKx:.                    ''' + RESET_SEQ,
RED+'''                                                          ;xXMMMMMMMMMMMMKd'                 ''' + RESET_SEQ,
RED+'''                                                       .dWMMW0          KMMMXl.              ''' + RESET_SEQ,
RED+'''                                                      xMMM0:              cXMMWl             ''' + RESET_SEQ,
RED+'''                                         ..,,;,'.   .XMMK,                  ;NMM0.           ''' + RESET_SEQ,
RED+'''                                     ,o0WMMMMMMMMMXkNMMd                      OMMK           ''' + RESET_SEQ,
RED+'''                  .;okKXNNX0kl'   .oNMMMXOdc::clx0WMMMk                        0MMd          ''' + RESET_SEQ,
RED+'''                c0MMMMWXKKXWMMMWkdWMMKc.           ,dK.                       \'MMW          ''' + RESET_SEQ,
RED+'''              :NMMWx;.      .:OMMMMX;                                           WMMk.        ''' + RESET_SEQ,
RED+'''             kMMNc             .dWO                                             ;OMMMO.      ''' + RESET_SEQ,
RED+'''            xMMX.                .                                               .kMMWc      ''' + RESET_SEQ,
RED+'''           'MMW.                                                                    :WMMl    ''' + RESET_SEQ,
RED+'''           dMMk                                                                      ;MMM    ''' + RESET_SEQ,
RED+'''     .cdkOONMMk                                                                       xMMO   ''' + RESET_SEQ,
RED+'''  .oXMMMMMMMMMN  '''+WHITE+'''                                                               '''+RED+'''      ,MMW   ''' + RESET_SEQ,
RED+''' ;WMMXl.   .,o0: '''+WHITE+'''                                                               '''+RED+'''      'MMW   ''' + RESET_SEQ,
RED+''';MMMl            '''+WHITE+'''             TEST BASED CERTIFICATION ENVIRONMENT              '''+RED+'''      lMM0   ''' + RESET_SEQ,
RED+'''XMMl             '''+WHITE+'''             TEST AGENT  version 1.1 - April 2015              '''+RED+'''     .WMM;   ''' + RESET_SEQ,
RED+'''WMM'             '''+WHITE+'''    Patrizio Tufarolo <patrizio.tufarolo@studenti.unimi.it>    '''+RED+'''    .XMMx    ''' + RESET_SEQ,
RED+'''0MMd             '''+WHITE+'''                                                               '''+RED+'''   cWMMd     ''' + RESET_SEQ,
RED+''''WMMd                                                                           .cXMMK,      ''' + RESET_SEQ,
RED+''' ;NMMNd;....................................................................,cdKMMM0:        ''' + RESET_SEQ,
RED+'''  .oNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWOl.          ''' + RESET_SEQ,
RED+'''     c0WMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWN0o,              ''' + RESET_SEQ,
]

worker.BANNER = '\n'.join(ARTLINES) + "\n" + worker.BANNER + "\n"


class TestAgent(tornado.web.Application):
    """
    18/05
    @todo: global testagent app
    """
    pool_executor_cls = ThreadPoolExecutor
    max_workers = 4

    def __init__(self, options=None, capp=None, events=None, io_loop=None, **kwargs):
        kwargs.update(handlers=handlers)
        super(TestAgent, self).__init__(**kwargs)

        self.options = options or default_options
        self.ssl_options = kwargs.get('ssl', None)
        # self.io_loop = io_loop or ioloop.IOLoop.instance()
        self.capp = capp

        # self.worker_thread = threading.Thread(target=self.run_worker)
        self.worker_process = Process(target=self.run_worker)

        self.events = events or Events(self.capp,
                                       db=self.options.db,
                                       persistent=self.options.persistent,
                                       enable_events=self.options.enable_events,
                                       max_tasks_in_memory=self.options.max_tasks)
        self.started = False


    def run_worker(self):
        from celery.bin import worker
        wrk = worker.worker(app=self.capp)
        wrk.run()

    def start(self):
        self.pool = self.pool_executor_cls(max_workers=self.max_workers)
        self.events.start()
        self.listen(self.options.apis_port, address=self.options.apis_address,
                    ssl_options=self.ssl_options, xheaders=True)
        # self.worker_thread.start()
        self.worker_process.start()
        global process
        process = self.worker_process
        self.started = True
        #self.io_loop.start()

    def stop(self):
        if self.started:
            self.events.stop()
            self.pool.shutdown(wait=False)
            self.started = False

    def delay(self, method, *args, **kwargs):
        return self.pool.submit(partial(method, *args, **kwargs))

    @property
    def transport(self):
        return getattr(self.capp.connection().transport,
                       driver_type=None)

logger = logging.getLogger(__name__)