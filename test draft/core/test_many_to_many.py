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




rcg = RecordingChannelGroup()



rc1 = RecordingChannel()
rc2 = RecordingChannel()
rc3 = RecordingChannel()

rcg.recordingchannels.append(rc1)
print rcg in rc1.recordingchannelgroups  # must be True even before commit
rcg.recordingchannels.append(rc2)
#~ rc1.recordingchannelgroups.append(rcg)  # <<<< this must bug


rc3.recordingchannelgroups.append(rcg)

session.add(rcg)
session.commit()
print rcg in rc1.recordingchannelgroups

print rcg
print rcg.recordingchannels

id1, id2 =  sql("SELECT * FROM RecordingChannelGroupXREFRecordingChannel")
print id1
print id2





