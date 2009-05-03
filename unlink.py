#!/usr/bin/python
# -*- coding: utf-8  -*-

"""
This bot unlinks a page on every page that links to it.

This script understands this command-line argument:

    -namespace:n - Number of namespace to process. The parameter can be used
                   multiple times. It works in combination with all other
                   parameters, except for the -start parameter. If you e.g.
                   want to iterate over all user pages starting at User:M, use
                   -start:User:M.

All other parameters will be regarded as part of the title of the page that
should be unlinked.

Example:

python unlink.py Foo bar -namespace:0 -namespace:6

    Removes links to the page [[Foo bar]] in articles and image descriptions.
"""

__version__='$Id$'

import wikipedia, pagegenerators
import editarticle
import re

# Summary messages in different languages
msg = {
          'ar':u'روبوت: إزالة وصلات "%s"',
          'de':u'Bot: Entlinke "%s"',
          'en':u'Robot: Unlinking "%s"',
          'fi':u'Botti poisti linkin sivulle "%s"',
          'he':u'בוט: מסיר קישורים לדף "%s"',
          'nn':u'robot: fjerna lenkje til "%s"',
          'no':u'robot: fjerner lenke til "%s"',
          'nl':u'Bot: verwijzing naar "%s" verwijderd',
          'pt':u'Bot: Retirando link para "%s"',
       }

class UnlinkBot:

    def __init__(self, pageToUnlink, namespaces):
        self.pageToUnlink = pageToUnlink

        gen = pagegenerators.ReferringPageGenerator(pageToUnlink)

        if namespaces != []:
            gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
        self.generator =  pagegenerators.PreloadingGenerator(gen)

        linktrail = wikipedia.getSite().linktrail()
        # The regular expression which finds links. Results consist of four groups:
        # group title is the target page title, that is, everything before | or ].
        # group section is the page section. It'll include the # to make life easier for us.
        # group label is the alternative link title, that's everything between | and ].
        # group linktrail is the link trail, that's letters after ]] which are part of the word.
        # note that the definition of 'letter' varies from language to language.
        self.linkR = re.compile(r'\[\[(?P<title>[^\]\|#]*)(?P<section>#[^\]\|]*)?(\|(?P<label>[^\]]*))?\]\](?P<linktrail>' + linktrail + ')')

    def handleNextLink(self, text, match, context = 100):
        """
        Returns a tuple (text, jumpToBeginning).
        text is the unicode string after the current link has been processed.
        jumpToBeginning is a boolean which specifies if the cursor position
        should be reset to 0. This is required after the user has edited the
        article.
        """
        # ignore interwiki links and links to sections of the same page as well as section links
        if not match.group('title') or self.pageToUnlink.site().isInterwikiLink(match.group('title')) or match.group('section'):
            return text, False

        linkedPage = wikipedia.Page(self.pageToUnlink.site(), match.group('title'))
        # Check whether the link found is to the current page itself.
        if linkedPage != self.pageToUnlink:
            # not a self-link
            return text, False
        else:
            # at the beginning of the link, start red color.
            # at the end of the link, reset the color to default
            wikipedia.output(text[max(0, match.start() - context) : match.start()] + '\03{lightred}' + text[match.start() : match.end()] + '\03{default}' + text[match.end() : match.end() + context])
            choice = wikipedia.inputChoice(u'\nWhat shall be done with this link?',  ['unlink', 'skip', 'edit', 'more context'], ['U', 's', 'e', 'm'], 'u')
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
                return self.handleNextLink(text, match, context = context + 100)
            else:
                new = match.group('label') or match.group('title')
                new += match.group('linktrail')
                return text[:match.start()] + new + text[match.end():], False

    def treat(self, page):
        # Show the title of the page we're working on.
        # Highlight the title in purple.
        wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" % page.title())
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
                text, jumpToBeginning = self.handleNextLink(text, match)
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
        comment = wikipedia.translate(wikipedia.getSite(), msg) % self.pageToUnlink.title()
        wikipedia.setAction(comment)

        for page in self.generator:
            self.treat(page)

def main():
    # This temporary array is used to read the title of the page
    # that should be unlinked.
    pageTitleParts = []
    # Which namespaces should be processed?
    # default to [] which means all namespaces will be processed
    namespaces = []

    for arg in wikipedia.handleArgs():
        if arg.startswith('-namespace:'):
            try:
                namespaces.append(int(arg[11:]))
            except ValueError:
                namespaces.append(arg[11:])
        else:
            pageTitleParts.append(arg)

    if pageTitleParts:
        page = wikipedia.Page(wikipedia.getSite(), ' '.join(pageTitleParts))
        bot = UnlinkBot(page, namespaces)
        bot.run()
    else:
        wikipedia.showHelp('selflink')

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
