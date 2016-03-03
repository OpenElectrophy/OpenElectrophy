#encoding : utf-8
"""

SQL mapper
============


Concepts
-------------------

This module is on top of sqlalchemy (and optionally PyTables) and offer the user the abbility to play with databases with few knownledges.

The model object is based on neo 0.2 enhanced with some classes (Oscillation, respiratorySignal, imageSerie, ImageMask, LickTrain)

Main possibilities of this mapper are:
  * Create automagically table schema from neo.description (enhenced by OpenElectrophy.description) on MySQL, SQLite or PG (and 
        and normally all sqlalchemy backends)
  * Create for the user new tables and its relationship (Ex Animal on top of Block)
  * when openning a databse explore all tables schema to also map new columns and new tables.
  * map transparently numpy.ndarray and quantities.Quantity in SQL table or in a HDF5 separated file.
  * cache loaded object in fixed size queue to avoid reloding when accing several times


Conversion
----------------------------


Rules of conversions:
    * standart python are converted naturally to one column with sqlalchemy types (str>Text, int>Integer, datetime>DateTime,  float > Float)
    * np.array and pq.Quantity attributes are manage in 2 possible ways:
        * in a separated SQL table: 'NumpyArrayTable'
        * in a separate HDF5 file with PyTbales
    * Classes that inerit in neo Quantities are manage with attributes (AnalogSIgnal.signal, SpikeTrain.times, ...)
    
Notes:
    * all numpy.array and pq.Quantity are deffered loaded. (They are load only when used)
    * np.array can be compressed with zlib or blosc this can speed R/W

Rules of relationship:
    * one_to_many and many_to_one : the child name have a column (Interger) which is also Index construct with: *parentname.lower()*+'_id'
    * many_to_many: a table  with XREF do the job. Ex:   table1XREFtable2



Schema creation and manipualtion
----------------------------------------------------------------


Example1 : Creating a db, the first opening  create the schema::

    url = 'sqlite:///myfirstdb.sqlite'
    open_db(url)



Standart save and load
-------------------------------------------

There are ways for playing with object in databases 

  1. the easy one is to open_db with:
      * use_global_session=True
      * myglobals = globals()

    With that you can do for creating::

        url = 'sqlite:///myfirstdb.sqlite'
        open_db(url, use_global_session=True, myglobals = globals())
        bl = Block(name = 'a new block')
        seg = Segment(name = 'a segment', index = 0)
        bl.segments.append(seg)
        bl.save()
        
    And this for loading::
    
        url = 'sqlite:///myfirstdb.sqlite'
        open_db(url, use_global_session=True, myglobals = globals())
        bl = Block.load(id = 50)
        print bl.id
        print bl.name
        # also
        bl = Block(id = 50)
        print bl.id
        print bl.name
        

  2. The sqlalchemy way play with session by our own::

        url = 'sqlite:///myfirstdb.sqlite'
        dbinfo = open_db(url, use_global_session=False, myglobals = globals())
        Session = dbinfo.Session # this is a session generator in sqlalchemy land.
        
        # create a session
        session = Session()
        bl = Block(name = 'a new block')
        seg = Segment(name = 'a segment', index = 0)
        bl.segments.append(seg)
        session.add(bl)
        session.commit()
        id_bl = bl.id
        session.close()
        
        # create another session
        session = Session()
        reload_bl = session.query(Block).get(id_bl)
        
    
    This way is safer with multiprocessing and GUI.


Mapped classes
--------------------------------

Classes in OE are generated on the fly when openning a db.

Each time a new db is opened (with open_db) each time the classes are re created by reflection of table.

When scripting, you can injected this mapped_classes dict in your locals() or globals() to use direectly object : Block, Segment, AnalogSignal, ...

Ex::

    open_db(url, myglobals= globals())

is equivalent to::

    dbinfo= open_db(url)
    globals().update(dbinfo.mapped_classes)

You also inject in globals() for standart scripting and interactive environement (ipython)::

    open_db(url, myglobals= globals())



If you want to avoid problems with neo namespace you can add a prefix to lass name (suffix_for_class_name = '_',) ::

    from neo import *
    print Block # this is a neo.Block
    open_db(url, myglobals= locals(), suffix_for_class_name = '_')
    print _Block # this is a OpenElectrophy.core.mapper._Block



Links with neo
---------------------------------

Mapped classes are not directly neo classes because:
  * Some neo classes directly inherits numpy.array that make the mapper tricky!
  * Some neo classes directly inherits numpy.array that force the mapper to load all BLOB columns
  * free attributes are dealt with annotations dict in neo they are standart mapped attributes in OE.

In short neo.Block is not a OpenElectrophy.Block  but it behaves the same (relationship, attributes).


You can convert objects from neo to OE with OEbase.to_neo method for all object.
And recipro objects OE to neo with OEBase.from_neo (class method).
This is usefull for toolboxes bases on neo objects.


Example: read with neo io and save to database::

    from neo import PlexonIO
    from OpenElectrophy import open_db
    reader = io.PlexonIO(filename='File_plexon_1.plx')
    block_neo = reader.read_block()
    url = 'sqlite:///' # in memory
    open_db(url, myglobals= globals())
    block_OE = Block.from_neo(bl, cascade = True) # this convert block and all hierachy
    block_OE.save() # this save the block and all the hierachy
    
Cache
------------------

To avoid multiple reload when queying several times the same object.
The mapper offer a very basic cache system : with the event load sytem of sqlalchemy.
The object is put is in big list (collections.deque) with a limit size so the object is referenced a least once.
At futur reaload the object is not reloaded.

Example::
    
    import quantities as pq
    url = 'sqlite:///myfirstdb.sqlite'
    open_db(url, myglobals = globals(), object_number_in_cache = 20)
    
    ana = AnalogSignal( signal = np.arange(1000)*pq.mV, t_start= 0.*pq.s, sampling_rate = 200*pq.Hz)
    ana.save()
    id = ana.id
    
    del ana
    for i in range(50):
        # the load is done only once
        ana  = AnalogSignal(id = id)



Reference
-----------------------


.. autofunction:: open_db

.. autofunction:: execute_sql

.. autoclass:: DataBaseConnectionInfo

   





"""

from collections import OrderedDict, deque

import sqlalchemy
import migrate.changeset #this add column create
from sqlalchemy import orm

from sqlalchemy import create_engine  , MetaData
from sqlalchemy import Table, Column, Integer, String, Float,  Text, UnicodeText, LargeBinary, DateTime, PickleType, Boolean
from sqlalchemy import BLOB
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import event
from sqlalchemy.orm import object_session

import os
import quantities as pq
from datetime import datetime
import numpy as np

DEFAULT_COMPRESS_LIB = 'lz4'
try:
    import lz4
except ImportError:
    DEFAULT_COMPRESS_LIB = 'snappy'
try:
    import snappy
except ImportError:
    DEFAULT_COMPRESS_LIB = 'blosc'
try:
    import blosc
except ImportError:
    DEFAULT_COMPRESS_LIB = 'zlib'
import zlib


import tables

from base import OEBase




MAX_BINARY_SIZE = 2**30


python_to_sa_conversion = { 
                                                        str : Text,
                                                        int : Integer,
                                                        datetime : DateTime,
                                                        float : Float,
                                                        #~ object: PickleType,
                                                        buffer: LargeBinary,
                                                        bool  : Boolean,
                                                        }
#~ sa_to_python_conversion = { }
#~ for k,v in python_to_sa_conversion.items():
    #~ sa_to_python_conversion[v] = k


global globalsession
globalsession = None
global globaldbinfo
globaldbinfo = None



def create_column_if_not_exists(table, attrname, attrtype):
    """
    Create a clolumn in a table given its python type.
    
    :param table: 
    
    :param attribute:
    
    """
    colnames = [ col.name for col in table.columns ]
    
    
    #~ if attrtype == np.ndarray or attrtype == pq.Quantity :
        #~ if attrname+'_blob' not in colnames:
            #~ col =  Column(attrname+'_shape', String(128))
            #~ col.create( table)
            #~ col =  Column(attrname+'_dtype', String(128))
            #~ col.create( table)
            #~ col =  Column(attrname+'_blob', LargeBinary(MAX_BINARY_SIZE))
            #~ col.create( table)
            #~ if attrtype == pq.Quantity :
                #~ col =  Column(attrname+'_units', String(128))
                #~ col.create( table)
    if attrtype == np.ndarray :
        if attrname+'_numpy_id' not in colnames:
            col =  Column(attrname+'_numpy_id', Integer)
            col.create( table)
    elif attrtype == pq.Quantity :
        if attrname+'_quantity_id' not in colnames:
            col =  Column(attrname+'_quantity_id', Integer)
            col.create( table)
    elif attrtype in python_to_sa_conversion:
        if attrname not in colnames:
            if attrtype is buffer:
                col = Column(attrname, LargeBinary(MAX_BINARY_SIZE))
            else:
                col = Column(attrname, python_to_sa_conversion[attrtype])
            col.create( table )
    else:
        raise NotImplementedError


#TODO
#~ def remove_column(table, attrname):
    #~ #TODO
    #~ table = metadata.tables[oeclass.tablename]
    #~ fieldtype = dict(oeclass.fields)[fieldname]
    
    #~ if fieldtype == numpy.ndarray :
        #~ for suffix in [ '_shape' , '_dtype' , '_blob' ]:
            #~ table.c[fieldname+suffix].drop()
    #~ else :
        #~ table.c[fieldname].drop()



def create_one_to_many_relationship_if_not_exists(parenttable, childtable):
    if parenttable.name.lower()+'_id' in childtable.columns: return
    col=  Column(parenttable.name.lower()+'_id', Integer)#, ForeignKey(parenttable.name+'.id'))
    col.create( childtable)
    ind = Index('ix_'+childtable.name.lower()+'_'+parenttable.name.lower()+'_id', col , unique = False)
    ind.create()

def create_many_to_many_relationship_if_not_exists(table1, table2, metadata):
    if table1.name>table2.name:
        xref_table = table1.name+'XREF'+table2.name
    else:
        xref_table = table2.name+'XREF'+table1.name
    if xref_table in metadata.tables: return
    c1 = Column(table1.name.lower()+'_id', Integer, ForeignKey(table1.name+'.id'), index = True, primary_key = True)
    c2 = Column(table2.name.lower()+'_id', Integer, ForeignKey(table2.name+'.id'), index = True, primary_key = True)
    table =  Table(xref_table, metadata, c1, c2  )
    table.create()




def create_table_from_class(oeclass, metadata):
    """
    Create one table from a OEclass (see classes module).
    This do not create relationship.
    
    :param tablename: tablename (str)
    
    :param schema_description: see schema_description
    
    :param metadata: sqlalchemy metadata
    
    """
    #~ columns = [ Column('id', Integer, primary_key=True, index = True) ,]
    #~ table =  Table(oeclass.tablename, metadata, *columns  , mysql_charset='utf8', mysql_engine='InnoDB',)
    table =  Table(oeclass.tablename, metadata, Column('id', Integer, primary_key=True, index = True)  , mysql_charset='utf8', mysql_engine='InnoDB',)
    #~ table =  Table(oeclass.tablename, metadata, Column('id', Integer, primary_key=True, index = True)  , mysql_engine='InnoDB',)
    table.create()
    for attrname, attrtype in oeclass.usable_attributes.items():
        create_column_if_not_exists(table,  attrname, attrtype)
    return table


def create_or_update_database_schema(engine, oeclasses, max_binary_size = MAX_BINARY_SIZE,):
    """
    Create a database schema from oeclasses list (see classes module).
    If the schema already exist check if all table and column exist.
    
    
    :params engine: sqlalchemy engine
    
    :params oeclasses: list of oeclass
    
    """
    
    metadata = MetaData(bind = engine)
    metadata.reflect()

    class_by_name = { }
    for oeclass in oeclasses:
        class_by_name[oeclass.__name__] = oeclass
    
    # check all tables
    for oeclass in oeclasses:
        tablename = oeclass.tablename
        
        if tablename not in metadata.tables.keys() :
            # create table that are not present in db from class_names list
            table = create_table_from_class(oeclass, metadata)
        else:
            #check if all attributes are in SQL columns
            table = metadata.tables[tablename]
            for attrname, attrtype in oeclass.usable_attributes.items():
                create_column_if_not_exists(table,  attrname, attrtype)
    
    if 'NumpyArrayTable' not in metadata.tables.keys() :
        c1 =  Column('id', Integer, primary_key=True, index = True)
        c2 = Column('dtype', String(128))
        c3 = Column('shape', String(128))
        c4 = Column('compress', String(16))
        c5 = Column('units', String(128))
        c6 =  Column('blob', LargeBinary(MAX_BINARY_SIZE))
        #~ c7 = Column('tablename',  String(128))
        #~ c8 = Column('attributename',  String(128))
        #~ c9 = Column('parent_id',  Integer)
        table =  Table('NumpyArrayTable', metadata, c1,c2,c3,c4,c5,c6)
        table.create()
    
    # check all relationship
    for oeclass in oeclasses:
        # one to many
        for childclassname in oeclass.one_to_many_relationship:
            parenttable = metadata.tables[oeclass.tablename]
            childtable = metadata.tables[class_by_name[childclassname].tablename]
            create_one_to_many_relationship_if_not_exists(parenttable, childtable)
        
        # many to many
        for classname2 in oeclass.many_to_many_relationship:
            table1 = metadata.tables[oeclass.tablename]
            table2 = metadata.tables[class_by_name[classname2].tablename]
            create_many_to_many_relationship_if_not_exists(table1, table2, metadata)
            
    metadata.create_all()


def create_classes_from_schema_sniffing( engine, oeclasses,
                                                                                suffix_for_class_name = '_',):
    """
    This function exxplore a database schema and generate classes ready to be mapped by sa.
    This detect attributes (even numpy or quantities one)
    You can give a list a already existing classes (oeclasses):
      * if the name already exists in this list, the class will iherit this one
      * if not, the class will inherits OEBase
    
    Why this ????
    Because a user can add table or column to any databse for a particular puporse so we can't directly
    map predefined classes from OpenElectrophy.core.classes (Block, Segment, ...). We need to generate new ones.
    
    :params engine: sqlalchemy engine
    
    :params oeclasses: list of oeclass
    
    :params suffix_for_class_name: suffix for theses classes name
    
    
    """
    class_by_name = { }
    for oeclasse in oeclasses:
        class_by_name[oeclasse.__name__] = oeclasse
    
    tablename_to_oeclass = { }
    for oeclass in oeclasses:
        tablename_to_oeclass[oeclass.tablename] = oeclass
    
    
    generated_classes = [ ]
    
    #~ classes_by_tablename = { }
    metadata = MetaData(bind = engine)
    metadata.reflect()
    
    all_many_to_many = { }
    for tablename, table in metadata.tables.items() :
        if tablename == 'NumpyArrayTable':
            continue
        
        # detect many_to_many_relationship
        if 'XREF' in tablename:
            table1, table2 = tablename.split('XREF')
            all_many_to_many[table1] = table2
            all_many_to_many[table2] = table1
            continue
        
        # create the generated class
        if tablename in tablename_to_oeclass:
            classname  = suffix_for_class_name+tablename_to_oeclass[tablename].__name__
            neoclass = tablename_to_oeclass[tablename].neoclass
            classbase = tablename_to_oeclass[tablename]
        else:
            classname = str(suffix_for_class_name+tablename)
            neoclass = None
            classbase = OEBase
        genclass = type(classname,(classbase,), { })
        genclass.tablename = tablename
        genclass.neoclass = neoclass
        genclass.usable_attributes = OrderedDict(  )
        genclass.one_to_many_relationship =  [ ]
        genclass.many_to_one_relationship =  [ ]
        genclass.many_to_many_relationship = [ ]
        
        
        
        # auto guess what are attributes
        for col in table.columns:
            if col.name =='id':
                pass
            
            elif col.name.endswith('_numpy_id'):
                arrayname = col.name.replace('_numpy_id', '')
                genclass.usable_attributes[arrayname] = np.ndarray
            elif col.name.endswith('_quantity_id'):
                arrayname = col.name.replace('_quantity_id', '')
                genclass.usable_attributes[arrayname] = pq.Quantity
            elif col.name.endswith('_id'):
                pass
                
            #~ elif col.name.endswith('_blob'):
                #~ arrayname = col.name.replace('_blob' , '')
                #~ if  ( arrayname+'_shape' in table.columns) and \
                    #~ ( arrayname+'_dtype' in table.columns):
                    #~ if ( arrayname+'_units' in table.columns):
                        #~ genclass.usable_attributes[arrayname] = pq.Quantity
                    #~ else:
                        #~ genclass.usable_attributes[arrayname] = np.ndarray
            #~ elif col.name.endswith('_dtype') or \
                    #~ col.name.endswith('_shape') or\
                    #~ col.name.endswith('_units'):
                #~ pass
                #done in_blob
            else:
                # when metadat.reflect() return the highest level type (Ex: sa.DATETIME and not sa.DateTime)
                # so we must go up in class inheritance
                t = None
                for ptype, satype in python_to_sa_conversion.items():
                    #~ print col.name, ptype, satype, col.type, type(col.type), issubclass(type(col.type), satype)
                    if issubclass(type(col.type), satype):
                        t = ptype
                #~ if t is None and type(col.type) == BLOB:
                    #~ t = object
                    #~ col.type = PickleType
                    #~ print col.type
                #~ print col.name, t
                genclass.usable_attributes[col.name] = t
        generated_classes.append(genclass)


    #  auto guess relationship
    tablename_to_generated_class = { }
    for genclass in generated_classes:
        tablename_to_generated_class[genclass.tablename] = genclass
    
    # many to many relationship
    for k,v in all_many_to_many.items():
        if v not in tablename_to_generated_class[k].many_to_many_relationship:
            tablename_to_generated_class[k].many_to_many_relationship.append(v)
            tablename_to_generated_class[v].many_to_many_relationship.append(k)
    
    # one to many relationship
    for g1 in generated_classes:
        table = metadata.tables[g1.tablename]
        for col in table.columns:
            if col.name.endswith('_id'):
                tablelower = col.name[:-3]
                for g2 in generated_classes:
                    if (tablelower==g2.__name__.lower()) and (g1.__name__ not in g2.one_to_many_relationship) and\
                            (g2.__name__ not in g1.many_to_many_relationship)  :
                        g1.many_to_one_relationship.append(g2.__name__)
                        g2.one_to_many_relationship.append(g1.__name__)
    
    return generated_classes




class SQL_NumpyArrayPropertyLoader():
    """ 
    Class to manage property of numpy.ndarray attribute in mapped classe.
    SQL table way.
    """
    def __init__(self, name, arraytype = np.ndarray, compress = 'blosc', NumpyArrayTableClass = None):
        assert arraytype == np.ndarray or arraytype == pq.Quantity
        self.name = name
        self.arraytype = arraytype
        self.compress = compress
        if arraytype == np.ndarray:
            self.id_name = self.name+'_numpy_id'
        elif arraytype == pq.Quantity:
            self.id_name = self.name+'_quantity_id'
        self.NumpyArrayTableClass = NumpyArrayTableClass
        
    def fget(self , inst):
        
        if hasattr(inst, self.name+'_array') :
            return getattr(inst, self.name+'_array')
        
        nprow = getattr(inst, 'NumpyArrayTable__'+self.name)
        
        
        #~ print 'fget',self.name,  nprow, inst.id
        
        
        if nprow is None or nprow.shape is None or nprow.dtype is None:
            return None
        
        if nprow.shape =='':
            shape = ()
        else:
            shape = tuple([ int(v) for v in  nprow.shape.split(',') ])
        
        dt = np.dtype(nprow.dtype)
        
        if nprow.compress == 'blosc':
            buf = blosc.decompress(nprow.blob)
        elif nprow.compress == 'zlib':
            buf = zlib.decompress(nprow.blob)
        elif nprow.compress == 'lz4':
            buf = lz4.decompress(nprow.blob)
        elif nprow.compress == 'snappy':
            buf = snappy.decompress(nprow.blob)        
        elif nprow.compress is None:
            buf = nprow.blob
            
            
        if np.prod(shape)==0:
            if len(buf) != 0:
                arr = np.frombuffer( buf , dtype = dt)
            else:
                arr= np.empty( shape, dtype = dt )
        else:
            arr = np.frombuffer( buf , dtype = dt)
            arr.flags.writeable = True
            arr = arr.reshape(shape)
        
        if self.arraytype == pq.Quantity:
            arr = pq.Quantity(arr, units = nprow.units, copy =False)
        
        # next access will be direct
        setattr(inst, self.name+'_array', arr)
        
        #~ delattr(inst, 'NumpyArrayTable__'+self.name)
        
        return arr


    def fset(self, inst, value):
        
        nprow = getattr(inst, 'NumpyArrayTable__'+self.name)
        #~ print 'fset',self.name,  nprow, value
        
        if nprow is None:
            nprow = self.NumpyArrayTableClass()
            setattr(inst, 'NumpyArrayTable__'+self.name, nprow)
        
        if value is None:
            if hasattr(inst, self.name+'_array') :
                delattr(inst, self.name+'_array')
            nprow.shape = None
            nprow.dtype = None
            nprow.blob = None
            nprow.units = None
            nprow.compress = None
            return 
        
        if self.arraytype == np.ndarray:
            assert (type(value) == np.ndarray) or (type(value) == np.memmap) , 'Value is not np.array or np.memmap but {}'.format(type(value))
        if self.arraytype == pq.Quantity:
            assert type(value) == pq.Quantity , '{} {} {} value is not pq.Quantity'.format(inst.__class__.__name__, self.name, value)
        
        shape = ('{},'*value.ndim)[:-1].format(*value.shape)
        if shape.endswith(',') : shape = shape[:-1]
        nprow.shape = shape
        
        nprow.dtype = value.dtype.str
        
        if self.compress == 'blosc':
            blob = blosc.compress(value.tostring(), typesize = value.dtype.itemsize, clevel= 9)
        else:
            if not value.flags['C_CONTIGUOUS']:
                buf = np.getbuffer(np.array(value, copy = True))
            else:     
                buf = np.getbuffer(value)
            if self.compress == 'zlib':
                blob = zlib.compress(buf)
            elif self.compress == 'lz4':
                blob = lz4.compress(buf)
            elif self.compress == 'snappy':
                blob = snappy.compress(buf)
            else :
                blob = buf
        nprow.compress = self.compress
        nprow.blob = blob
        
        if self.arraytype == pq.Quantity:
            nprow.units = value.dimensionality.string
        
        setattr(inst, self.name+'_array', value)
        





class HDF5_NumpyArrayPropertyLoader():
    """ 
    Class to manage property of numpy.ndarray attribute in mapped classe.
    HDF5 (PyTable) table way.
    """
    def __init__(self, name, arraytype = np.ndarray, hfile = None):
        assert arraytype == np.ndarray or arraytype == pq.Quantity
        self.name = name
        self.arraytype = arraytype
        self.hfile = hfile
        
    def fget(self , inst):
        if hasattr(inst, self.name+'_array') :
            return getattr(inst, self.name+'_array')
        else:
            arr = load_array_from_hdf5_file(self.hfile, inst, self.name, self.arraytype)
            setattr(inst, self.name+'_array', arr)
            return arr

    def fset(self, inst, value):
        setattr(inst, self.name+'_array', value)


def load_array_from_hdf5_file(hfile, inst, arrayname, arraytype):
    where = '/'
    arrname =  '{}_{}_{}'.format(inst.tablename, arrayname, inst.id)
    
    if not where+arrname in hfile:
        return None
    else:
        arr = hfile.getNode(where, arrname)
        arr = arr.read()
    
    if arraytype == pq.Quantity:
        unitsname =  '{}_{}_{}_units'.format(inst.tablename, arrayname, inst.id)
        units = hfile.getNodeAttr(where, unitsname)
        arr = pq.Quantity(arr, units = units, copy =False)
    
    return arr

def save_array_to_hdf5_file(hfile, inst, arrayname, arraytype, value):
    where = '/'
    arrname =  '{}_{}_{}'.format(inst.tablename,arrayname, inst.id)
    
    atom = tables.Atom.from_dtype(value.dtype)
    
    if arraytype == pq.Quantity:
        unitsname =  '{}_{}_{}_units'.format(inst.tablename, arrayname, inst.id)
        #~ print 'unitsname', unitsname, inst.tablename, inst.id
    
    # FIXME delete an array
    if  where+arrname in hfile:
        #~ print 'deja!!!!'
        hfile.removeNode('/', arrname)
        
    if arraytype == pq.Quantity and where+unitsname in hfile:
            hfile.delNodeAttr('/', unitsname)
    
    if value is None: return
    
    if value.ndim ==0:
        #~ if arraytype == np.ndarray:
            #~ hfile.setNodeAttr('/', arrname, value)
        #~ elif arraytype == pq.Quantity:
            #~ hfile.setNodeAttr('/', arrname, value.magnitude)
        
        if arraytype == np.ndarray:
            hfile.createArray(where, arrname, value)
        elif arraytype == pq.Quantity:
            hfile.createArray(where, arrname, value.magnitude)
        #~ print 'ndim 0', arrayname, value
            
    elif np.prod(value.shape)==0:
        #~ print type(inst), arrayname,  value.shape
        a = hfile.createEArray(where,arrname, atom, value.shape)
    else:
        #~ print type(inst), arrayname,  value.shape
        a = hfile.createCArray(where,arrname, atom, value.shape)
        
        a[:] = value[:]

    if arraytype == pq.Quantity:
        units = value.dimensionality.string
        #~ atom = tables.StringAtom(itemsize=128)
        #~ unitsname =  '{}_{}_{}_units'.format(inst.tablename, arrname, inst.id)
        #~ a = hfile.createCArray(where,arrname, atom, (1,) )
        #~ a[:] = units
        hfile.setNodeAttr('/', unitsname, units)
        #~ print 'ici', unitsname, units
    
    hfile.flush()



class EventOnHdf5Load:
    def __init__(self, hfile = None):
        self.hfile = hfile
    def __call__(self, target, context):
        #~ print 'EventOnHdf5Load', target.tablename, target.id
        for attrname, attrtype in target.usable_attributes.items():
            if attrtype == np.ndarray or attrtype == pq.Quantity:
                arr = load_array_from_hdf5_file(self.hfile, target, attrname, attrtype)
                #~ print 'in load', type(target), attrname, arr
                if  arr is not None:
                    setattr(target, attrname+'_array', arr)

class EventOnHdf5AfterInsert:
    def __init__(self, hfile = None):
        self.hfile = hfile
    def __call__(self, mapper, connection, target):
        #~ print 'EventOnHdf5AfterInsert', target.tablename, target.id
        for attrname, attrtype in target.usable_attributes.items():
            if attrtype == np.ndarray or attrtype == pq.Quantity:
                if not hasattr(target, attrname+'_array' ): continue
                arr = getattr(target, attrname+'_array' )
                if  arr is not None:
                    save_array_to_hdf5_file(self.hfile, target, attrname, attrtype, arr)


class EventOnHdf5AfterUpdate:
    def __init__(self, hfile = None):
        self.hfile = hfile
    def __call__(self, mapper, connection, target):
        #~ print 'EventOnHdf5AfterUpdate', target.tablename, target.id
        for attrname, attrtype in target.usable_attributes.items():
            if attrtype == np.ndarray or attrtype == pq.Quantity:
                if not hasattr(target, attrname+'_array' ): continue
                arr = getattr(target, attrname+'_array' )
                if  arr is not None:
                    save_array_to_hdf5_file(self.hfile, target, attrname, attrtype, arr)

class EventOnHdf5AfterDelete:
    def __init__(self, hfile = None):
        self.hfile = hfile
    def __call__(self, mapper, connection, target):
        print 'EventOnHdf5AfterDelete', target.tablename, target.id, 'TODO'






def map_generated_classes(engine, generated_classes, relationship_lazy = 'select', 
                                                numpy_storage_engine =  'sqltable',  compress = False, hfile = None):
    """
    This function map all classes to the db connected with engine.
    
    :param engine: a sqlalchemy Engine.
    
    :param generated_classes: is a list (return by create_classes_from_schema_sniffing) of classes.
        Each class hold some attributes for helping the mapper:
            * genclass.tablename
            * genclass.neoclass
            * genclass.usable_attributes
            * genclass.one_to_many_relationship
            * genclass.many_to_one_relationship
            * genclass.many_to_many_relationship
    
    :param relationship_lazy: see open_db
    :param numpy_storage_engine: see open_db
    :param compress: see open_db
    
    """
    metadata = MetaData(bind = engine)
    metadata.reflect()
    
    nptable = metadata.tables['NumpyArrayTable']
    NumpyArrayTableClass = type('NumpyArrayTableClass', (object,), {})
    orm.mapper(NumpyArrayTableClass , nptable , properties = { 'blob':orm.deferred( nptable.c['blob'])  })
    
    # class by tablename
    tablename_to_class = { }
    for genclass in generated_classes:
        tablename_to_class[genclass.tablename] = genclass

    #~ for tablename, genclass in tablename_to_class.items():
    for genclass in generated_classes:
        table = metadata.tables[genclass.tablename]
        for parentname in genclass.many_to_one_relationship :
            table.c[parentname.lower()+'_id'].append_foreign_key( ForeignKey(parentname+'.id') ) 
        
        for attrname, attrtype in genclass.usable_attributes.items():
            if attrtype == np.ndarray or attrtype == pq.Quantity:
                if attrtype == np.ndarray: id_name = '_numpy_id'
                elif attrtype ==  pq.Quantity: id_name = '_quantity_id'
                table.c[attrname+id_name].append_foreign_key( ForeignKey('NumpyArrayTable.id') ) 
        
        
    
    
    

    for genclass in generated_classes:
    #~ for classname, class_ in generated_classes.items():
        table = metadata.tables[genclass.tablename]
        
        properties = { }
        # deferred loading for numpy or Quantities fields
        #~ for attrname, attrtype in genclass.usable_attributes.items():
            #~ if attrtype == np.ndarray or attrtype == pq.Quantity:
                # FIXME: think about this : _shape defered or not
                #~ properties[attrname+'_shape'] = orm.deferred( table.columns[attrname+'_shape'] , group = attrname)
                #~ properties[attrname+'_dtype'] = orm.deferred( table.columns[attrname+'_dtype'] , group = attrname)
                #properties[attrname+'_blob'] = orm.deferred( table.columns[attrname+'_blob'] , group = attrname)
                #~ properties[attrname+'_blob'] = orm.deferred( table.columns[attrname+'_blob'] , )
                #~ if  attrtype == pq.Quantity:
                    #~ properties[attrname+'_units'] = orm.deferred( table.columns[attrname+'_units'] , group = attrname)
        
        # one to many relationship
        for childname in genclass.one_to_many_relationship:
            #~ print genclass.tablename, childname
            properties[childname.lower()+'s'] = orm.relationship(tablename_to_class[childname],
                                                                primaryjoin = table.c.id==metadata.tables[childname].c[table.name.lower()+'_id'],
                                                                #~ order_by = metadata.tables[childname].c['id'],
                                                                #~ order_by = 'name',
                                                                backref=orm.backref(table.name.lower()),
                                                                #FIXME:
                                                                cascade="all, delete",
                                                                #FIXME:
                                                                lazy = relationship_lazy,
                                                                )
        # many to many relationship
        for tablename2 in genclass.many_to_many_relationship:
            if table.name>tablename2:
                # in other case is done with bacref
                xref = table.name+'XREF'+tablename2
                xreftable =metadata.tables[xref]
                
                properties[tablename2.lower()+'s'] = orm.relationship(tablename_to_class[tablename2],
                                                                                            primaryjoin = table.c.id==xreftable.c[table.name.lower()+'_id'],
                                                                                            secondary = xreftable,
                                                                                            secondaryjoin = metadata.tables[tablename2].c.id==xreftable.c[tablename2.lower()+'_id'],
                                                                                            lazy = ((relationship_lazy != "immediate") and relationship_lazy) or 'select',
                                                                                            foreign_keys = [xreftable.c[table.name.lower()+'_id'],  xreftable.c[tablename2.lower()+'_id']],
                                                                                            backref = orm.backref(table.name.lower()+'s'),
                                                                                            )
                                                                                        
            
            # one to one relationship with NumpyArrayTable
        for attrname, attrtype in genclass.usable_attributes.items():
            if attrtype == np.ndarray or attrtype == pq.Quantity:
                if attrtype == np.ndarray: id_name = '_numpy_id'
                elif attrtype ==  pq.Quantity: id_name = '_quantity_id'
                
                
                properties['NumpyArrayTable__'+attrname] = orm.relationship(NumpyArrayTableClass, 
                                                                                                                                            primaryjoin = nptable.c.id == table.c['{}{}'.format(attrname, id_name)],
                                                                                                                                            cascade="all, delete",
                                                                                                                                            #~ lazy = 'select',
                                                                                                                                            #~ lazy = 'immediate',
                                                                                                                                            lazy = 'joined',
                                                                                                                                            #~ lazy = 'dynamic',# invalid
                                                                                                                                            
                                                                                                                                            uselist=False,
                                                                                                                                            #~ foreign_keys = nptable.c.id,
                                                                                                                                            )
        
        orm.mapper(genclass , table , properties = properties , )
    
        # magic reconstruction for  np.ndarray pq.Quantity (pq.Quantity scalar)
        for attrname, attrtype in genclass.usable_attributes.items():
            if attrtype == np.ndarray or attrtype == pq.Quantity:
                if numpy_storage_engine ==  'sqltable':
                    np_dyn_load = SQL_NumpyArrayPropertyLoader(attrname, arraytype =attrtype, compress = compress, NumpyArrayTableClass = NumpyArrayTableClass)
                elif numpy_storage_engine ==  'hdf5':
                    np_dyn_load = HDF5_NumpyArrayPropertyLoader(attrname, arraytype =attrtype, hfile = hfile)
                    
                setattr(genclass, attrname, property( fget = np_dyn_load.fget,  fset = np_dyn_load.fset ))
                    
                
        
    return metadata




class  MyBasicCache():
    """Basic cache based of deque"""
    def __init__(self, maxsize = 200):
        self.d = deque()
        self.maxsize = maxsize
        
    def add(self, ob):
        # startegy is basic : each object if presente is remove and then pop on right
        if ob in self.d:
            self.d.remove(ob)
        self.d.append(ob)
        self.clean()
        
    def clean(self):
        #~ print 'cache size', len(self.d)
        while len(self.d) >= self.maxsize:
            self.d.popleft()
    
    def clear(self):
        self.d.clear()


class EventLoadListennerForCache:
    """
    This is an event listenner for very basic cache system.
    All loaded object are put in a deque to keep a ref on the object to avoid another load.
    """
    def __init__(self, cache = None):
        if cache is None:
            self.cache = MyBasicCache()
        else:
            self.cache = cache
    
    def __call__(self, target, context):
        #~ print 'event_load_for_cache', target.tablename, target.id
        self.cache.add(target)



class DataBaseConnectionInfo(object):
    """
    This is a simple class used when open_db and that have theses attributes :
        * url
        * mapped_classes
        * Session
        * metadata
        * cache
    
    """
    def __init__(self, **kargs):
        self.__dict__.update(kargs)
        
        self.classes_by_name = dict([ (c.__name__, c) for c in self.mapped_classes])
    
    def get_class(self, name):
        return self.classes_by_name.get(name, None)
    
        
        


def open_db(url, myglobals = None, suffix_for_class_name = '', use_global_session = True, 
                        object_number_in_cache = None,  numpy_storage_engine = 'sqltable', compress = DEFAULT_COMPRESS_LIB,
                        hdf5_filename = None,
                        relationship_lazy = 'select', predefined_classes = None, max_binary_size = MAX_BINARY_SIZE,):
    """
    Hight level function from playing with a database: this function create sqlalchemy engine, inspect database, create classes, map then and create caches.
    
    :param url: url in sqlalchemy style
    :param myglobals: your locals() or globals() dict if you want to put mapped classes directly in your namespace
    :param suffix_for_class_name: you can add a suffix to class name to avoid conflct with neo for instance (AnalogSignal or _AnalogSignal)
    :param use_global_session: True by default. True is convinient for easy script mode there is a global session for all object. Do not do this for multiprocessing or GUI.
    :param object_number_in_cache: default=None. use a basic memory cache with a fixed object length to avoid to reload objects from db each time you need them.
                                                            If None do not cache anything.
    :param numpy_storage_engine: 'sqltable' or 'hdf5' all numpy.array ( and pq.Quantity) can be stored directly in sql tables or separated hdf5.
                                                                    'sqltable': great because your database is consistent but this is slow, SQL is not optimized for for big binaries object.
                                                                    'hdf5': great because this is faster but you need to provide a separated file than url for storage.
    :param compress: 'lz4', 'snappy',  'blosc', 'zlib' or None do compress with all BLOB for np.array (save disk space and band width)
                                            Note that compression include a memory overhead (beauause np.array buffer + compress buffer)
    :param hdf5_filename: if numpy_storage_engine is hdf5 you need to provide the filename.
    :param relationship_lazy: sqlalchemy option for relationship (default 'select') 
                            Can be 'select', 'immediate', dynamic'
                            See http://docs.sqlalchemy.org/en/latest/orm/relationships.html?highlight=lazy
    :param predefined_classes: if None it take the OpenElectrophy.core.oeclasses for creating the schema. You can also provide something else.
    :param max_binary_size: max size for BLOB column depend of engine (SQLite limited to 2Go, MySQL need some configs, ...)
    
    
    :rtype: :py:class:`DataBaseConnectionInfo` object with url, mapped classes, metadata. See 
    
    Usage in script mode:
        >>> url = 'sqlite://mydatabase.sqlite'
        >>> open_db(url, myglobals = globals() )
        >>> 
    
    Advanced usage for GUI or multiprocessing:
        >>> url = 'sqlite://mydatabase.sqlite'
        >>> dbinfo = open_db(url, myglobals =None,  use_global_session = False  )
        >>> session = dbinfo.Session()
        >>> print dbinfo.mapped_classes
    
    
    
    """
    engine = create_engine(url, echo=False, convert_unicode = True, encoding = 'utf8') #client_encoding='utf8'
    
    if predefined_classes is None:
        from OpenElectrophy.core import oeclasses
        predefined_classes = oeclasses
    
    create_or_update_database_schema( engine, predefined_classes, max_binary_size = max_binary_size)
    generated_classes = create_classes_from_schema_sniffing( engine, predefined_classes, 
                                                suffix_for_class_name = suffix_for_class_name,
                                                )
    
    # TODO check if hdf5_filename and numpy_storage_engine ara consistent
    if numpy_storage_engine ==  'sqltable':
        hfile = None
    elif numpy_storage_engine ==  'hdf5':
        hfile =  tables.openFile(hdf5_filename, mode = "a", filters = tables.Filters(complevel=9, complib='blosc',))
    
    metadata = map_generated_classes(engine, generated_classes, relationship_lazy = relationship_lazy,
                                    numpy_storage_engine = numpy_storage_engine, compress = compress, hfile = hfile )
    
    if numpy_storage_engine ==  'hdf5':
        for genclass in generated_classes:
            #~ event.listen(genclass, 'load', EventOnHdf5Load(hfile = hfile) )
            event.listen(genclass, 'after_insert', EventOnHdf5AfterInsert(hfile = hfile))
            event.listen(genclass, 'after_update', EventOnHdf5AfterUpdate(hfile = hfile))
            event.listen(genclass, 'after_delete', EventOnHdf5AfterDelete(hfile = hfile))


    if object_number_in_cache:
        cache = MyBasicCache(maxsize = object_number_in_cache)
        l = EventLoadListennerForCache(cache = cache)
        for genclass in generated_classes:
            event.listen(genclass, 'load', l)
    else:
        cache = None
    
    
    if myglobals is not None:
        d = { }
        for genclass in generated_classes:
            d[genclass.__name__] = genclass
        myglobals.update(d)
    
    Session = orm.scoped_session(orm.sessionmaker(bind=metadata.bind , autocommit=False, autoflush=True))
    #~ Session = orm.sessionmaker(bind=metadata.bind , autocommit=False, autoflush=True)
    
    
    dbinfo = DataBaseConnectionInfo( url =url,mapped_classes = generated_classes,Session = Session,
                                                metadata = metadata, cache = cache, numpy_storage_engine = numpy_storage_engine,
                                                compress = compress)

    if use_global_session:
        global globalsession
        globalsession = Session()
        global globaldbinfo
        globaldbinfo = dbinfo
    
    return dbinfo
    

def execute_sql(query ,session = None, column_split = True, 
                                            column_as_numpy = True, **kargs):
    """
    This function is a hight level execute litteral SQL in a session.
    
    :param session: the sqlaclhemy session. If None try globalsession
    
    :param column_split: default True. For traditional SQL execution, the result is given by raw.
                                    In case of True the result is given by column in a tutle.
                                    a, b, c = execute_sql('SELECT table.a, table.b, table.c FROM table')
    
    :param column_as_numpy: defalt True, in case column_split=True the result can be numpy.array
    
    Usage:
        >>> a, b, c = execute_sql('SELECT table.a, table.b, table.c FROM table')
    
    """
    if session is None:
        session = globalsession
    assert session is not None, 'You must give a session for execute_sql'
    
    pres = session.execute(query, kargs)
    res = pres.fetchall()
    
    if len(res) == 0:
        if column_split :
            if column_as_numpy:
                res = [ np.array([ ]) for i in pres.keys() ]
            else:
                res = [ [ ] for i in pres.keys() ]
        else:
            res = [ ]
    else:
        if column_split :
            res2 = np.array( res, dtype = object)
            res = [ ]
            for i in range(res2.shape[1]):
                if column_as_numpy:
                    res += [ res2[:,i] ]
                else :
                    res += [ res2[:,i].tolist() ]
    return res

# alias
sql  = execute_sql
