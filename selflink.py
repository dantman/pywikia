#!/usr/bin/python
# -*- coding: utf-8  -*-

"""
This bot goes over multiple pages of the home wiki, searches for selflinks, and
allows removing them.

This script understands various command-line arguments:

    -start:        used as -start:page_name, specifies that the robot should
                   go alphabetically through all pages on the home wiki,
                   starting at the named page.

    -file:         used as -file:file_name, read a list of pages to treat
                   from the named textfile. Page titles should be enclosed
                   in [[double-squared brackets]].

    -ref:          used as -ref:page_name, specifies that the robot should
                   work on all pages referring to the named page.

    -links:        used as -links:page_name, specifies that the robot should
                   work on all pages referred to from the named page.

    -cat:          used as -cat:category_name, specifies that the robot should
                   work on all pages in the named category.

    -namespace:n - Number of namespace to process. The parameter can be used
                   multiple times. It works in combination with all other
                   parameters, except for the -start parameter. If you e.g.
                   want to iterate over all user pages starting at User:M, use
                   -start:User:M.

All other parameters will be regarded as a page title; in this case, the bot
will only work on a single page.
"""

__version__='$Id$'

import wikipedia, pagegenerators, catlib
import editarticle
import re, sys

# Summary messages in different languages
# NOTE: Predefined replacement tasks might use their own dictionary, see 'fixes'
# below.
msg = {
          'de':u'Bot: Entferne Selbstlinks',
          'he':u'רובוט: מסיר קישורים של הדף לעצמו',
          'fr':u'Bot: Enlève autoliens',
          'en':u'Robot: Removing selflinks',
          'pt':u'Bot: Retirando link para o próprio artigo'
       }    

class XmlDumpSelflinkPageGenerator:
    """
    Generator which will yield Pages that might contain selflinks.
    These pages will be retrieved from a local XML dump file
    (cur table).
    """
    def __init__(self, xmlFilename):
        """
        Arguments:
            * xmlFilename  - The dump's path, either absolute or relative
        """

        self.xmlFilename = xmlFilename

    def __iter__(self):
        import xmlreader
        mysite = wikipedia.getSite()
        dump = xmlreader.XmlDump(self.xmlFilename)
        for entry in dump.parse():
            title = re.escape(entry.title)
            if not mysite.nocapitalize:
                title = '[%s%s]%s' % (title[0].lower(), title[0].upper(), title[1:])
            selflinkR = re.compile(r'\[\[' + title + '(\|[^\]]*)?\]\]')
            if selflinkR.search(entry.text):
                yield wikipedia.Page(mysite, entry.title)
                continue

class SelflinkBot:

    def __init__(self, generator):
        self.generator = generator
        linktrail = wikipedia.getSite().linktrail()
        # The regular expression which finds links. Results consist of four groups:
        # group title is the target page title, that is, everything before | or ].
        # group section is the page section. It'll include the # to make life easier for us.
        # group label is the alternative link title, that's everything between | and ].
        # group linktrail is the link trail, that's letters after ]] which are part of the word.
        # note that the definition of 'letter' varies from language to language.
        self.linkR = re.compile(r'\[\[(?P<title>[^\]\|#]*)(?P<section>#[^\]\|]*)?(\|(?P<label>[^\]]*))?\]\](?P<linktrail>' + linktrail + ')')

    def handleNextLink(self, page, text, match, context = 100):
        """
        Returns a tuple (text, jumpToBeginning).
        text is the unicode string after the current link has been processed.
        jumpToBeginning is a boolean which specifies if the cursor position
        should be reset to 0. This is required after the user has edited the
        article.
        """
        # ignore interwiki links and links to sections of the same page as well as section links
        if not match.group('title') or page.site().isInterwikiLink(match.group('title')) or match.group('section'):
            return text, False

        linkedPage = wikipedia.Page(page.site(), match.group('title'))
        # Check whether the link found is to the current page itself.
        if linkedPage != page:
            # not a self-link
            return text, False
        else:
            # at the beginning of the link, start red color.
            # at the end of the link, reset the color to default
            colors = [None for c in text[max(0, match.start() - context) : match.start()]] + [12 for c in text[match.start() : match.end()]] + [None for c in text[match.end() : match.end() + context]]
            wikipedia.output(text[max(0, match.start() - context) : match.end() + context], colors = colors)
            choice = wikipedia.inputChoice(u'\nWhat shall be done with this selflink?',  ['unlink', 'make bold', 'skip', 'edit', 'more context'], ['U', 'b', 's', 'e', 'm'], 'u')
            wikipedia.output(u'')

            if choice == 's':
                # skip this link
                return text, False
            elif choice == 'e':
                editor = editarticle.TextEditor()
                newText = editor.edit(text, jumpIndex = match.start())
                # if user didn't press Cancel
                if newText:
                    return newText, True
                else:
                    return text, True
            elif choice == 'm':
                # show more context by recursive self-call
                return self.handleNextLink(page, text, match, context = context + 100)
            else:
                new = match.group('label') or match.group('title')
                new += match.group('linktrail')
                if choice == 'u':
                    return text[:match.start()] + new + text[match.end():], False
                else:
                    # make bold
                    return text[:match.start()] + "'''" + new + "'''" + text[match.end():], False
    
    def treat(self, page):
        # Show the title of the page where the link was found.
        # Highlight the title in purple.
        colors = [None] * 6 + [13] * len(page.title()) + [None] * 4
        wikipedia.output(u"\n\n>>> %s <<<" % page.title(), colors = colors)
        try:
            oldText = page.get()
            text = oldText
            curpos = 0
            while curpos < len(text):
                match = self.linkR.search(text, pos = curpos)
                if not match:
                    break
                # Make sure that next time around we will not find this same hit.
                curpos = match.start() + 1
                text, jumpToBeginning = self.handleNextLink(page, text, match)
                if jumpToBeginning:
                    curpos = 0

            if oldText == text:
                wikipedia.output(u'No changes necessary.')
            else:
                wikipedia.showDiff(oldText, text)
                page.put(text)
        except wikipedia.NoPage:
            wikipedia.output(u"Page %s does not exist?!" % page.aslink())
        except wikipedia.IsRedirectPage:
            wikipedia.output(u"Page %s is a redirect; skipping." % page.aslink())
        except wikipedia.LockedPage:
            wikipedia.output(u"Page %s is locked?!" % page.aslink())

    def run(self):
        comment = wikipedia.translate(wikipedia.getSite(), msg)
        wikipedia.setAction(comment)

        for page in self.generator:
            self.treat(page)

def main():
    #page generator
    gen = None
    # This temporary array is used to read the page title if one single
    # page to work on is specified by the arguments.
    pageTitle = []
    # Which namespaces should be processed?
    # default to [] which means all namespaces will be processed
    namespaces = []
    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()

    for arg in wikipedia.handleArgs():
        if arg.startswith('-xml'):
            if len(arg) == 4:
                xmlFilename = wikipedia.input(u'Please enter the XML dump\'s filename:')
            else:
                xmlFilename = arg[5:]
            gen = XmlDumpSelflinkPageGenerator(xmlFilename)
        elif arg == '-sql':
            # NOT WORKING YET
            query = """
SELECT page_namespace, page_title
FROM page JOIN pagelinks JOIN text ON (page_id = pl_from AND page_id = old_id)
WHERE pl_title = page_title
AND pl_namespace = page_namespace
AND page_namespace = 0
AND (old_text LIKE concat('%[[', page_title, ']]%')
    OR old_text LIKE concat('%[[', page_title, '|%'))
LIMIT 100"""
            gen = pagegenerators.MySQLPageGenerator(query)
        elif arg.startswith('-namespace:'):
            namespaces.append(int(arg[11:]))
        else:
            generator = genFactory.handleArg(arg)
            if generator:
                gen = generator
            else:
                pageTitle.append(arg)

    if pageTitle:
        page = wikipedia.Page(wikipedia.getSite(), ' '.join(pageTitle))
        gen = iter([page])
    if not gen:
        wikipedia.showHelp('selflink')
    else:
        if namespaces != []:
            gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
        preloadingGen = pagegenerators.PreloadingGenerator(gen)
        bot = SelflinkBot(preloadingGen)
        bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
