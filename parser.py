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

class lexer:
    class TEXT:
        """ Text node. Text="""
    class SQRE_OPEN:
        """ Square open symbols [ N="""
    class SQRE_CLOSE:
        """ Square close symbols ] N="""
    class PIPE:
        """ Pipe symbol """
    class CURL_OPEN:
        """ Curl open symbols { N="""
    class CURL_CLOSE:
        """ Curl close symbols } N="""
    class ANGL_OPEN:
        """ Angular open symbols < N="""
    class ANGL_CLOSE:
        """ Anglular close symbol > N="""
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
    class EQUAL_SIGN:
        """ equal sign for movies and madness \o/ """
    class APOSTROPHE:
        """ ', right """
     
    def __init__(self, string):
        self.wikipwn = (a for a in string)
    
    def lexer(self):
        text = ''
        c = self.getchar()
        while True:
            if (c in ('[', ']', '{', '}', '<', '>', '=', '\'')):
                if text:
                    yield (lexer.TEXT, text)
                    text = ''
                num = 1
                t = self.getchar()
                while (t == c):
                    t = self.getchar()
                    num += 1
                if   (c == '['): yield (lexer.SQRE_OPEN,  num)
                elif (c == ']'): yield (lexer.SQRE_CLOSE, num)
                elif (c == '{'): yield (lexer.CURL_OPEN,  num)
                elif (c == '}'): yield (lexer.CURL_CLOSE, num)
                elif (c == '<'): yield (lexer.ANGL_OPEN,  num)
                elif (c == '>'): yield (lexer.ANGL_CLOSE, num)
                elif (c == '='): yield (lexer.EQUAL_SIGN, num)
                elif (c == '\''): yield(lexer.APOSTROPHE, num)
                c = t
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
            elif re.match('\s', c): # whitespace eater pro (TM)
                if text:
                    yield (lexer.TEXT, text)
                    text = ''
                ws = c
                c = self.getchar()
                while re.match('\s', c):
                    ws += c
                    c = self.getchar()   #eat up remaining whitespace
                if (ws.count('\n') > 1):
                    yield (lexer.NEWPAR, ws)
                else:
                    yield (lexer.WHITESPACE, ws)
            else:
                text = text + c
                c = self.getchar()

    def getchar(self): 
        return self.wikipwn.next()
        
    