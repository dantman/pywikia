# -*- coding: utf-8  -*-
"""
(C) 2003 Thomas R. Koll, <tomk32@tomk32.de>
 Distribute under the terms of the PSF license.
"""

__version__='$Id$'

DEBUG = 0
import xmllib, re
class WdTXMLParser(xmllib.XMLParser):
    def __init__(self):
        self.elements={
            'item':(self.start_item, self.end_item),
            'title':(self.start_title, self.end_title),
            'link':(self.start_link, self.end_link),
            'description':(self.start_description, self.end_description)
            }
        self.expecting_title = 0
        self.expecting_item = 0
        self.expecting_link = 0
        self.expecting_description = 0
        self.results = {}
        self.rLink  = re.compile ('.*[\r\n]*(http://.*)', re.UNICODE)
        self.rCount = re.compile ('.*: (\d*)', re.UNICODE)
        self.rTitle = re.compile ('(.*): (.*)', re.UNICODE)
        xmllib.XMLParser.__init__(self)

    def start_item(self, attrs):
        self.expecting_item = 1
        
    def end_item(self):
        if self.date and self.link and self.count:
            self.results[self.title] = {
                'date' : self.date,
                'link' : self.link,
                'count' : self.count
                }
        self.expecting_item = 0

    def start_title(self,attrs):
        self.expecting_title = 1
        self.title = u""

    def end_title(self):
        self.expecting_title = 0
        
    def start_link(self,attrs):
        self.expecting_link = 1
        self.link = u""

    def end_link(self):
        self.expecting_link = 0

    def start_description(self,attrs):
        self.expecting_description = 1
        self.count = u""

    def end_description(self):
        self.expecting_description = 0
        
    def handle_data(self,data):

        if DEBUG:
            print data
        if self.expecting_item == 0:
            return
        if self.expecting_title:
            data = self.rTitle.match(data)
            if data: 
                self.date = data.group(1)
                self.title = data.group(2)
        if self.expecting_link:
            data = self.rLink.match(data)
            if data:
                self.link = data.group(1)
        if self.expecting_description:
            data = self.rCount.match(data)
            if data:
                self.count = data.group(1)
