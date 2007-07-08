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

class ParseError(Exception):
    """ booh """

class parser:
    def __init__(self, string):
        self.wikipwn = [a for a in lexer(string).lexer()]
        self.counter = 0
    
    def expect(self, types, values=None):
        #print 'Expect: %s %s' % (types, values)
        token = self.wikipwn[self.counter]
        if (token[0] not in types):
            if values:
                raise ParseError("Expected one of (%r, %r), got %r" % (types, values, token))
            else:
                raise ParseError("Expected one of (%r), got %r" % (types, token))
        if values:
            if (token[1] not in values):
                raise ParseError("Expected one of (%r, %r), got %r" % (types, values, token))
        self.counter += 1
        return token

    def parsetext(self):
            data = ''
            try:
                while(True): data += self.expect([lexer.TEXT, lexer.WHITESPACE])[1]
            except ParseError, e: pass
            return data
    
    def parseurl(self):
        pre = self.expect([lexer.SQRE_OPEN])[1]-1
        url = self.expect([lexer.TEXT])[1]
        # checkurl, raise ParseError
        try:
            ws = self.expect([lexer.WHITESPACE])[1]
        except ParseError:
            aft = self.expect([lexer.SQRE_CLOSE])[1]-1
            return ('['*pre, url, ']'*aft)

        if '\n' in ws:
            raise ParseError('No newlines allowed in external links')
        desc = ''
        try:
            while(True): desc += self.expect([lexer.TEXT, lexer.WHITESPACE])[1]
        except ParseError, e: pass
        aft = self.expect([lexer.SQRE_CLOSE])[1]-1
        return ('['*pre, url, desc, ']'*aft)
    
    def parsewikilink(self):
        pre = self.expect([lexer.SQRE_OPEN])[1]-2
        if (pre < 0): raise ParseError('Not a wiki link')
        page = ''
        try:
            while(True): page += self.expect([lexer.TEXT, lexer.WHITESPACE])[1]
        except ParseError,e: pass
        # if not re.match(...): raise ParseError
        try:
            aft = self.expect([lexer.SQRE_CLOSE])[1]-2
        except ParseError, e: pass
        else:
            if (aft < 0):
                raise ParseError('Not a wiki link')
            return ('['*pre, page, ']'*aft)
        print 'boom.'
        return 0

    def parseone(self):
        token = self.wikipwn[self.counter]
        if (token[0] == lexer.EOF):
            raise StopIteration
        if (token[0] == lexer.TEXT or token[0] == lexer.WHITESPACE): #text
            try: return self.parsetext();
            except ParseError, e: pass
        if (token[0] == lexer.SQRE_OPEN): #wikilink or external link
            begin = self.counter
            try: return self.parsewikilink();
            except ParseError, e: pass
            self.counter = begin
            try: return self.parseurl();
            except ParseError, e: pass
            self.counter = begin
            return ('[' * self.expect([lexer.SQRE_OPEN])[1])
            
            try: self.expect([lexer.SQRE_OPEN], [1])
            except ParseError, e: pass
            else: return self.parseurl()
    
            # Wikilink
            try: self.expect([lexer.SQRE_OPEN], [2]) #wikilink
            except ParseError, e: pass
                
class lexer:
    class TEXT:
        """ Text """
    class SQRE_OPEN:
        """ Square bracket open """
    class SQRE_CLOSE:
        """ Square bracket close """
    class PIPE:
        """ Pipe symbol """
    class CURL_OPEN:
        """ Curly bracket open """
    class CURL_CLOSE:
        """ Curly bracket close """
    class ANGL_OPEN:
        """ Angular bracket open """
    class ANGL_CLOSE:
        """ Angular bracket close """
    class NEWPAR:
        """ New paragraph """
    class TAB_OPEN:
        """ Table open """
    class TAB_NEWLINE:
        """ Table new row """
    class TAB_CLOSE:
        """ Table close """
    class WHITESPACE:
        """ Whitespace """
    class EQUAL_SIGN:
        """ Equal sign """
    class APOSTROPHE:
        """ Apostrophe """
    class EOF:
        """ End Of File """
     
    def __init__(self, string):
        self.wikipwn = (a for a in string)
    
    def lexer(self):
        text = ''
        try:
            c = self.getchar()
            while True:
                if (c in ('[', ']', '{', '}', '<', '>', '=', '\'')):
                    if text:
                        yield (lexer.TEXT, text)
                        text = ''
                    num = 1
                    try:
                        t = self.getchar()
                        while (t == c):
                            t = self.getchar()
                            num += 1
                    finally:
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
                    try:
                        t = self.getchar()
                    except StopIteration:
                        yield (lexer.PIPE, None)
                        raise
                    
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
                    ws = ''
                    try:
                        while re.match('\s', c):
                            ws += c
                            c = self.getchar()   #eat up remaining whitespace
                    finally:
                        if (ws.count('\n') > 1):
                            yield (lexer.NEWPAR, ws)
                        else:
                            yield (lexer.WHITESPACE, ws)
                else:
                    text = text + c
                    c = self.getchar()
        except StopIteration: pass
        if text:
            yield (lexer.TEXT, text)
        yield (lexer.EOF, None)

    def getchar(self): 
        return self.wikipwn.next()

            
        
    