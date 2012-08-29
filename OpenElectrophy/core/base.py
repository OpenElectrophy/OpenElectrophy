#encoding : utf-8 

import quantities as pq
import numpy as np

import neo


class OEBase(object):
    """
    Base for generic class in OpenElectrophy.
    
    """

    def __new__( cls, session = None,*args, **kargs):
        if 'id' in kargs:
            obj = cls.load(id =kargs['id'],  session = session)
        else:
            obj = super( OEBase,cls).__new__(cls)
        obj.neoinstance = None
        return obj
    
    def __init__(self, **kargs):
        for k,v in kargs.items():
            if k in self.usable_attributes:
                setattr(self, k, v)
        self.neoinstance = None

    
    def __repr__(self):
        t = super(OEBase, self).__repr__()
        t += '\n'
        t += '  id: {}\n'.format(self.id)
        for attrname, attrtype in self.usable_attributes.items():
            #~ if attrtype not in [ np.ndarray ,pq.Quantity ]:
                t += '  {}: {}\n'.format(attrname,getattr(self,attrname))
            #~ else:
                #~ t += '  {} shape: {} \n'.format(attrname,getattr(self,attrname+'_shape'))
        return t
    
    def save(self, session = None):
        if session is None:
            from sqlmapper import globalsesession
            session = globalsesession
        assert session is not None, 'You must give a session for loading {}'.format(cls.__classname__)
        self.update()
        session.add(self)
        session.commit()
    
    def update(self, session = None):
        # force the instance to be in session.dirty
        # util for mutable np.array or pq.Quantoties fileds
        for attrname, attrtype  in self.usable_attributes.items():
            if attrtype == np.ndarray or attrtype == pq.Quantity :
                setattr(self, attrname, getattr(self, attrname))
        

    @classmethod
    def load(cls, id, session = None,):
        if session is None:
            from sqlmapper import globalsesession
            session = globalsesession
        assert session is not None, 'You must give a session for loading {}'.format(cls.__classname__)
        return session.query(cls).get(id)
    
    @classmethod
    def from_neo(cls, neoinstance, mapped_classes, cascade =False):
        """
        Create a generic OE instance from a neo object.
        Util for inseritng in db.
        
        Usage:
          >>> import neo
          >>> reader = neo.io.PlexonIO(filename = 'a file.plx')
          >>> bl = reader.read() # this give a neo Block
          >>> import OpenElectrophy
          >>> from OpenElectrophy import *
          >>> generic_classes, Session = open_db(..., use_global_session = True)
          >>> bl2 = OEBase.from_neo(bl, generic_classes) # this give a generic OE Block
          >>> bl2.save()
        """
        if hasattr(neoinstance, 'OEinstance'):
            OEinstance = neoinstance.OEinstance
        else:
            mapped_class = None
            for  class_ in mapped_classes:
                if class_.neoclass == type(neoinstance):
                    mapped_class = class_
            assert mapped_class is not None, 'Do not known this object {}'.format(type(neoinstance).__name__)
            neoclassname =  type(neoinstance).__name__
            
            kargs = {}
            attrnames = [attr[0] for attr in mapped_class.attributes ]
            for k in mapped_class.usable_attributes:
                if k == mapped_class.inheriting_quantities:
                    # speciale case : the neo object is itself a OE attributes
                    kargs[k] = neoinstance.view(pq.Quantity)
                elif k in attrnames:
                    # standart case: neo attributes is OE attribute
                    kargs[k]  = getattr(neoinstance, k)
                elif k in neoinstance.annotations:
                    # speciale casse: the OE attribute is in annotations (free attributes)
                    kargs[k] = neoinstance.annotations[k]
            OEinstance = mapped_class(**kargs)
            OEinstance.neoinstance = neoinstance
            neoinstance.OEinstance = OEinstance
        
        if cascade:
            for childname in OEinstance.many_to_many_relationship:
                for child in getattr(neoinstance, childname.lower()+'s'):
                    if not hasattr(child, 'OEinstance'):
                        OEchild = OEBase.from_neo(child, mapped_classes, cascade = True)
                    else:
                        OEchild = child.OEinstance
                    if OEchild not in getattr(OEinstance, childname.lower()+'s'):
                        getattr(OEinstance, childname.lower()+'s').append( OEchild )
                        getattr(OEchild, OEinstance.tablename.lower()+'s').append( OEinstance )
            for childname in OEinstance.one_to_many_relationship:
                if not hasattr(neoinstance, childname.lower()+'s'): continue
                for child in getattr(neoinstance, childname.lower()+'s'):
                    getattr(OEinstance, childname.lower()+'s').append(OEBase.from_neo(child, mapped_classes, cascade = True))
            for parentname in OEinstance.many_to_one_relationship:
                if hasattr(neoinstance, parentname):
                    neoparent = getattr(neoinstance, parentname)
                    if not hasattr(neoparent, 'OEinstance'):
                        setattr(OEinstance, parentname, OEBase.from_neo(neoparent, mapped_classes, cascade = True))
        
        # TODO: find a system to remove OEinstance to all neo obj when cascade
        #~ if not keep_link_to_neo:
            #~ delattr(neoinstance, 'OEinstance')
        return OEinstance

    def to_neo(self, cascade = False):
        if self.neoclass is not None:
            # attributes
            if self.neoinstance is None:
                kargs = {}
                for k in self.usable_attributes:
                    kargs[k] = getattr(self, k)
                self.neoinstance = self.neoclass(**kargs)
            
            # cascade relationships
            if cascade:
                for childname in self.many_to_many_relationship:
                    for child in getattr(self, childname.lower()+'s'):
                        neochild = child.neoinstance
                        if neochild is None:
                            neochild = child.to_neo(cascade = True)
                        if neochild is not None and neochild not in getattr(self.neoinstance, childname.lower()+'s'):
                            getattr(self.neoinstance, childname.lower()+'s').append( neochild )
                            getattr(neochild, self.tablename.lower()+'s').append( self.neoinstance )
                for childname in self.one_to_many_relationship:
                    for child in getattr(self, childname.lower()+'s'):
                        getattr(self.neoinstance, childname.lower()+'s').append(child.to_neo(cascade = True))
                for parentname in self.many_to_one_relationship:
                    if hasattr(self, parentname.lower()):
                        OEparent = getattr(self, parentname.lower())
                        neoparent = OEparent.neoinstance
                        if neoparent is None:
                            neoparent = OEparent.to_neo(cascade=True)
                        if neoparent is not None:
                            setattr(self.neoinstance, parentname.lower(), neoparent)
            
            return self.neoinstance
        
            
            
            
            
