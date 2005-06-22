# -*- coding: utf-8  -*-
"""
This bot will make direct text replacements. It will retrieve information on
which pages might need changes either from an SQL dump or a text file, or only
change a single page.

You can run the bot with the following commandline parameters:

-sql         - Retrieve information from a local SQL dump (cur table, see
               http://download.wikimedia.org).
               Argument can also be given as "-sql:filename".
-file        - Work on all pages given in a local text file.
               Will read any [[wiki link]] and use these articles.
               Argument can also be given as "-file:filename".
-cat         - Work on all pages which are in a specific category.
               Argument can also be given as "-cat:categoryname".
-page        - Only edit a single page.
               Argument can also be given as "-page:pagename". You can give this
               parameter multiple times to edit multiple pages.
-regex       - Make replacements using regular expressions. If this argument
               isn't given, the bot will make simple text replacements.
-except:XYZ  - Ignore pages which contain XYZ. If the -regex argument is given,
               XYZ will be regarded as a regular expression.
-fix:XYZ     - Perform one of the predefined replacements tasks, which are given
               in the dictionary 'fixes' defined inside this file.
               The -regex argument and given replacements will be ignored if
               you use -fix.
               Currently available predefined fixes are:
                   * HTML - convert HTML tags to wiki syntax, and fix XHTML
-namespace:n - Namespace to process. Works only with a sql dump
-always      - Don't prompt you for each replacement
other:       - First argument is the old text, second argument is the new text.
               If the -regex argument is given, the first argument will be
               regarded as a regular expression, and the second argument might
               contain expressions like \\1 or \g<name>.
      
NOTE: Only use either -sql or -file or -page, but don't mix them.

Examples:

If you want to change templates from the old syntax, e.g. {{msg:Stub}}, to the
new syntax, e.g. {{Stub}}, download an SQL dump file (cur table) from
http://download.wikimedia.org, then use this command:

    python replace.py -sql -regex "{{msg:(.*?)}}" "{{\\1}}"

If you have a dump called foobar.sql and want to fix typos, e.g.
Errror -> Error, use this:

    python replace.py -sql:foobar.sql "Errror" "Error"

If you have a page called 'John Doe' and want to convert HTML tags to wiki
syntax, use:
    
    python replace.py -page:John_Doe -fix:HTML
"""
#
# (C) Daniel Herding, 2004
#
# Distributed under the terms of the PSF license.
#

from __future__ import generators
import sys, re
import wikipedia, pagegenerators, config

# Summary messages in different languages
# NOTE: Predefined replacement tasks might use their own dictionary, see 'fixes'
# below.
msg = {
       'de':u'Bot: Automatisierte Textersetzung %s',
       'en':u'Robot: Automated text replacement %s',
       'es':u'Robot: Reemplazo automático de texto %s',
       'fr':u'Bot : Remplacement de texte automatisé %s',
       'hu':u'Robot: Automatikus szövegcsere %s',
       'is':u'Vélmenni: breyti texta %s',
       'pt':u'Bot: Mudança automática %s',
       }

# Predefined replacements tasks.
fixes = {
    'cat': {
        'regex': True,
        'msg': {
            'de':u'Bot: entferne Grundkategorien'
            },
        'replacements': {
            r'\[\[Kategorie:Zeit:.+?\]\][\r\n ]*': '',
            r'\[\[Kategorie:Raum:.+?\]\][\r\n ]*': '',
            r'\[\[Kategorie:Thema:.+?\]\][\r\n ]*': '',
            r'\[\[Kategorie:Typ:.+?\]\][\r\n ]*': '',
        }
    },
            
    # These replacements will convert HTML to wiki syntax where possible, and
    # make remaining tags XHTML compliant.
    'HTML': {
        'regex': True,
        # We don't want to mess up pages which discuss HTML tags, so we skip
        # all pages which contain nowiki tags.
        'exceptions':  ['<nowiki>'],
        'msg': {
               'en':u'Robot: converting/fixing HTML',
               'de':u'Bot: konvertiere/korrigiere HTML',
              },
        'replacements': {
            # Everything case-insensitive (?i)
            # Keep in mind that MediaWiki automatically converts <br> to <br />
            # when rendering pages, so you might comment the next two lines out
            # to save some time/edits.
            #r'(?i)<br>':                      r'<br />',
            # linebreak with attributes
            #r'(?i)<br ([^>/]+?)>':            r'<br \1 />',
            r'(?i)<b>(.*?)</b>':              r"'''\1'''",
            r'(?i)<strong>(.*?)</strong>':    r"'''\1'''",
            r'(?i)<i>(.*?)</i>':              r"''\1''",
            r'(?i)<em>(.*?)</em>':            r"''\1''",
            # horizontal line without attributes in a single line
            r'(?i)([\r\n])<hr[ /]*>([\r\n])': r'\1----\2',
            # horizontal line without attributes with more text in the same line
            r'(?i) +<hr[ /]*> +':             r'\r\n----\r\n',
            # horizontal line with attributes; can't be done with wiki syntax
            # so we only make it XHTML compliant
            r'(?i)<hr ([^>/]+?)>':            r'<hr \1 />',
            # a header where only spaces are in the same line
            r'(?i)([\r\n]) *<h1> *([^<]+?) *</h1> *([\r\n])':  r"\1= \2 =\3",
            r'(?i)([\r\n]) *<h2> *([^<]+?) *</h2> *([\r\n])':  r"\1== \2 ==\3",
            r'(?i)([\r\n]) *<h3> *([^<]+?) *</h3> *([\r\n])':  r"\1=== \2 ===\3",
            r'(?i)([\r\n]) *<h4> *([^<]+?) *</h4> *([\r\n])':  r"\1==== \2 ====\3",
            r'(?i)([\r\n]) *<h5> *([^<]+?) *</h5> *([\r\n])':  r"\1===== \2 =====\3",
            r'(?i)([\r\n]) *<h6> *([^<]+?) *</h6> *([\r\n])':  r"\1====== \2 ======\3",
            # TODO: maybe we can make the bot replace <p> tags with \r\n's.
        }
    },
    # Grammar fixes for German language
    'grammar-de': {
        'regex': True,
        'exceptions':  ['sic!'],
        'msg': {
               'de':u'Bot: korrigiere Grammatik',
              },
        'replacements': {
            u'([Ss]owohl) ([^,\.]+?), als auch':              r'\1 \2 als auch',
            #u'([Ww]eder) ([^,\.]+?), noch':                   r'\1 \2 noch',
            u'(?=\W)(\d[\d\.\,]*\d|\d)($|€|DM|mg|g|kg|l|t|ms|s|min|h|µm|mm|cm|dm|m|km|°C|K|kB|MB|TB)(?=\W)': r'\1 \2',
            u'(\d+)\.(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)':   r'\1. \2',
        }
    },
    
}

class ReplacePageGenerator:
    """
    Generator which will yield Pages for pages that might contain text to
    replace. These pages might be retrieved from a local SQL dump file or a
    text file, or as a list of pages entered by the user.

    Arguments:
        * source       - Where the bot should retrieve the page list from.
                         Can be 'sqldump', 'textfile' or 'userinput'.
        * replacements - A dictionary where keys are original texts and values
                         are replacement texts.
        * exceptions   - A list of strings; pages which contain one of these
                         won't be changed.
        * regex        - If the entries of replacements and exceptions should
                         be interpreted as regular expressions
        * namespace    - Namespace to process in case of a SQL dump. -1 means
                         that all namespaces should be searched.
        * textfilename - The textfile's path, either absolute or relative, which
                         will be used when source is 'textfile'.
        * sqlfilename  - The dump's path, either absolute or relative, which
                         will be used when source is 'sqldump'.
        * pagenames    - a list of pages which will be used when source is
                         'userinput'.
    """
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
        """
        Generator which will yield Pages to pages that might contain text to
        replace. These pages will be retrieved from a local sql dump file
        (cur table).
    
        Arguments:
            * sqlfilename  - the dump's path, either absolute or relative
            * replacements - a dictionary where old texts are keys and new texts
                             are values
            * exceptions   - a list of strings; pages which contain one of these
                             won't be changed.
            * regex        - if the entries of replacements and exceptions should
                             be interpreted as regular expressions
        """
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
        """
        Generator which will yield pages that are listed in a text file created by
        the bot operator. Will regard everything inside [[double brackets]] as a
        page name, and yield Pages for these pages.
    
        Arguments:
            * textfilename - the textfile's path, either absolute or relative
        """
        import catlib
        category = catlib.Category(wikipedia.getSite(), self.categoryname)
        for page in category.articles(recurse = False):
            yield page

    def read_pages_from_text_file(self):
        """
        Generator which will yield pages that are listed in a text file created by
        the bot operator. Will regard everything inside [[double brackets]] as a
        page name, and yield Pages for these pages.
    
        Arguments:
            * textfilename - the textfile's path, either absolute or relative
        """
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
        '''
        Generator which will yield pages that are listed in a wiki page. Will
        regard everything inside [[double brackets]] as a page name, except for
        interwiki and category links, and yield Pages for these pages.
    
        Arguments:
            * pagetitle - the title of a page on the home wiki
        '''
        listpage = wikipedia.Page(wikipedia.getSite(), self.pagetitle)
        list = wikipedia.get(listpage, read_only = True)
        # TODO - UNFINISHED
    
    # TODO: Make MediaWiki's search feature available.
    def generate(self):
        '''
        Starts the generator.
        '''
        if self.source == 'sqldump':
            for pl in self.read_pages_from_sql_dump():
                yield pl
        elif self.source == 'textfile':
            for pl in self.read_pages_from_text_file():
                yield pl
        elif self.source == 'category':
            for pl in self.read_pages_from_category():
                yield pl
        elif self.source == 'userinput':
            for pagename in self.pagenames:
                yield wikipedia.Page(wikipedia.getSite(), pagename)

class ReplaceRobot:
    def __init__(self, generator, replacements, exceptions = [], regex = False, acceptall = False):
        self.generator = generator
        self.replacements = replacements
        self.exceptions = exceptions
        self.regex = regex
        self.acceptall = acceptall

    def checkExceptions(self, original_text):
        """
        If one of the exceptions applies for the given text, returns the 
        substring. which matches the exception. Otherwise it returns None.
        """
        for exception in self.exceptions:
            if self.regex:
                exception = re.compile(exception)
                hit = exception.search(original_text)
                if hit:
                    return hit.group(0)
            else:
                hit = original_text.find(exception)
                if hit != -1:
                    return original_text[hit:hit + len(exception)]
        return None

    def doReplacements(self, original_text):
        """
        Returns the text which is generated by applying all replacements to the
        given text.
        """
        new_text = original_text
        for old, new in self.replacements.iteritems():
            if self.regex:
                # TODO: compiling the regex each time might be inefficient
                oldR = re.compile(old)
                new_text = oldR.sub(new, new_text)
            else:
                new_text = new_text.replace(old, new)
        return new_text
        
    def run(self):
        """
        Starts the robot.
        """
        # Run the generator which will yield Pages to pages which might need to be
        # changed.
        for pl in self.generator.generate():
            print ''
            try:
                # Load the page's text from the wiki
                original_text = pl.get()
            except wikipedia.NoPage:
                wikipedia.output(u'Page %s not found' % pl.linkname())
                continue
            except wikipedia.LockedPage:
                wikipedia.output(u'Skipping locked page %s' % pl.linkname())
                continue
            except wikipedia.IsRedirectPage:
                continue
            match = self.checkExceptions(original_text)
            # skip all pages that contain certain texts
            if match:
                wikipedia.output(u'Skipping %s because it contains %s' % (pl.linkname(), match))
            else:
                new_text = self.doReplacements(original_text)
                if new_text == original_text:
                    wikipedia.output('No changes were necessary in %s' % pl.linkname())
                else:
                    wikipedia.output(u'>>> %s <<<' % pl.linkname())
                    wikipedia.showColorDiff(original_text, new_text)
                    if not self.acceptall:
                        choice = wikipedia.input(u'Do you want to accept these changes? [y|n|a(ll)]')
                        if choice in ['a', 'A']:
                            self.acceptall = True
                    if self.acceptall or choice in ['y', 'Y']:
                        pl.put(new_text)
    
def main():
    # How we want to retrieve information on which pages need to be changed.
    # Can either be 'sqldump', 'textfile' or 'userinput'.
    source = None
    # Array which will collect commandline parameters.
    # First element is original text, second element is replacement text.
    commandline_replacements = []
    # A dictionary where keys are original texts and values are replacement texts.
    replacements = {}
    # Don't edit pages which contain certain texts.
    exceptions = []
    # Should the elements of 'replacements' and 'exceptions' be interpreted
    # as regular expressions?
    regex = False
    # Predefined fixes from dictionary 'fixes' (see above).
    fix = None
    # the dump's path, either absolute or relative, which will be used when source
    # is 'sqldump'.
    sqlfilename = None
    # the textfile's path, either absolute or relative, which will be used when
    # source is 'textfile'.
    textfilename = None
    # the category name which will be used when source is 'category'.
    categoryname = None
    # a list of pages which will be used when source is 'userinput'.
    pagenames = []
    # will become True when the user presses a ('yes to all') or uses the -always
    # commandline paramater.
    acceptall = False
    # Which namespace should be processed when using a SQL dump
    # default to -1 which means all namespaces will be processed
    namespace = -1
    # Load default summary message.
    wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg))

    # Read commandline parameters.
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'replace')
        if arg:
            if arg == '-regex':
                regex = True
            elif arg.startswith('-file'):
                if len(arg) == 5:
                    textfilename = wikipedia.input(u'Please enter the filename:')
                else:
                    textfilename = arg[6:]
                source = 'textfile'
            elif arg.startswith('-cat'):
                if len(arg) == 4:
                    categoryname = wikipedia.input(u'Please enter the category name:')
                else:
                    categoryname = arg[5:]
                source = 'category'
            elif arg.startswith('-sql'):
                if len(arg) == 4:
                    sqlfilename = wikipedia.input(u'Please enter the SQL dump\'s filename:')
                else:
                    sqlfilename = arg[5:]
                source = 'sqldump'
            elif arg.startswith('-page'):
                if len(arg) == 5:
                    pagenames.append(wikipedia.input(u'Which page do you want to chage?'))
                else:
                    pagenames.append(arg[6:])
                source = 'userinput'
            elif arg.startswith('-except:'):
                exceptions.append(arg[8:])
            elif arg.startswith('-fix:'):
                fix = arg[5:]
            elif arg == '-always':
                acceptall = True
            elif arg.startswith('-namespace:'):
                namespace = int(arg[11:])
            else:
                commandline_replacements.append(arg)

    if source == None or len(commandline_replacements) not in [0, 2]:
        # syntax error, show help text from the top of this file
        wikipedia.output(__doc__, 'utf-8')
        wikipedia.stopme()
        sys.exit()
    if (len(commandline_replacements) == 2 and fix == None):
        replacements[commandline_replacements[0]] = commandline_replacements[1]
        wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg ) % ' (-' + commandline_replacements[0] + ' +' + commandline_replacements[1] + ')')
    elif fix == None:
        old = wikipedia.input(u'Please enter the text that should be replaced:')
        new = wikipedia.input(u'Please enter the new text:')
        change = '(-' + old + ' +' + new
        replacements[old] = new
        while True:
            old = wikipedia.input(u'Please enter another text that should be replaced, or press Enter to start:')
            if old == '':
                change = change + ')'
                break
            new = wikipedia.input(u'Please enter the new text:')
            change = change + ' & -' + old + ' +' + new
            replacements[old] = new
        default_summary_message =  wikipedia.translate(wikipedia.getSite(), msg) % change
        wikipedia.output(u'The summary message will default to: %s' % default_summary_message)
        summary_message = wikipedia.input(u'Press Enter to use this default message, or enter a description of the changes your bot will make:')
        if summary_message == '':
            summary_message = default_summary_message
        wikipedia.setAction(summary_message)
    else:
        # Perform one of the predefined actions.
        try:
            fix = fixes[fix]
        except KeyError:
            wikipedia.output(u'Available predefined fixes are: %s' % fixes.keys())
            wikipedia.stopme()
            sys.exit()
        if fix.has_key('regex'):
            regex = fix['regex']
        if fix.has_key('msg'):
            wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), fix['msg']))
        if fix.has_key('exceptions'):
            exceptions = fix['exceptions']
        replacements = fix['replacements']

    gen = ReplacePageGenerator(source, replacements, exceptions, regex, namespace,  textfilename, sqlfilename, categoryname, pagenames)
    preloadingGen = pagegenerators.PreloadingGenerator(gen, pageNumber = 20)
    bot = ReplaceRobot(preloadingGen, replacements, exceptions, regex, acceptall)
    bot.run()


if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
