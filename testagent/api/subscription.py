__author__ = 'Patrizio Tufarolo'
__email__ = 'patrizio.tufarolo@studenti.unimi.it'
'''
Project: testagent
Author: Patrizio Tufarolo <patrizio.tufarolo@studenti.unimi.it>
Date: 11/05/15
'''
from testagent.api.ViewBaseHandler import BaseHandler
from tornado.web import HTTPError
from tornado.escape import json_decode
import json

class BaseTaskHandler(BaseHandler):
    def get_task_args(self):
        try:
            body = self.request.body
            options = json_decode(body) if body else {}
        except ValueError as e:
            raise HTTPError(400, str(e))
        args = options.pop('args', [])
        kwargs = options.pop('kwargs', {})

        if not isinstance(args, (list, tuple)):
            raise HTTPError(400, 'args must be an array')

        return args, kwargs, options

    def write_error(self, status_code, **kwargs):
        self.set_status(status_code)

    def safe_result(self, result):
        "returns json encodable result"
        try:
            json.dumps(result)
        except TypeError:
            return repr(result)
        else:
            return result


class SubscriptionService(BaseTaskHandler):
    def post(self, config):
        pass
