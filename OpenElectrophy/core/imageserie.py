#encoding : utf-8 
"""


"""



import quantities as pq
from datetime import datetime
import numpy as np

from .base import OEBase


class ImageSerie(OEBase):
    """
    Class to handle a timed serie of image (a video...).
    """
    tablename = 'ImageSerie'
    neoclass = None
    attributes =[ ('name', str),
                                                ('t_start', pq.Quantity, 0),
                                                ('sampling_rate', pq.Quantity, 0),
                                                ('images', np.ndarray, 3),
                                                ]
    one_to_many_relationship = [ ]
    many_to_one_relationship = [ 'Segment' ]
    many_to_many_relationship = [ ]
    inheriting_quantities = None
