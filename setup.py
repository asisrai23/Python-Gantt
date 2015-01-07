#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup, Extension

setup (
    name = 'python-gantt',
    version = '0.3.0',
    author = 'Alexandre Norman',
    author_email = 'norman@xael.org',
    license ='gpl-3.0.txt',
    keywords="gantt, graphics, scheduling, project management",
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
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Scientific/Engineering :: Visualization",
        ],
    packages=['gantt'],
    url = 'http://xael.org/norman/python/python-gantt/',
    description = 'This is a python class to create gantt chart using SVG.',
    long_description=open('README.txt').read(),
    requires=[
        'svgwrite (>=1.1.6)',
        'clize (>=2.0)',
        ],
    )
