#!/usr/bin/python
# -*- coding: utf-8  -*-

import wikipedia, pagegenerators

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
    gen = pagegenerators.AllpagesPageGenerator()
    preloadingGen = pagegenerators.PreloadingGenerator(gen)
    bot = TouchBot(preloadingGen)
    bot.run()
    
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()