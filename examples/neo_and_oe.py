# -*- coding: utf-8 -*-
"""

neo and OpenElectrophy
-----------------------------------------

OpenElectrophy is based on neo wich provide:
    * great object model (neo.core)
    * great file readers (neo.io)

OpenElectropphy mapped object are not directly neo objects because some of them
inherits numpy (or quantities) wich made the ORM difficult.

Common features beteween neo and OpenElectrophy:
    * same schema, same classe name, same attribute name
    * same relationship

Differences:
   * neo classes that inerhits nump.ndarray  have equivalent but with attributes
     Ex: neo.AnalogSignal is a numpy.array OpenElectrophy.AnalogSignal.signal is a numpy.array
   * neo objects have annotations dict from extra attributes, in OE they are standart attributes

neo object can be transformed to OpenElectrophy objects and vis versa.

In this example:
  * you use neo.io to read a file
  * tranfrom it in OpenElectrophy object
  * save it to a db
  * load it again
  * transform back to neo



"""

import sys
sys.path.append('..')

if __name__== '__main__':

    from OpenElectrophy import open_db, neo_to_oe
    # connection to a DB
    open_db( url = 'sqlite:///test.sqlite', myglobals= globals(), use_global_session = True)
    
    import neo
    import urllib
    # Plexon files
    distantfile = 'https://portal.g-node.org/neo/plexon/File_plexon_3.plx'
    localfile = './File_plexon_3.plx'
    urllib.urlretrieve(distantfile, localfile)
    #create a reader
    reader = neo.io.PlexonIO(filename = 'File_plexon_3.plx')
    # read the block
    neo_bl = reader.read(cascade = True, lazy = False)[0]

    #transform to mapped class
    oe_bl = neo_to_oe(neo_bl, cascade = True)
    oe_bl.save()
    bl_id = oe_bl.id

    #open again, load and transform to neo
    open_db( url = 'sqlite:///test.sqlite', myglobals= globals(), use_global_session = True)
    oe_bl2 = Block(id = bl_id)
    print type(oe_bl2)
    noe_bl2 = oe_bl2.to_neo(cascade = True)
    print type(noe_bl2)

