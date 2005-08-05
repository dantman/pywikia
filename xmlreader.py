# -*- coding: utf-8  -*-

"""
Each XmlEntry object represents a page, as read from an XML source

The MediaWikiXmlHandler can be used for the XML given by Special:Export
as well as for XML dumps.

The XmlDump class reads a pages_current XML dump (like the ones offered on
http://download.wikimedia.org/wikipedia/de/) and offers a generator over
XmlEntry objects which can be used by other bots.
"""
import threading, time
import xml.sax
import codecs, re
import wikipedia

class XmlEntry:
    """
    Represents a page.
    """
    def __init__(self, title, id, text, timestamp):
        # TODO: there are more tags we can read.
        self.title = title
        self.id = id
        self.text = text
        self.timestamp = timestamp

class MediaWikiXmlHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self.inContributorTag = False
        
    def setCallback(self, callback):
        self.callback = callback
        
    def startElement(self, name, attrs):
        self.destination = None
        if name == 'contributor':
            self.inContributorTag = True
        elif name == 'text':
            self.destination = 'text'
            self.text=u''
        elif name == 'id':
            if self.inContributorTag:
                self.destination = 'userid'
                self.userid = u''
            else:
                self.destination = 'id'
                self.id = u''
        elif name == 'title':
            self.destination = 'title'
            self.title=u''
        elif name == 'timestamp':
            self.destination = 'timestamp'
            self.timestamp=u''

    def endElement(self, name):
        if name == 'contributor':
            self.inContributorTag = False
        elif name == 'revision':
            # All done for this.
            text = self.text
            # Remove trailing newlines and spaces
            while text and text[-1] in '\n ':
                text = text[:-1]
            # Replace newline by cr/nl
            text = u'\r\n'.join(text.split('\n'))
            # Decode the timestamp
            timestamp = (self.timestamp[0:4]+
                         self.timestamp[5:7]+
                         self.timestamp[8:10]+
                         self.timestamp[11:13]+
                         self.timestamp[14:16]+
                         self.timestamp[17:19])
            self.title = self.title.strip()
            # Report back to the caller
            entry = XmlEntry(self.title, self.id, text, timestamp)
            self.callback(entry)
            
    def characters(self, data):
        if self.destination == 'text':
            self.text += data
        elif self.destination == 'id':
                self.id += data 
        elif self.destination == 'title':
            self.title += data
        elif self.destination == 'timestamp':
            self.timestamp += data

class XmlParserThread(threading.Thread):
    """
    This XML parser will run as a single thread. This allows the XmlDump
    generator to yield pages before the parser has finished reading the
    entire dump.
    
    There surely are more elegant ways to do this.
    """
    def __init__(self, filename, handler):
        threading.Thread.__init__(self)
        self.filename = filename
        self.handler = handler
    
    def run(self):
        xml.sax.parse(self.filename, self.handler)

class XmlDump(object):
    """
    Represents an XML dump file. Reads the local file at initialization,
    parses it, and offers access to the resulting XmlEntries via a generator.
    
    NOTE: This used to be done by a SAX parser, but this solution with regular
    expressions is about 10 to 20 times faster.
    """
    def __init__(self, filename):
        self.filename = filename

    def parse(self): 
        '''
        Generator which reads some lines from the XML dump file, and
        parses them to create XmlEntry objects. Stops when the end of file is
        reached.
        '''
        Rpage = re.compile('<page>\s*<title>(?P<title>.+?)</title>\s*<id>(?P<pageid>\d+?)</id>\s*(<restrictions>(?P<restrictions>.+?)</restrictions>)?\s*<revision>\s*<id>(?P<revisionid>\d+?)</id>\s*<timestamp>(?P<timestamp>.+?)</timestamp>\s*<contributor>\s*(<username>(?P<username>.+?)</username>\s*<id>(?P<userid>\d+?)</id>|<ip>(?P<ip>.+?)</ip>)\s*</contributor>\s*(?P<minor>(<minor/>))?\s*(?:<comment>(?P<comment>.+?)</comment>\s*)?(<text xml:space="preserve">(?P<text>.*?)</text>|<text xml:space="preserve" />)\s*</revision>\s*</page>', re.DOTALL)
        f = codecs.open(self.filename, 'r', encoding = wikipedia.myencoding(), errors='replace')
        print 'Reading XML dump...'
        eof = False
        lines = u''
        while not eof:
            line = f.readline()
            lines += line
            if line == '':
                eof = True
            elif line == u'</page>\n':
                # unescape characters
                lines = lines.replace('&gt;', '>')
                lines = lines.replace('&lt;', '<')
                lines = lines.replace('&quot;', '"')
                lines = lines.replace('&amp;', '&')
                m = Rpage.search(lines)
                if not m:
                    print 'ERROR: could not parse these lines:'
                    print lines
                    lines = u''
                else:
                    lines = u''
                    text = m.group('text') or u''
                    entry = XmlEntry(title = m.group('title'), id = m.group('pageid'), text = text, timestamp = m.group('timestamp'))
                    yield entry
