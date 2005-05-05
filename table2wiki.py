#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Nifty script to convert HTML-tables to Wikipedia's syntax.


-file:filename
      will read any [[wikipedia link]] and use these articles

-sql:XYZ
      reads a local SQL cur dump, available at http://download.wikimedia.org/.
      Searches for pages with HTML tables, and tries to convert them on the live
      wiki. Example:
      python table2wiki.py -sql:20040711_cur_table.sql.sql -lang:de

SQL-Query

SELECT CONCAT('[[', cur_title, ']]')
       FROM cur
       WHERE (cur_text LIKE '%<table%'
         OR cur_text LIKE '%<TABLE%')
         AND cur_title REGEXP "^[A-N]"
         AND cur_namespace=0
       ORDER BY cur_title
       LIMIT 500


FEATURES
Save against missing </td>
Corrects attributes of tags

KNOW BUGS
Broken HTML-tables will most likely result in broken wiki-tables!
Please check every article you change.


"""

# (C) 2003 Thomas R. Koll, <tomk32@tomk32.de>
#
# Distribute under the terms of the PSF license.
__version__='$Id$'

import re,sys,wikipedia,config,time

msg_no_warnings = {'de':'Bot: Tabellensyntax konvertiert',
                   'en':'User-controlled Bot: table syntax updated',
                   'es':'Bot controlado: actualizada sintaxis de tabla',
                   'nl':'Tabel gewijzigd van HTML- naar Wikisyntax',
                   'pt':'Bot: Sintaxe da tabela HTML para Wiki atualizada',
                  }

msg_one_warning = {'de':'Bot: Tabellensyntax konvertiert - %d Warnung!',
                   'en':'User-controlled Bot: table syntax updated - %d warning!',
                   'es':'Bot controlado: actualizada sintaxis de tabla - %d aviso!',
                   'nl':'Tabel gewijzigd van HTML- naar Wikisyntax - %d waarschuwing!',
                   'pt':'Bot: Sintaxe da tabela HTML para Wiki atualizada - %d aviso',
                  }

msg_multiple_warnings = {'de':'Bot: Tabellensyntax konvertiert - %d Warnungen!',
                         'en':'User-controlled Bot: table syntax updated - %d warnings!',
                         'es':'Bot controlado: actualizada sintaxis de tabla - %d avisos!',
                         'nl':'Tabel gewijzigd van HTML- naar Wikisyntax - %d waarschuwingen!',
                         'pt':'Bot: Sintaxe da tabela HTML para Wiki atualizada - %d avisos',
                        }

class TableSqlDumpGenerator:
    def __init__(self, sqlfilename):
        import sqldump
        self.sqldump = sqldump.SQLdump(sqlfilename, wikipedia.myencoding())

    def generate(self):
        tableTagR = re.compile('<table', re.IGNORECASE)
        for entry in self.sqldump.entries():
            if tableTagR.search(entry.text):
                pl = wikipedia.PageLink(wikipedia.getSite(), entry.full_title())
                yield pl

class SinglePageGenerator:
    '''Pseudo-generator'''
    def __init__(self, pl):
        self.pl = pl
    
    def generate(self):
        yield self.pl
                 
class Table2WikiRobot:
    def __init__(self, generator, debug = False, quietMode = False):
        self.generator = generator
        self.debug = debug
        self.quietMode = quietMode
        
    def convert(self, text):
        '''
        Converts all HTML tables in text to wiki syntax. If text contains wiki
        tables, tries to beautify them.
        Returns converted text if page was successfully changed, otherwise returns
        None.
        '''
        warnings = 0
        # this array will contain strings that will be shown in case of possible
        # errors, before the user is asked if he wants to accept the changes.
        warning_messages = []
        newText = text
        ##################
        # bring every <tag> into one single line.
        num = 1
        while num != 0:
            newText, num = re.subn("([^\r\n]{1})(<[tT]{1}[dDhHrR]{1})",
                                   r"\1\r\n\2", newText)
            
        ##################
        # every open-tag gets a new line.
    
    
        ##################
        # <table> tag with attributes, with more text on the same line
        newText = re.sub("[\r\n]*?<(?i)(table) ([\w\W]*?)>([\w\W]*?)[\r\n ]*",
                         r"\r\n{| \2\r\n\3", newText)
        # <table> tag without attributes, with more text on the same line
        newText = re.sub("[\r\n]*?<(TABLE|table)>([\w\W]*?)[\r\n ]*",
                         r"\r\n{|\n\2\r\n", newText)
        # <table> tag with attributes, without more text on the same line
        newText = re.sub("[\r\n]*?<(TABLE|table) ([\w\W]*?)>[\r\n ]*",
                         r"\r\n{| \2\r\n", newText)
        # <table> tag without attributes, without more text on the same line
        newText = re.sub("[\r\n]*?<(TABLE|table)>[\r\n ]*",
                         "\r\n{|\r\n", newText)
        # end </table>
        newText = re.sub("[\s]*<\/(TABLE|table)>", "\r\n|}", newText)
        
        ##################
        # captions
        newText = re.sub("<caption ([\w\W]*?)>([\w\W]*?)<\/caption>",
                         r"\r\n|+\1 | \2", newText)
        newText = re.sub("<caption>([\w\W]*?)<\/caption>",
                         r"\r\n|+ \1", newText)
        
        ##################
        # <th> often people don't write them within <tr>, be warned!
        newText = re.sub("[\r\n]+<(TH|th)([^>]*?)>([\w\W]*?)<\/(th|TH)>",
                         r"\r\n!\2 | \3\r\n", newText)
    
        # fail save. sometimes people forget </th>
        # <th> without attributes
        newText, n = re.subn("[\r\n]+<(th|TH)>([\w\W]*?)[\r\n]+",
                             r"\r\n! \2\r\n", newText)
        if n>0:
            warning_messages.append('WARNING: found <th> without </th>. (%d occurences)' % n)
            warnings += n
    
        # <th> with attributes
        newText, n = re.subn("[\r\n]+<(th|TH)([^>]*?)>([\w\W]*?)[\r\n]+",
                             r"\n!\2 | \3\r\n", newText)
        if n>0:
            warning_messages.append('WARNING: found <th> without </th>. (%d occurences)' % n)
            warnings += n
    
    
        ##################
        # very simple <tr>
        newText = re.sub("[\r\n]*<(tr|TR)([^>]*?)>[\r\n]*",
                         r"\r\n|-----\2\r\n", newText)
        newText = re.sub("[\r\n]*<(tr|TR)>[\r\n]*",
                         r"\r\n|-----\r\n", newText)
        
        ##################
        # normal <td> without arguments
        newText = re.sub("[\r\n]+<(td|TD)>([\w\W]*?)<\/(TD|td)>",
                         r"\r\n| \2\r\n", newText)         
    
        ##################
        # normal <td> with arguments
        newText = re.sub("[\r\n]+<(td|TD)([^>]*?)>([\w\W]*?)<\/(TD|td)>",
                         r"\r\n|\2 | \3", newText)
    
        # WARNING: this sub might eat cells of bad HTML, but most likely it
        # will correct errors
        # TODO: some more docu please
        newText, n = re.subn("[\r\n]+<(td|TD)>([^\r\n]*?)<(td|TD)>",
                             r"\r\n| \2\r\n", newText)
        if n>0:
            warning_messages.append('WARNING: (sorry, bot code unreadable (1). I don\'t know why this warning is given.) (%d occurences)' % n)
            warnings += n
        
        # fail save, sometimes it's a <td><td></tr>
        #        newText, n = re.subn("[\r\n]+<(td|TD)>([^<]*?)<(td|TD)><\/(tr|TR)>",
        #                             "\r\n| \\2\r\n", newText)
        #        newText, n = re.subn("[\r\n]+<(td|TD)([^>]*?)>([^<]*?)<(td|TD)><\/(tr|TR)>",
        #                             "\r\n|\\2| \\3\r\n", newText)
        #
        newText, n = re.subn("[\r\n]+<(td|TD)([^>]+?)>([^\r\n]*?)<\/(td|TD)>",
                             r"\r\n|\2 | \3\r\n", newText)
        if n>0:
            warning_messages.append('WARNING: found <td><td></tr>, but no </td>. (%d occurences)' % n)
            warnings += n
        
        # fail save. sometimes people forget </td>
        # <td> without arguments, with missing </td> 
        newText, n = re.subn("<(td|TD)>([^<]*?)[\r\n]+",
                             r"\r\n| \2\r\n", newText)
        if n>0:
            warning_messages.append('WARNING: found <td> without </td>. (%d occurences)' % n)
            warnings += n
    
        # <td> with arguments, with missing </td> 
        newText, n = re.subn("[\r\n]*<(td|TD)([^>]*?)>([\w\W]*?)[\r\n]+",
                             r"\r\n|\2 | \3\r\n", newText)
        if n > 0:
            warning_messages.append('NOTE: Found <td> without </td>. This shouldn\'t cause problems.')
    
        # TODO: some docu please
        newText, n = re.subn("<(td|TD)>([\w\W]*?)[\r\n]+",
                             r"\r\n| \2\r\n", newText)
    
        if n>0:
            warning_messages.append('WARNING: (sorry, bot code unreadable (2). I don\'t know why this warning is given.) (%d occurences)' % n)
            warnings += n
    
    
        ##################
        # Garbage collecting ;-)
        newText = re.sub("<td>[\r\n]*<\/tr>", "", newText)
        newText = re.sub("[\r\n]*<\/[Tt][rRdDhH]>", "", newText)
        
        ##################
        # OK, that's only theory but works most times.
        # Most browsers assume that <th> gets a new row and we do the same
        #        newText, n = re.subn("([\r\n]+\|\ [^\r\n]*?)([\r\n]+\!)",
        #                             "\\1\r\n|-----\\2", newText)
        #        warnings = warnings + n
        # adds a |---- below for the case the new <tr> is missing
        #        newText, n = re.subn("([\r\n]+\!\ [^\r\n]*?[\r\n]+)(\|\ )",
        #                             "\\1|-----\r\n\\2", newText)
        #        warnings = warnings + n
        
        
        ##################
        # most <th> come with '''title'''. Senseless in my eyes cuz
        # <th> should be bold anyways.
        newText = re.sub("[\r\n]+\!([^'\n\r]*)'''([^'\r\n]*)'''",
                         r"\r\n!\1\2", newText)
        
        ##################
        # kills indention within tables. Be warned, it might seldom bring
        # bad results.
        # True by default. Set 'deIndentTables = False' in user-config.py
        if config.deIndentTables:
            num = 1
            while num != 0:
                newText, num = re.subn("(\{\|[\w\W]*?)\n[ \t]+([\w\W]*?\|\})",
                                       r"\1\r\n\2", newText)
                
        ##################
        # kills additional spaces after | or ! or {|
        # This line was creating problems, so I commented it out --Daniel
        # newText = re.sub("[\r\n]+\|[\t ]+?[\r\n]+", "\r\n| ", newText)
        # kills trailing spaces and tabs
        newText = re.sub("\r\n(.*)[\t\ ]+[\r\n]+",
                         r"\r\n\1\r\n", newText)
        # kill extra new-lines
        newText = re.sub("[\r\n]{4,}(\!|\|)",
                         r"\r\n\1", newText);
    
    
        ##################        
        # shortening if <table> had no arguments/parameters
        newText = re.sub("[\r\n]+\{\|[\ ]+\| ", "\r\n\{| ", newText)
        # shortening if <td> had no articles
        newText = re.sub("[\r\n]+\|[\ ]+\| ", "\r\n| ", newText)
        # shortening if <th> had no articles
        newText = re.sub("\n\|\+[\ ]+\|", "\n|+ ", newText)
        # shortening of <caption> had no articles
        newText = re.sub("[\r\n]+\![\ ]+\| ", "\r\n! ", newText)
        
        ##################
        # proper attributes. attribute values need to be in quotation marks.
        num = 1
        while num != 0:
            # group 1 starts with newlines, followed by a table tag
            # (either !, |, {|, or |---), then zero or more attribute key-value
            # pairs where the value already has correct quotation marks, and
            # finally the key of the attribute we want to fix here.
            # group 3 is the value of the attribute we want to fix here.
            # We recognize it by searching for a string of non-whitespace characters
            # - [^\s]+? - which is not embraced by quotation marks - [^"]
            # group 4 is a whitespace character and probably unnecessary..
            newText, num = re.subn(r'([\r\n]+(\!|\||\{\|)[^\r\n\|]+)[ ]*=[ ]*([^"][^\s]+?[^"])(\s)',
                                   r'\1="\3"\4', newText, 1)
           
        ##################
        # merge two short <td>s
        num = 1
        while num != 0:
            newText, num = re.subn("[\r\n]+(\|[^\|\-\}]{1}[^\n\r]{0,35})" +
                                   "[\r\n]+(\|[^\|\-\}]{1}[^\r\n]{0,35})[\r\n]+",
                                   r"\r\n\1 |\2\r\n", newText)
        ####
        # add a new line if first is * or #
        newText = re.sub("[\r\n]+\| ([*#]{1})",
                         r"\r\n|\r\n\1", newText)
        
        ##################
        # strip <center> from <th>
        newText = re.sub("([\r\n]+\![^\r\n]+?)<center>([\w\W]+?)<\/center>",
                         r"\1 \2", newText)
        # strip align="center" from <th> because the .css does it
        # if there are no other attributes than align, we don't need that | either
        newText = re.sub("([\r\n]+\! +)align\=\"center\" +\|",
                         r"\1", newText)
        # if there are other attributes, simply strip the align="center"
        newText = re.sub("([\r\n]+\![^\r\n\|]+?)align\=\"center\"([^\n\r\|]+?\|)",
                         r"\1 \2", newText)
        
        ##################
        # kill additional spaces within arguments
        num = 1
        while num != 0:
            newText, num = re.subn("[\r\n]+(\||\!)([^|\r\n]*?)[ \t]{2,}([^\r\n]+?)",
                                   r"\r\n\1\2 \3", newText)
            
        ##################
        # I hate those long lines because they make a wall of letters
        # Off by default, set 'splitLongParagraphs = True' in user-config.py
        if config.splitLongParagraphs:
            num = 1
            while num != 0:
                # TODO: how does this work? docu please.
                # why are only äöüß used, but not other special characters?
                newText, num = re.subn("(\r\n[A-Z]{1}[^\n\r]{200,}?[a-zäöüß]\.)\ ([A-ZÄÖÜ]{1}[^\n\r]{200,})",
                                       r"\1\r\n\2", newText)
                
        ##################
        if newText!=text:
            import difflib
            if self.debug:
                print text
                print newText
            elif not self.quietMode:
                for line in difflib.ndiff(text.split('\n'), newText.split('\n')):
                    if line[0] == '-':
                        wikipedia.output(line)
                for line in difflib.ndiff(text.split('\n'), newText.split('\n')):
                    if line[0] == '+':
                        wikipedia.output(line)
    
            if config.table2wikiAskOnlyWarnings and warnings == 0:
                doUpload="y"
            else:
                for warning_message in warning_messages:
                    print warning_message
                if config.table2wikiSkipWarnings:
                    doUpload="n"
                else:
                    print "There were " + str(warnings) + " replacement(s) that might lead to bad output"
                    doUpload = wikipedia.input(u'Is it correct? [y|N]')
                        
    
            if doUpload == 'y':
                return (newText, warnings)
            else:
                return (None, 0)
        else:
            print "No changes were necessary"
            return (None, 0)
    
    def treat(self, pl):
        '''
        Loads a page, converts all HTML tables in its text to wiki syntax,
        and saves the converted text.
        Returns True if the converted table was successfully saved, otherwise
        returns False.
        '''
        site = pl.site()
        try:
            text = pl.get()
        except wikipedia.NoPage:
            wikipedia.output(u"ERROR: couldn't find %s" % pl.linkname())
            return False
        except wikipedia.LockedPage:
            wikipedia.output(u'Skipping locked page %s' % pl.linkname())
            return False
        except wikipedia.IsRedirectPage:
            wikipedia.output(u'Skipping redirect %s' % pl.linkname())
            return False
        converted_text, warnings = self.convert(text)
        # If the user pressed 'n'
        if not converted_text:
            return False
        else:
            if warnings == 0:
                # get edit summary message
                wikipedia.setAction(wikipedia.translate(site.lang, msg_no_warnings))
            elif warnings == 1:
                wikipedia.setAction(wikipedia.translate(site.lang, msg_one_warning) % warnings)
            else:
                wikipedia.setAction(wikipedia.translate(site.lang, msg_multiple_warnings) % warnings)
            pl.put(converted_text)
            return True

    def run(self):
        for pl in self.generator.generate():
            self.treat(pl)
            
def main():
    quietMode = False # use -quiet to get less output
    # if the -file argument is used, page titles are stored in this array.
    # otherwise it will only contain one page.
    articles = []
    # if -file is not used, this temporary array is used to read the page title.
    page_title = []
    debug = False
    source = None
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg)
        if arg:
            if arg.startswith('-file:'):
                f=open(arg[6:], 'r')
                R=re.compile(r'.*\[\[([^\]]*)\]\].*')
                m = False
                for line in f.readlines():
                    m=R.match(line)            
                    if m:
                        articles.append(m.group(1))
                    else:
                        print "ERROR: Did not understand %s line:\n%s" % (
                            arg[6:], repr(line))
                f.close()
            elif arg.startswith('-sql'):
                if len(arg) == 4:
                    sqlfilename = wikipedia.input(u'Please enter the SQL dump\'s filename: ')
                else:
                    sqlfilename = arg[5:]
                source = 'sqldump'
            elif arg.startswith('-skip:'):
                articles = articles[articles.index(arg[6:]):]
            elif arg.startswith('-auto'):
                config.table2wikiAskOnlyWarnings = True
                config.table2wikiSkipWarnings = True
                print "Automatic mode!\n"
            elif arg.startswith('-quiet'):
                quietMode = True
            elif arg.startswith('-debug'):
                debug = True
            else:
                page_title.append(arg)

    if source == 'sqldump':
        gen = TableSqlDumpGenerator(sqlfilename)
    # if the page is given as a command line argument,
    # connect the title's parts with spaces
    elif page_title != []:
        page_title = ' '.join(page_title)
        pl = wikipedia.PageLink(wikipedia.getSite(), page_title)
        gen = SinglePageGenerator(pl)

    bot = Table2WikiRobot(gen, debug, quietMode)
    bot.run()
            
try:
    main()
except:
    wikipedia.stopme()
    raise
else:
    wikipedia.stopme()
