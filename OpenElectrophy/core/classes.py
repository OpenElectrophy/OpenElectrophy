#encoding : utf-8 
"""
This file extend neo.description :
 * remove Spike, Epoch, Event, IrregularlySampledSignal
 * add Oscillation, RespiratorySignal, LickTrain
 

"""


import neo

from collections import OrderedDict
import quantities as pq
from datetime import datetime
import numpy as np

import neo

from base import OEBase


"""
oeclasses is a list containing all classes like this:

class Block(OEBase):
    # in OE there no difference between recommend or necessary
    tablename = 'Block'
    neoclass = neo.Block
    usable_attributes = neod.classes_necessary_attributes['Block'] + neod.classes_recommended_attributes['Block']
    one_to_many_relationship = neod.one_to_many_relationship['Block']
    many_to_one_relationship = [ ]
    many_to_many_relationship = neod.many_to_many_relationship['Block']
    inheriting_quantities = None
    
"""


not_in_OE = [ 'Spike', 'Epoch', 'Event', 'IrregularlySampledSignal' ]
with_color = ['AnalogSignal', 'SpikeTrain', 'EventArray', 'EpochArray', 'Unit']



oeclasses = [ ]
for neoname, neoclass in neo.class_by_name.items():
    if neoname in not_in_OE:
        continue
    
    one_to_many = [ ]
    if hasattr(neoclass, '_data_child_objects'):
        for e in neoclass._data_child_objects:
            if e not in not_in_OE:
                one_to_many.append(e)
    
    if hasattr(neoclass, '_container_child_objects'):
        for e in neoclass._container_child_objects:
            if e not in not_in_OE:
                one_to_many.append(e)
    
    many_to_many = [ ]
    for e in neoclass._multi_parent_objects:
        if e not in not_in_OE:
            many_to_many.append(e)
    
    if hasattr(neoclass, '_quantity_attr'):
        inheriting_quantities = neoclass._quantity_attr
    else:
        inheriting_quantities = None
    
    usable_attributes = OrderedDict()
    attributes = list(neoclass._necessary_attrs) + list(neoclass._recommended_attrs)
    for attribute in attributes:
        attrname, attrtype = attribute[0], attribute[1]
        usable_attributes[attrname] = attrtype
    
    if neoname in with_color and 'color' not in usable_attributes:
        usable_attributes['color'] = str
    
    classattr = dict(tablename = neoname,
                            neoclass = neoclass,
                            attributes = attributes,
                            usable_attributes = usable_attributes,
                            one_to_many_relationship  = one_to_many,
                            many_to_one_relationship =[ ],
                            many_to_many_relationship  = many_to_many,
                            inheriting_quantities = inheriting_quantities,
                            )
    oeclasses.append(type(neoname, (OEBase,), classattr))



# extend with other classes
from oscillation import Oscillation
from licktrain import LickTrain
from respirationsignal import RespirationSignal
from imageserie import ImageSerie
from imagemask import ImageMask

extention_classes =  [ Oscillation, LickTrain, RespirationSignal, ImageSerie, ImageMask]

for oeclass in extention_classes:
    oeclasses.append(oeclass)
    oeclass.usable_attributes = OrderedDict()
    for attribute in oeclass.attributes:
        attrname, attrtype = attribute[0], attribute[1]
        oeclass.usable_attributes[attrname] = attrtype


class_by_name = { }
for class_ in oeclasses:
    class_by_name[class_.__name__] = class_



#~ one_to_many_relationship['AnalogSignal'] = ['Oscillation', ]
#~ one_to_many_relationship['Segment'] += [ 'LickTrain', 'RespirationSignal',  'ImageSerie', ]
#~ one_to_many_relationship['Block'] +=  ['ImageMask', ]




# check bijectivity of many_to_one_relationship and one_to_many_relationship
# check bijectivity of many_to_many_relationship
for c1 in class_by_name.keys():
    for c2 in class_by_name[c1].one_to_many_relationship:
        if c1 not in class_by_name[c2].many_to_one_relationship :
            class_by_name[c2].many_to_one_relationship.append(c1)
    for c2 in class_by_name[c1].many_to_one_relationship:
        if c1 not in class_by_name[c2].one_to_many_relationship :
            class_by_name[c2].one_to_many_relationship.append(c1)
    for c2 in class_by_name[c1].many_to_many_relationship:
        if c1 not in class_by_name[c2].many_to_many_relationship :
            class_by_name[c2].many_to_many_relationship.append(c1)
    



