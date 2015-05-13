from __future__ import absolute_import

__author__ = 'Patrizio Tufarolo'
__email__ = 'patrizio.tufarolo@studenti.unimi.it'
'''
Project: testagent
Author: Patrizio Tufarolo <patrizio.tufarolo@studenti.unimi.it>
Date: 20/04/15
'''

from testagent.api import events
from testagent.api import tasks
from testagent.api import subscription
settings = dict()

handlers = [
    #Tasks
    (r"/tasks", tasks.ListTasks),
    (r"/task/info/(.*)", tasks.TaskInfo),
    (r"/task/result/(.+)", tasks.TaskResult),

    # Events WebSocket API
    (r"/task/events/task-sent/(.*)", events.TaskSent),
    (r"/task/events/task-received/(.*)", events.TaskReceived),
    (r"/task/events/task-started/(.*)", events.TaskStarted),
    (r"/task/events/task-succeeded/(.*)", events.TaskSucceeded),
    (r"/task/events/task-failed/(.*)", events.TaskFailed),
    (r"/task/events/task-revoked/(.*)", events.TaskRevoked),
    (r"/task/events/task-retried/(.*)", events.TaskRetried),
]

subscription_handlers = [
    (r"/subscribe", subscription.SubscriptionService)
]