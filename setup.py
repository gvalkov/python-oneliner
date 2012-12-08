#!/usr/bin/env python
# encoding: utf-8

from os.path import abspath, dirname, join
from sys import version_info
from setuptools import setup


here = abspath(dirname(__file__))

classifiers = (
    'Development Status :: 3 - Alpha',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.1',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'License :: OSI Approved :: BSD License',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Operating System :: POSIX :: Linux',
)

console_scripts = \
    ['pyl-{0.major}.{0.minor} = oneliner:main'.format(version_info)]

kw = {
    'name'                 : 'oneliner',
    'version'              : '0.1.0',

    'description'          : 'module for writing practical python one-liners',
    'long_description'     : open(join(here, 'README.rst')).read(),

    'author'               : 'Georgi Valkov',
    'author_email'         : 'georgi.t.valkov@gmail.com',
    'license'              : 'New BSD License',
    'url'                  : 'https://github.com/gvalkov/python-oneliner',

    'keywords'             : 'oneliner one-liner',
    'classifiers'          : classifiers,

    'py_modules'           : ['oneliner'],
    'entry_points'         : {'console_scripts' : console_scripts},
    'zip_safe'             : True,
}

setup(**kw)
