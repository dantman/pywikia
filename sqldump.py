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

import re, time
import wikipedia, config


class SQLentry:
    '''
    Represents a wiki page, read from an SQL dump. 
    
    An instance of this class will have the following attributes:
    * self.id is the page ID (integer)
    * self.namespace is the namespace ID (integer)
    * self.title is the page title without namespace (unicode)
    * self.text is the text on that page (unicode)
    * self.comment is the last edit summary (unicode)
    * self.userid is the last editor's ID (integer)
    * self.username is the last editor's username (unicode)
    * self.timestamp is the time of the last edit (time tuple)
    * self.restrictions is True if the page is locked (boolean)
    * self.counter is the # of page views, disabled on Wikimedia wikis (integer)
    * self.redirect is True if the page is a redirect (boolean)
    * self.minor is True if the last edit was marked as minor (boolean)
    * self.new is True if the last edit was the first one (boolean)
    * self.random is a random number used for the 'Random Page' function (float)
    * self.touched is the date of the last cache update (time tuple)

    See http://meta.wikimedia.org/wiki/Cur_table for details.
    '''

    def __init__(self, id, namespace, title, text, comment, userid, username, timestamp, restrictions, counter, redirect, minor, new, random, inversetimestamp, touched):
        '''
        Constructor. All parameters should be strings, as read from the SQL
        dump. This function will convert them to formats which are more
        appropriate for the data types.
        '''
        self.id = int(id)
        self.namespace = int(namespace)
        self.title = title
        self.text = text
        self.comment = comment
        self.userid = int(userid)
        self.username = username
        # convert to a 9-dimensional time tuple, see http://python.org/doc/2.3.4/lib/module-time.html
        self.timestamp = time.strptime(timestamp, '%Y%m%d%H%M%S')
        # convert to boolean
        self.restrictions = (restrictions != '')
        self.counter = int(counter)
        self.redirect = (redirect == '1')
        self.minor = (minor == '1')
        self.new = (new == '1')
        self.random = float(random)
        # Inversetimestamp is obsolete, so we ignore it.
        #self.inversetimestamp = inversetimestamp
        
        # Basically, I would want to convert touched to time tuple, as I did
        # with timestamp. But I noticed a problem: in the nds: dump touched
        # comes before inversetimestamp, and that would cause strptime to crash.
        # So we simply leave touched as it is and hope that this is the only
        # exception where entries are mixed up. If you find other such cases,
        # please report.
        #self.touched = time.strptime(touched, '%Y%m%d%H%M%S')
        self.touched = touched

        # MediaWiki escapes apostrophes, backslashes and quotes with
        # backslashes. We need to unescape them again.
        # This regular expression matches a backslash followed by a group, where
        # the group matches either an apostrophe, a backslashes or a quote.
        escapedR = re.compile(r'\\([\\\"\'])')
        # The group \1 is the character we really want, while the leading
        # backslash is only escape information we don't need.
        self.title = escapedR.sub(r"\1", self.title)
        self.text = escapedR.sub(r"\1", self.text)
        self.comment = escapedR.sub(r"\1", self.comment)
        self.username = escapedR.sub(r"\1", self.username)
        
        # convert \n and \r to newlines and carriage returns.
        self.text = self.text.replace('\\r', '\r')
        self.text = self.text.replace('\\n', '\n')
        # comments can also contain newline characters 
        self.comment = self.comment.replace('\\r', '\r')
        self.comment = self.comment.replace('\\n', '\n')
        # I hope that titles and usernames can't :-)

    def full_title(self):
        '''
        Returns the full page title in the form 'namespace:title', using the
        localized namespace titles defined in your family file.
        '''
        namespace_title = wikipedia.family.namespace(wikipedia.mylang, self.namespace)
        if namespace_title == None:
            return self.title
        else:
            return namespace_title + ':' + self.title

    def age(self):
        '''
        Returns the time passed since the last edit, in relation to the current
        system time, in seconds (floating point number).
        '''
        return time.time() - time.mktime(self.timestamp)

# Represents one parsed SQL dump file. Reads the local file at initialization,
# parses it with a regular expression, and offers access to the resulting
# SQLentry objects through the entries() generator.
class SQLdump:
    def __init__(self, filename, encoding):
        self.filename = filename
        self.encoding = encoding
    
    def entries(self):
        '''
        Generator which reads one line at a time from the SQL dump file, and
        parses it to create SQLentry objects. Stops when the end of file is
        reached.
        '''
        # This regular expression will match one SQL database entry (i.e. a
        # page), and each group represents an attribute of that entry.
        # NOTE: We don't need re.DOTALL because newlines are escaped.
        pageR = re.compile("\((\d+),"      # cur_id             (page ID number)
                         + "(\d+),"        # cur_namespace      (namespace number)
                         + "'(.*?)',"      # cur_title          (page title w/o namespace)
                         + "'(.*?)',"      # cur_text           (page contents)
                         + "'(.*?)',"      # cur_comment        (last edit's summary text)
                         + "(\d+),"        # cur_user           (user ID of last contributor)
                         + "'(.*?)',"      # cur_user_text      (user name)
                         + "'(\d{14})',"   # cur_timestamp      (time of last edit)
                         + "'(.*?)',"      # cur_restrictions   (protected pages have 'sysop' here)
                         + "(\d+),"        # cur_counter        (view counter, disabled on WP)
                         + "([01]),"       # cur_is_redirect
                         + "([01]),"       # cur_minor_edit
                         + "([01]),"       # cur_is_new
                         + "([\d\.]+?)," # cur_random         (for random page function)
                         + "'(\d{14})',"   # inverse_timestamp  (obsolete)
                         + "'(\d{14})'\)") # cur_touched        (cache update timestamp)
        print 'Reading SQL dump'
        # Open the file, read it using the given encoding, and replace invalid
        # characters with question marks.
        import codecs
        f=codecs.open(self.filename, 'r', encoding = self.encoding, errors='replace')
        eof = False
        while not eof:
            # Read only one (very long) line because we would risk out of memory
            # errors if we read the entire file at once
            line = f.readline()
            if line == '':
                print 'End of file.'
                eof = True
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
                filename = wikipedia.input(u'Please enter the SQL dump\'s filename: ')
            else:
                filename = arg[5:]
    sqldump = SQLdump(filename, wikipedia.myencoding())
    Rpercentlink = re.compile('\[\[[^\]]*?%[A-F1-6][A-F1-6][^\]]*?\]\]')
    for page in sqldump.entries():
        text = ''
        i = wikipedia.getLanguageLinks(page.text)
        for k in i.keys():
            text += '[[%s:%s]]' % (k, i[k])
        #wikipedia.output(page.full_title())
        if Rpercentlink.search(text):
            wikipedia.output(u'*[[%s]]' % page.full_title())
 
