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

from tornado import ioloop



from testagent.urls import subscription_handlers
from testagent.events import Events
from testagent.options import default_options
import testagent.options


import threading

class TestAgentSubscription(tornado.web.Application):
    pool_executor_cls = ThreadPoolExecutor
    max_workers = 1

    def __init__(self, options=None, io_loop=None, **kwargs):
        kwargs.update(handlers=subscription_handlers)
        super(TestAgentSubscription, self).__init__(**kwargs)

        self.options = options or default_options
        self.ssl = kwargs.get('ssl', None)
        self.io_loop = io_loop or ioloop.IOLoop.instance()
        self.started = False

    def start(self):
        self.pool = self.pool_executor_cls(max_workers=self.max_workers)

        if not (True
                and self.options.broker_url
                and self.options.backend_broker_url
                and self.options.results_exchange_name
                and self.options.results_exchange_type
                and self.options.results_queue_name
                and self.options.results_routing_key):

            self.listen(self.options.subscription_port, address=self.options.subscription_address,
                        ssl_options=self.ssl, xheaders=True)
            self.io_loop.start()
            self.started = True

    def stop(self):
        if self.started:
            self.pool.shutdown(wait=False)
            self.started = False

    def delay(self, method, *args, **kwargs):
        return self.pool.submit(partial(method, *args, **kwargs))

logger = logging.getLogger(__name__)