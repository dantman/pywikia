# -*- coding: utf-8  -*-
"""
This is a script originally written by Wikihermit and then rewritten by Filnik, to delete the templates used to warn in the
pages that a page is blocked, when the page isn't blocked at all. Indeed, very often sysops block the pages for a setted
time but then the forget to delete the warning! This script is useful if you want to delete those useless warning left in these
pages.

Parameters:

-always         Doesn't ask every time if the bot should make the change or not, do it always.
-page           Work only on one page

Note: This script uses also genfactory, you can use those generator as default.

--- Warning! ---
You have to edit this script in order to add your preferences otherwise the script won't work!

If you have problems, ask on botwiki ( http://botwiki.sno.cc ) or on IRC (#pywikipediabot)

--- Example of how to use the script ---

python blockpageschecker.py -always

python blockpageschecker.py -cat:Geography -always

"""
#
# (C) Wikihermit, 2007
# (C) Filnik, 2007
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: blockpageschecker.py,v 1.1 2007/12/7 19.23.00 filnik Exp$'
#

import re
import wikipedia, catlib, pagegenerators, config

#######################################################
#--------------------- PREFERENCES -------------------#
################### -- Edit below! -- #################

# Use only regex! - Regex to delete the template
templateToRemove = {
            'en':[r'\{\{(?:[Tt]emplate:|)[Pp]p-protected\}\}', r'{\{([Tt]emplate:|)[Pp]p-dispute\}\}',
                  r'{\{(?:[Tt]emplate:|)[Pp]p-template\}\}', r'{\{([Tt]emplate:|)[Pp]p-usertalk\}\}'],
           'fr':[r'\{\{(?:[Tt]emplate:|[Mm]odèle:|)[Pp]rotection(|[^\}]*)\}\}', 
                 r'\{\{(?:[Tt]emplate:|[Mm]odèle:|)(?:[Pp]age|[Aa]rchive|[Mm]odèle) protégée?\}\}',
                 r'\{\{(?:[Tt]emplate:|[Mm]odèle:|)[Ss]emi[- ]?protection\}\}'
                ],
            'it':[r'{\{(?:[Tt]emplate:|)[Aa]vvisobloccoparziale(?:|[ _]scad\|(.*?))\}\}', r'{\{(?:[Tt]emplate:|)[Aa]vvisoblocco(?:|[ _]scad\|(?:.*?))\}\}'],
            }
# Category where the bot will check
categoryToCheck = {
            'en':[u'Category:Protected'],
            'fr':[u'Category:Page semi-protégée', u'Category:Page protégée'],
            'it':[u'Categoria:Pagine semiprotette', u'Categoria:Voci_protette'],
            }
# Comment used when the Bot edits
comment = {
            'en':u'Bot: Deleting out-dated template',
            'fr':u'Robot : Retrait du bandeau protection/semi-protection d\'une page qui ne l\'es plus',
            'it':u'Bot: Tolgo template di avviso blocco scaduto',
            }
# Check list to block the users that haven't set their preferences
project_inserted = ['en', 'fr', 'it']

#######################################################
#------------------ END PREFERENCES ------------------#
################## -- Edit above! -- ##################
    
def main():
    # Loading the comments
    global templateToRemove; global categoryToCheck; global comment; global project_inserted
    if config.mylang not in project_inserted:
        wikipedia.output(u"Your project is not supported by this script. You have to edit the script and add it!")
        wikipedia.stopme()
    # always, define a generator to understand if the user sets one, defining what's genFactory
    always = False; generator = False; genFactory = pagegenerators.GeneratorFactory()
    # To prevent Infinite loops
    errorCount = 0
    # Loading the default options.
    for arg in wikipedia.handleArgs():
        if arg == '-always':
            always = True
        elif arg.startswith('-page'):
            if len(arg) == 5:
                generator = [wikipedia.Page(wikipedia.getSite(), wikipedia.input(u'What page do you want to use?'))]
            else:
                generator = [wikipedia.Page(wikipedia.getSite(), arg[6:])]
        else:
            generator = genFactory.handleArg(arg)
    # Load the right site
    site = wikipedia.getSite()
    # Take the right templates to use, the category and the comment
    TTR = wikipedia.translate(site, templateToRemove)
    category = wikipedia.translate(site, categoryToCheck)
    commentUsed = wikipedia.translate(site, comment)
    if not generator:
        generator = list()
        # Define the category if no other generator has been setted
        for CAT in category:
            cat = catlib.Category(site, CAT)
            # Define the generator
            gen = pagegenerators.CategorizedPageGenerator(cat)
            for pageCat in gen:
                generator.append(pageCat)
    # Main Loop
    for page in generator:
        pagename = page.title()
        wikipedia.output('Loading %s...' % pagename)
        try:
            # The same as .get() but it loads also the editRestriction var, that's what we
            # need to understand if the page is protected or not.
            (text, useless, editRestriction) = page._getEditPage()
        except wikipedia.NoPage:
            wikipedia.output("%s doesn't exist! Skipping..." % pagename)
        except wikipedia.IsRedirectPage:
            wikipedia.output("%s is a redirect! Skipping..." % pagename)
        if editRestriction == 'sysop':
            wikipedia.output(u'The page is protected to the sysop, skipping...')
            continue
        elif editRestriction == 'autoconfirmed':
            wikipedia.output(u'The page is editable only for the autoconfirmed users, skipping...')
            continue
        else:
            wikipedia.output(u'The page is editable for all, deleting the template...')
            # Only to see if the text is the same or not...
            oldtext = text
            # Deleting the template because the page doesn't need it.
            for replaceToPerform in TTR:
                text = re.sub(replaceToPerform, '', text)
            if oldtext != text:
                # Ok, asking if the change has to be performed and do it.
                wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" % page.title())
                wikipedia.showDiff(oldtext, text)
                choice = ''
                while 1:
                    if not always:
                        choice = wikipedia.inputChoice(u'Do you want to accept these changes?', ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
                    if choice.lower() in ['a', 'all']:
                        always = True
                    if choice.lower() in ['n', 'no']:
                        break
                    if choice.lower() in ['y', 'yes'] or always:
                        try:
                            page.put(text, commentUsed)
                        except wikipedia.EditConflict:
                            wikipedia.output(u'Edit conflict! skip!')
                            break
                        except wikipedia.ServerError:
                            # Sometimes there is this error that's quite annoying because
                            # can block the whole process for nothing. 
                            errorCount += 1
                            if errorCount < 5:
                                wikipedia.output(u'Server Error! Wait..')
                                time.sleep(3)
                                continue
                            else:
                                # Prevent Infinite Loops
                                raise wikipedia.ServerError(u'Fifth Server Error!')
                        except wikipedia.SpamfilterError, e:
                            wikipedia.output(u'Cannot change %s because of blacklist entry %s' % (page.title(), e.url))
                            break
                        except wikipedia.PageNotSaved, error:
                            wikipedia.output(u'Error putting page: %s' % (error.args,))
                            break
                        except wikipedia.LockedPage:
                            wikipedia.output(u'The page is still protected. Skipping...')
                            break
                        else:
                            # Break only if the errors are one after the other
                            errorCount = 0
                            break
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
