import os
from collections import OrderedDict
from django.test import TestCase
from strongMan.apps.certificates.container_reader import X509Reader, PKCS1Reader
from strongMan.apps.certificates.models import Certificate, UserCertificate, CertificateDoNotDelete
from strongMan.apps.certificates.services import UserCertificateManager
from strongMan.apps.server_connections.models import Authentication, EapAuthentication, \
    CertificateAuthentication, CaCertificateAuthentication, Connection, IKEv2EAP, Child, Address, Proposal
from strongMan.apps.pools.models.pools import Pool


class ServerConnectionModelTest(TestCase):
    def setUp(self):
        pool = Pool(poolname='testPool', addresses='10.1.0.0/16').save()  # attribute, attributevalues

        connection = Connection(profile='rw', version='2', pool=pool, send_certreq=False, enabled=True)
        connection.save()

        child1 = Child(name='all', mode='TUNNEL', connection=connection)
        child1.save()
        child2 = Child(name='child_2', mode='TUNNEL', connection=connection)
        child2.save()

        Proposal(type='aes128gcm128-ntru128', connection=connection).save()
        Proposal(type='aes128gcm128-ecp256', connection=connection).save()

        Address(value='127.0.0.1', local_ts=child1, remote_ts=child2, local_addresses=connection).save()
        Address(value='127.0.0.2', local_ts=child1, remote_ts=child2, remote_addresses=connection).save()

        bytes = Paths.X509_googlecom.read()
        manager = UserCertificateManager()
        manager.add_keycontainer(bytes)

        certificate = Certificate.objects.first().subclass()
        auth = EapAuthentication(name='local-eap', auth='eap-ttls', local=connection, round=2)
        auth.save()
        CaCertificateAuthentication(name='remote-1', auth='pubkey',
                                    ca_cert=certificate, ca_identity="adsfasdf", remote=connection).save()
        CertificateAuthentication(name='local-1', identity=certificate.identities.first(), auth='pubkey',
                                  local=connection).save()

    def test_child_added(self):
        self.assertEquals(2, Child.objects.count())

    def test_address_added(self):
        self.assertEquals(2, Address.objects.count())

    def test_connection_added(self):
        self.assertEquals(1, Connection.objects.count())

    def test_proposal_added(self):
        self.assertEquals(2, Proposal.objects.count())

    def test_authentication_added(self):
        self.assertEquals(3, Authentication.objects.count())

    # def test_secret_added(self):
    #     self.assertEquals(1, Secret.objects.count())


    # def test_secret_dict(self):
    #     secret = Secret.objects.first()
    #     self.assertTrue(isinstance(secret.dict(), OrderedDict))

    def test_delete_all_connections(self):
        connection = Connection.objects.first()

        self.assertEquals(2, Child.objects.count())
        self.assertEquals(3, Authentication.objects.count())

        connection.delete()
        self.assertEquals(0, Authentication.objects.count())
        self.assertEquals(0, Child.objects.count())

    def test_delete_all_connections_subclass(self):
        connection = IKEv2EAP(profile='rw2', version='1', send_certreq=False, enabled=True)
        connection.save()
        Child(name='all', mode='TUNNEL', connection=connection).save()

        self.assertEquals(1, IKEv2EAP.objects.count())
        self.assertEquals(3, Child.objects.count())
        self.assertEquals(2, Connection.objects.count())

        connection.delete()
        self.assertEquals(0, IKEv2EAP.objects.count())
        self.assertEquals(2, Child.objects.count())
        self.assertEquals(1, Connection.objects.count())

    # def test_secrets_encrypted_field(self):
    #     Secret.objects.all().delete()
    #     password = "adsfasdfasdf"
    #     secret = Secret()
    #     secret.type = "as"
    #     secret.data = password
    #     secret.save()
    #
    #     data = Secret.objects.first().data
    #     self.assertEqual(data, password)

    def test_prevent_certificate_delete(self):
        cert = UserCertificate.objects.first()
        with self.assertRaises(CertificateDoNotDelete):
            cert.delete()

    def test_prevent_certificate_delete(self):
        UserCertificateManager.add_keycontainer(Paths.X509_rsa_ca_der.read())
        cert = UserCertificate.objects.get(pk=2)
        cert.delete()


class TestCert:
    def __init__(self, path):
        self.path = path
        self.parent_dir = os.path.join(os.path.dirname(__file__), os.pardir)

    def read(self):
        absolute_path = self.parent_dir + "/certificates/certs/" + self.path
        with open(absolute_path, 'rb') as f:
            return f.read()

    def read_x509(self, password=None):
        bytes = self.read()
        reader = X509Reader.by_bytes(bytes, password)
        reader.parse()
        return reader

    def read_pkcs1(self, password=None):
        bytes = self.read()
        reader = PKCS1Reader.by_bytes(bytes, password)
        reader.parse()
        return reader


class Paths:
    X509_rsa_ca = TestCert("ca.crt")
    X509_rsa_ca_samepublickey_differentserialnumber = TestCert("hsrca_doppelt_gleicher_publickey.crt")
    X509_rsa_ca_samepublickey_differentserialnumber_san = TestCert("cacert_gleicher_public_anderer_serial.der")
    PKCS1_rsa_ca = TestCert("ca2.key")
    PKCS1_rsa_ca_encrypted = TestCert("ca.key")
    PKCS8_rsa_ca = TestCert("ca2.pkcs8")
    PKCS8_ec = TestCert("ec.pkcs8")
    PKCS8_rsa_ca_encrypted = TestCert("ca_enrypted.pkcs8")
    X509_rsa_ca_der = TestCert("cacert.der")
    X509_ec = TestCert("ec.crt")
    PKCS1_ec = TestCert("ec2.key")
    X509_rsa = TestCert("warrior.crt")
    PKCS12_rsa = TestCert("warrior.pkcs12")
    PKCS12_rsa_encrypted = TestCert("warrior_encrypted.pkcs12")
    X509_googlecom = TestCert("google.com_der.crt")
