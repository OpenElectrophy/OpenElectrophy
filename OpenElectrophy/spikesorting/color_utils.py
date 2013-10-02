# -*- coding: utf-8 -*-
"""
Basic color conversion bewteen:
   * matplotlib a list of r, g, b in range 0 1
   * QColor from Qt
   * HTML color    #ff00ff


"""



from matplotlib.colors import ColorConverter

import string


def mpl_to_mplRGB(color):
    return ColorConverter().to_rgb( color )

def html_to_mplRGB(color):
    color = color.replace('#', '')
    rgb = [ ]
    for i in range(3):
        rgb.append(float(string.atoi('0x'+color[i*2:i*2+2], 16))/255.)
    return rgb

def mpl_to_html(color):
    html = '#'
    for e in color:
        colorhex = str(hex(int(e*255))).replace('0x','')
        if len(colorhex) == 1:
            colorhex = '0'+colorhex
        html += colorhex
    return html
