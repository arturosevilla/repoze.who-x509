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

import unittest
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc
from repoze.who.plugins.x509.utils import *
from tests import TestX509Base


class TestUtils(TestX509Base):
    """Unit tests for the tools of this plugin"""

    def test_normal_distinguished_name_parse(self):
        dn = self.generate_dn(
            CN='common name',
            O='organization',
            OU='organization unit',
            C='co',
            ST='state',
            L='locality'
        )
        
        parsed = parse_dn(dn)
        self.assertEqual('common name', parsed['CN'][0])
        self.assertEqual('organization', parsed['O'][0])
        self.assertEqual('organization unit', parsed['OU'][0])
        self.assertEqual('co', parsed['C'][0])
        self.assertEqual('state', parsed['ST'][0])
        self.assertEqual('locality', parsed['L'][0])

    def test_parsing_with_confusing_dn(self):
        dn = self.generate_dn(
            C='MX',
            ST='Stuff/stuff',
            L='Locality, local',
            O='Organ., data',
            OU='unit unit+unit',
            CN='name',
            emailAddress='weird@example.com'
        )

        parsed = parse_dn(dn)
        self.assertEqual('MX', parsed['C'][0])
        self.assertEqual('Stuff/stuff', parsed['ST'][0])
        self.assertEqual('Locality, local', parsed['L'][0])
        self.assertEqual('Organ., data', parsed['O'][0])
        self.assertEqual('unit unit+unit', parsed['OU'][0])
        self.assertEqual('name', parsed['CN'][0])

    def test_multiple_values_for_dn(self):
        dn = '/C=MX/C=US/ST=state/ST=secondstate'
        parsed = parse_dn(dn)
        assert 'MX' in parsed['C']
        assert 'US' in parsed['C']
        assert 'state' in parsed['ST']
        assert 'secondstate' in parsed['ST']

    def test_incomplete_value_for_attribute(self):
        dn = '/C='
        self.assertRaises(ValueError, parse_dn, dn)

        dn = '/C=MX/CN='
        self.assertRaises(ValueError, parse_dn, dn)

    def test_malformed_attribute(self):
        dn = '/Casdf'
        self.assertRaises(ValueError, parse_dn, dn)

    def test_no_dn_in_string(self):
        dn = 'I am a regular string'
        self.assertRaises(ValueError, parse_dn, dn)

    def test_empty_string(self):
        self.assertRaises(ValueError, parse_dn, '')

    def test_invalid_value_at_attribute(self):
        dn = '/C=MX/CN='
        self.assertRaises(ValueError, parse_dn, dn)

    def test_verify_incorrect_certificate(self):
        environ = self.make_environ(
            {'C': 'stuff'},
            {'C': 'stuff'},
            None,
            None,
            verified=False
        )

        assert not verify_certificate(
            environ,
            'SSL_CLIENT_VERIFY',
            'SSL_CLIENT_V_START',
            'SSL_CLIENT_V_END'
        )

    def test_verify_certificate_with_dates_other_than_utc(self):
        start = datetime.utcnow() + relativedelta(months=-1)
        end = datetime.utcnow() + relativedelta(months=11)

        environ = self.make_environ(
            {'C': 'stuff'},
            {'C': 'stuff'},
            start,
            end
        )

        assert not verify_certificate(
            environ,
            'SSL_CLIENT_VERIFY',
            'SSL_CLIENT_V_START',
            'SSL_CLIENT_V_END'
        )

    def test_verify_certificate_with_invalid_date_range(self):
        start = datetime.utcnow() + relativedelta(months=2)
        start = start.replace(tzinfo=tzutc())
        environ = self.make_environ(
            '/C=MX',
            '/C=MX',
            start=start
        )

        assert not verify_certificate(
            environ,
            'SSL_CLIENT_VERIFY',
            'SSL_CLIENT_V_START',
            'SSL_CLIENT_V_END'
        )

        end = datetime.utcnow() + relativedelta(days=-5)
        end = end.replace(tzinfo=tzutc())
        environ = self.make_environ(
            '/C=MX',
            '/C=MX',
            end=end
        )

        assert not verify_certificate(
            environ,
            'SSL_CLIENT_VERIFY',
            'SSL_CLIENT_V_START',
            'SSL_CLIENT_V_END'
        )

    def test_verify_certificate_without_dates(self):
        environ = self.make_environ(
            {'C': 'stuff'},
            {'C': 'stuff'}
        )

        environ['SSL_CLIENT_V_START'] = None
        environ['SSL_CLIENT_V_END'] = None
        assert verify_certificate(
            environ,
            'SSL_CLIENT_VERIFY',
            'SSL_CLIENT_V_START',
            'SSL_CLIENT_V_END'
        )

    def test_verify_certificate_without_start_date(self):
        environ = self.make_environ(
            {'C': 'stuff'},
            {'C': 'stuff'}
        )

        environ['SSL_CLIENT_V_START'] = None
        assert verify_certificate(
            environ,
            'SSL_CLIENT_VERIFY',
            'SSL_CLIENT_V_START',
            'SSL_CLIENT_V_END'
        )

    def test_verify_certificate_without_end_date(self):
        environ = self.make_environ(
            {'C': 'stuff'},
            {'C': 'stuff'}
        )

        environ['SSL_CLIENT_V_END'] = None
        assert verify_certificate(
            environ,
            'SSL_CLIENT_VERIFY',
            'SSL_CLIENT_V_START',
            'SSL_CLIENT_V_END'
        )

    def test_verify_correct_certificate(self):
        issuer = {'C': 'MX', 'ST': 'State', 'CN': 'name', 'O': 'org'}
        subject = {'C': 'MX', 'ST': 'State', 'CN': 'issuer', 'O': 'ca'}
        environ = self.make_environ(issuer, subject)
        assert verify_certificate(
            environ,
            'SSL_CLIENT_VERIFY',
            'SSL_CLIENT_V_START',
            'SSL_CLIENT_V_END'
        )

