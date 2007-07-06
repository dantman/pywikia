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

# System loosely based on 'the dragon book':
# Compilers, Principles, Techniques and Tools, Aho, Sethi, Ullman, 1st edition, 1986

class OutOfCharsException(Exception):
    """ lexer pwn error """

class lexer:
    class TEXT:
        """ Text node. Text="""
    class WL_OPEN:
        """ Wikilink opener [[ """
    class WL_CLOSE:
        """ Wikilink closer ]] """
    class PIPE:
        """ Pipe symbol """
    class CURL_OPEN:
        """ Curl open symbols { N="""
    class CURL_CLOSE:
        """ Curl close symbols } N="""
    class ANGL_OPEN:
        """ Angular open symbol < """
    class ANGL_CLOSE:
        """ Anglular close symbol > """
    class NEWPAR:
        """ New paragraph """
    class TAB_OPEN:
        """ Table open {| """
    class TAB_NEWLINE:
        """ Table new row |- """
    class TAB_CLOSE:
        """ Table close |} """
    class WHITESPACE:
        """ Whitespace class. """
     
    def __init__(self, string):
        self.wikipwn = (a for a in string)
    
    def lexer(self):
        text = ''
        try:
            c = self.getchar()
            while True:
                if (c == '['):
                    t = self.getchar()
                    if (t == '['):
                        if text:
                            yield (lexer.TEXT, text)
                            text = ''
                        yield (lexer.WL_OPEN, None)
                        c = self.getchar()
                    else:
                        text = text + c
                        c = t
                elif (c == ']'):
                    t = self.getchar()
                    if (t == ']'):
                        if text:
                            yield (lexer.TEXT, text)
                            text = ''
                        yield (lexer.WL_CLOSE, None)
                        c = self.getchar()
                    else:
                        text = text + c
                        c = t
                elif (c == '{'):
                    if text:
                        yield (lexer.TEXT, text)
                        text = ''
                    c = self.getchar()
                    if (c == '|'): # begin table
                        yield (lexer.TAB_OPEN, None)
                        c = self.getchar()
                        continue #at the next while loop
                    num = 1
                    while (c == '{'):
                        c = self.getchar()
                        num += 1
                    yield (lexer.CURL_OPEN, num)
                elif (c == '}'):
                    if text:
                        yield (lexer.TEXT, text)
                        text = ''
                    num = 0
                    while (c == '}'):
                        self.getchar(c)
                        num += 1
                    yield (lexer.CURL_CLOSE, num)
                elif (c == '<'):
                    if text:
                        yield (lexer.TEXT, text)
                        text = ''
                    yield (lexer.ANGL_OPEN, None)
                    c = self.getchar()
                elif (c == '>'):
                    if text:
                        yield (lexer.TEXT, text)
                        text = ''
                    yield (lexer.ANGL_OPEN, None)
                    c = self.getchar()
                elif (c == '|'):
                    if text:
                        yield (lexer.TEXT, text)
                        text = ''
                    t = self.getchar()
                    if (t == '-'):
                        yield (lexer.TAB_NEWLINE, None)
                        c = self.getchar()
                    elif (t == '}'):
                        yield (lexer.TAB_CLOSE, None)
                        c = self.getchar()
                    else:
                        yield (lexer.PIPE, None)
                        c = t
                elif (c == ' ' or c == '\t'):
                    if text:
                        yield (lexer.TEXT, text)
                        text = ''
                    yield (lexer.WHITESPACE, None)
                    while (c == ' ' or c == '\t'):
                        c = self.getchar()   #eat up remaining spaces
                elif (c == '\n'):
                    if text:
                        yield (lexer.TEXT, text)
                        text = ''
                    t = self.getchar()
                    while (t == ' '):
                        t = self.getchar()  #ignore any spaces
                    if (t == '\n'): #new paragraph
                        yield (lexer.NEWPAR, None)
                    while (c == '\n'): #eat up remaining newlines
                        c = self.getchar()
                else:
                    text = text + c
                    c = self.getchar()
        except OutOfCharsException:
            pass

    def getchar(self): 
        return self.wikipwn.next()
        
    