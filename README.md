# OpenElectrophy

## Note:
OpenElectrophy is quite old now:
  * few compatibility for python 3
  * PyQT4 only
  * neo 0.4.x only (schema have change since 0.5)

For theses reasons, OpenElectrophy will have maintenance for some year
but won't have any improvement.

If you are a new user you should not go with it.
Having a big storage in a database is not a good idea today as datasets get too big.

All interesting part of OpenElectrophy have been ported to other projects:
  * For reading/manipulating electrohysiological dataset use [neo](https://github.com/NeuralEnsemble/python-neo) but with newer version
  * For spike sorting use [tridesclous](https://github.com/tridesclous/tridesclous)
  * If you need viewers, [ephyviewer](https://github.com/NeuralEnsemble/ephyviewer)


## 

OpenElectrophy is a python module for electrophysioly data analysis (intra- and extra-cellular).
OpenElectrophy is build on top of Neo :
    * It includes the powerful Neo (0.4.x) IO that can read a quantity of data formats (Plexon, NeuroExplorer, Spike2, TDT, Axon, BlackRock, ...) 
    * Neo object ready for analyses (AnalogSIgnal, SpikeTrain, RecordingChannel, Segment, Block ...)

But OpenElectrophy also provide:
    * A GUI for exploring dataset
    * A complete offline spikesorting tool chain = GUI and/or command line.
    * A timefrequency toolbox = fast wavelet scalogram plotting +  transient oscillation in LFP detection.
    * Viewers for neo objects.
    * A database for storage.
