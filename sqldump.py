"""
Reads a cur SQL dump and offers a generator over SQLentry objects. Each SQLentry
object represents a page.
"""

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

# Represents one parsed SQL dump file. Reads the local file at initialization,
# parses it with a regular expression, and offers access to the resulting
# SQLentry objects through the entries list variable.
class SQLdump:
    def __init__(self, filename, encoding):
        print 'Reading SQL dump'
        import codecs
        f=codecs.open(filename, 'r', encoding = encoding)
        contents = f.read()
        f.close()
        self.entries = []
        pageR = re.compile("\((\d+),"     # cur_id
                         + "(\d+),"       # cur_namespace
                         + "\'(.*?)\',"   # cur_title
                         + "\'(.*?)\',"   # cur_text           (page contents)
                         + "\'(.*?)\',"   # cur_comment        (last edit's summary text)
                         + "(\d+),"       # cur_user           (user ID of last contributor)
                         + "\'(.*?)\',"   # cur_user_text      (user name)
                         + "\'(\d+)\',"   # cur_timestamp
                         + "\'(.*?)\',"   # cur_restrictions   (protected page?)
                         + "(\d+),"       # cur_counter        (view counter, disabled)
                         + "(\d+),"       # cur_is_redirect
                         + "(\d+),"       # cur_minor_edit
                         + "(\d+),"       # cur_is_new
                         + "([\d\.]+?),"  # cur_random         (for random page function)
                         + "\'(\d+)\',"   # inverse_timestamp  (obsolete)
                         + "\'(\d+)\'")   # cur_touched        (cache update timestamp)
        print 'Parsing SQL dump'
        for id, namespace, title, text, comment, userid, username, timestamp, restrictions, counter, redirect, minor, new, random, inversetimestamp, touched in pageR.findall(contents):
             new_entry = SQLentry(id, namespace, title, text, comment, userid, username, timestamp, restrictions, counter, redirect, minor, new, random, inversetimestamp, touched)
             self.entries.append(new_entry)

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
    for page in sqldump.pages():
        print page.title
            
            
 
