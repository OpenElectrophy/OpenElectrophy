.. _spike_introduction_section:

********************************
Spike sorting
********************************



Introduction
==========================

The major feature of OpenElectrophy is the integration of a full spike detection/sorting framework.
Spike sorting is a central step for good studies in extra cellular recordings.
Many algorithms and methods have been proposed for the last 15 years on this topic and
many commercial and free tools exist to help researchers achieving this delicate task.

Today an electrophysiologist have choice between:
   * Integrated but commercial tools
   * Free tools but not integrated (One for signal visualization + comand line for detection + command line for sorting + GUI for manual corretion)
   * Free tools but very specialized for a hardware or a file formats.
   * Free tools build arround one super new methods for sorting.

OpenElectrophy does not provide another tools for spike sorting, it provides a framework for spike sorting.

OpenElectrophy try to provide both:
   * Complete chain for sorting from filtering to manual sorting (included waveform alignement, noise estimation, detection, ...)
   * Integrated GUI for both manual and automatic spike sorting.
   * Multi methods for each step of processing. OpenElectrophy is agnostic, we do not prefer gaussian mixture over paramagnetic clustering.
   * Multi Segment spike sorting = If you have several files you can sort them jointly!!! (and split SpikeTrain after automaticaly)
   * Fancy visualistation tools for manual sorting = NDViewer with lasso selection (aka GGobi), cross correlagram, fast list
   * Simple integration of spike sorting on polytrode.
   * Easy scripting tools for sorting if you do want GUI.

With OpenElectrophy we try to make a bridge between experimentalist and methotologists:
   * Experimentalist can enjoy a simle but powerfull tool.
   * Methodologists can contribute to spike sorting tools chain with minimal coding efforts.


.. warning::

  Counter to what many people think, OpenElectrophy spike sorting suite is no longer tight with a database.
  You can open a file (with neo) and play with the spike sorting in a minute (for small files!).



Start
=======================

To open the spike sorting window:
   1- You need to open a file or a database with the OpenElectrophy main window. 
      Note that for an fast *try and play* you can open the fake file **Try OpenElectrophy**
   2 - In the second tabs, **ByRecordingChannelGroup**, expand the Block you want to work work with.
   3 - Inspect how the ByRecordingChannelGroup is construct:
         * If the RecordingChannelGroup is composed by the good set of RecordingChannel , you can directly
           select in the RecordingChannelGroup's context menu (right click) **SpikeSorting**
         * If the grouping is not good or not done. You select several RecordingChannel and on the context menu **Create group and do spike sorting**          

.. image:: /images/spikesorting/context_menu_1.png

or

.. image:: /images/spikesorting/context_menu_2.png

Note that the second case is frequent because few propietary formats provide the good grouping
which is probe dependant. For instance, on the A16 by neuronexus you have 4 tetrodes.
  * Group 1 includes channels : 1, 2, 6, 3
  * Group 2 includes channels : 5, 4, 7,8
  * Group 3 includes channels : 10, 9, 12 , 13
  * Group 4 includes channels : 15, 16, 14, 11


Keep in mind, that in OpenElectrophy philosophy, you always detect/sort spikes on a RecordingChannelGroup. 
(not on AnalogSignal nor SpikeTrain nor a RecordingChannel).
RecordingChannelGroup encapsulates both AnalogSignal, SpikeTrain, RecordingChannel. `See Neo diagram <http://pythonhosted.org/neo/core.html>`.
In particular, RecordingChannelGroup offers an auto-magic concatenation of all AnalogSignals 
in different Segments of the same Block.



Tool Chain and Steps
======================

`This scholarpedia page <http://www.scholarpedia.org/article/Spike_sorting>`_ is a good reading before reading this
tutorial.

For spike sorting, a classic and proven tool chain is:
    1. Filtering
    2. Detection
    3. Waveform extraction and alignement
    4. Feature extraction
    5. Clustering

But for single Unit detection it could be:
    1. Filtering
    2. Detection
    3. Artifact remove

For *already filtered and detected spike* with dedicated hardware:
    1. Feature extraction
    2. Clustering

For advance user and experts, a fine tools chain can be:
    1. Filtering
    2. Detection
    3. Rough aveform extraction
    4. Feature extraction
    5. Rough clustering
    6. Fine waveform alignement
    7. Fine clustering
   
The **Tool chain** widget is done for that purpose.
 
.. image:: /images/spikesorting/toolchain_widget.png

In upper right, you can choose the mode (aka your tool chain) adapted on your needs:
   * from full band signal to clustered spike
   * from filtered band signal to clustered spike
   * from waveform to clustered spike
   * from feature to clustered spike
   * from full band signal to detected spike


For each mode, you have a column tabbed widget with one tab per step.

For each step, you can choose with a combobox the method you want to use.
For example for clustering, you can choose between : gaussian mixture, KMean, mean shift, ...

For each method you have a parameters set associated with default values.

For each method, you can:
   * Run it
   * Contextual documentation onthe method.
   * For some of them, display extra informations specifics to taht partocular method

.. warning::
    
    It is really important to read contextual doc of methods (**Info on ...** button) them because documentation on methods is there and no more on this html documentation.


Each time you *Run* a method a full refresh of all other widget is operated.

For convinience, in upper right, you can run the all chain at once, which is equivalent to run each selected method at all step.

 


The main window, dockable widgets and views template
=====================================================================

To cover needs and habits of different labs, the spike sorting dialog offers a completely user adjustable layout.
It is based on dockable widgets and window areas. Widgets are mainly various types of plots (the filtered signal, the waveforms or the feature projection...) or lists.

Some widgets are useful for detection (signal, filtered signal, signal statistic, ...). Others are useful for manual clustering (NDviewer, 3D viewer, spike list...).
Others are useful to control the sorting quality (ISI, cross-correlogram...)


All widgets can be visible or not. They can be floating, tiled or tabbed onto one another.
You can move a widget by clicking in its title bar and dragging it over places. When an area is highlighted in blue you can drop it at this new place.
In this way the user can customize the layout to her/his own needs: many small figures in a mosaic layout, one big plot, many tabbed...

Be aware than the more widget displayed the slower the UI. Also note that refreshement of visible widgets
is done for each action (compute a step or manual sorting).


You can select what is visble here with the menu **Select displayed plots**
Some predifined template help you in the that choice, in the **View template menu**.

.. image:: /images/spikesorting/mainwindow_1.png
    :width: 800

List of view/widget
=========================================

Note : 
 * in the example, we have a tetrode detection that 's why we have 4 signals and four waveforms...
 * the following plots are NOT a good spike sorting it is just for tutorial (and it is not real data too)


Here is a list of main widgets (and thoses which need explaination):

 * **Full Band Signal** / **Filtered Signal**
 
  .. image:: /images/spikesorting/widget_signals.png

  From upper left to bottom rigth:
    * You can navigate in segments
    * Select the width of the window
    * Select the Y range of the signal. (same as mouse wheel)
    * Add manualy a spike
    * Select a spike (magenta)
    * Change options like auto zoom
    * Move along X with step by step mode.
    * Move along X with slider mode.
    * Move along X with absolut time.


  Note:
    * mouse wheel on signals is Y zoom only.
    * The larger is the window (X size) the slower is the responsiveness
    * For the **Filtered Signal** view you can have the threshold for some methods.

 
 * **Feature ND Viewer**
 
  .. image:: /images/spikesorting/widget_ndviewer.png
 
  The **ND viewer** is the best tool for best practice. I is not intuitive so needs some explanations.
  In a standard way, displaying clusters in high (more than 3!) dimensional space is a problem. To overcome this problem, some people use a combination of all
  dimensions two by two. Others use various 3D representations. However in this two cases the view angle is seriously restricted, it is the projection of a big hyper cube (ND) 
  to only one face (2D or 3D) of this hyper cube. In real life,
  two clusters are not necessary well separated in one of this hyper-cube's face but better in a complex hyper plane that brings
  into play a combination of all features/dimensions.
  
  The **ND viewer** try to mimic the really good `RGGobi viewer package <http://www.ggobi.org/rggobi/>`_.
  
  In the NDviewer, the weight of each projection is displayed on the left for each dimension.
  You have a button for a random projection. An important feature is the dynamic tour in the N-D space, 
  static views can hide some cluster separation. You have a button for a random tour and a button for 
  optimized tour. The latter try to converge to a plane that visually separate clusters, although this is quite experimental for now.
  
  NDViewer also supports manual selection :
     * pipet selection (one point)
     * lasso selection
     * polygon selection
  Individual spike selection is very useful to link a spike shape and its projection in a particular hyperplane.     



 * **Spike List**
 
  .. image:: /images/spikesorting/widget_spikelist.png
 
  This is the list of all spikes! It helps for manual and chirurgical spike sorting.
  It can be convinient for one by one see all spike (some old researchers do that on small datasets!!)
  Columns are:
   * spike number (color is cluster)
   * On which Segment it belong
   * time
   * if the spike is visible (True or False). Remember that not all spikes are visible at the same time, see **Sample subset**
   
  You can select one or several spikes to highlight them in other widgets.
   
  You have a context menu to:
     * move the selected spike to trash
     * group selected spikes in a new cluster
 
 
 * **Unit List**,
 
  .. image:: /images/spikesorting/widget_unitlist.png
 
  This is the most important widget for manual spike sorting (in conjuction with spike list and NDviewer). It lists all detected clusters.
 
  When you select one or several on this list you can:
        * delete clusters
        * move cluster to trash
        * group one or several cluster into one unit
        * select all related spikes in the spike list and ndviewer
        * regroup unit that are too small
        * hide/show clusters
        * explode a cluster which means to recluster this subset of spikes
        * set a name and color to a Unit

 * **Features Parallel Plot**
 
  .. image:: /images/spikesorting/widget_featuresparallelplot.png
  
  The parallel plot display all N features in 1D. The X axis index is the dimension number of the feature space.
  Each cluster is a bundle but it is often hard to distinguish cluster separation in that
  way.  For plotting  performance and convenient reasons only features of a random subset of spikes of each cluster are plotted.
  You can change the size of the subset by clicking on the settings icon.
 
 * **Features3D**

  .. image:: /images/spikesorting/widget_features3D.png
  
  In this plot you can choose 3 dimensions of the feature space for plotting 
  in spike projections in a 3D scatter plot. This mimics a feature of
  `Plexon Offline Spikesorter <http://www.plexon.com>`_.
  It is useful but not as powerful as the **NDviewer**.
  
  
 * **Features Wilson Plot**
 
  .. image:: /images/spikesorting/widget_featureswilsonplot.png
   
  This widget plots 2D projections of spikes in the feature space using all dimension pair combinations. If the first, second and third dimensions
  are sufficient to clusterize spikes, it can be useful. However, in general this view contains dangerous view angle side effects.
   
  
 * **Summary**
 
  .. image:: /images/spikesorting/widget_summary.png
 
  If you are a bit lost with the neo object (Segment, RecordingChannel, RecordingChannelGroup) this widget is
  your best friend. It gives you a summary of:
    * how many Segments are involved in the sorting
    * how many RecordingChannel are involved in the sorting
    * which AnalogSignal with size and sampling rate are involved in the sorting
    * how many Unit will be created
    * how many SpikeTrains will be created


Sample subset
===============================

.. warning::

   This section is really really important!!! Many questions come from misunderstanding on it.


Nowadays, in many studies it is possible to play with big number of spikes in long recording and with low detection threshold.
You can have several hundred of thousand spikes! Plotting all of them on a single figure is not possible. 
It is too much CPU and memory consuming (more than the detection it self). Moreover it is useless to plot all spikes
at the same time for large numbers since you could not see anything except a big ugly cloud.

A good practice is to randomly select a subset of these spikes. Then it is easier to perceive clusters and it considerably fastens plotting.
A number between 500 and 10000 is usually good. Try different solutions with your data and computer hardware.

This feature is provided by the toolbar:

 .. image:: /images/spikesorting/subset_menu.png

When you press the **sample subset** button, it draws a new random subset for plotting.

Note : 
 * some widgets like Waveform use subsets of the main subset for plotting reason. 
 * some widget do not take in account this spike subsampling (spike list, spike on signal, ...)

Importantly, when you press the **refresh** button it does not draw another subset.



Selection and manual sorting
============================

Some widgets provide the ability to manually select one or several spikes:
 * Spike list
 * Unit list
 * NDviewer (which offer different type of selection: pipette, lasso or polygon)
 * Waveform (one spike only)
 * Signal with pipet (one spike only)

Selected spikes are displayed in magenta.

It is useful for manual spike sorting: selected spikes can be grouped into a new cluster or sent to the trash.
It is also useful to see side effects like artifacts.

Of course the selection is propagated to other visible widgets. For example, selecting a particular waveform helps
to understand the feature projection in the ND Viewer and vice versa.

This selection tool is very useful but a bit slow for display refreshment for the moment, the whole team is working on improving it!



Save SpikeTrain
===========================================

When you press **save**, you will save the actual spike sorting set to the main OpenElectrophty window.

2 cases:
   * you are in file mode, you must export with the main OpenElectrophy tree view the result of your spike sorting before closing.
   * you are in database mode, the SpikeTrain and Unit are directly saved in your DB and you can play with them instantly.



Spike sorting with scripts
=============================================

.. automodule:: spikesorting
.. literalinclude:: ../../examples/spikesorting.py


General but important notes
==================================

 * If you have coded a new spike sorting method, contact us. It normally should be easy to add your method in OpenElectrophy.
 * If you have an idea for the graphic interface, new widget and so on, send a mail to the list.
 * This is a completely **free** contribution to the extracellular electrophysiology community. Be aware of that work. A citation is polite, a wine bottle is better, a contribution to methods or dataset testing is the best!













 
