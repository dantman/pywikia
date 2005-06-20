# -*- coding: utf-8  -*-
'''
This bot seeks of information.

You can run the bot with the following commandline parameters:

-sql         - Search information from a local SQL dump.
               Argument can also be given as "-sql:filename".

TODO:

-file        - Search information from a local text file.
               Argument can also be given as "-file:filename".
-cat         - Search categories.
               Argument can also be given as "-cat:category_name".
-page        - Only search a single page.
               Argument can also be given as "-page:pagename".
-namespace   - Search in namespaces

Syntax: python find.py -argument
Use find.py 1.3, version without bug

'''
#
# (C) E2m, 2004
#
__version__ = '$Id$'
#
# Distributed under the terms of the PSF license.
#

from __future__ import generators
import sys, re, codecs
import wikipedia, config, sqldump, catlib

class ReadPages:
    
    def __init__(self, source, replacements, exceptions, regex = False, namespace = -1, textfilename = None, sqlfilename = None, categoryname = None, pagenames = None):
        self.source = source
        self.replacements = replacements
        self.exceptions = exceptions
        self.regex = regex
        self.namespace = namespace
        self.textfilename = textfilename
        self.sqlfilename = sqlfilename
        self.categoryname = categoryname
        self.pagenames = pagenames
    
    def read_pages_from_sql_dump(self):

        mysite = wikipedia.getSite()
        import sqldump
        dump = sqldump.SQLdump(self.sqlfilename, wikipedia.myencoding())
        for entry in dump.entries():
            skip_page = False
            if self.namespace != -1 and self.namespace != entry.namespace:
                continue
            else:
                for exception in self.exceptions:
                    if self.regex:
                        exception = re.compile(exception)
                        if exception.search(entry.text):
                            skip_page = True
                            break
                    else:
                        if entry.text.find(exception) != -1:
                            skip_page = True
                            break
            if not skip_page:
                for old in self.replacements.iterkeys():
                    if self.regex:
                        old = re.compile(old)
                        if old.search(entry.text):
                            yield wikipedia.Page(mysite, entry.full_title())
                            break
                    else:
                        if entry.text.find(old) != -1:
                            yield wikipedia.Page(mysite, entry.full_title())
                            break

    def read_pages_from_category(self):
        category = catlib.Category(wikipedia.getSite(), self.categoryname)
        for page in category.articles(recurse = False):
            yield page

    def read_pages_from_text_file(self):
        f = open(self.textfilename, 'r')
        # regular expression which will find [[wiki links]]
        R = re.compile(r'.*\[\[([^\]]*)\]\].*')
        m = False
        for line in f.readlines():
            # BUG: this will only find one link per line.
            # TODO: use findall() instead.
            m=R.match(line)
            if m:
                yield wikipedia.Page(wikipedia.getSite(), m.group(1))
        f.close()

    def read_pages_from_wiki_page(self):
        listpage = wikipedia.Page(wikipedia.getSite(), self.pagetitle)
        list = wikipedia.get(listpage, read_only = True)

    def generate(self):
        #-sql
        if self.source == 'sqldump':
            for pl in self.read_pages_from_sql_dump():
                yield pl
        #-file
        elif self.source == 'textfile':
            for pl in self.read_pages_from_text_file():
                yield pl
        #-cat
        elif self.source == 'category':
            for pl in self.read_pages_from_category():
                yield pl
        #-page
        elif self.source == 'userinput':
            for pagename in self.pagenames:
                yield wikipedia.Page(wikipedia.getSite(), pagename)

                
class FindPages:

    def __init__(self, source, replacements, exceptions, regex = False, namespace = -1, textfilename = None, sqlfilename = None, categoryname = None, pagenames = None):
        self.source = source
        self.replacements = replacements
        self.exceptions = exceptions
        self.regex = regex
        self.namespace = namespace
        self.textfilename = textfilename
        self.sqlfilename = sqlfilename
        self.categoryname = categoryname
        self.pagenames = pagenames
        self.search = search
        self.record = record
        
    def search (self):
        if count == None:
            old = wikipedia.input(u'Text search (Case and Acent Sensitive):')
            new = " "
            replacements[old] = new

    # Save search in find.dat
    def record (self):
        count = 0
        arq = codecs.open('find.dat', 'w', 'utf-8')
        for pl in self.generate:
            arq.write("# [[%s]] \n" % pl.linkname())
            count +=1
            print str(count), pl.linkname()
        arq.close()

def main():
    source = None
    replacements = {}
    exceptions = []
    regex = False
    title = False
    count = None
    sqlfilename = 'dump.sql'
    textfilename = ''
    pagenames = []
    namespace = -1

if __name__ == "__main__":
    try:
        for arg in sys.argv[1:]:
            arg = wikipedia.argHandler(arg)
            if arg:
                if arg == '-regex':
                    regex = True
                elif arg.startswith('-file'):
                    if len(arg) == 5:
                        textfilename = wikipedia.input(u'Please enter the filename:')
                    else:
                        textfilename = arg[6:]
                    source = 'textfile'
                elif arg.startswith('-sql'):
                    if len(arg) == 4:
                        sqlfilename = wikipedia.input(u'Please enter the SQL dump\'s filename:')
                    else:
                        sqlfilename = arg[5:]
                    source = 'sqldump'
                elif arg.startswith('-cat'):
                    if len(arg) == 4:
                        categoryname = wikipedia.input(u'Please enter the category name:')
                    else:
                        categoryname = arg[5:]
                    source = 'category'
                elif arg.startswith('-page'):
                    if len(arg) == 5:
                        pagenames.append(wikipedia.input(u'Which page do you want to find?'))
                    else:
                        pagenames.append(arg[6:])
                    source = 'userinput'
                else:
                    wikipedia.output(__doc__, 'utf-8')
                    sys.exit()

    except:
        wikipedia.stopme()
        raise
    else:
        wikipedia.stopme()
