import sys
import os

sys.path.append('../..')

from OpenElectrophy import *
import quantities as pq

url = 'sqlite://'

#~ url = 'sqlite:///test_db_1.sqlite'
#~ if os.path.exists('test_db_1.sqlite'):
    #~ os.remove('test_db_1.sqlite')



mapperInfo = open_db(url, myglobals = globals(), )
session = mapperInfo.Session()



neo_bl = TryItIO().read_block(nb_segment = 1, duration = 2)

bl = OEBase.from_neo(neo_bl, cascade = True, mapped_classes = mapperInfo.mapped_classes)
print bl
print bl.segments
seg = bl.segments[0]
print seg.analogsignals

bl.save(session)
id_block = bl.id

session.expunge_all()


bl = Block.load(id = id_block)
print bl
print bl.segments
seg = bl.segments[0]
print seg.analogsignals

#~ print bl.neoinstance
#~ print seg.neoinstance

neo_seg = seg.to_neo(cascade = True)

#~ print bl.neoinstance
#~ print seg.neoinstance


print len(neo_seg.analogsignals)
for a in neo_seg.analogsignals:
    print a.annotations['channel_index']


print neo_seg.block
print neo_seg.block.recordingchannelgroups


