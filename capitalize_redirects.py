# -*- coding: utf-8  -*-

#
# (C) Yrithinnd
# Class licensed under terms of the MIT license
#

import time, sys
import wikipedia, pagegenerators, catlib

msg = {
    'en': u'Robot: Create redirect to [[%s]]',
    'pt': u'Bot: Criando redirect para [[%s]]',
    }

class CapitalizeBot:
    def __init__(self, generator, acceptall = False):
        self.generator = generator
        self.acceptall = False

    def run(self):
        for page in self.generator:
            page_t = page.title()
            np = wikipedia.Page(wikipedia.getSite(), page_t.capitalize())
            colors = [None] * 3 + [13] * len(page_t) + [None] * 4
            wikipedia.output(u'>> %s <<\n' % page_t, colors = colors)
            if not np.exists():
                wikipedia.output(u'%s don\'t exist' % np.title())
                if not self.acceptall:
                    choice = wikipedia.inputChoice(u'Do you want create redirect?',  ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
                    if choice in ['a', 'A']:
                        self.acceptall = True
                if self.acceptall or choice in ['y', 'Y']:
                    try:
                        wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg) % page_t)
                        np.put(u"#REDIRECT [[%s]]" % page_t)
                        print
                    except:
                        wikipedia.output(u"An error occured. Retrying in 15 seconds...")
                        time.sleep(15)
                        continue
            else:
                wikipedia.output(u'%s already exist, skipping...\n' % np.title())
    
def main():
    gen = None
    source = None
    textfilename = None
    categoryname = None
    pageNames = []
    referredPageName = None
    acceptall = False
    namespaces = []
    startpage = None

    for arg in wikipedia.handleArgs():
        if arg.startswith('-file'):
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
        elif arg.startswith('-page'):
            if len(arg) == 5:
                pageNames.append(wikipedia.input(u'Which page do you want to chage?'))
            else:
                pageNames.append(arg[6:])
            source = 'singlepage'
        elif arg.startswith('-ref'):
            if len(arg) == 4:
                referredPageName = wikipedia.input(u'Links to which page should be processed?')
            else:
                referredPageName = arg[5:]
            source = 'ref'
        elif arg.startswith('-start'):
            if len(arg) == 6:
                firstPageTitle = wikipedia.input(u'Which page do you want to chage?')
            else:
                firstPageTitle = arg[7:]
            source = 'allpages'
        elif arg == '-always':
            acceptall = True
        elif arg.startswith('-namespace:'):
            namespaces.append(int(arg[11:]))
        else:
            commandline_replacements.append(arg)
        
    if source == 'textfile':
        gen = pagegenerators.TextfilePageGenerator(textfilename)
    elif source == 'category':
        cat = catlib.Category(wikipedia.getSite(), categoryname)
        gen = pagegenerators.CategorizedPageGenerator(cat)
    elif source == 'singlepage':
        pages = [wikipedia.Page(wikipedia.getSite(), pageName) for pageName in pageNames]
        gen = iter(pages)
    elif source == 'allpages':
        namespace = wikipedia.Page(wikipedia.getSite(), firstPageTitle).namespace()
        gen = pagegenerators.AllpagesPageGenerator(firstPageTitle, namespace)
    elif source == 'ref':
        referredPage = wikipedia.Page(wikipedia.getSite(), referredPageName)
        gen = pagegenerators.ReferringPageGenerator(referredPage)
    elif source == None or len(commandline_replacements) not in [0, 2]:
        wikipedia.stopme()
        wikipedia.showHelp(u'capitalize_redirects')
        sys.exit()
    if namespaces != []:
        gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
    preloadingGen = pagegenerators.PreloadingGenerator(gen, pageNumber = 20)
    bot = CapitalizeBot(preloadingGen, acceptall)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
