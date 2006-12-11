#!/usr/bin/python
# coding: utf-8

"""
Include commons template in home wiki.

This bot functions mainly in the en.wikipedia, because it
compares the names of articles and category in English
language (standard language in Commons). If the name of
an article in Commons will not be in English but with
redirect, this also functions.

Command-line arguments:

    -cat           Work on all pages which are in a specific category.
                   Argument can also be given as "-cat:categoryname".

    -ref           Work on all pages that link to a certain page.
                   Argument can also be given as "-ref:referredpagetitle".

    -link          Work on all pages that are linked from a certain page.
                   Argument can also be given as "-link:linkingpagetitle".

    -start         Work on all pages on the home wiki, starting at the named page.
                   
Single pages use: commons_link.py article

"""
#
# Distributed under the terms of the MIT license.
#

__version__='$Id$'

import wikipedia, pagegenerators
import re

comment = {
    'en':'Robot: Include commons template'
    }

class CommonsLinkBot:
    def __init__(self, generator, acceptall = False):
        self.generator = generator
        self.acceptall = acceptall
            
    def run(self):
        for page in self.generator:
            try:
                wikipedia.output(u'\n>>>> %s <<<<' % page.title())
                commons = wikipedia.Site('commons', 'commons')
                commonspage = wikipedia.Page(commons, page.title())
                try:
                    getcommons = commonspage.get(get_redirect=True)
                    if page.title() == commonspage.title():
                        oldText = page.get()
                        text = oldText

                        # find commons template
                        findTemplate=re.compile(ur'\{\{[Cc]ommons')
                        s = findTemplate.search(text)
                        findTemplate2=re.compile(ur'\{\{[Ss]isterlinks')
                        s2 = findTemplate2.search(text)
                        if s or s2:
                            wikipedia.output(u'** Already done.')
                        else:
                            # TODO: input template before categories and interwikis
                            text = (text+'{{commons|{{subst:PAGENAME}}}}')
                            if oldText == text:
                                continue
                            else:
                                wikipedia.showDiff(oldText, text)
                                if not self.acceptall:
                                    choice = wikipedia.inputChoice(u'Do you want to accept these changes?', ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
                                    if choice in ['a', 'A']:
                                        self.acceptall = True
                                if self.acceptall or choice in ['y', 'Y']:
                                    try:
                                        msg = wikipedia.translate(wikipedia.getSite(), comment)
                                        page.put(text, msg)
                                    except wikipedia.EditConflict:
                                        wikipedia.output(u'Skipping %s because of edit conflict' % (page.title()))
                            
                except wikipedia.NoPage:
                    wikipedia.output(u'Page does not exist in Commons!')
                    
            except wikipedia.NoPage:
                wikipedia.output(u'Page %s does not exist?!' % page.title())
            except wikipedia.IsRedirectPage:
                wikipedia.output(u'Page %s is a redirect; skipping.' % page.title())
            except wikipedia.LockedPage:
                wikipedia.output(u'Page %s is locked?!' % page.title())

def main():
    singlepage = []
    gen = None
    start = None
    
    for arg in wikipedia.handleArgs():
        if arg.startswith('-start:'):
            start = wikipedia.Page(wikipedia.getSite(),arg[7:])
            gen = pagegenerators.AllpagesPageGenerator(start.titleWithoutNamespace(),namespace=start.namespace())
        elif arg.startswith('-cat:'):
            import catlib
            cat = catlib.Category(wikipedia.getSite(),'Category:%s'%arg[5:])
            gen = pagegenerators.CategorizedPageGenerator(cat)
        elif arg.startswith('-ref:'):
            ref = wikipedia.Page(wikipedia.getSite(), arg[5:])
            gen = pagegenerators.ReferringPageGenerator(ref)
        elif arg.startswith('-link:'):
            link = wikipedia.Page(wikipedia.getSite(), arg[6:])
            gen = pagegenerators.LinkedPageGenerator(link)
        else:
            singlepage.append(arg)

    if singlepage:
        page = wikipedia.Page(wikipedia.getSite(), ' '.join(singlepage))
        gen = iter([page])
    if not gen:
        wikipedia.showHelp(u'commons_link')
    else:
        preloadingGen = pagegenerators.PreloadingGenerator(gen)
        bot = CommonsLinkBot(preloadingGen, acceptall=False)
        bot.run()
                
if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
