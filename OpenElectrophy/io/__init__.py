# -*- coding: utf-8 -*-
"""
Add some more IOs than neo.io
"""

import neo

from .tryitio import TryItIO


iolist = [ TryItIO ] + neo.io.iolist
