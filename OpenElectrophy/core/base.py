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
        for k in self.usable_attributes:
            setattr(self, k, None)
        for k,v in kargs.items():
            if k in self.usable_attributes:
                setattr(self, k, v)
        self.neoinstance = None

    
    def __repr__(self):
        t = super(OEBase, self).__repr__()
        t += '\n'
        if hasattr(self, 'id'):
            t += '  id: {}\n'.format(self.id)
        #~ else:
            
        for attrname, attrtype in self.usable_attributes.items():
            #~ if attrtype not in [ np.ndarray ,pq.Quantity ]:
                t += '  {}: {}\n'.format(attrname,getattr(self,attrname))
            #~ else:
                #~ t += '  {} shape: {} \n'.format(attrname,getattr(self,attrname+'_shape'))
        return t
    
    def save(self, session = None):
        if session is None:
            from sqlmapper import globalsession
            session = globalsession
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
            from sqlmapper import globalsession
            session = globalsession
        assert session is not None, 'You must give a session for loading {}'.format(cls.__classname__)
        return session.query(cls).get(id)
    
    @classmethod
    def from_neo(cls, neoinstance, mapped_classes = None, cascade =False):
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
        if mapped_classes is None:
            from sqlmapper import globaldbinfo
            mapped_classes = globaldbinfo.mapped_classes
        assert mapped_classes is not None, 'You must give a mapped_classes'
        
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
                        #~ getattr(OEchild, OEinstance.tablename.lower()+'s').append( OEinstance ) # DONE with orm.backref
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

    def to_neo(self, cascade = False, with_many_to_many = True,
                with_one_to_many = True, with_many_to_one = True,
                propagate_many_to_many = False):
        # TODO ?
        # with_many_to_many  with_one_to_many with_many_to_one
        if self.neoclass is not None:
            #~ print 'to_neo', self.__class__, self.id
            # attributes
            if self.neoinstance is None:
                #~ print type(self), self.id
                #~ print 'yep', self.id
                #~ self.neoinstance = 'doing'
                kargs = {}
                for k in self.usable_attributes:
                    kargs[k] = getattr(self, k)
                self.neoinstance = self.neoclass(**kargs)
                self.neoinstance.OEinstance = self
            # cascade relationships
            if cascade:
                if with_many_to_many:
                    for childname in self.many_to_many_relationship:
                        for child in getattr(self, childname.lower()+'s'):
                            neochild = child.neoinstance
                            if neochild is None:
                                neochild = child.to_neo(cascade = True, with_many_to_many = with_many_to_many and propagate_many_to_many,
                                                            with_one_to_many = with_one_to_many, with_many_to_one = with_many_to_one)
                            #~ if neochild is not None and neochild not in getattr(self.neoinstance, childname.lower()+'s'):
                            if neochild is not None and not list_contains(getattr(self.neoinstance, childname.lower()+'s'), neochild):
                                getattr(self.neoinstance, childname.lower()+'s').append( neochild )
                                getattr(neochild, self.tablename.lower()+'s').append( self.neoinstance )
                if with_one_to_many:
                    for childname in self.one_to_many_relationship:
                        for child in getattr(self, childname.lower()+'s'):
                            neochild = child.to_neo(cascade = True,with_many_to_many = with_many_to_many and propagate_many_to_many,
                                                            with_one_to_many = with_one_to_many, with_many_to_one = with_many_to_one)
                            if neochild is None: continue
                            neochildren = getattr(self.neoinstance, childname.lower()+'s')
                            if not list_contains(neochildren, neochild):
                                neochildren.append(neochild)
                            #~ if neochild is not None and neochild not in neochildren:
                                #~ neochildren.append(neochild)
                if with_many_to_one:
                    for parentname in self.many_to_one_relationship:
                        if hasattr(self, parentname.lower()):
                            OEparent = getattr(self, parentname.lower())
                            if OEparent is None: continue
                            neoparent = OEparent.neoinstance
                            if neoparent is None:
                                neoparent = OEparent.to_neo(cascade=True,with_many_to_many = with_many_to_many and propagate_many_to_many,
                                                            with_one_to_many = with_one_to_many, with_many_to_one = with_many_to_one)
                                #~ neoparent = OEparent.to_neo(cascade=False)
                            if neoparent is not None:
                                setattr(self.neoinstance, parentname.lower(), neoparent)
            
            return self.neoinstance

# alias
neo_to_oe = OEBase.from_neo


# some hack for python list when contain numpy.array
def list_contains(l, e):
    # should be
    # return s in l
    return np.any([ e is e2 for e2 in l ])
