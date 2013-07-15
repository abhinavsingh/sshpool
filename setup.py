# -*- coding: utf-8 -*-
"""
    sshpool
    ~~~~~~~

    Pool of SSH channels accessible via RESTful API and command line utility

    :copyright: (c) 2013 by Abhinav Singh.
    :license: BSD, see LICENSE for more details.
"""
from setuptools import setup, find_packages
import sshpool

entry_points = {
    'console_scripts': [
        'sshpoold = sshpool.sshpoold:main',
        'sshpoolctl = sshpool.sshpoolctl:main',
    ],
}

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: BSD License',
    'Operating System :: MacOS',
    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Programming Language :: Python :: 2.7',
    'Topic :: Utilities',
]

setup(
    name                = 'sshpool',
    version             = sshpool.__version__,
    description         = sshpool.__description__,
    long_description    = open('README.md').read().strip(),
    author              = sshpool.__author__,
    author_email        = sshpool.__author_email__,
    url                 = sshpool.__homepage__,
    license             = sshpool.__license__,
    packages            = find_packages(),
    install_requires    = open('requirements.txt', 'rb').read().strip().split(),
    tests_require       = open('test_requirements.txt', 'rb').read().strip().split(),
    entry_points        = entry_points,
    classifiers         = classifiers
)