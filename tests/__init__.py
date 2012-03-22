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

"""
Test suite for repoze.who-x509
"""

from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc
from datetime import datetime
import unittest
import locale


class TestX509Base(unittest.TestCase):
    """Base class for testing X509 predictes"""

    def generate_dn(self, **kwargs):
        return ''.join(['/' + t + '=' +  v for t, v in kwargs.iteritems()])

    def make_environ(self, issuer, subject, start=None, end=None,
                     verified=True,
                     prefix=None,
                     verify_key='SSL_CLIENT_VERIFY',
                     validity_start_key='SSL_CLIENT_V_START',
                     validity_end_key='SSL_CLIENT_V_END',
                     issuer_key='SSL_CLIENT_I_DN',
                     subject_key='SSL_CLIENT_S_DN'):
        # By default consider that our certificate was signed a month ago for
        # the common validity of one year.
        prefix = prefix or ''
        if start is None:
            start = datetime.utcnow() + relativedelta(months=-1)
            start = start.replace(tzinfo=tzutc())
        if end is None:
            end = datetime.utcnow() + relativedelta(months=11)
            end = end.replace(tzinfo=tzutc())

        locale.setlocale(locale.LC_ALL, 'en_US.utf8')
        datefmt = '%b %d %H:%M:%S %Y %Z'
        start, end = start.strftime(datefmt), end.strftime(datefmt)

        environ = {}
        environ[verify_key] = 'SUCCESS' if verified else 'FAILED'
        environ[prefix + validity_start_key] = start
        environ[prefix + validity_end_key] = end
        environ[prefix + issuer_key] = issuer if isinstance(issuer, basestring)\
                                       else self.generate_dn(**issuer)
        environ[prefix + subject_key] = subject if isinstance(
            subject,
            basestring) else self.generate_dn(**subject)

        return environ

