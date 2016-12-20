# -*- coding: utf-8 -*-
from ..qt import *

import sys


if sys.version_info > (3,):
    from .icons import icons_py3 as icons 
else:
    from .icons import icons 


from .myguidata import *
from .mymatplotlib import *
from .mypyqtgraph import *
from .resthtml import rest_to_html