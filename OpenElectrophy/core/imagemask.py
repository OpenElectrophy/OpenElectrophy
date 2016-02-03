#encoding : utf-8 
"""


"""

import quantities as pq
from datetime import datetime
import numpy as np

from .base import OEBase


class ImageMask(OEBase):
    """
    Class to handle mask in image.
    """
    tablename = 'ImageMask'
    neoclass = None
    attributes = [ ('name', str),
                                                ('info', str),
                                                ('mask', np.ndarray, 2),
                                                ]
    one_to_many_relationship = [ ]
    many_to_one_relationship = [ 'Block' ]
    many_to_many_relationship = [ ]
    inheriting_quantities = None
