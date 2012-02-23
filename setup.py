#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Matthew Good
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
# most of the code from Matt Good, https://github.com/mgood/jsonmapper


from setuptools import setup


setup(
    name = 'JSONMapperHGMMPFork',
    version = '0.15',
    description = "Mapping JSON to objects and vice versa, this is a product of Christopher Lenz and Matthew Good with slight modifications",
    long_description = '',
    author = 'Martin Peschke',
    author_email = 'martin@per-4.com',
    requires=['simplejson', 'httplib2', 'formencode', 'pyramid', 'mako'],
    license = 'BSD',
    url = 'https://github.com/MartinPeschke/jsonmapper',
    packages = ['jsonmapper'],
)
