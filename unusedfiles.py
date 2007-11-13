#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
This bot appends some text to all unused images and other text to the respective uploaders.

You are asked for confirmation before every change.
"""
__version__ = '$Id$'

import wikipedia
import pagegenerators
import sys

comment = {
    'en': u'images for elimination',
    'he': u'תמונות להסרה',
    'pt': u'marcação de imagens para eliminação',
    }

def appendtext(page, apptext):
    try:
        text = page.get()
    except wikipedia.IsRedirectPage:
        return
    # Here go edit text in whatever way you want. If you find you do not  (he meant "Here you can go editing...")
    # want to edit this page, just return
    text += apptext;
    if text != page.get():
        wikipedia.showDiff(page.get(),text)
        if wikipedia.input('Do you want to save the changes? (Y/N)') in 'yY':
            msg = wikipedia.translate(wikipedia.getSite(), comment)
            page.put(text, msg)

def main():
    for arg in wikipedia.handleArgs():
        start.append(arg)

    mysite = wikipedia.getSite()
    # If anything needs to be prepared, you can do it here

    basicgenerator = pagegenerators.UnusedFilesGenerator()
    generator = pagegenerators.PreloadingGenerator(basicgenerator)
    for page in generator:
        #print page.title()
        if '<table id="mw_metadata" class="mw_metadata">' not in page.getImagePageHtml() and 'http://' not in page.get():
            wikipedia.output(u'\n' + page.title())
            appendtext(page,u'\n\n{{subst:No-use2}}')
            uploader = page.getFileVersionHistory().pop()[1]
            usertalkname = u'User Talk:' + uploader
            usertalkpage = wikipedia.Page(mysite,usertalkname)
            msg2uploader = u'\n\n{{img-sem-uso|' + page.title() + u'}}'
            appendtext(usertalkpage,msg2uploader)

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
