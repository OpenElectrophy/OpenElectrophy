# -*- coding: utf-8 -*-
"""
Add some more IOs than neo.io
"""

import neo

from .tryitio import TryItIO
from .neurolabscope2 import Neurolabscope2IO
from .neurolabscope1 import Neurolabscope1IO

iolist = [ TryItIO, Neurolabscope2IO, Neurolabscope1IO] + neo.io.iolist
