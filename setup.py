#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup, Extension

gantt = Extension('gantt',
                 sources = ['gantt/gantt.py', 'gantt/__init__.py', 'gantt/example.py'])

from gantt import *

# Install : python setup.py install
# Register : python setup.py register

#  platform = 'Unix',
#  download_url = 'http://xael.org/norman/python/python-gantt/',

setup (
    name = 'python-gantt',
    version = gantt.__version__,
    author = 'Alexandre Norman',
    author_email = 'norman@xael.org',
    license ='gpl-3.0.txt',
    keywords="gantt, graphics, schedulling, project management",
    # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    platforms=[
        "Operating System :: OS Independent",
        ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Scientific/Engineering :: Visualization",
        ],
    packages=['gantt'],
    url = 'http://xael.org/norman/python/python-gantt/',
    description = 'This is a python class to create gantt schema and to convert org-mode projects in gantt schema',
    long_description=open('README.txt').read() + "\n" + open('CHANGELOG').read(),
    )
