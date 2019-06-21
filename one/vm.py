import pyone
from one.template import Template
from pyone import OneServer

class Vm:

    def __init__(self, template:Template, server:OneServer):
        self._template = template
        self._server = server

    def allocate(self, host):
        self._identifier = self._server.vm.allocate(self._template.info(), True)
        self._server.vm.deploy(self._identifier, host)

        return self._identifier

    def deallocate(self):
        self._server.vm.action("terminate", self._identifier)

    def getMonitoringInfo(self):
        return self._server.vm.info(self._identifier)
