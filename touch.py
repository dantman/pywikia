#!/usr/bin/python
# -*- coding: utf-8  -*-

"""
This bot goes over multiple pages of the home wiki, and edits them without
changing. This is for example used to get category links in templates
working.

This script understands various command-line arguments:

    -start:        used as -start:page_name, specifies that the robot should
                   go alphabetically through all pages on the home wiki,
                   starting at the named page.

    -file:         used as -file:file_name, read a list of pages to treat
                   from the named textfile. Page titles should be enclosed
                   in [[double-squared brackets]].

    -ref:          used as -start:page_name, specifies that the robot should
                   touch all pages referring to the named page.

    -links:        used as -links:page_name, specifies that the robot should
                   touch all pages referred to from the named page.

    -cat:          used as -cat:category_name, specifies that the robot should
                   touch all pages in the named category.

    -redir         specifies that the robot should touch redirect pages;
                   otherwise, they will be skipped.

All other parameters will be regarded as a page title; in this case, the bot
will only touch a single page.
"""

__version__='$Id: touch.py,v 1.13 2006/03/01 14:07:06 russblau Exp $'

import wikipedia, pagegenerators, catlib, config
import sys

class TouchBot:
    def __init__(self, generator, touch_redirects):
        self.generator = generator
        self.touch_redirects = touch_redirects

    def run(self):
        for page in self.generator:
            try:
                # get the page, and save it using the unmodified text.
                # whether or not getting a redirect throws an exception
                # depends on the variable self.touch_redirects.
                text = page.get(get_redirect = self.touch_redirects)
                page.put(text)
            except wikipedia.NoPage:
                print "Page %s does not exist?!" % page.aslink()
            except wikipedia.IsRedirectPage:
                print "Page %s is a redirect; skipping." % page.aslink()
            except wikipedia.LockedPage:
                print "Page %s is locked?!" % page.aslink()

def main():
    # Disable cosmetic changes because we don't want to modify any page
    # content, so that we don't flood the histories with minor changes.
    config.cosmetic_changes = False
    #page generator
    gen = None
    redirs = False
    # If the user chooses to work on a single page, this temporary array is
    # used to read the words from the page title. The words will later be
    # joined with spaces to retrieve the full title.
    pageTitle = []
    for arg in wikipedia.handleArgs():
        if arg.startswith('-start:'):
            page = wikipedia.Page(wikipedia.getSite(), arg[7:])
            gen = pagegenerators.AllpagesPageGenerator(page.titleWithoutNamespace(), namespace = page.namespace())
        elif arg.startswith('-ref:'):
            referredPage = wikipedia.Page(wikipedia.getSite(), arg[5:])
            gen = pagegenerators.ReferringPageGenerator(referredPage)
        elif arg.startswith('-links:'):
            linkingPage = wikipedia.Page(wikipedia.getSite(), arg[7:])
            gen = pagegenerators.LinkedPageGenerator(linkingPage)
        elif arg.startswith('-file:'):
            gen = pagegenerators.TextfilePageGenerator(arg[6:])
        elif arg.startswith('-cat:'):
            cat = catlib.Category(wikipedia.getSite(), arg[5:])
            gen = pagegenerators.CategorizedPageGenerator(cat)
        elif arg == '-redir':
            redirs = True
        else:
            pageTitle.append(arg)

    if pageTitle:
        # work on a single page
        page = wikipedia.Page(wikipedia.getSite(), ' '.join(pageTitle))
        gen = iter([page])
    if not gen:
        wikipedia.showHelp('touch')
    else:
        preloadingGen = pagegenerators.PreloadingGenerator(gen)
        bot = TouchBot(preloadingGen, redirs)
        bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
