from __future__ import absolute_import

__author__ = 'Patrizio Tufarolo'
__email__ = 'patrizio.tufarolo@studenti.unimi.it'
'''
Project: testagent
Author: Patrizio Tufarolo <patrizio.tufarolo@studenti.unimi.it>
Date: 20/05/15
'''

import logging
import tornado.web

from functools import partial
from concurrent.futures import ThreadPoolExecutor
from tornado.httpserver import HTTPServer
from ssl import CERT_REQUIRED

from testagent.utils.Singleton import Singleton
from testagent.services.handlers.SubscriptionServiceHandlers import handlers
from testagent.options import default_options
from testagent.utils import abs_path
from testagent.exceptions.SubscriptionServiceException import SubscriptionServiceException

logger = logging.getLogger(__name__)

class TestAgentSubscription(tornado.web.Application, Singleton):
    pool_executor_cls = ThreadPoolExecutor
    max_workers = 1
    started = False

    def __init__(self):
        Singleton.__init__(self)
        self.options = default_options

    def configure(self, options, **kwargs):
        Singleton.configure(self)
        options = options if options else self.options
        self.ssl = None
        if options.subscription_server_cert and options.subscription_server_key:
            self.ssl = dict(
                certfile=abs_path(options.subscription_server_cert),
                keyfile=abs_path(options.subscription_server_key)
            )
            if options.subscription_client_ca:
                self.ssl["ca_certs"] = abs_path(options.subscription_client_ca)
                self.ssl["cert_reqs"] = CERT_REQUIRED

        tornado.web.Application.__init__(self, debug=options.debug, handlers=handlers, ssl_options=self.ssl)
        self.started = False
        self.options = options
        self.http_server = HTTPServer(self, ssl_options=self.ssl)

    @Singleton._if_configured(SubscriptionServiceException)
    def start(self):
        self.pool = self.pool_executor_cls(max_workers=self.max_workers)
        self.listen(
            self.options.subscription_port,
            address=self.options.subscription_address,
            ssl_options=self.ssl,
            xheaders=True
        )
        logger.info("Subscription APIs available at http%s://%s:%s" % ('s' if self.ssl else '', self.options.subscription_address, self.options.subscription_port))
        self.started = True

    @Singleton._if_configured(SubscriptionServiceException)
    def listen(self, port, address="", **kwargs):
        self.http_server.listen(port, address)

    @Singleton._if_configured(SubscriptionServiceException)
    def stop(self):
        if self.started:
            self.http_server.close_all_connections()
            self.http_server.stop()
            self.pool.shutdown(wait=False)
            self.started = False

    @Singleton._if_configured(SubscriptionServiceException)
    def delay(self, method, *args, **kwargs):
        return self.pool.submit(partial(method, *args, **kwargs))


logger = logging.getLogger(__name__)
