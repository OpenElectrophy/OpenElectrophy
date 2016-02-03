#encoding : utf-8 
"""


"""

import quantities as pq
from datetime import datetime
import numpy as np

from .base import OEBase


class LickTrain(OEBase):
    """
    Class to handle a lick train of an animal.
    """
    tablename = 'LickTrain'
    neoclass = None
    attributes =[ ('name', str),
                                            ('index', int),
                                            ('t_start', pq.Quantity, 0),
                                            ('t_stop', pq.Quantity, 0),
                                            ('times', pq.Quantity, 1),
                                            ('durations', pq.Quantity, 1),
                                            ]
    one_to_many_relationship = [ ]
    many_to_one_relationship = [ 'Segment' ]
    many_to_many_relationship = [ ]
    inheriting_quantities = None
