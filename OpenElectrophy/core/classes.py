#encoding : utf-8 
"""
This file extend neo.description :
 * remove Spike, Epoch, Event, IrregularlySampledSignal
 * add Oscillation, RespiratorySignal, LickTrain
 

"""

from collections import OrderedDict
import quantities as pq
from datetime import datetime
import numpy as np

import neo
from neo import description as neod
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





class_names = neod.class_by_name.keys()
not_in_OE = [ 'Spike', 'Epoch', 'Event', 'IrregularlySampledSignal' ]
for e in not_in_OE:
    class_names.remove(e)

oeclasses = [ ]
for name in class_names:
    if name in neod.one_to_many_relationship:
        one_to_many = list(neod.one_to_many_relationship[name])
        for e in not_in_OE:
            if e in one_to_many:
                one_to_many.remove(e)
    else:
        one_to_many = [ ]
    
    if name in neod.many_to_many_relationship:
        many_to_many = list(neod.many_to_many_relationship[name])
        for e in not_in_OE:
            if e in many_to_many:
                many_to_many_relationship[name].remove(e)
    else:
        many_to_many = [ ]
    
    if name in neod.classes_inheriting_quantities:
        inheriting_quantities = neod.classes_inheriting_quantities[name]
    else:
        inheriting_quantities = None
    
    usable_attributes = OrderedDict()
    attributes = neod.classes_necessary_attributes[name] + neod.classes_recommended_attributes[name]
    for attribute in attributes:
        attrname, attrtype = attribute[0], attribute[1]
        usable_attributes[attrname] = attrtype
    
    classattr = dict(tablename = name,
                            neoclass = neod.class_by_name[name],
                            attributes = attributes,
                            usable_attributes = usable_attributes,
                            one_to_many_relationship  = one_to_many,
                            many_to_one_relationship =[ ],
                            many_to_many_relationship  = many_to_many,
                            inheriting_quantities = inheriting_quantities,
                            )
    oeclasses.append(type(name, (OEBase,), classattr))
    


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
    



