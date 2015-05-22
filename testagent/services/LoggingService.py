from __future__ import absolute_import

__author__ = 'Patrizio Tufarolo'
__email__ = 'patrizio.tufarolo@studenti.unimi.it'
'''
Project: testagent
Author: Patrizio Tufarolo <patrizio.tufarolo@studenti.unimi.it>
Date: 20/05/15
'''

from testagent.utils.Singleton import Singleton
from testagent.exceptions.LoggingServiceException import LoggingServiceException
import logging
from functools import wraps

class LoggingService(Singleton):
    _log_parameters = {}
    logger = None
    file_logger = None
    _logger_configured = False
    @staticmethod
    def _configured_logger(func):
        @wraps(func)
        def wrapper(inst, *args, **kwargs):
            if not inst.check_configured_logger():
                raise LoggingServiceException("Logger not yet configured")
            else:
                return func(inst, *args, **kwargs)
        return wrapper

    @staticmethod
    def _not_configured_logger(func):
        @wraps(func)
        def wrapper(inst, *args, **kwargs):
            if inst.check_configured_logger():
                raise LoggingServiceException("Logger already configured")
            else:
                return func(inst, *args, **kwargs)
        return wrapper

    def configure(self, options):
        self._log_parameters["evidences_directory"] = options.evidences_directory
        self._log_parameters["evidences_log_level"] = options.evidences_log_level
        self._log_parameters["evidences_use_syslog"] = False
        if options.evidences_syslog_server:
            self._log_parameters["evidences_syslog_server"] = options.evidences_syslog_server
            self._log_parameters["evidences_syslog_port"] = options.evidences_syslog_port
            self._log_parameters["evidences_use_syslog"] = True
        super(LoggingService, self).configure()

    @_not_configured_logger
    def setup_logger(self):
        self.logger = logging.getLogger("TestAgent")
        self.file_logger = logging.FileHandler("/var/log/testagent/testagent.log")
        self.file_logger.setLevel(logging.INFO)
        self.file_logger.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(self.file_logger)
        self._logger_configured = True

    @Singleton._if_configured(LoggingServiceException)
    def get_parameter(self, name):
        if name in self._log_parameters:
            return self._log_parameters[name]
        else:
            raise LoggingServiceException("Parameter not defined")

    @_configured_logger
    def get_generic_logger(self):
        return self.logger

    @_configured_logger
    def get_file_handler(self):
        return self.file_logger

    def check_configured_logger(self):
        return self._logger_configured






class StreamToLogger(object):
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())