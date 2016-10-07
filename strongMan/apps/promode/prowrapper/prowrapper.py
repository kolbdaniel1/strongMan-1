from strongMan.apps.vici.wrapper.wrapper import ViciWrapper
from strongMan.apps.vici.wrapper.exception import ViciLoadException


class ProViciWrapper(ViciWrapper):

    def get_version_pro(self):
        '''
        :rtype: dict
        '''
        try:
            return self.session.version()
        except Exception as e:
            raise ViciLoadException("Version information cannot be loaded!")

    def list_conns(self):
        connections = []
        for connection in self.session.list_conns():
            connections += connection
        return connections

    def get_conns(self):
        return self.session.get_conns()

    def list_certs(self):
        certs = []
        for cert in self.session.list_certs():
            certs += cert
        return certs
