# -*- coding: utf-8 -*-
import sys
from setuptools import setup

setup(
    name='lys',
    version='0.3',
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
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    packages=['lys'],
    zip_safe=False
)
