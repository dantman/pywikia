#!/usr/bin/python
# -*- coding: utf-8  -*-

"""
This bot goes over multiple pages of the home wiki, and looks for
images that are linked inline (i.e., they are hosted from an
external server and hotlinked, instead of using the wiki's upload
function.

It is especially useful when you intend to disable the inline linking
feature.

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

__version__='$Id$'

import wikipedia, pagegenerators, catlib, weblinkchecker, upload
import sys, re

msg = {
    'en': u'This image was inline linked from %s. No information on author, copyright status, or license is available.',
    'pl': u'Obraz ten został dolinkowany z adresu %s. Brak jest informacji o autorze, prawach autorskich czy licencji.',
    'pt': u'Esta imagem foi inserida como linha de %s. Nenhum infomação sobre autor, direitos autorais ou licença foi listada.', 
}

###################################
# This is still work in progress! #
###################################

class InlineImagesRobot:
    def __init__(self, generator):
        self.generator = generator

    def run(self):
        for page in self.generator:
            try:
                # get the page, and save it using the unmodified text.
                # whether or not getting a redirect throws an exception
                # depends on the variable self.touch_redirects.
                text = page.get()
                originalText = text
                for url in weblinkchecker.weblinksIn(text, withoutBracketed = True):
                    filename = url.split('/')[-1]
                    description = wikipedia.translate(wikipedia.getSite(), msg) % url
                    bot = upload.UploadRobot(url, description = description)
                    # TODO: check duplicates
                    #filename = bot.uploadImage()
                    #if filename:
                    #    text = text.replace(url, u'[[Image:%s]]' % filename) # 
                # only save if there were changes
                #if text != originalText:
                #    page.put(text)
            except wikipedia.NoPage:
                print "Page %s does not exist?!" % page.aslink()
            except wikipedia.IsRedirectPage:
                print "Page %s is a redirect; skipping." % page.aslink()
            except wikipedia.LockedPage:
                print "Page %s is locked?!" % page.aslink()

def main():
    #page generator
    gen = None
    # If the user chooses to work on a single page, this temporary array is
    # used to read the words from the page title. The words will later be
    # joined with spaces to retrieve the full title.
    pageTitle = []
    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()

    for arg in wikipedia.handleArgs():
        generator = genFactory.handleArg(arg)
        if generator:
            gen = generator
        else:
            pageTitle.append(arg)

    if pageTitle:
        # work on a single page
        page = wikipedia.Page(wikipedia.getSite(), ' '.join(pageTitle))
        gen = iter([page])
    if not gen:
        wikipedia.showHelp('inline_images')
    else:
        preloadingGen = pagegenerators.PreloadingGenerator(gen)
        bot = InlineImagesRobot(preloadingGen)
        bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
