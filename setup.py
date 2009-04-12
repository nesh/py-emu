#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 Djordjevic Nebojsa <djnesh@gmail.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.


from distutils.cmd import Command
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = 'py-emu',
    version = '0.0.1',
    description = 'Python based emulators',
    long_description = '',
    author = 'Nebojsa Djordjevic',
    author_email = 'djnesh@gmail.com',
    #license = 'BSD',
    #url = 'http://github.com/nesh/srcyr2lat',
    #zip_safe = True,
    #packages = ['srcyr2lat'],
    #test_suite = 'srcyr2lat.tests',
    #scripts=['bin/srcyr2lat']
)
