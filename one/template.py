from pyone import OneServer

class Template:

    def __init__(self, identifier:int, server:OneServer):
        self._identifier = identifier
        self._server = server

    def info(self):
        return self._server.template.info(self._identifier).TEMPLATE
