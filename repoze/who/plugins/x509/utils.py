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
This module contains utilities related to repoze who x509 plugin.
"""

from dateutil.parser import parse as date_parse
from dateutil.tz import tzutc
from datetime import datetime
import re


VERIFY_KEY = 'SSL_CLIENT_VERIFY'
VALIDITY_START_KEY = 'SSL_CLIENT_V_START'
VALIDITY_END_KEY = 'SSL_CLIENT_V_END'

# OpenSSL's DNs are separated by /, but the problem is that it may have any
# escaped characters as value.
# Thanks to David Esperanza
_DN_SSL_REGEX = re.compile('(/\\s*\\w+=)')

_TZ_UTC = tzutc()


__all__ = ['parse_dn', 'verify_certificate', 'VERIFY_KEY',
           'VALIDITY_START_KEY', 'VALIDITY_END_KEY']

def parse_dn(dn):
    """
    Parses a OpenSSL-like distinguished name into a dictionary. The keys are
    the attribute types and the values are lists (multiple values for that
    type).

    "Multi-values" are not supported (e.g., O=company+CN=name).
    
    :param dn: The distinguished name.
    
    :raise ValueError: When you input an invalid or empty distinguished name.
    """
    parsed = {}
    split_string = _DN_SSL_REGEX.split(dn)
    if split_string[0] == '':
        split_string.pop(0)
    for i in range(0, len(split_string), 2):
        try:
            type_, value = split_string[i][1:-1], split_string[i + 1]
        except IndexError:
            raise ValueError('Invalid DN')

        if len(value) == 0:
            raise ValueError('Invalid DN: Invalid value')

        if type_ not in parsed:
            parsed[type_] = []
        parsed[type_].append(value)

    if len(parsed) == 0:
        raise ValueError('Invalid DN: Empty DN')

    return parsed


def verify_certificate(environ, verify_key, validity_start_key,
                       validity_end_key):
    """
    Checks if the client certificate is valid. Start and end data is optional,
    as not all SSL mods give that information.

    :param environ: The WSGI environment.
    :param verify_key: The key for the value in the environment where it was
        stored if the certificate is valid or not.
    :param validity_start_key: The key for the value in the environment with
        the encoded datetime that indicates the start of the validity range.
    :param validity_end_key: The key for the value in the environment with the
        encoded datetime that indicates the end of the validity range.
    """
    verified = environ.get(verify_key)
    validity_start = environ.get(validity_start_key)
    validity_end = environ.get(validity_end_key)
    if verified != 'SUCCESS':
        return False

    if validity_start is None or validity_end is None:
        return True

    validity_start = date_parse(validity_start)
    validity_end = date_parse(validity_end)

    if validity_start.tzinfo != _TZ_UTC or validity_end.tzinfo != _TZ_UTC:
        # Can't consider other timezones
        return False

    now = datetime.utcnow().replace(tzinfo=_TZ_UTC)
    return validity_start <= now <= validity_end

