# -*- coding: utf-8 -*-
import sys
from setuptools import setup

setup(
    name='lys',
    version='1.0',
    description='Simple HTML templating for Python',
    long_description=open('README.rst').read(),
    url='http://github.com/mdamien/lys',
    author='Damien MARIÉ',
    author_email='damien@dam.io',
    test_suite='nose.collector',
    tests_require=['nose'],
    license='MIT',
    install_requires=["future"] if sys.version_info < (3,) else [],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    packages=['lys'],
    zip_safe=False
)
