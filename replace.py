# -*- coding: utf-8 -*-
"""
This bot will make direct text replacements. It will retrieve information on
which pages might need changes either from an XML dump or a text file, or only
change a single page.

These command line parameters can be used to specify which pages to work on:

&params;

    -xml           Retrieve information from a local XML dump (pages-articles
                   or pages-meta-current, see http://download.wikimedia.org).
                   Argument can also be given as "-xml:filename".

    -page          Only edit a specific page.
                   Argument can also be given as "-page:pagetitle". You can
                   give this parameter multiple times to edit multiple pages.

Furthermore, the following command line parameters are supported:

    -regex         Make replacements using regular expressions. If this argument
                   isn't given, the bot will make simple text replacements.

    -nocase        Use case insensitive regular expressions.

    -except:XYZ    Ignore pages which contain XYZ. If the -regex argument is
                   given, XYZ will be regarded as a regular expression.

    -summary:XYZ   Set the summary message text for the edit to XYZ, bypassing
                   the predefined message texts with original and replacements
                   inserted.

    -fix:XYZ       Perform one of the predefined replacements tasks, which are
                   given in the dictionary 'fixes' defined inside the file
                   fixes.py.
                   The -regex and -nocase argument and given replacements will
                   be ignored if you use -fix.
                   Currently available predefined fixes are:
&fixes-help;

    -namespace:n   Number of namespace to process. The parameter can be used
                   multiple times. It works in combination with all other
                   parameters, except for the -start parameter. If you e.g.
                   want to iterate over all categories starting at M, use
                   -start:Category:M.

    -always        Don't prompt you for each replacement

    -recursive     Recurse replacement until possible. Be careful, this might
                   lead to an infinite loop.

    -allowoverlap  When occurences of the pattern overlap, replace all of them.
                   Be careful, this might lead to an infinite loop.

    other:         First argument is the old text, second argument is the new text.
                   If the -regex argument is given, the first argument will be
                   regarded as a regular expression, and the second argument might
                   contain expressions like \\1 or \g<name>.

Examples:

If you want to change templates from the old syntax, e.g. {{msg:Stub}}, to the
new syntax, e.g. {{Stub}}, download an XML dump file (pages-articles) from
http://download.wikimedia.org, then use this command:

    python replace.py -xml -regex "{{msg:(.*?)}}" "{{\\1}}"

If you have a dump called foobar.xml and want to fix typos in articles, e.g.
Errror -> Error, use this:

    python replace.py -xml:foobar.xml "Errror" "Error" -namespace:0

If you have a page called 'John Doe' and want to convert HTML tags to wiki
syntax, use:

    python replace.py -page:John_Doe -fix:HTML
"""
#
# (C) Daniel Herding, 2004
#
# Distributed under the terms of the MIT license.
#

from __future__ import generators
import sys, re
import wikipedia, pagegenerators,catlib, config

# Imports predefined replacements tasks from fixes.py
import fixes

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;':     pagegenerators.parameterHelp,
    '&fixes-help;': fixes.help,
}

__version__='$Id$'

# Summary messages in different languages
# NOTE: Predefined replacement tasks might use their own dictionary, see 'fixes'
# below.`v
msg = {
       'ar':u'%s روبوت : استبدال تلقائي للنص',
       'de':u'Bot: Automatisierte Textersetzung %s',
       'en':u'Robot: Automated text replacement %s',
       'el':u'Ρομπότ: Αυτόματη αντικατάσταση κειμένου %s',
       'es':u'Robot: Reemplazo automático de texto %s',
       'fr':u'Bot : Remplacement de texte automatisé %s',
       'he':u'רובוט: החלפת טקסט אוטומטית %s',
       'hu':u'Robot: Automatikus szövegcsere %s',
       'ia':u'Robot: Reimplaciamento automatic de texto %s',
       'id':u'Bot: Penggantian teks otomatis %s',
       'is':u'Vélmenni: breyti texta %s',
       'it':u'Bot: Sostituzione automatica %s',
       'ka':u'რობოტი: ტექსტის ავტომატური შეცვლა %s',
       'ksh':u'Bot: hät outomatesch Täx jetuusch: %s',
       'lt':u'robotas: Automatinis teksto keitimas %s',
       'nds':u'Bot: Text automaatsch utwesselt: %s',
       'nl':u'Bot: automatisch tekst vervangen %s',
       'pl':u'Robot automatycznie zamienia tekst %s',
       'pt':u'Bot: Mudança automática %s',
       'sr':u'Бот: Аутоматска замена текста %s',
       }

class XmlDumpReplacePageGenerator:
    """
    Generator which will yield Pages to pages that might contain text to
    replace. These pages will be retrieved from a local XML dump file
    (cur table).
    """
    def __init__(self, xmlFilename, replacements, exceptions):
        """
        Arguments:
            * xmlFilename  - The dump's path, either absolute or relative
            * replacements - A list of 2-tuples of original text (as a compiled
                             regular expression) and replacement text (as a
                             string).
            * exceptions   - A list of compiled regular expression; pages which
                             contain text that matches one of these won't be
                             changed.
        """

        self.xmlFilename = xmlFilename
        self.replacements = replacements
        self.exceptions = exceptions

    def __iter__(self):
        import xmlreader
        mysite = wikipedia.getSite()
        dump = xmlreader.XmlDump(self.xmlFilename)
        for entry in dump.parse():
            skip_page = False
            for exception in self.exceptions:
                if exception.search(entry.text):
                    skip_page = True
                    break
            if not skip_page:
                # TODO: leave out pages that only have old inside nowiki, comments, math
                for old, new in self.replacements:
                    if old.search(entry.text):
                        yield wikipedia.Page(mysite, entry.title)
                        break

class ReplaceRobot:
    """
    A bot that can do text replacements.
    """
    def __init__(self, generator, replacements, exceptions = [], acceptall = False, allowoverlap = False,
                 recursive = False, addedCat = None):
        """
        Arguments:
            * generator    - A generator that yields Page objects.
            * replacements - A list of 2-tuples of original text (as a compiled
                             regular expression) and replacement text (as a
                             string).
            * exceptions   - A list of compiled regular expression; pages which
                             contain text that matches one of these won't be
                             changed.
            * acceptall    - If True, the user won't be prompted before changes
                             are made.
            * allowoverlap - If True, when matches overlap, all of them are replaced.
            * addedCat     - If set to a value, add this category to every page touched.
        """
        self.generator = generator
        self.replacements = replacements
        self.exceptions = exceptions
        self.acceptall = acceptall
        self.allowoverlap = allowoverlap
        self.recursive = recursive
        self.addedCat = addedCat

    def checkExceptions(self, original_text):
        """
        If one of the exceptions applies for the given text, returns the
        substring which matches the exception. Otherwise it returns None.
        """
        for exception in self.exceptions:
            hit = exception.search(original_text)
            if hit:
                return hit.group(0)
        return None

    def doReplacements(self, original_text):
        """
        Returns the text which is generated by applying all replacements to the
        given text.
        """
        new_text = original_text
        for old, new in self.replacements:
            new_text = wikipedia.replaceExcept(new_text, old, new, ['nowiki', 'comment', 'math', 'pre'], allowoverlap = self.allowoverlap)
        return new_text

    def run(self):
        """
        Starts the robot.
        """
        # Run the generator which will yield Pages which might need to be
        # changed.
        for page in self.generator:
            try:
                # Load the page's text from the wiki
                original_text = page.get()
                if not page.canBeEdited():
                    wikipedia.output(u'Skipping locked page %s' % page.title())
                    continue
            except wikipedia.NoPage:
                wikipedia.output(u'Page %s not found' % page.title())
                continue
            except wikipedia.IsRedirectPage:
                original_text = page.get(get_redirect=True)
            match = self.checkExceptions(original_text)
            # skip all pages that contain certain texts
            if match:
                wikipedia.output(u'Skipping %s because it contains %s' % (page.title(), match))
            else:
                new_text = self.doReplacements(original_text)
                if new_text == original_text:
                    wikipedia.output('No changes were necessary in %s' % page.title())
                else:
                    if self.recursive:
                        newest_text = self.doReplacements(new_text)
                        while (newest_text!=new_text):
                            new_text = newest_text
                            newest_text = self.doReplacements(new_text)

                    if self.addedCat:
                        cats = page.categories()
                        if self.addedCat not in cats:
                            cats.append(self.addedCat)
                            new_text = wikipedia.replaceCategoryLinks(new_text, cats)
                    # Show the title of the page we're working on.
                    # Highlight the title in purple.
                    wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" % page.title())
                    wikipedia.showDiff(original_text, new_text)
                    if not self.acceptall:
                        choice = wikipedia.inputChoice(u'Do you want to accept these changes?', ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
                        if choice in ['a', 'A']:
                            self.acceptall = True
                    if self.acceptall or choice in ['y', 'Y']:
                        try:
                            page.put(new_text)
                        except wikipedia.EditConflict:
                            wikipedia.output(u'Skipping %s because of edit conflict' % (page.title(),))
                        except wikipedia.SpamfilterError, e:
                            wikipedia.output(u'Cannot change %s because of blacklist entry %s' % (page.title(), e.url))
                        except wikipedia.LockedPage:
                            wikipedia.output(u'Skipping %s (locked page)' % (page.title(),))

def prepareRegexForMySQL(pattern):
    pattern = pattern.replace('\s', '[:space:]')
    pattern = pattern.replace('\d', '[:digit:]')
    pattern = pattern.replace('\w', '[:alnum:]')

    pattern = pattern.replace("'", "\\" + "'")
    #pattern = pattern.replace('\\', '\\\\')
    #for char in ['[', ']', "'"]:
    #    pattern = pattern.replace(char, '\%s' % char)
    return pattern


def main():
    gen = None
    # summary message
    summary_commandline = None
    # Array which will collect commandline parameters.
    # First element is original text, second element is replacement text.
    commandline_replacements = []
    # A list of 2-tuples of original text and replacement text.
    replacements = []
    # Don't edit pages which contain certain texts.
    exceptions = []
    # Should the elements of 'replacements' and 'exceptions' be interpreted
    # as regular expressions?
    regex = False
    # Predefined fixes from dictionary 'fixes' (see above).
    fix = None
    # the dump's path, either absolute or relative, which will be used when source
    # is 'xmldump'.
    xmlFilename = None
    useSql = False
    PageTitles = []
    # will become True when the user presses a ('yes to all') or uses the -always
    # commandline paramater.
    acceptall = False
    # Will become True if the user inputs the commandline parameter -nocase
    caseInsensitive = False
    # Which namespaces should be processed?
    # default to [] which means all namespaces will be processed
    namespaces = []
    # Do all hits when they overlap
    allowoverlap = False
    # Do not recurse replacement
    recursive = False
    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()
    # Load default summary message.
    # BUG WARNING: This is probably incompatible with the -lang parameter.
    wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg))

    # Read commandline parameters.
    for arg in wikipedia.handleArgs():
        if arg == '-regex':
            regex = True
        elif arg.startswith('-xml'):
            if len(arg) == 4:
                xmlFilename = wikipedia.input(u'Please enter the XML dump\'s filename:')
            else:
                xmlFilename = arg[5:]
        elif arg =='-sql':
            useSql = True
        elif arg.startswith('-page'):
            if len(arg) == 5:
                PageTitles.append(wikipedia.input(u'Which page do you want to chage?'))
            else:
                PageTitles.append(arg[6:])
        elif arg.startswith('-except:'):
            exceptions.append(arg[8:])
        elif arg.startswith('-fix:'):
            fix = arg[5:]
        elif arg == '-always':
            acceptall = True
        elif arg == '-recursive':
            recursive = True
        elif arg == '-nocase':
            caseInsensitive = True
        elif arg.startswith('-namespace:'):
            namespaces.append(int(arg[11:]))
        elif arg.startswith('-summary:'):
            wikipedia.setAction(arg[9:])
            summary_commandline = True
        elif arg.startswith('-allowoverlap'):
            allowoverlap = True
        else:
            generator = genFactory.handleArg(arg)
            if generator:
                gen = generator
            else:
                commandline_replacements.append(arg)

    if (len(commandline_replacements)%2):
        raise wikipedia.Error, 'require even number of replacements.'
    elif (len(commandline_replacements) == 2 and fix == None):
        replacements.append((commandline_replacements[0], commandline_replacements[1]))
        if summary_commandline == None:
            wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg ) % ' (-' + commandline_replacements[0] + ' +' + commandline_replacements[1] + ')')
    elif (len(commandline_replacements) > 1):
        if (fix == None):
            #replacements.extend(commandline_replacements)
            for i in xrange (0,len(commandline_replacements),2):
                replacements.append((commandline_replacements[i],
                                     commandline_replacements[i+1]))

        else:
           raise wikipedia.Error, 'Specifying -fix with replacements is undefined'
    elif fix == None:
        old = wikipedia.input(u'Please enter the text that should be replaced:')
        new = wikipedia.input(u'Please enter the new text:')
        change = '(-' + old + ' +' + new
        replacements.append((old, new))
        while True:
            old = wikipedia.input(u'Please enter another text that should be replaced, or press Enter to start:')
            if old == '':
                change = change + ')'
                break
            new = wikipedia.input(u'Please enter the new text:')
            change = change + ' & -' + old + ' +' + new
            replacements.append((old, new))
        if not summary_commandline == True:
            default_summary_message =  wikipedia.translate(wikipedia.getSite(), msg) % change
            wikipedia.output(u'The summary message will default to: %s' % default_summary_message)
            summary_message = wikipedia.input(u'Press Enter to use this default message, or enter a description of the changes your bot will make:')
            if summary_message == '':
                summary_message = default_summary_message
            wikipedia.setAction(summary_message)

    else:
        # Perform one of the predefined actions.
        try:
            fix = fixes.fixes[fix]
        except KeyError:
            wikipedia.output(u'Available predefined fixes are: %s' % fixes.fixes.keys())
            wikipedia.stopme()
            sys.exit()
        if fix.has_key('regex'):
            regex = fix['regex']
        if fix.has_key('msg'):
            wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), fix['msg']))
        if fix.has_key('exceptions'):
            exceptions = fix['exceptions']
        replacements = fix['replacements']


    # already compile all regular expressions here to save time later
    for i in range(len(replacements)):
        old, new = replacements[i]
        if not regex:
            old = re.escape(old)
        if caseInsensitive:
            oldR = re.compile(old, re.UNICODE | re.IGNORECASE)
        else:
            oldR = re.compile(old, re.UNICODE)
        replacements[i] = oldR, new
    for i in range(len(exceptions)):
        exception = exceptions[i]
        if not regex:
            exception = re.escape(exception)
        if caseInsensitive:
            exceptionR = re.compile(exception, re.UNICODE | re.IGNORECASE)
        else:
            exceptionR = re.compile(exception, re.UNICODE)
        exceptions[i] = exceptionR

    if xmlFilename:
        gen = XmlDumpReplacePageGenerator(xmlFilename, replacements, exceptions)
    elif useSql:
        whereClause = 'WHERE (%s)' % ' OR '.join(["old_text RLIKE '%s'" % prepareRegexForMySQL(old.pattern) for (old, new) in replacements])
        if exceptions:
            exceptClause = 'AND NOT (%s)' % ' OR '.join(["old_text RLIKE '%s'" % prepareRegexForMySQL(exc.pattern) for exc in exceptions])
        else:
            exceptClause = ''
        query = u"""
SELECT page_namespace, page_title
FROM page
JOIN text ON (page_id = old_id)
%s
%s
LIMIT 200""" % (whereClause, exceptClause)
        gen = pagegenerators.MySQLPageGenerator(query)

    elif PageTitles:
        pages = [wikipedia.Page(wikipedia.getSite(), PageTitle) for PageTitle in PageTitles]
        gen = iter(pages)

    if not gen:
        # syntax error, show help text from the top of this file
        wikipedia.showHelp('replace')
        wikipedia.stopme()
        sys.exit()
    if namespaces != []:
        gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
    preloadingGen = pagegenerators.PreloadingGenerator(gen, pageNumber = 50)
    bot = ReplaceRobot(preloadingGen, replacements, exceptions, acceptall, allowoverlap, recursive)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
