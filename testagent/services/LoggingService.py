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
class LoggingService(Singleton):
    _log_parameters = {}

    def configure(self, options):
        self._log_parameters["evidences_directory"] = options.evidences_directory
        self._log_parameters["evidences_log_level"] = options.evidences_log_level
        self._log_parameters["evidences_use_syslog"] = False
        if options.evidences_syslog_server:
            self._log_parameters["evidences_syslog_server"] = options.evidences_syslog_server
            self._log_parameters["evidences_syslog_port"] = options.evidences_syslog_port
            self._log_parameters["evidences_use_syslog"] = True

        super(LoggingService, self).configure()

    @Singleton._if_configured(LoggingServiceException)
    def get_parameter(self, name):
        if name in self._log_parameters:
            return self._log_parameters[name]
        else:
            raise LoggingServiceException("Parameter not defined")


