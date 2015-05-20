# -*- coding: utf-8 -*-

from __future__ import absolute_import

from testagent.parser import CollectorParser
import celery.utils.log
from testagent.structure import Collector
from testagent.exceptions.ParserException import ParserException
from testagent.exceptions.ProbeExecutionError import ProbeExecutionError
from testagent.services.WorkerService import WorkerService
from celery.signals import task_success


import importlib

logger = celery.utils.log.get_task_logger(__name__)

app = WorkerService()
app.configure()

@app.app.task(bind=True)
def start_certification(self, xml):
    print("Received an XML message:")
    print(xml)

    results = []
    current_testcase = 0
    all_testcases = 0

    try:
        cp = CollectorParser()
        cp.set_input(xml)
        my_collector = cp.parse()
    except Exception as e:
        raise

    if not my_collector or not isinstance(my_collector, Collector):
        raise ParserException("Unable to parse")

    try:
        probe = importlib.import_module("testagent.probes." + my_collector.getTot())
    except IOError:
        raise ProbeExecutionError(my_collector.getTot() + " No such file or directory")
    except:
        raise

    all_testcases = len(my_collector.getTestcases())
    for testcase in my_collector.getTestcases():
        probe.probe.appendAtomics()
        if logger:
            probe.probe.setLogger(logger)

        testcase_result = probe.probe.run(self, current_testcase+1, all_testcases, testcase)
        results.append(testcase_result)
        current_testcase += 1

    return results
