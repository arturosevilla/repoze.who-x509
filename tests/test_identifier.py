# -*- coding: utf-8 -*-
# Copyright (C) 2012 Ckluster Technologies
# All Rights Reserved.
#
# This software is subject to the provision stipulated in
# http://www.ckluster.com/OPEN_LICENSE.txt.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from zope.interface.verify import verifyClass, verifyObject
from repoze.who.interfaces import IIdentifier
from repoze.who.middleware import match_classification

from repoze.who.plugins.x509 import X509Identifier
from tests import TestX509Base

class TestX509Identifier(TestX509Base):
    
    def test_object_conforms_to_IIdentifier(self):
        verifyObject(IIdentifier, X509Identifier('Test'))

    def test_class_conforms_to_IIdentifier(self):
        verifyClass(IIdentifier, X509Identifier)

    def test_remember_without_headers(self):
        identifier = X509Identifier('Test')
        assert identifier.remember({}, None) is None

    def test_forget_without_headers(self):
        identifier = X509Identifier('Test')
        assert identifier.forget({}, None) is None

    def test_match_default_classification(self):
        identifier = X509Identifier('Test')
        assert identifier in match_classification(
            IIdentifier,
            (identifier,),
            'browser'
        )

    def test_dont_match_default_classification(self):
        identifier = X509Identifier('Test')
        assert identifier not in match_classification(
            IIdentifier,
            (identifier,),
            'other'
        )

    def test_match_custom_classification(self):
        identifier = X509Identifier('Test', classifications=['ios', 'browser'])
        assert identifier in match_classification(
            IIdentifier,
            (identifier,),
            'ios'
        )

    def test_dont_match_custom_classification(self):
        identifier = X509Identifier('Test', classifications=['ios', 'browser'])
        assert identifier not in match_classification(
            IIdentifier,
            (identifier,),
            'other'
        )

    def test_identify_default_values(self):
        identifier = X509Identifier('SSL_CLIENT_S_DN')
        environ = self.make_environ(
            {'CN': 'Issuer', 'C': 'US', 'O': 'Company'},
            {'CN': 'Name', 'Email': 'email@example.com', 'C': 'US'}
        )
        creds = identifier.identify(environ)
        assert creds is not None
        assert 'login' in creds
        assert 'subject' in creds

        self.assertEquals(creds['subject'], environ['SSL_CLIENT_S_DN'])
        self.assertEquals(creds['login'], 'email@example.com')

    def test_identify_default_values_server_variable(self):
        identifier = X509Identifier('SSL_CLIENT_S_DN')
        environ = self.make_environ(
            {'CN': 'Issuer', 'C': 'US', 'O': 'Company'},
            {'CN': 'Name', 'Email': 'email@domain.com', 'C': 'US'}
        )
        environ['SSL_CLIENT_S_DN_Email'] = 'email@example.com'
        creds = identifier.identify(environ)
        assert creds is not None
        assert 'login' in creds
        assert 'subject' in creds

        self.assertEquals(creds['subject'], environ['SSL_CLIENT_S_DN'])
        self.assertEquals(creds['login'], 'email@example.com')

    def test_invalid_subject_dn(self):
        identifier = X509Identifier('stuff')
        environ = self.make_environ(
            {'CN': 'Issuer', 'C': 'US', 'O': 'Company'},
            {'CN': 'Name', 'Email': 'email@example.com', 'C': 'US'}
        )
        creds = identifier.identify(environ)
        assert creds is None

    def test_invalid_certificate(self):
        identifier = X509Identifier('stuff')
        environ = self.make_environ(
            {'CN': 'Issuer', 'C': 'US', 'O': 'Company'},
            {'CN': 'Name', 'Email': 'email@example.com', 'C': 'US'},
            verified=False
        )
        creds = identifier.identify(environ)
        assert creds is None

    def test_without_field_in_dn(self):
        identifier = X509Identifier('SSL_CLIENT_S_DN', login_field='Lala')
        environ = self.make_environ(
            {'CN': 'Issuer', 'C': 'US', 'O': 'Company'},
            {'CN': 'Name', 'Email': 'email@example.com', 'C': 'US'}
        )
        creds = identifier.identify(environ)
        assert creds is None

    def test_invalid_dn(self):
        identifier = X509Identifier('SSL_CLIENT_S_DN')
        environ = self.make_environ(
            {'CN': 'Issuer', 'C': 'US', 'O': 'Company'},
            ''
        )
        creds = identifier.identify(environ)
        assert creds is None

    def test_allow_multiple_values(self):
        identifier = X509Identifier('SSL_CLIENT_S_DN', multiple_values=True)
        environ = self.make_environ(
            {'CN': 'Issuer', 'C': 'US', 'O': 'Company'},
            '/Email=email1@example.com/Email=email2@example.com/O=Org'
        )
        creds = identifier.identify(environ)
        
        assert 'email1@example.com' in creds['login']
        assert 'email2@example.com' in creds['login']

    def test_allow_multiple_values_server_variables(self):
        identifier = X509Identifier('SSL_CLIENT_S_DN', multiple_values=True)
        environ = self.make_environ(
            {'CN': 'Issuer', 'C': 'US', 'O': 'Company'},
            {'CN': 'Name', 'Email': 'email@domain.com', 'C': 'US'}
        )
        environ['SSL_CLIENT_S_DN_Email'] = ''
        environ['SSL_CLIENT_S_DN_Email_0'] = 'email1@example.com'
        environ['SSL_CLIENT_S_DN_Email_1'] = 'email2@example.com'
        creds = identifier.identify(environ)

        assert 'email1@example.com' in creds['login']
        assert 'email2@example.com' in creds['login']

    def test_multiple_values_but_disabled(self):
        identifier = X509Identifier('SSL_CLIENT_S_DN')
        environ = self.make_environ(
            {'CN': 'Issuer', 'C': 'US', 'O': 'Company'},
            '/Email=email1@example.com/Email=email2@example.com/O=Org'
        )
        creds = identifier.identify(environ)
        assert creds is None

