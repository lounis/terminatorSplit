#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Project : fluks-imports
# Author  : Lounis Rahmani

import csv
import logging
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='trSplit',
    version='0.0.1',
    description='Wrapper script for splitting Terminator terminal emulator',
    author='Lounis Rahmani',
    author_email='lrahmani@fluksaqua.com',
    packages=[
        'trSplit',
    ],
    package_dir={'trSplit': 'trSplit'},
    entry_points={
        'console_scripts': [
            'trsplit= trSplit:split',
        ],
    },
    include_package_data=True,
    install_requires=[
    ],
)
