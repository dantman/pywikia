#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This is a script written to add the template "orphan" to the pages that aren't linked by other pages.
It can give some strange Errors sometime, I hope that all of them are fixed in this version.

These command line parameters can be used to specify which pages to work on:

&params;

-xml              Retrieve information from a local XML dump (pages-articles
                  or pages-meta-current, see http://download.wikimedia.org).
                  Argument can also be given as "-xml:filename".

-page             Only edit a specific page.
                  Argument can also be given as "-page:pagetitle". You can
                  give this parameter multiple times to edit multiple pages.

Furthermore, the following command line parameters are supported:

-enable:            - Enable or disable the bot via a Wiki Page.

-disambig:          - Set a page where the bot save the name of the disambig pages found (default: skip the pages)

-limit:             - Set how many pages check.

-always             - Always say yes, won't ask

--- FixMes ---
* Check that all the code hasn't bugs

--- Credit and Help ---
This Script has been developed by Pietrodn and Filnik on botwiki. If you want to help us
improving our script archive and pywikipediabot's archive or you simply need help
you can find us here: http://botwiki.sno.cc

--- Examples ---
python lonelypages.py -enable:User:Bot/CheckBot -always
"""
#
# (C) Pietrodn, it.wiki 2006-2007
# (C) Filnik, it.wiki 2007
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: lonelypages.py,v 1.0 2007/12/28 19.16.00 filnik Exp$'
#

import wikipedia, pagegenerators
import re

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;':     pagegenerators.parameterHelp,
}

#####################################################
# Here you have to put the config for your Project. #
#####################################################

# ************* Modify only below! ************* #

# Template to add in the orphan pages
Template = {
            'ar':u'{{يتيمة|تاريخ={{نسخ:اسم_شهر}} {{نسخ:عام}}}}',
            'en':u'{{Orphan|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}',
            'it':u'{{O||mese={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}',
            'zh':u'{{subst:Orphan/auto}}',
            }

# Comment that the Bot will use to put the template
commento = {
            'ar':u'بوت: صفحة يتيمة، إضافة قالب',
            'en':u'Bot: Orphan page, add template',
            'it':u'Bot: Voce orfana, aggiungo template {{O}}',
            'zh':u'機器人: 本頁的鏈入頁面太少',
           }

# When you add a disambig to the list of disambig pages
#(if you set disambigPage to None, you can put here nothing)
commenttodisambig = {
           'ar':u'بوت: إضافة صفحة توضيح',
           'en':u'Bot: Adding a disambig page',
           'it':u'Bot: Aggiungo una disambigua',
           'zh':u'機器人: 增加消歧義頁面',
           }

# Use regex to prevent to put the same template twice!
# If you need help with regex, ask on botwiki ( http://botwiki.sno.cc )
# Warning: put always "()" inside the regex, so the bot will find "something"
exception = {
            'ar': [ur'\{\{(?:قالب:|)(يتيمة)[\|\}]'],
            'en': [r'\{\{(?:template:|)(orphan)[\|\}]', r'\{\{(?:template:|)(wi)[\|\}]'],
            'it': [r'\{\{(?:template:|)(o)[\|\}]'],
            'zh': [r'\{\{(?:template:|)(orphan)[\|\}]'],
            }

# ************* Modify only above! ************* #

def main():
    # Load the configurations in the function namespace
    global commento; global Template; global disambigPage; global commenttodisambig
    global exception

    enablePage = None # Check if someone set an enablePage or not
    limit = 50000 # All the pages! (I hope that there aren't so many lonely pages in a project..)
    generator = None # Check if the bot should use the default generator or not
    genFactory = pagegenerators.GeneratorFactory() # Load all the default generators!
    nwpages = False # Check variable for newpages
    always = False # Check variable for always
    disambigPage = None # If no disambigPage given, not use it.
    # Arguments!
    for arg in wikipedia.handleArgs():
        if arg.startswith('-enable'):
            if len(arg) == 7:
                enablePage = wikipedia.input(u'Would you like to check if the bot should run or not?')
            else:
                enablePage = arg[8:]
        if arg.startswith('-disambig'):
            if len(arg) == 9:
                disambigPage = wikipedia.input(u'In which page should the bot save the disambig pages?')
            else:
                disambigPage = arg[10:]
        elif arg.startswith('-limit'):
            if len(arg) == 6:
                limit = int(wikipedia.input(u'How many pages do you want to check?'))
            else:
                limit = int(arg[7:])
        elif arg.startswith('-newpages'):
            if len(arg) == 9:
                nwlimit = 50 # Default: 50 pages
            else:
                nwlimit = int(arg[10:])
            generator = wikipedia.getSite().newpages(number = nwlimit)
            nwpages = True
        elif arg == '-always':
            always = True
        else:
            genFactory.handleArg(arg)
    # Retrive the site
    wikiSite = wikipedia.getSite()

    if not generator:
        generator = genFactory.getCombinedGenerator()

    # If the generator is not given, use the default one
    if not generator:
        generator = wikiSite.lonelypages(repeat = True, number = limit)
    # Take the configurations according to our project
    comment = wikipedia.translate(wikiSite, commento)
    commentdisambig = wikipedia.translate(wikiSite, commenttodisambig)
    template = wikipedia.translate(wikiSite, Template)
    exception = wikipedia.translate(wikiSite, exception)
    # EnablePage part
    if enablePage != None:
        # Define the Page Object
        enable = wikipedia.Page(wikiSite, enablePage)
        # Loading the page's data
        try:
            getenable = enable.get()
        except wikipedia.NoPage:
            wikipedia.output(u"%s doesn't esist, I use the page as if it was blank!" % enable.title())
            getenable = ''
        except wikiepedia.IsRedirect:
            wikipedia.output(u"%s is a redirect, skip!" % enable.title())
            getenable = ''
        # If the enable page is set to disable, turn off the bot
        # (useful when the bot is run on a server)
        if getenable != 'enable':
            wikipedia.output('The bot is disabled')
            return
    # DisambigPage part
    if disambigPage != None:
        disambigpage = wikipedia.Page(wikiSite, disambigPage)
        try:
            disambigtext = disambigpage.get()
        except wikipedia.NoPage:
            wikipedia.output(u"%s doesn't esist, skip!" % disambigpage.title())
            disambigtext = ''
        except wikiepedia.IsRedirect:
            wikipedia.output(u"%s is a redirect, don't use it!" % disambigpage.title())
            disambigPage = None
    # Main Loop
    for page in generator:
        if nwpages == True:
            page = page[0] # The newpages generator returns a tuple, not a Page object.
        wikipedia.output(u"Checking %s..." % page.title())
        # Used to skip the first pages in test phase...
        #if page.title()[0] in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q']:
            #continue
        if page.isRedirectPage(): # If redirect, skip!
            wikipedia.output(u'%s is a redirect! Skip...' % page.title())
            continue
        # refs is not a list, it's a generator while resList... is a list, yes.
        refs = page.getReferences()
        refsList = list()
        for j in refs:
            if j == None:
                # We have to find out why the function returns that value
                wikipedia.output(u'Error: 1 --> Skip page')
                continue
            refsList.append(j)
        # This isn't possible with a generator
        if refsList != []:
            wikipedia.output(u"%s isn't orphan! Skip..." % page.title())
            continue
        # Never understood how a list can turn in "None", but it happened :-S
        elif refsList == None:
            # We have to find out why the function returns that value
            wikipedia.output(u'Error: 2 --> Skip page')
            continue
        else:
            # Ok, no refs, no redirect... let's check if there's already the template
            try:
                oldtxt = page.get()
            except wikipedia.NoPage:
                wikipedia.output(u"%s doesn't exist! Skip..." % page.title())
                continue
            except wikipedia.IsRedirectPage:
                wikipedia.output(u"%s is a redirect! Skip..." % page.title())
                continue
            # I've used a loop in a loop. If I use continue in the second loop, it won't do anything
            # in the first. So let's create a variable to avoid this problem.
            Find = False
            for regexp in exception:
                res = re.findall(regexp, oldtxt.lower())
                # Found a template! Let's skip the page!
                if res != []:
                    wikipedia.output(u'Your regex has found something in %s, skipping...' % page.title())
                    Find = True
                    break
            # Skip the page..
            if Find:
                continue
            # Is the page a disambig?
            if page.isDisambig() and disambigPage != None:
                wikipedia.output(u'%s is a disambig page, report..' % page.title())
                if not page.title().lower() in disambigtext.lower():
                    disambigtext = u"%s\n*[[%s]]" % (disambigtext, page.title())
                    disambigpage.put(disambigtext, commentdisambig)
                    continue
            # Is the page a disambig but there's not disambigPage? Skip!
            elif page.isDisambig():
                 wikipedia.output(u'%s is a disambig page, skip...' % page.title())
                 continue
            else:
                # Ok, the page need the template. Let's put it there!
                newtxt = u"%s\n%s" % (template, oldtxt) # Adding the template in the text
                wikipedia.output(u"\t\t>>> %s <<<" % page.title()) # Showing the title
                wikipedia.showDiff(oldtxt, newtxt) # Showing the changes
                choice = 'y' # Default answer
                if not always:
                    choice = wikipedia.inputChoice(u'Orphan page found, shall I add the template?',  ['Yes', 'No', 'All'], ['y', 'n', 'a'])
                if choice == 'a':
                    always = True
                    choice = 'y'
                if choice == 'y':
                    try:
                        page.put(newtxt, comment)
                    except wikipedia.EditConflict:
                        wikipedia.output(u'Edit Conflict! Skip...')
                        continue
if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()
