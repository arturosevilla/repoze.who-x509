**********************************
The :mod:`repoze.who` X509 plugin
**********************************

:Author: `Arturo Sevilla <http://www.ckluster.com/>`_.
:Latest release: |release|

.. module:: repoze.who.plugins.x509
.. moduleauthor:: Arturo Sevilla <arturo@ckluster.com>

.. topic:: Overview

    This plugin enables :mod:`repoze.who` to identify (not completely
    authenticate) according to SSL client certificates. It can check the fields
    (attribute types) in the subject distinguished name.

    It supports "out of the box" ``mod_ssl`` if ``mod_wsgi`` is also activated
    in Apache, and Nginx SSL functionality. However, this documentation also
    includes configuration examples for both Apache and Nginx for when both are
    working as reverse proxies.

    This plugin was developed independently of the repoze project (copyrighted
    to Agendaless Consulting, Inc.).

Installing this plugin
======================

The minimum requirements for installation are :mod:`repoze.who`,
and ``python-dateutil``. If you want to run the tests, then
Nose and its coverage plugin will also be installed. It can be installed with
``easy_install``::
    
    easy_install repoze.who-x509

Support and development
=======================

The project is hosted on `GitHub
<https://github.com/arturosevilla/repoze.who-x509/>`_.

Quick setup
===========

If you want to use the ``IIdentifier`` object, then you can build it as
follows, and the pass it to the ``identifiers`` parameter of
``repoze.who.middleware.PluggableAuthenticationMiddleware``::
    
    from repoze.who.plugins.x509 import X509Identifier

    identifer = X509Identifier('SSL_CLIENT_S_DN')

The required parameter of :py:class:`X509Identifier` is the WSGI environment
key of the "distinguished name" of the client certificate subject. By default
the credentials are based on the "Email" field, but it can be customized as
follows::

    from repoze.who.plugis.x509 import X509Identifier

    identifier = X509Identifier('SSL_CLIENT_S_DN', login_field='CN')

In this case it will try to get the credentials from the common name of the
client certificate subject.

Contents
========

.. toctree::
   :maxdepth: 2

   changes
   configuration

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

