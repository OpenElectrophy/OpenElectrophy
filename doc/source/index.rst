.. OpenElectrophy documentation master file, created by
   sphinx-quickstart on Thu Nov 22 14:25:23 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to OpenElectrophy's documentation!
==========================================

.. image:: /images/OpenElectrophy_logo.png


OpenElectrophy is a python module for electrophysioly data analysis (intra- and extra-cellular).
OpenElectrophy is build on top of `Neo`_ :
    * It includes the powerful Neo IO that can read a quantity of data formats (Plexon, NeuroExplorer, Spike2, TDT, Axon, BlackRock, ...) 
    * neo object ready for analyses (AnalogSIgnal, SpikeTrain, RecordingChannel, Segment, Block ...)

For new user a main interest in OpenElectrophy is the spike sorting tool chain. See :ref:`spike_introduction_section`.

.. image:: /images/spikesorting/mainwindow_1.png
    :width: 400

But OpenElectrophy also provide:
    * A GUI for exploring dataset
    * A complete offline spikesorting tool chain = GUI and/or command line.
    * A timefrequency toolbox = fast wavelet scalogram plotting +  transient oscillation in LFP detection.
    * Viewers for neo objects.
    * A database for storage.


.. image:: /images/viewers/signal_and_timefreq.png
    :height: 200
.. image:: /images/treeview_1.png
    :height: 200
.. image:: /images/viewers/signal_params.png
    :height: 200


Contents:

.. toctree::
   :maxdepth: 1
   
   installation
   screenshots
   gettingstarted
   spikesorting
   viewers
   script_examples
   licence
   authors
   mailinglist
   links
   faq
   developers_guide
   

.. todo:

   installation
   whatisnew
   manual
  

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



.. _Neo: http://packages.python.org/neo/