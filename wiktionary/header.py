#!/usr/bin/python
# -*- coding: utf-8  -*-

'''
This module contains code to store Wiktionary content in Python objects.
The objects can output the content again in Wiktionary format by means of the wikiWrap methods

I'm currently working on a parser that can read the textual version in the various Wiktionary formats and store what it finds in the Python objects.

The data dictionaries will be moved to a separate file, later on. Right now it's practical to have everything together. They also still need to be expanded to contain more languages and more Wiktionary formats. Right now I like to keep everything together to keep my sanity.

The code is still very much alpha level and the scope of what it can do is still rather limited, only 3 parts of speech, only 2 different Wiktionary output formats, only langnames matrix for about 8 languages. On of the things on the todo list is to harvest the content of this matrix dictionary from the various Wiktionary projects. GerardM put them all in templates already.
'''

from structs import *

class Header:
    def __init__(self,line):
        """ Constructor
            Generally called with one parameter:
            - The line read from a Wiktonary page
              after determining it's probably a header
        """
        self.type=''        # The type of header, i.e. lang, pos, other
        self.contents=''    # If lang, which lang? If pos, which pos?

        self.level=None
        self.header = ''

        if line.count('=')>1:
            self.level = line.count('=') // 2 # integer floor division without fractional part
            self.header = line.replace('=','')
        elif not line.find('{{')==-1:
            self.header = line.replace('{{-','').replace('-}}','')

        self.header = self.header.replace('{{','').replace('}}','').strip().lower()

        # Now we know the content of the header, let's try to find out what it means:
        if pos.has_key(self.header):
            self.type=u'pos'
            self.contents=pos[self.header]
        if langnames.has_key(self.header):
            self.type=u'lang'
            self.contents=self.header
        if invertedlangnames.has_key(self.header):
            self.type=u'lang'
            self.contents=invertedlangnames[self.header]
        if otherheaders.has_key(self.header):
            self.type=u'other'
            self.contents=otherheaders[self.header]

    def __repr__(self):
        return self.__module__+".Header("+\
            "contents='"+self.contents+\
            "', header='"+self.header+\
            "', level="+str(self.level)+\
            ", type='"+self.type+\
            "')"
