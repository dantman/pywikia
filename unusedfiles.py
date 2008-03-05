#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
This bot appends some text to all unused images and other text to the respective uploaders.

Parameters:

-always     Don't be asked every time.

"""

#
# (C) Leogregianin, 2007
# (C) Filnik, 2008
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import wikipedia
import pagegenerators
import sys

#***** SETTINGS *******#
#                      #
#   - EDIT BELOW -     #
#                      #
#**********************#

comment = {
    'en': u'images for elimination',
    'he': u'תמונות להסרה',
    'it': u'Bot: segnalo immagine orfana da eliminare',
    'pt': u'marcação de imagens para eliminação',
    }

template_to_the_image = {
    'en': u'\n\n{{subst:No-use2}}',
    'it': u'\n\n{{immagine orfana}}',
    }
template_to_the_user = {
    'en': u'\n\n{{img-sem-uso|%s}}',
    'it': u'\n\n{{Utente:Filbot/Immagine orfana}}',
    }
except_text = {
    'en': u'<table id="mw_metadata" class="mw_metadata">',
    'it': u'<table id="mw_metadata" class="mw_metadata">',
    }

#***** SETTINGS *******#
#                      #
#   - EDIT ABOVE -     #
#                      #
#**********************#

def appendtext(page, apptext, always):
    try:
        text = page.get()
    except wikipedia.IsRedirectPage:
        return
    # Here go edit text in whatever way you want. If you find you do not  (he meant "Here you can go editing...")
    # want to edit this page, just return
    text += apptext;
    if text != page.get():
        wikipedia.showDiff(page.get(),text)
        choice = wikipedia.inputChoice(u'Do you want to accept these changes?', ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
        if choice.lower() in ['a', 'all']:
            always = True
            choice = 'y'
        if choice.lower() in ['y', 'yes']:
            msg = wikipedia.translate(wikipedia.getSite(), comment)
            page.put(text, msg)

def main():
    always = False
    for arg in wikipedia.handleArgs():
        if arg == '-always':
            always = True

    mysite = wikipedia.getSite()
    # If anything needs to be prepared, you can do it here
    template_image = wikipedia.translate(wikipedia.getSite(), template_to_the_image)
    template_user = wikipedia.translate(wikipedia.getSite(), template_to_the_user)
    except_text_translated = wikipedia.translate(wikipedia.getSite(), except_text)
    basicgenerator = pagegenerators.UnusedFilesGenerator()
    generator = pagegenerators.PreloadingGenerator(basicgenerator)
    for page in generator:
        #print page.title()
        if except_text_translated not in page.getImagePageHtml() and 'http://' not in page.get():
            wikipedia.output(u'\n' + page.title())
            appendtext(page, template_image, always)
            uploader = page.getFileVersionHistory().pop()[1]
            usertalkname = u'User Talk:%s' % uploader
            usertalkpage = wikipedia.Page(mysite,usertalkname)
            msg2uploader = template_user % page.title()
            appendtext(usertalkpage,msg2uploader, always)

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
