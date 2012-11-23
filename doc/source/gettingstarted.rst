*****************
Getting started
*****************





Introduction
=======================

This is a an OpenElectrophy, one hour, User Interface (UI) tutorial.

This page aims to present a step by step example of how to use the OpenElectrophy graphical user interface.
Briefly, it shows an example of how to insert new data into the database, how to visualize and explore these new data, 
and finally how to detect events of interest like spikes and oscillations. 
More detailed informations about all these steps can be found in the :ref:`manual_page`. 
Moreover, this page is an introduction to the UI only, if you want an introduction on how to write analysis script with OpenElectrophy Python classes, please refer to :ref:`scripting_page`.

Before starting
==========================


Before starting you need to have Python and OpenElectrophy properly installed  on your computer.
See :ref:`installation_page` section.

For a better understanding it is a good idea to also read the :ref:`class_definitions` section.

Starting UI
=========================

Os:
 * Linux : open a console (terminal) type ``startOpenElectrophy``
 * Windows : click (or make a shortcut on your desktop) on ``c:\python27\Lib\site-packages\OpenElectrophy.egg\EGG-INFO\scripts\startOpenElectrophy``


Creating an empty database
=============================

OpenElectrophy deals with MySQL server or an SQLite database file.
It is easier to start with a SQLite file. So we use this in the demo but keep in mind that the MySQL server is more powerful.

* Click on Dataset -> Create a new database
* Choose the SQLite tab
* Choose and type a database name (with its full path from the current directory), here for example test.sqlite (note : you can use the file explorer on the right)


.. image:: /images/gettingstarted/create_sqlite.png


Logging to the MySQL database schema
======================================

* Click on Menu : Dataset -> Open a database.
* Choose the SQLite tab.
* Use the file explorer to choose the created db or type its name (with its full path from the current directory): test.sqlite

.. image:: /images/gettingstarted/open_sqlite.png

If the database you have selected is empty, you should now face the standard OpenElectrophy window with no data. 

.. image:: /images/gettingstarted/mainwindow_init.png

Inserting new data
======================

To import data, in the Menu: Dataset -> Import data in this db :

* In the upper drop-down menu, you can choose the file type of the data you want to import. OpenElectrophy knows many common formats of electrophysiological systems.
* For this tutorial, we will choose : TryOpenElectrophy.  This is a fake IO. It does not read/write any file. It generates a full set of data with many features : Block, Segments, AnalogSignals, Events, ...
* Select the "IO specifics params" tab
* Leave all options by default and click Open. It will take a few seconds to generate the data.

.. image:: /images/gettingstarted/import_data_example.png



Exploring and visualizing stored data
=========================================

The data are now stored in the database. 

Sometimes in order to see them in OpenElectrophy you need to refresh the knowledge OpenElectrophy has of the database.
For that click on the upper right "tool" button -> popup menu -> refresh view, or press F5.

.. image:: /images/gettingstarted/refresh_view.png

A new line "Block: 1" appeared in the "Hierarchic explorer". This explorer is a tree view of the database content. 
You can unfold the tree content by clicking on the arrows at the beginning of each line and get something like this: 

.. image:: /images/gettingstarted/first_view.png

You can observe that we have one block, in which are presents 5 segments, in which are presents 4 analogsignals, 2 epocharrays and 6 spiketrains.

But with a db, you can have many views on your data. 
Click on the tab ByRecordingChannelGroup and you get another view: 
one block, in which are present 4 recordingpoints and 6 units. Each recordingpoint has 5 analogsignals. The data are the same, only the way they are viewed is different.

.. image:: /images/gettingstarted/second_view.png


If you right-click on any line, you get a contextual menu which is object-dependent. For example, if you right click on any block you have: 

.. image:: /images/gettingstarted/right_click.png

If you choose the "Edit" option, you have access to the parameters related to the block stored in the database 
and managed by OpenElectrophy. You can simply modify any of these fields but you need to click on the "Save" button 
to get the new parameter values stored in the database. 

.. image:: /images/gettingstarted/edit_fields.png


Plot analogsignal
========================


Now let's plot the data:

* Right-click on an analogsignal in the hierarchical tree view to its contextual menu
* Left click on "View AnalogSignals" which pops up a new window with a plt othe analogsignal

.. image:: /images/gettingstarted/draw_analog.png

The bottom toolbar allow to either:

* replay the analogsignal, with any speed multiplier
* advance along the signal by adjustable fixed time step
* use a sliding cursor to move at any time points of the signal

.. warning::
    In order to speed the plot refresh time, each time the plot is moving, only a subsampled analogsignal is plotted. The full signal is plotted after one second with no action on the plot

Using the Control or Shift keys, you can select multiple analogsignals before right-clicking on one of them to get the contectual menu. Then choosing "View analogsignals" will plot all selected
signals in the same window. 

.. image:: /images/gettingstarted/draw_multiple.png

But at first all signals will overlap each other. To correct for this, left click in the plot area to get the plot paramater window.

.. image:: /images/gettingstarted/plot_options.png

Click on "Spread all identical gain" to add offsets to the signals and separate them.

Below "Automatic color", click on "Progressive" to have different colors for each analogsignal.

.. image:: /images/gettingstarted/draw_analog_2.png

In OpenElectrophy main window, the analogsignal contextual menu (right click) also propose to "View  Time Frequency". This plots at time-frequency map of all the selected analogsignals. Just select one signal and plot its time frequency map. As for standard plot, clicking in the plot area will open the time frequency parameter window. Adjust the clim (maximum oscillatory power represented by the colorscale) to 1.5 as below:

.. image:: /images/gettingstarted/tf_options.png

Then moving in the time frequency plot you should get something like that:

.. image:: /images/gettingstarted/tf_analog.png

Note the time frequency map is computed on the fly,  you do not need to pre-compute them, store them and plot them. But this could be a limitation for very slow computers or very large number of simultaneously plotted maps.

Finally, the contextual menu of Segment object allows to make some simultaneous plots of objects in the segment.




Detecting oscillations
========================



Detecting spikes
===========================



Create a new view
========================

















