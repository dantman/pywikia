#!/usr/bin/python
# -*- coding: utf-8  -*-

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