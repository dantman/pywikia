# -*- coding: utf-8  -*-
"""
Reads a cur SQL dump and offers a generator over SQLentry objects. Each SQLentry
object represents a page.
"""
#
# (C) Daniel Herding, 2004
#
# Distributed under the terms of the PSF license.
# 

import re
import wikipedia, config

    
# Represents a wiki page, read from an SQL dump. See
# http://meta.wikimedia.org/wiki/Cur_table for details.
class SQLentry:
    def __init__(self, id, namespace, title, text, comment, userid, username, timestamp, restrictions, counter, redirect, minor, new, random, inversetimestamp, touched):
        self.id = id
        self.namespace = namespace
        self.title = title
        self.text = text
        self.comment = comment
        self.userid = userid 
        self.username = username
        self.timestamp = timestamp
        self.restrictions = restrictions
        self.counter = counter
        self.redirect = redirect
        self.minor = minor
        self.new = new
        self.random = random
        self.inversetimestamp = inversetimestamp
        self.touched = touched

    # Returns the full page title in the form 'namespace:title'.
    # WARNING: The bot doesn't use the localized (translated) MediaWiki default
    # namespace identifiers, instead we are using a feature described at
    # http://meta.wikimedia.org/wiki/MediaWiki_User's_Guide:_Namespaces#Automatic_conversions_of_page_names
    # which automatically redirects the default namespace identifiers to the
    # localized ones when requesting a page.
    # This is OK when you want to load, save, move or delete the page, but if
    # you want to put the string returned by this function into another page's
    # text, you should somehow change this function to make it return the
    # localized namespace identifiers. 
    def full_title(self):
        namespace_title = wikipedia.family.namespace(wikipedia.mylang, int(self.namespace))
        if namespace_title == None:
            return self.title
        else:
            return namespace_title + ':' + self.title

# Represents one parsed SQL dump file. Reads the local file at initialization,
# parses it with a regular expression, and offers access to the resulting
# SQLentry objects through the entries() generator.
class SQLdump:
    def __init__(self, filename, encoding):
        self.filename = filename
        self.encoding = encoding
    
    # Generator. Reads one line at a time from the SQL dump file, and parses it
    # to create SQLentry objects. Stops when the end of file is reached.
    def entries(self):
        pageR = re.compile("\((\d+),"    # cur_id
                         + "(\d+),"      # cur_namespace
                         + "'(.*?)',"    # cur_title
                         + "'(.*?)',"    # cur_text           (page contents)
                         + "'(.*?)',"    # cur_comment        (last edit's summary text)
                         + "(\d+),"      # cur_user           (user ID of last contributor)
                         + "'(.*?)',"    # cur_user_text      (user name)
                         + "'(\d+)',"    # cur_timestamp
                         + "'(.*?)',"    # cur_restrictions   (protected page?)
                         + "(\d+),"      # cur_counter        (view counter, disabled on WP)
                         + "(\d),"      # cur_is_redirect
                         + "(\d),"      # cur_minor_edit
                         + "(\d),"      # cur_is_new
                         + "([\d\.]+?)," # cur_random         (for random page function)
                         + "'(\d+)',"    # inverse_timestamp  (obsolete)
                         + "'(\d+)'\)")  # cur_touched        (cache update timestamp)
        print 'Reading SQL dump'
        import codecs
        f=codecs.open(self.filename, 'r', encoding = self.encoding, errors='replace')
        while True:
            # read only one (very long) line because we would risk out of memory
            # errors if we read the entire file at once
            line = f.readline()
            # unescape apostrophes
            line = line.replace("\\'", "'")
            if line == '':
                print 'End of file.'
                break
            self.entries = []
            for id, namespace, title, text, comment, userid, username, timestamp, restrictions, counter, redirect, minor, new, random, inversetimestamp, touched in pageR.findall(line):
                 new_entry = SQLentry(id, namespace, title, text, comment, userid, username, timestamp, restrictions, counter, redirect, minor, new, random, inversetimestamp, touched)
                 yield new_entry
        f.close()

# test routines
if __name__=="__main__":
    import sys
    for arg in sys.argv[1:]:
        arg = unicode(arg, config.console_encoding)
        if wikipedia.argHandler(arg):
            pass
        elif arg.startswith('-sql'):
            if len(arg) == 4:
                filename = wikipedia.input('Please enter the SQL dump\'s filename: ')
            else:
                filename = arg[5:]
    sqldump = SQLdump(filename, wikipedia.myencoding())
    Rpercentlink = re.compile('\[\[[^\]]*?%[A-F1-6][A-F1-6][^\]]*?\]\]')
    for page in sqldump.entries():
        #wikipedia.output(page.full_title())
        if Rpercentlink.search(page.text):
            wikipedia.output('*[[%s]]' % page.full_title())
 
