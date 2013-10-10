.. _spike_introduction_section:

********************************
Spike sorting
********************************



Introduction
==========================

The main feature of OpenElectrophy is that it integrates a full spike detection and sorting framework.
Spike sorting is critical for extracellular recordings and many tools, both free and commerical and implementing a wide variety of algorithsm, are available to solve this delicate problem.

Today electrophysiologists may choose between:
   * Integrated but commercial tools
   * Non-integrated free tools: i.e., separate GUI and command-line tools for signal visualization, detection, sorting, and manual reclustering
   * Free tools that are very specialized for specific hardware or file formats
   * Free tools built around one super new sorting method for sorting

OpenElectrophy does *not* provide another tool for spike sorting. Instead, it provides a *framework* for spike sorting.

OpenElectrophy provides all of the following:
   * A complete chain for sorting from filtering to manual reclustering (included waveform alignment, noise estimation, detection, etc.)
   * An integrated GUI for both manual and automatic spike sorting.
   * Multiple methods for each step of processing. OpenElectrophy is agnostic: we do not prefer gaussian mixture models over paramagnetic clustering, for example.
   * Multi-Segment spike sorting: if you have several files you can sort them jointly! (and automatically split out the SpikeTrain objects afterwards)
   * Fancy visualistation tools for manual sorting: NDViewer with lasso selection (aka GGobi), cross correlogram, fast list
   * Simple integration of spike sorting on polytrode
   * Easy scripting tools for sorting if you do want to use a GUI

Finally, OpenElectrophy provides a bridge between experimentalists and methodologists:
   * Experimentalists can enjoy a simple but powerful tool.
   * Methodologists can contribute to spike sorting toolchain with minimal coding effort.


.. warning::

  Unlike in previous versions, the OpenElectrophy spike sorting suite is no longer tightly integrated with a database.
  You can open a file (with neo) and play with the spike sorting in seconds (as long as the file size is not too large)!



Start
=======================

To open the spike sorting window:
   1- You need to open a file or a database with the OpenElectrophy main window. 
      Note that for an fast *try and play* you can open the fake file **Try OpenElectrophy**
   2 - In the second tab, **ByRecordingChannelGroup**, expand the Block you want to work work with.
   3 - Inspect how the ByRecordingChannelGroup is constructed:
         * If the RecordingChannelGroup is composed of the correct set of RecordingChannel, you can directly select in the RecordingChannelGroup's context menu (right click) **SpikeSorting**
         * If the grouping is not yet done or not correct: select several RecordingChannel and on the context menu **Create group and do spike sorting**          

.. image:: /images/spikesorting/context_menu_1.png

or

.. image:: /images/spikesorting/context_menu_2.png

Note that the second case is quite frequent because few propietary formats provide the correct grouping (since this is usually probe-dependent).
For instance, on the A16 by neuronexus you have 4 tetrodes.
  * Group 1 includes channels : 1, 2, 6, 3
  * Group 2 includes channels : 5, 4, 7,8
  * Group 3 includes channels : 10, 9, 12 , 13
  * Group 4 includes channels : 15, 16, 14, 11


Keep in mind, that in OpenElectrophy philosophy, you always detect/sort spikes on a RecordingChannelGroup (not on AnalogSignal nor SpikeTrain nor RecordingChannel).
RecordingChannelGroup encapsulates both AnalogSignal, SpikeTrain, RecordingChannel. `See Neo diagram <http://pythonhosted.org/neo/core.html>`.
In particular, RecordingChannelGroup offers an auto-magic concatenation of all AnalogSignals 
in different Segments of the same Block.



Tool Chain and Steps
======================

`This scholarpedia page <http://www.scholarpedia.org/article/Spike_sorting>`_ is good background reading before reading this tutorial.

For spike sorting, a classic and proven tool chain is:
    1. Filtering
    2. Detection
    3. Waveform extraction and alignement
    4. Feature extraction
    5. Clustering

But if you know there is only one possible unit, for instance with juxtacellular recording,  it could be:
    1. Filtering
    2. Detection
    3. Artifact remove

For spikes that have already been filtered and detected by dedicated hardware:
    1. Feature extraction
    2. Clustering

For advanced users, it might be:
    1. Filtering
    2. Detection
    3. Rough waveform extraction
    4. Feature extraction
    5. Rough clustering
    6. Fine waveform alignement
    7. Fine clustering
   
The **Tool chain** widget is done for that purpose.
 
.. image:: /images/spikesorting/toolchain_widget.png

In the upper right, you can choose the mode (aka your tool chain) appropriate to your needs:
   * from a full band signal to clustered spikes
   * from a filtered signal to clustered spikes
   * from waveforms to clustered spikes
   * from features to clustered spikes
   * from a full band signal to detected spikes


For each mode, you have a column tabbed widget with one tab per step.

For each step, you can choose with a combobox the method you want to use.
For example for clustering, you can choose between : gaussian mixture, KMean, mean shift, ...

For each method you have a parameter set associated with default values.

For each method, you can:
   * Run it
   * View contextual documentation on the method.
   * For some of them, display extra information specifics to that particular method

.. warning::
    
    It is very important to read the contextual doc of methods (**Info on ...** button). The documentation is kept there and not in this page.


Each time you *Run* a method a full refresh of all other widget occurs.

For convenience, in the upper right, you can run the whole chain at once, which is equivalent to running each selected method step-by-step.

 


The main window, dockable widgets and views template
=====================================================================

To accomodate the needs and habits of different labs, the spike sorting dialog offers a completely user adjustable layout.
It is based on dockable widgets and window areas. Widgets are mainly various types of plots (the filtered signal, the waveforms or the feature projection...) or lists.

Some widgets are useful for detection (signal, filtered signal, signal statistic, ...). Others are useful for manual clustering (NDviewer, 3D viewer, spike list...).
Others are useful to control the sorting quality (ISI, cross-correlogram...)


All widgets can be visible or invisible. They can be floating, tiled or tabbed onto one another.
You can move a widget by clicking in its title bar and dragging it. You can drop it in any area that is highlighted in blue.
In this way you can customize the layout to your own needs: many small figures in a mosaic layout, one big plot, many tabbed widgets ....

Remember that after each action (computing a step, or manual sorting), all visible widgets will be refreshed. The UI will run slowly if too many widgets are displayed.


You can select what is visible here with the menu **Select displayed plots**
Some predefined templates are available in the **View template menu**.

.. image:: /images/spikesorting/mainwindow_1.png
    :width: 800

List of view/widget
=========================================

Note: 
 * The example is based on tetrode technology, and therefore there are four signals and four waveforms per spike
 * The example is intended to demonstrate the capabilities of OpenElectrophy. It does not use real data and is not meant to demonstrate proper spike sorting technique
 

Here is a list of the main widgets (and those which need explanation):

 * **Full Band Signal** / **Filtered Signal**
 
  .. image:: /images/spikesorting/widget_signals.png

  From upper left to bottom rigth:
    * Navigate the segments
    * Select the width of the window
    * Select the Y range of the signal. (same as mouse wheel)
    * Add a spike manually
    * Select a spike (magenta)
    * Change options like auto zoom
    * Move along X with step by step mode.
    * Move along X with slider mode.
    * Move along X with absolute time.


  Note:
    * mouse wheel on signals is Y zoom only.
    * The larger is the window (X size), the slower the responsiveness
    * For the **Filtered Signal** view you can have the threshold for some methods.

 
 * **Feature ND Viewer**
 
  .. image:: /images/spikesorting/widget_ndviewer.png
 
  The **ND viewer** is the best tool for best practice, but it is not necessarily intuitive and needs some explanation.
  Displaying clusters in high (more than 3!) dimensional space is difficult. To overcome this problem, some people use a combination of 2D plots of all pairs of dimensions. Others use various 3D representations. However in this two cases the view angle is seriously restricted: it is the projection of a big hyper cube (ND) 
  onto only one face (2D or 3D) of this hyper cube. In real life,
  two clusters are not necessary well separated in one of this hyper-cube's face but better in a complex hyper plane that brings
  into play a combination of all features/dimensions.
  
  The **ND viewer** try to mimic the really good `RGGobi viewer package <http://www.ggobi.org/rggobi/>`_.
  
  In the NDviewer, the weight of each projection is displayed on the left for each dimension.
  You have a button for a random projection. An important feature is the dynamic tour in the N-D space: 
  static views can hide some cluster separation. You have a button for a random tour and a button for 
  an optimized tour. The latter tries to converge to a plane that visually separates clusters, although this is quite experimental for now.
  
  NDViewer also supports manual selection :
     * pipet selection (one point)
     * lasso selection
     * polygon selection
  Individual spike selection is very useful to link a spike's shape and its projection onto a particular hyperplane.     



 * **Spike List**
 
  .. image:: /images/spikesorting/widget_spikelist.png
 
  This is the list of all spikes! It helps for manual, even surgical, spike sorting.
  Some prefer to view all spikes ones by one, although this is not viable for modern large datasets.
  The columns are:
   * spike number (color is cluster)
   * the parent Segment
   * time
   * whether the spike is visible (True or False). Remember that not all spikes are visible at the same time, see **Sample subset**
   
  You can select one or several spikes to highlight them in other widgets.
   
  You have a context menu to:
     * move the selected spike to trash
     * group selected spikes in a new cluster
 
 
 * **Unit List**,
 
  .. image:: /images/spikesorting/widget_unitlist.png
 
  This is the most important widget for manual spike sorting (in conjuction with spike list and NDviewer). It lists all detected clusters.
 
  When you select one or several clusters on this list you can:
        * delete clusters
        * move cluster to trash
        * group one or several cluster into one unit
        * select all related spikes in the spike list and ndviewer
        * regroup unit that are too small
        * hide/show clusters
        * explode a cluster (i.e., recluster this subset of spikes)
        * set a name and color to a Unit

 * **Features Parallel Plot**
 
  .. image:: /images/spikesorting/widget_featuresparallelplot.png
  
  The parallel plot displays all N features in 1D. The X axis index is the dimension number of the feature space.
  Each cluster is a bundle but it is often hard to distinguish cluster separation in that
  way.  For plotting performance and convenience reasons, only features of a random subset of spikes of each cluster are plotted.
  You can change the size of the subset by clicking on the settings icon.
 
 * **Features3D**

  .. image:: /images/spikesorting/widget_features3D.png
  
  In this plot you can choose 3 dimensions of the feature space for plotting 
  spike projections in a 3D scatter plot. This mimics a feature of
  `Plexon Offline Spikesorter <http://www.plexon.com>`_.
  It is useful but not as powerful as the **NDviewer**.
  
  
 * **Features Wilson Plot**
 
  .. image:: /images/spikesorting/widget_featureswilsonplot.png
   
  This widget plots 2D projections of spikes in the feature space using all pairs of dimensions. If the first, second and third dimensions
  are sufficient to cluster spikes, it can be useful. However, this view can have dangerous view angle side effects.
   
  
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

   This section is really really important!!! Many questions come from misunderstanding it.


Nowadays, with long recordings and a low detection threshold it is possible to play with a huge number of spikes, perhaps millions! Plotting all of them on a single figure is simply not possible due to the required CPU and memory resources (more than the detection itself). Moreover it is useless to plot all spikes
at the same time for large numbers since you could not see anything except a big ugly cloud.

A good practice is to randomly select a subset of these spikes. Then it is easier to perceive clusters and it considerably speeds up the plotting.
A number between 500 and 10000 is usually good. Try different solutions with your data and computer hardware.

This feature is provided by the toolbar:

 .. image:: /images/spikesorting/subset_menu.png

When you press the **sample subset** button, it draws a new random subset for plotting.

Note : 
 * some widgets like Waveform use subsets of the main subset for plotting reasons. 
 * some widgets do not take into account this spike subsampling (spike list, spike on signal, ...)

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

This selection tool is very useful but refreshing the dislpay is a bit slow at the moment. The whole team is working on improving it!



Save SpikeTrain
===========================================

When you press **save**, you will save the actual spike sorting set to the main OpenElectrophy window.

Consider two cases:
   * you are in file mode: before closing, you must use the main OpenElectrophy tree view to export the results of your spike sorting
   * you are in database mode: the SpikeTrain and Unit are directly saved in your DB and you can play with them instantly



Spike sorting with scripts
=============================================

.. automodule:: spikesorting
.. literalinclude:: ../../examples/spikesorting.py


General but important notes
==================================

 * If you have coded a new spike sorting method, contact us. It normally should be easy to add your method in OpenElectrophy.
 * If you have an idea for the graphic interface, new widget and so on, send an email to the list.
 * This is a completely **free** contribution to the extracellular electrophysiology community. Please be aware of that work. A citation is polite, a wine bottle is better, a contribution to methods or dataset testing is the best!













 
