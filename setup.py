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

from setuptools import setup, find_packages
from ez_setup import use_setuptools
import os

use_setuptools()

here = os.path.abspath(os.path.dirname(__file__))
readme = open(os.path.join(here, 'README')).read()
version = open(os.path.join(here, 'VERSION')).readline().strip()

setup(name='repoze.who-x509',
      version=version,
      description='x509 repoze.who plugin',
      long_description=readme,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'License :: OSI Approved :: BSD License',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Security'
      ],
      keywords='web x509 repoze who authentication client certificate',
      author='Arturo Sevilla',
      author_email='arturo@ckluster.com',
      namespace_packages=['repoze', 'repoze.who', 'repoze.who.plugins'],
      url='http://www.ckluster.com/',
      license='Modified BSD License (http://www.ckluster.com/OPEN_LICENSE.txt)',
      packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*',
                                      'tests']),
      include_package_data=True,
      zip_safe=True,
      tests_require=[
          'repoze.who >= 1.0.14,<=1.99',
          'python-dateutil < 2.0',
          'coverage',
          'nose'
      ],
      install_requires=[
          'repoze.who >= 1.0.14,<=1.99',
          'python-dateutil < 2.0',
      ],
      setup_requires=['nose>=1.0'],
      test_suite='nose.collector',
      entry_points=''
)
