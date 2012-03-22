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
Repoze who x509 plugin. It contains support for an identifier implementation.
"""

from zope.interface import implements as zope_implements
from repoze.who.interfaces import IIdentifier

from .utils import *


__all__ = ['X509Identifier']


class X509Identifier(object):
    """
    IIdentifier for HTTP requests with client certificates.
    """
    zope_implements(IIdentifier)

    classifications = { IIdentifier: ['browser'] }

    def __init__(self, subject_dn_key, login_field='Email',
                 multiple_values=False, verify_key=VERIFY_KEY,
                 start_key=VALIDITY_START_KEY, end_key=VALIDITY_END_KEY,
                 classifications=None):
        """
        :param subject_dn_key: The WSGI environment key for the subject
            distinguished name (it also works as the base for the server
            variables).
        :param login_field: The field of the distinguished name that will use
            to recognize the user.
        :param multiple_values: Determines if we allow to have multiple values
            in the ``login_field``.
        :param verify_key: The WSGI environment key where it can check if the
            client certificate is valid.
        :param start_key: The WSGI environment key with the encoded datetime of
            the start of the validity range.
        :param end_key: The WSGI environment key with the encoded datetime of
            the end of the validity range.
        :param classifications: The ``repoze.who`` classifications for this
            identifier (used with the classifier).
        """
        self.subject_dn_key = subject_dn_key
        self.login_field = login_field
        self.verify_key = verify_key
        self.start_key = start_key
        self.end_key = end_key
        self.multiple_values = multiple_values
        if classifications is not None:
            self.classifications[IIdentifier] = classifications

    # IIdentifier
    def identify(self, environ):
        """
        Gets the credentials for this request.
    
        :param environ: The WSGI environment.
        """
        subject_dn = environ.get(self.subject_dn_key)
        if subject_dn is None or not verify_certificate(
            environ,
            self.verify_key,
            self.start_key,
            self.end_key
        ):
            return None

        creds = {'subject': subject_dn }
        # First let's try with Apache-like var name, if None then parse the DN
        key = self.subject_dn_key + '_' + self.login_field
        login = environ.get(key)
        if login is None:
            try:
                login = parse_dn(subject_dn)[self.login_field]
            except:
                login = None
        else:
            values = []
            try:
                n = 0
                while True:
                    values.append(environ[key + '_' + str(n)])
                    n += 1
            except KeyError:
                pass
            
            if n == 0:
                login = [login]
            else:
                login = values
                

        if login is None:
            return None

        if not self.multiple_values and len(login) > 1:
            return None
        elif not self.multiple_values:
            creds['login'] = login[0]
        else:
            creds['login'] = login

        return creds

    # IIdentifier
    def forget(self, environ, identity):
        """
        Not used. We can't forget because it is client certificated based.
        """
        # We can't forget
        return None

    # IIdentifier
    def remember(self, environ, identity):
        """
        Not used. The browser always remembers the client credentials.
        """
        # We always remember as it is provided by the server
        return None

