#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
This is not a complete bot; rather, it is a template from which simple
bots can be made. Change workon to edit the contents of a Wikipedia page,
save the result as mybot.py, and then just run:

python mybot.py

to have your change be done on all pages of the wiki. If that takes too
long to work in one stroke, run:

python mybot.py Pagename

to do all pages starting at pagename.

There is one standard command line option:
-test:  Ask for input after every change
"""
import wikipedia
import pagegenerators
import sys

def workon(page):
    try:
        text = page.get()
    except wikipedia.IsRedirectPage:
        return
    # Here go edit text in whatever way you want. If you find you do not
    # want to edit this page, just return
    if text != page.get():
       page.put(text) # Adding a summary text would be good
       if test:
           wikipedia.input(u"Changed [[%s]]. Press enter to continue."%page.title())

try:
    start = []
    test = False
    for arg in wikipedia.handleArgs():
        if arg.startswith("-test"):
            test = True
        else:
            start.append(arg)
    start = " ".join(start) + "!"
    mysite = wikipedia.getSite()
    # If anything needs to be prepared, you can do it here
    basicgenerator = pagegenerators.AllpagesPageGenerator(start=start)
    generator = pagegenerators.PreloadingGenerator(basicgenerator)
    for page in generator:
        workon(page)

finally:
   wikipedia.stopme()

