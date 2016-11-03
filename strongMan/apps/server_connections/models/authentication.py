import sys
from collections import OrderedDict

from django.db import models

from strongMan.apps.certificates.models import UserCertificate, AbstractIdentity, DnIdentity
from strongMan.apps.eap_secrets.models import Secret


class Authentication(models.Model):
    local = models.ForeignKey("server_connections.Connection", null=True, blank=True, default=None, related_name='server_local')
    remote = models.ForeignKey("server_connections.Connection", null=True, blank=True, default=None, related_name='server_remote')
    name = models.TextField()  # starts with remote-* or local-*
    auth = models.TextField()
    round = models.IntegerField(default=1)

    @property
    def connection(self):
        if self.local is not None:
            return self.local
        elif self.remote is not None:
            return self.remote
        else:
            return None

    def dict(self):
        parameters = OrderedDict(auth=self.auth, round=self.round)
        auth = OrderedDict()
        auth[self.name] = parameters
        return auth

    @classmethod
    def get_types(cls):
        subclasses = [subclass() for subclass in cls.__subclasses__()]
        return [subclass.get_typ() for subclass in subclasses]

    def get_typ(self):
        return type(self).__name__

    def subclass(self):
        for cls in self.get_types():
            authentication_class = getattr(sys.modules[__name__], cls)
            authentication = authentication_class.objects.filter(id=self.id)
            if authentication:
                return authentication.first()
        return self

    def has_private_key(self):
        return False

    def has_eap_secret(self):
        return False

    def get_key_dict(self):
        pass

    def get_secret(self):
        pass

    def _get_algorithm_type(self, algorithm):
        if algorithm == 'ec':
            return 'ECDSA'
        elif algorithm == 'rsa':
            return 'RSA'
        else:
            raise Exception('Algorithm of key is not supported!')


class CaCertificateAuthentication(Authentication):
    ca_cert = models.ForeignKey(UserCertificate, null=True, blank=True, default=None,
                                related_name='server_ca_cert_authentication')
    ca_identity = models.TextField()

    def dict(self):
        auth = super(CaCertificateAuthentication, self).dict()
        parameters = auth[self.name]
        parameters['cacerts'] = [self.ca_cert.der_container]
        parameters['id'] = self.ca_identity
        return auth


class AutoCaAuthentication(Authentication):
    ca_identity = models.TextField()

    def dict(self):
        auth = super(AutoCaAuthentication, self).dict()
        parameters = auth[self.name]
        parameters['cacerts'] = [cert.der_container for cert in UserCertificate.objects.filter(is_CA=True)]
        parameters['id'] = self.ca_identity
        return auth


class EapAuthentication(Authentication):
    secret = models.ForeignKey(Secret, null=False, blank=False, related_name='eap_secret', on_delete=models.PROTECT)

    def dict(self):
        auth = super(EapAuthentication, self).dict()
        return auth

    def has_eap_secret(self):
        return True

    def get_secret(self):
        return self.secret


class CertificateAuthentication(Authentication):
    identity = models.ForeignKey(AbstractIdentity, null=True, blank=True, default=None, related_name='server_cert_identity')

    def dict(self):
        auth = super(CertificateAuthentication, self).dict()
        values = auth[self.name]
        ident = self.identity.subclass()
        if not isinstance(ident, DnIdentity):
            values['id'] = ident.value()
        values['certs'] = [self.identity.subclass().certificate.der_container]
        return auth

    def has_private_key(self):
        return self.identity.subclass().certificate.subclass().has_private_key

    def get_key_dict(self):
        key = self.identity.subclass().certificate.subclass().private_key
        return OrderedDict(type=self._get_algorithm_type(key.algorithm), data=key.der_container)


class EapTlsAuthentication(Authentication):
    identity = models.ForeignKey(AbstractIdentity, null=True, blank=True, default=None, related_name='server_tls_identity')
    secret = models.ForeignKey(Secret, null=False, blank=False, related_name='eap_tls_secret', on_delete=models.PROTECT)

    def dict(self):
        auth = super(EapTlsAuthentication, self).dict()
        values = auth[self.name]
        values['certs'] = [self.identity.subclass().certificate.der_container]
        return auth

    def has_private_key(self):
        return self.identity.subclass().certificate.subclass().has_private_key

    def get_key_dict(self):
        key = self.identity.subclass().certificate.subclass().private_key
        return OrderedDict(type=self._get_algorithm_type(key.algorithm), data=key.der_container)

    def has_eap_secret(self):
        return True

    def get_secret(self):
        return self.secret
