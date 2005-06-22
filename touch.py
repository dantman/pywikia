#!/usr/bin/python
# -*- coding: utf-8  -*-

"""
This bot goes over multiple pages of the home wiki, and edits them without
changing. This is for example used to get category links in templates
working.

This script understands various command-line arguments:

    -start:        used as -start:pagename, specifies that the robot should
                   go alphabetically through all pages on the home wiki,
                   starting at the named page.

    -file:         used as -file:filename, read a list of pages to treat
                   from the named textfile. Page titles should be enclosed
                   in [[double-squared brackets]].

    -ref:          used as -start:pagename, specifies that the robot should
                   touch all pages referring to the named page.

All other parameters will be regarded as a page title; in this case, the bot
will only touch a single page.
"""
import wikipedia, pagegenerators
import sys

class TouchBot:
    def __init__(self, generator):
        self.generator = generator

    def run(self):
        for page in self.generator.generate():
            try:
                text = page.get()
                page.put(text)
            except wikipedia.NoPage:
                print "Page %s does not exist?!?!"%page.aslink()
            except wikipedia.IsRedirectPage:
                pass
            except wikipedia.LockedPage:
                pass

def main():
    #page generator
    gen = None
    pageTitle = []
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'touch')
        if arg:
            if arg.startswith('-start:'):
                gen = pagegenerators.AllpagesPageGenerator(arg[7:])
            elif arg.startswith('-ref:'):
                referredPage = wikipedia.Page(wikipedia.getSite(), arg[5:])
                gen = pagegenerators.ReferringPageGenerator(referredPage)
            elif arg.startswith('-file:'):
                gen = pagegenerators.TextfilePageGenerator(arg[6:])
            else:
                pageTitle.append(arg)

    if pageTitle:
        page = wikipedia.Page(wikipedia.getSite(), ' '.join(pageTitle))
        gen = pagegenerators.SinglePageGenerator(page)

    preloadingGen = pagegenerators.PreloadingGenerator(gen)
    bot = TouchBot(preloadingGen)
    bot.run()
    
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()