#!/usr/bin/python
# -*- coding: utf-8  -*-
import codecs

__version__ = ''

vertfile = None

def openFile(filename):
    try:
        vertfile = codecs.open(filename, 'a', 'utf-8')
    except IOError:
        vertfile = codecs.open(filename, 'w', 'utf-8')

def add( localName, fromName, toName ):
    if vertfile:
        # save the text in a vertfile (will be written in utf-8)
        vertfile.write( u'%s\t%s\t%s' % (localName, fromName, toName) + '\n')
        vertfile.flush()
