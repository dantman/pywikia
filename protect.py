# -*- coding: utf-8 -*-
"""
This script can be used to protect and unprotect pages en masse.
Of course, you will need an admin account on the relevant wiki.
 
Syntax: python protect.py OPTION...
 
Command line options:
 
-page:       Protect specified page
-cat:        Protect all pages in the given category.
-nosubcats:  Don't protect pages in the subcategories.
-links:      Protect all pages linked from a given page.
-file:       Protect all pages listed in a text file.
-ref:        Protect all pages referring from a given page.
-images:     Protect all images used on a given page.
-always:     Don't prompt to protect pages, just do it.
-summary:    Supply a custom edit summary.
-unprotect:   Actually unprotect pages instead of protecting
-edit:PROTECTION_LEVEL Set edit protection level to PROTECTION_LEVEL
-move:PROTECTION_LEVEL Set move protection level to PROTECTION_LEVEL

## Without support ##
## -create:PROTECTION_LEVEL Set move protection level to PROTECTION_LEVEL ##
 
Values for PROTECTION_LEVEL are: sysop, autoconfirmed, none.
If an operation parameter (edit, move or create) is not specified, default
protection level is 'sysop' (or 'none' if -unprotect).
 
Examples:
 
Protect everything in the category "To protect" prompting.
    python protect.py -cat:"To protect" -always
 
Unprotect all pages listed in text file "unprotect.txt" without prompting.
    python protect.py -file:unprotect.txt -unprotect
"""
 
# Written by http://it.wikisource.org/wiki/Utente:Qualc1
# Created by modifying delete.py
__version__ = '$Id: delete.py 4946 2008-01-29 14:58:25Z wikipedian $'
 
#
# Distributed under the terms of the MIT license.
#
 
import wikipedia, catlib
import pagegenerators
 
# Summary messages for protecting from a category.
msg_simple_protect = {
    'en': u'Bot: Protecting a list of files.',
    'it': u'Bot: Protezione di una lista di pagine.',
    'pt': u'Bot: Protegendo uma lista de artigos.',
}
msg_protect_category = {
    'en': u'Robot - Protecting all pages from category %s',
    'it': u'Bot: Protezione di tutte le pagine nella categoria %s.',
    'pt': u'Bot: Protegendo todos os artigos da categoria %s',
}
msg_protect_links = {
    'en': u'Robot - Protecting all pages linked from %s',
    'it': u'Bot: Protezione di tutte le pagine linkate da %s.',
    'pt': u'Bot: Protegendo todos os artigos ligados a %s',
}
msg_protect_ref = {
    'en': u'Robot - Protecting all pages referring from %s',
    'it': u'Bot: Protezione di tutte le pagine con link verso %s.',
    'pt': u'Bot: Protegendo todos os artigos afluentes a %s',
}
msg_protect_images = {
    'en': u'Robot - Protecting all images on page %s',
    'it': u'Bot: Protezione di tutte le immagini presenti in %s.',
    'pt': u'Bot: Protegendo todas as imagens do artigo %s',
}
 
class ProtectionRobot:
    """
    This robot allows protection of pages en masse.
    """
 
    def __init__(self, generator, summary, always = False, unprotect=False,
                edit='sysop', move='sysop', create='sysop'):
        """
        Arguments:
            * generator - A page generator.
            * always - Protect without prompting?
            * edit, move, create - protection level for these operations
            * unprotect - unprotect pages (and ignore edit, move, create params)
        """
        self.generator = generator
        self.summary = summary
        self.always = always
        self.unprotect = unprotect
        self.edit = edit
        self.move = move
 
    def run(self):
        """
        Starts the robot's action.
        """
        #Loop through everything in the page generator and (un)protect it.
        for page in self.generator:
            wikipedia.output(u'Processing page %s' % page.title())
            print self.edit, self.move#, self.create
            page.protect(unprotect=self.unprotect, reason=self.summary, prompt=self.always,
                        edit=self.edit, move=self.move)
 
# Asks a valid protection level for "operation".
# Returns the protection level chosen by user.
def choiceProtectionLevel(operation, default):
    default = default[0]
    firstChar = map(lambda level: level[0], protectionLevels)
    choiceChar = wikipedia.inputChoice('Choice a protection level to %s:' % operation, 
                            protectionLevels, firstChar, default = default)
    for level in protectionLevels:
        if level.startswith(choiceChar):
            return level
 
def main():
    global protectionLevels
    protectionLevels = ['sysop', 'autoconfirmed', 'none']
 
    pageName = ''
    summary = ''
    always = False
    doSinglePage = False
    doCategory = False
    protectSubcategories = True
    doRef = False
    doLinks = False
    doImages = False
    fileName = ''
    gen = None
    edit = ''
    move = ''
    defaultProtection = 'sysop'
 
    # read command line parameters
    for arg in wikipedia.handleArgs():
        if arg == '-always':
            always = True
        elif arg.startswith('-file'):
            if len(arg) == len('-file'):
                fileName = wikipedia.input(u'Enter name of file to protect pages from:')
            else:
                fileName = arg[len('-file:'):]
        elif arg.startswith('-summary'):
            if len(arg) == len('-summary'):
                summary = wikipedia.input(u'Enter a reason for the protection:')
            else:
                summary = arg[len('-summary:'):]
        elif arg.startswith('-cat'):
            doCategory = True
            if len(arg) == len('-cat'):
                pageName = wikipedia.input(u'Enter the category to protect from:')
            else:
                pageName = arg[len('-cat:'):]
        elif arg.startswith('-nosubcats'):
            protectSubcategories = False
        elif arg.startswith('-links'):
            doLinks = True
            if len(arg) == len('-links'):
                pageName = wikipedia.input(u'Enter the page to protect from:')
            else:
                pageName = arg[len('-links:'):]
        elif arg.startswith('-ref'):
            doRef = True
            if len(arg) == len('-ref'):
                pageName = wikipedia.input(u'Enter the page to protect from:')
            else:
                pageName = arg[len('-ref:'):]
        elif arg.startswith('-page'):
            doSinglePage = True
            if len(arg) == len('-page'):
                pageName = wikipedia.input(u'Enter the page to protect:')
            else:
                pageName = arg[len('-page:'):]
        elif arg.startswith('-images'):
            doImages = True
            if len(arg) == len('-images'):
                pageName = wikipedia.input(u'Enter the page with the images to protect:')
            else:
                pageName = arg[len('-images:'):]
        elif arg.startswith('-unprotect'):
            defaultProtection = 'none'
        elif arg.startswith('-edit'):
            edit = arg[len('-edit:'):]
            if edit not in protectionLevels:
                edit = choiceProtectionLevel('edit', defaultProtection)
        elif arg.startswith('-move'):
            move = arg[len('-move:'):]
            if move not in protectionLevels:
                move = choiceProtectionLevel('move', defaultProtection)
        elif arg.startswith('-create'):
            create = arg[len('-create:'):]
            if create not in protectionLevels:
                create = choiceProtectionLevel('create', defaultProtection)
 
    mysite = wikipedia.getSite()
 
    if doSinglePage:
        if not summary:
            summary = wikipedia.input(u'Enter a reason for the protection:')
        page = wikipedia.Page(mysite, pageName)
        gen = iter([page])
    elif doCategory:
        if not summary:
            summary = wikipedia.translate(mysite, msg_protect_category) % pageName
        ns = mysite.category_namespace()
        categoryPage = catlib.Category(mysite, ns + ':' + pageName)
        gen = pagegenerators.CategorizedPageGenerator(categoryPage, recurse = protectSubcategories)
    elif doLinks:
        if not summary:
            summary = wikipedia.translate(mysite, msg_protect_links) % pageName
        linksPage = wikipedia.Page(mysite, pageName)
        gen = pagegenerators.LinkedPageGenerator(linksPage)
    elif doRef:
        if not summary:
            summary = wikipedia.translate(mysite, msg_protect_ref) % pageName
        refPage = wikipedia.Page(mysite, pageName)
        gen = pagegenerators.ReferringPageGenerator(refPage)
    elif fileName:
        if not summary:
            summary = wikipedia.translate(mysite, msg_simple_protect)
        gen = pagegenerators.TextfilePageGenerator(fileName)
    elif doImages:
        if not summary:
            summary = wikipedia.translate(mysite, msg_protect_images) % pageName
        gen = pagegenerators.ImagesPageGenerator(wikipedia.Page(mysite, pageName))
 
    if gen:
        wikipedia.setAction(summary)
        # We are just protecting pages, so we have no need of using a preloading page generator
        # to actually get the text of those pages.
        if not edit: edit = defaultProtection
        if not move: move = defaultProtection
        bot = ProtectionRobot(gen, summary, always, edit=edit, move=move)
        bot.run()
    else:
        wikipedia.showHelp(u'protect')
 
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
