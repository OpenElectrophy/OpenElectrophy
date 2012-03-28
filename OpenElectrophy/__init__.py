"""
The OpenElectrophy project aims to simplify data- and analysis-sharing
for intra- and extra-cellular recordings.
In short with OpenElectrophy you will be able to play with neural signals,
spikes and oscillations.

OpenElectrophy has three main goals:
 * to be a good storage management compatible with huge datasets procuded in neuroscience labs
 * to be a quick, click’n play, intuitive user interface with wich experimentalists can explore their data
 * to be a quality toolbox to design analysis scripts

 
What is great with OpenElectrophy:
 * base on neo : http://packages.python.org/neo/ so include many data formats
  (Plexon, NeuroExplorer, Spike2, TDT, ...)
 * It includes a tool for spike detection and spike sorting that implements many methods.
 * A fast wavelet scalogram plotting to analyze local field potential (LFP) oscillations.
 * A tool for detecting transient oscillations in LFP that allows completely new approaches on oscillations.
"""

# Authors Samuel Garcia
# Copyright (c) 2012 Samuel Garcia


from core import *
import version