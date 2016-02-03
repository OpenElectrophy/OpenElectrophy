#encoding : utf-8 
"""


"""



import quantities as pq
from datetime import datetime
import numpy as np

from .base import OEBase


class RespirationSignal(OEBase):
    """
    Class to handle a respiration signal and its cycle (inspiration/expiration)
    """
    tablename = 'RespirationSignal'
    neoclass = None
    attributes = [ ('name', str),
                                        ('channel_index', int),
                                        ('t_start', pq.Quantity, 0),
                                        ('sampling_rate', pq.Quantity, 0),
                                        ('signal', pq.Quantity, 1),
                                        ('cycle_times', pq.Quantity, 2),
                                        ]
    one_to_many_relationship = [ ]
    many_to_one_relationship = [ 'Segment' ]
    many_to_many_relationship = [ ]
    inheriting_quantities = None


