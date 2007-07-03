# -*- coding: utf-8  -*-
""" Mediawiki wikitext parser """
#
# (C) 2007 Merlijn 'valhallasw' van Deen
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'

# 

import re
import xml.dom.minidom as dom
class ParseError(Exception):
    """ Error thrown when the wikiparser cannot use this function to parse """

regexp =   {
            'title': re.compile(r'[^\x23\x7c\x3c\x3e\x5b\x5d\x7b\x7d\x00-\x1f\x7f]+'),
            'pl_begin': re.compile(r'\[\['),
            'pl_end': re.compile(r'\]\]')
           }

#parsers that return values or ParseErrors
def subparseTitle(data, counter):
    # The following characters are not allowed in page titles:
    #   \x23 #      \x7c |      \x3c <      \x3e >
    #   \x5b [      \x5d ]      \x7b {      \x7d}
    # and the ASCII character codes 0-31 [\x00-\x1f] and 127. [\x7f]
    match = regexp['title'].match(data[counter:])
    if match:
        return match.group()
    else:
        raise ParseError("Regexp 'title' did not match on column %i" % (counter,))
        
#parsers that return tuples of type (num chars, DOM object)
def parseWikiLink(document, data, counter):
    assert data[counter:counter+2] == '[['
    
    node = None
    
    try:
        title = subparseTitle(data, counter+2)
    except ParseError, e:
        print "%r" % e
        pass
    else:
        if data[counter+len(title)+2:counter+len(title)+4] == ']]':
            node = document.createElement('wikilink')
            node.setAttribute('href', title)
            retval = (len(title) + 4, node)
    if not retval:
       retval = (2, document.createTextNode('[['))
    return retval

def parseText(document, data, counter, endre=re.compile(r'$')):
    node = document.createTextNode('')
    while not endre.match(data[counter:]):
        # check for pagelink
        if regexp['pl_begin'].match(data[counter:]):
            if len(node) > 0:
                yield node
            (move, node) = parseWikiLink(document, data, counter)
            counter += move
            yield node
            node = document.createTextNode('')
        else:
            node.appendData(data[counter])
            counter += 1
    yield node

def doParse(data):
    document = dom.Document()
    document.appendChild(document.createElement('wiki'))
    headnode = document.firstChild
    for i in parseText(document, data, 0):
        headnode.appendChild(i)
    return document.toxml()
        
    
        
        
    
    
    