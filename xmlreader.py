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
import wikipedia

class XmlEntry:
    """
    Represents a page.
    """
    def __init__(self, title, text, timestamp):
        # TODO: there are more tags we can read.
        self.title = title
        self.text = text
        self.timestamp = timestamp

class MediaWikiXmlHandler(xml.sax.handler.ContentHandler):
    def setCallback(self, callback):
        self.callback = callback
        
    def startElement(self, name, attrs):
        self.destination = None
        if name == 'page':
            self.text=u''
            self.title=u''
            self.timestamp=u''
        elif name == 'text':
            self.destination = 'text'
            self.text=u''
        elif name == 'title':
            self.destination = 'title'
            self.title=u''
        elif name == 'timestamp':
            self.destination = 'timestamp'
            self.timestamp=u''

    def endElement(self, name):
        if name == 'revision':
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
            entry = XmlEntry(self.title, text, timestamp)
            self.callback(entry)
            
    def characters(self, data):
        if self.destination == 'text':
            self.text += data
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
    """
    def __init__(self, filename):
        self.filename = filename
        self.finished = False
        self.handler = MediaWikiXmlHandler()
        self.handler.setCallback(self.oneDone)
        self.parserThread = XmlParserThread(self.filename, self.handler)
        # thread dies when program terminates
        self.parserThread.setDaemon(True)
        # this temporary variable will contain an XmlEntry given by the parser
        # until it has been yielded by the generator.
        self.lastEntry = None

    def oneDone(self, entry):
        self.lastEntry = entry
        # wait until this class has yielded the page. Otherwise the parser
        # thread would give another page before we had time to yield the
        # current one.
        while self.lastEntry:
            time.sleep(0.001)

    def __call__(self):
        '''
        Generator which reads one line at a time from the SQL dump file, and
        parses it to create SQLentry objects. Stops when the end of file is
        reached.
        '''
        wikipedia.output(u'Reading XML dump')
        self.parserThread.start()
        while self.parserThread.isAlive():
            if self.lastEntry:
                yield self.lastEntry
                self.lastEntry = None
            else:
                # wait 10 ms
                time.sleep(0.001)
