#encoding : utf-8 
"""
Simple code to transform rest to html
"""

from docutils import core
from docutils.writers.html4css1 import Writer,HTMLTranslator

class NoHeaderHTMLTranslator(HTMLTranslator):
    def __init__(self, document):
        HTMLTranslator.__init__(self,document)
        self.head_prefix = ['','','','','']
        self.body_prefix = []
        self.body_suffix = []
        #~ self.stylesheet = []

_w = Writer()
_w.translator_class = NoHeaderHTMLTranslator

def rest_to_html(string):
    return core.publish_string(string,writer=_w)
    
def test1():
    test = """
Test example of reST__ document.

__ http://docutils.sf.net/rst.html

- item 1
- item 2
- item 3

"""
    print rest_to_html(test)

if __name__ == '__main__':
    test1()