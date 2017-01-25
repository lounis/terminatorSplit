#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 FluqsAqua
#
# Project : fluks-imports
# Author  : Lounis Rahmani <lrahmani@fluksaqua.com>

from __future__ import absolute_import, print_function, division

import os
import logging

from . import terminatorSplit

DEBUG = os.path.exists('.debug')

if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)
elif os.path.exists('.info'):
    logging.getLogger().setLevel(logging.INFO)


def split():
    return terminatorSplit.main()
