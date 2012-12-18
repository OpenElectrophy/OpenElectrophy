# -*- coding: utf-8 -*-
"""
Update 
------------------

If you want to update a row, it is easy:
 * Load an object
 * modify its attributes
 * Save the object


"""

import sys
sys.path.append('..')

if __name__== '__main__':

    from OpenElectrophy import open_db
    # connection to a DB
    open_db( url = 'sqlite:///test.sqlite', myglobals= globals(), use_global_session = True)

    # I know the ID
    id= 2
    seg = Segment.load(id)

    # Modify attribute
    seg.name = 'modified name'

    # save 
    seg.save()
