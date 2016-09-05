from sys import version_info
from setuptools import setup


classifiers = [
    'Development Status :: 3 - Alpha',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: BSD License',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Operating System :: POSIX :: Linux',
]

console_scripts = [
    'pyl-{0.major}.{0.minor} = oneliner:main'.format(version_info)
]

kw = {
    'name':             'oneliner',
    'version':          '0.2.1',
    'description':      'practical python one-liners',
    'long_description': open('README.rst').read(),
    'author':           'Georgi Valkov',
    'author_email':     'georgi.t.valkov@gmail.com',
    'license':          'Revised BSD License',
    'url':              'https://github.com/gvalkov/python-oneliner',
    'keywords':         'oneliner one-liner',
    'classifiers':      classifiers,
    'py_modules':       ['oneliner'],
    'entry_points':     {'console_scripts': console_scripts},
    'zip_safe':         True,
}

if __name__ == '__main__':
    setup(**kw)
