.. OpenElectrophy documentation master file, created by
   sphinx-quickstart on Thu Nov 22 14:25:23 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to OpenElectrophy's documentation!
==========================================

.. image:: /images/OpenElectrophy_logo.png


The OpenElectrophy project aims to simplify data- and analysis-sharing for intra- and extra-cellular recordings.
In short with OpenElectrophy you will be able to play with neural signals, spikes and oscillations.


OpenElectrophy has four main goals:
	* to be a good storage management compatible with huge datasets procuded in neuroscience labs
	* to be a quick, click'n play, intuitive user interface with wich experimentalists can explore their data
	* to be a quality toolbox to design analysis scripts
	* to be a good framework for off-line spike sorting offering many methods for experimentalists.

For that OpenElectrophy is based on:
	* Neo : an open source project dedicated to electrophysiological data input/output
	* MySQL, SQLite and sqlalchemy : 3 powerful tools for managing databases
	* Qt4 : one of the best tool to design high quality User Interfaces (UI)
	* PyQtGraph : A very efficient data plotter
	* python, scipy, numpy, matplotlib (and more) : an opensourced toolbox suite that covers exhaustively the needs for scientific data processing

What is great with OpenElectrophy:
	* It includes the powerful Neo IO that can read a quantity of data formats (Plexon, NeuroExplorer, Spike2, TDT, Axon, Elphy, ...) 
	* You can easily share your data with other labs for collaboration
	* It includes a tool for spike detection and spike sorting that implements many methods.
	* A fast wavelet scalogram plotting to analyze local field potential (LFP) oscillations.
	* A tool for detecting transient oscillations in LFP that allows completely new approaches on oscillations.
	* A collection of simple example scripts which can be adapted to design your own data analyses.
	* With OpenElectrophy, thanks to python, mysql and more you can still use old scripts that were written in matlab, C, R
	* It is completly free!


Contents:

.. toctree::
   :maxdepth: 1
   
   gettingstarted
   licence
   authors
   mailinglist
   links
   faq

.. todo:

   installation
   whatisnew
   manual
  

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
