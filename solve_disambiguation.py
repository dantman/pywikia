# -*- coding: utf-8 -*-
"""
Script to help a human solve disambiguations by presenting a set of options.

Specify the disambiguation page on the command line. The program will
pick up the page, and look for all alternative links, and show them with
a number adjacent to them. It will then automatically loop over all pages
referring to the disambiguation page, and show 30 characters on each side
of the reference to help you make the decision between the
alternatives. It will ask you to type the number of the appropriate
replacement, and perform the change robotically.

It is possible to choose to replace only the link (just type the number) or
replace both link and link-text (type 'r' followed by the number).

Multiple references in one page will be scanned in order, but typing 'n' on
any one of them will leave the complete page unchanged; it is not possible to
leave only one reference unchanged.

Command line options:

   -pos:XXXX adds XXXX as an alternative disambiguation

   -just       only use the alternatives given on the command line, do not
               read the page for other possibilities

   -redir      if the page is a redirect page, use the page redirected to as
               the (only) alternative; if not set, the pages linked to from
               the page redirected to are used. If the page is not a redirect
               page, this will raise an error

   -primary    "primary topic" disambiguation (Begriffsklärung nach Modell 2).
               That's titles where one topic is much more important, the
               disambiguation page is saved somewhere else, and the important
               topic gets the nice name.

   -primary:XY like the above, but use XY as the only alternative, instead of
               searching for alternatives in [[Keyword (disambiguation)]].
               Note: this is the same as -primary -just -pos:XY

   -file:XYZ   reads a list of pages, which can for example be gotten through
               extract_names.py. XYZ is the name of the file from which the
               list is taken. If XYZ is not given, the user is asked for a
               filename.
               Page titles should be saved one per line, without [[brackets]].
               The -pos parameter won't work if -file is used.

   -always:XY  instead of asking the user what to do, always perform the same
               action. For example, XY can be "r0", "u" or "2". Be careful with
               this option, and check the changes made by the bot. Note that
               some choices for XY don't make sense and will result in a loop,
               e.g. "l" or "m".

Options that are accepted by more robots:

   -lang:XX  set your home wikipedia to XX instead of the one given in
             username.dat

To complete a move of a page, one can use:

    python solve_disambiguation.py -just -pos:New_Name Old_Name
"""
#
# (C) Rob W.W. Hooft, 2003
# (C) Daniel Herding, 2004
# (C) Andre Engels, 2003-2004
# (C) WikiWichtel, 2004
#
# Distribute under the terms of the PSF license.
#
__version__='$Id$'
#
import wikipedia, config
import re,sys

# This is a purely interactive robot. We set the delays lower.
wikipedia.get_throttle.setDelay(5)
wikipedia.put_throttle.setDelay(10)

# Summary message when run without -redir parameter
msg={
    'en':u'Robot-assisted disambiguation: %s',
    'da':u'Retter flertydigt link til: %s',
    'de':u'Bot-unterstützte Begriffsklärung: %s',
    'nl':u'Robot-geholpen doorverwijzing: %s',
    'fr':u'Homonymie résolue à l\'aide du robot: %s'
    }

# Summary message when run with -redir parameter
msg_redir={
          'en':u'Robot-assisted disambiguation: %s',
          'da':u'Retter flertydigt link til: %s',
          'de':u'Bot-unterstützte Redirectauflösung: %s',
          'nl':u'Robot-geholpen doorverwijzing: %s',
          'fr':u'Correction de lien vers redirect: %s'
          }

# disambiguation page name format for "primary topic" disambiguations
# (Begriffsklärungen nach Modell 2)
primary_topic_format={
          'de':u'%s_(Begriffsklärung)',
          'en':u'%s_(disambiguation)',
          'nl':u'%s_(doorverwijspagina)'
          }

# letters that can follow a link and are regarded as part of this link
# This depends on the linktrail setting in LanguageXx.php.
# See http://meta.wikipedia.org/wiki/Locales_for_the_Wikipedia_Software
# to find out the setting for your Wikipedia.
# Note: this is a regular expression.
link_trail={
   'de':u'[a-z|ä|ö|ü|ß]*',
   'da':u'[a-z|æ|ø|å]*',
   'en':u'[a-z]*',
   'fr':u'[a-z|à|â|ç|é|è|ê|î|ô|û]*',
   'nl':u'[a-z|ä|ö|ü|ï|ë|é|è|é|à|ç]*'
   }

# List pages that will be ignored if they got a link to a disambiguation
# page. An example is a page listing disambiguations articles.
# Special chars should be encoded with unicode (\x##) and space used
# instead of _

# TODO: convert everything to regular exceptions (only de: done yet, will crash)
ignore={
    'nl':('Wikipedia:Onderhoudspagina',
          'Wikipedia:Doorverwijspagina',
          'Wikipedia:Lijst van alle tweeletter-combinaties',
          'Gebruiker:Hooft/robot/Interwiki/lijst van problemen',
          'Wikipedia:Woorden die niet als zoekterm gebruikt kunnen worden',
          'Gebruiker:Puckly/Bijdragen',
          'Gebruiker:Waerth/bijdragen',
          "Wikipedia:Project aanmelding bij startpagina's",
          'Gebruiker:Gustar/aantekeningen denotatie annex connotatie',
          'Wikipedia:Protection log',
          'Gebruiker:Pven/Romeinse cijfers'),
     'en':('Wikipedia:Links to disambiguating pages',
          'Wikipedia:Disambiguation pages with links',
          'Wikipedia:Multiple-place names \([A-Z]\)',
          'Wikipedia:Non-unique personal name',
          "User:Jerzy/Disambiguation Pages i've Editted",
          'User:Gareth Owen/inprogress',
          'TLAs from [A-Z][A-Z][A-Z] to [A-Z][A-Z][A-Z]',
          'List of all two-letter combinations',
          'User:Daniel Quinlan/redirects.+',
          'User:Oliver Pereira/stuff',
          'Wikipedia:French Wikipedia language links',
          'Wikipedia:Polish language links',
          'Wikipedia:Undisambiguated abbreviations/.+',
          'List of acronyms and initialisms',
          'Wikipedia:Usemod article histories',
          'User:Pizza Puzzle/stuff',
          'List of generic names of political parties',
          'Talk:List of initialisms/marked',
          'Talk:List of initialisms/sorted',
          'Talk:Programming language',
          'Talk:SAMPA/To do',
          "Wikipedia:Outline of Roget's Thesaurus",
          'User:Wik/Articles',
          'User:Egil/Sandbox',
          'Wikipedia talk:Make only links relevant to the context',
          'Wikipedia:Common words, searching for which is not possible'
      ),
    'da':('Wikipedia:Links til sider med flertydige titler'),
    'fr':('Wikip�dia:Liens aux pages d\'homonymie',
          'Wikip�dia:Homonymie',
          'Wikip�dia:Homonymie/Homonymes dynastiques',
          'Wikip�dia:Prise de d�cision, noms des membres de dynasties/liste des dynastiens',
          'Liste de toutes les combinaisons de deux lettres',
          'STLs de [A-Z]AA � [A-Z]ZZ',
          'Wikip�dia:Pages sans interwiki,.',
          ),
    'de':(
          u'100 Wörter des 21. Jahrhunderts',
          u'Abkürzungen/[A-Z]',
          u'Benutzer:Zwobot/Probleme',
          u'Benutzer:Katharina/Begriffsklärungen',
          u'Benutzer:Tsor/Begriffsklärungen',
          u'Benutzer Diskussion:.+',
          u'Dreibuchstabenkürzel von [A-Z][A-Z][A-Z] bis [A-Z][A-Z][A-Z]',
          u'GISLexikon \([A-Z]\)',
          u'Lehnwort',
          u'Liste aller 2-Buchstaben-Kombinationen',
          u'Wikipedia:Archiv:.+',
          u'Wikipedia:Begriffsklärung.*',
          u'Wikipedia:Artikelwünsche/Ding-Liste/[A-Z]',
          u'Wikipedia:Geographisch mehrdeutige Bezeichnungen',
          u'Wikipedia:Liste mathematischer Themen/BKS',
          u'Wikipedia:WikiProjekt Altertumswissenschaft/.+',
      )
    }



def getReferences(pl):
    refs = wikipedia.getReferences(pl, follow_redirects = False)
    print "Found %d references" % len(refs)
    # Remove ignorables
    if ignore.has_key(pl.code()):
        ignore_regexes =[]
        for ig in ignore[pl.code()]:
            ig = ig.encode(wikipedia.myencoding())
            ignore_regexes.append(re.compile(ig))
        for Rignore in ignore_regexes:
            for i in range(len(refs)-1, -1, -1):
                if Rignore.match(refs[i]):
                    wikipedia.output('Ignoring page ' + refs[i], wikipedia.myencoding())
                    del refs[i]
    return refs

def unique(list):
    # remove duplicate entries
    result={}
    for i in list:
        result[i]=None
    return result.keys()


def makepath(path):
    """ creates missing directories for the given path and
        returns a normalized absolute version of the path.

    - if the given path already exists in the filesystem
      the filesystem is not modified.

    - otherwise makepath creates directories along the given path
      using the dirname() of the path. You may append
      a '/' to the path if you want it to be a directory path.

    from holger@trillke.net 2002/03/18
    """
    from os import makedirs
    from os.path import normpath,dirname,exists,abspath

    dpath = normpath(dirname(path))
    if not exists(dpath): makedirs(dpath)
    return normpath(abspath(path))

# the option that's always selected when the bot wonders what to do with
# a link. If it's None, the user is prompted (default behaviour).
always = None
alternatives = []
getalternatives = 1
debug = 0
solve_redirect = 0
# if the -file argument is used, page titles are dumped in this array.
# otherwise it will only contain one page.
page_list = []
# if -file is not used, this temporary array is used to read the page title.
page_title = []
primary = False

for arg in sys.argv[1:]:
    arg = unicode(arg, config.console_encoding)
    if wikipedia.argHandler(arg):
        pass
    elif arg.startswith('-primary:'):
        primary = True
        getalternatives=0
        alternatives.append(arg[9:])
    elif arg == '-primary':
        primary = True
    elif arg.startswith('-always:'):
        always = arg[8:]
    elif arg.startswith('-file'):
        if len(arg) == 5:
            # todo: check for console encoding to allow special characters
            # in filenames, as done below with pagename
            file = wikipedia.input(u'Please enter the list\'s filename:')
        else:
            file = arg[6:]
        # open file and read page titles out of it
        f=open(file)
        for line in f.readlines():
            if line != '\n':
                page_list.append(line)
        f.close()
    elif arg.startswith('-pos:'):
        if arg[5]!=':':
            pl=wikipedia.PageLink(wikipedia.mylang,arg[5:])
            if pl.exists():
                alternatives.append(pl.linkname())
            else:
                print "Possibility does not actually exist:",pl
                answer = wikipedia.input(u'Use it anyway? [y|N]')
                if answer in ('Y', 'y'):
                    alternatives.append(pl.linkname())
        else:
            alternatives.append(arg[5:])
    elif arg=='-just':
        getalternatives=0
    elif arg=='-redir':
        solve_redirect=1
    else:
        page_title.append(arg)

# if the disambiguation page is given as a command line argument,
# connect the title's parts with spaces
if page_title != []:
     page_title = ' '.join(page_title)
     page_list.append(page_title)

# if no disambiguation pages was given as an argument, and none was
# read from a file, query the user
if page_list == []:
    pagename = wikipedia.input(u'Which page to check:')
    page_list.append(pagename)

for wrd in (page_list):
    # when run with -redir argument, there's another summary message
    if solve_redirect:
        wikipedia.setAction(wikipedia.translate(wikipedia.mylang,msg_redir) % wrd)
    else:
        wikipedia.setAction(wikipedia.translate(wikipedia.mylang,msg) % wrd)

    thispl = wikipedia.PageLink(wikipedia.mylang, wrd)

    # If run with the -primary argument, read from a file which pages should
    # not be worked on; these are the ones where the user pressed n last time.
    # If run without the -primary argument, don't ignore any pages.
    skip_primary = []
    filename = 'disambiguations/' + thispl.urlname() + '.txt'
    try:
        # The file is stored in the disambiguation/ subdir. Create if necessary.
        f = open(makepath(filename), 'r')
        for line in f.readlines():
            # remove trailing newlines and carriage returns
            while line[-1] in ['\n', '\r']:
                line = line[:-1]
            #skip empty lines
            if line != '':
                skip_primary.append(line)
        f.close()
    except IOError:
        pass

    if solve_redirect:
        try:
            target = thispl.getRedirectTo()
            target = unicode(target, wikipedia.myencoding()) 
            alternatives.append(target)
        except wikipedia.NoPage:
            print "The specified page was not found."
            user_input = wikipedia.input(u"Please enter the name of the page where the redirect should have pointed at, or press enter to quit:")
            if user_input == "":
                sys.exit(1)
            else:
                alternatives.append(user_input)
        except wikipedia.IsNotRedirectPage:
            print "The specified page is not a redirect."
            sys.exit(1)
    elif getalternatives:
        try:
            if primary:
                disamb_pl = wikipedia.PageLink(wikipedia.mylang, primary_topic_format[wikipedia.mylang] % wrd)
                thistxt = disamb_pl.get()
            else:
                thistxt = thispl.get()
        except wikipedia.IsRedirectPage,arg:
            thistxt = wikipedia.PageLink(wikipedia.mylang, str(arg)).get()
        thistxt = wikipedia.removeLanguageLinks(thistxt)
        thistxt = wikipedia.removeCategoryLinks(thistxt, wikipedia.mylang)
        w=r'([^\]\|]*)'
        Rlink = re.compile(r'\[\['+w+r'(\|'+w+r')?\]\]')
        for a in Rlink.findall(thistxt):
            alternatives.append(a[0])

    alternatives = unique(alternatives)
    # sort possible choices
    alternatives.sort()

    # print choices on screen
    for i in range(len(alternatives)):
        wikipedia.output(u"%3d - %s" % (i, alternatives[i]))
    
    def treat(refpl, thispl):
        '''
        Parameters:
            thispl - The disambiguation page or redirect we don't want anything
                     to link on
            refpl - A page linking to thispl
        Returns False if the user pressed q to completely quit the program.
        Otherwise, returns True.
        '''
        try:
            text=refpl.get()
            # make a backup of the original text so we can show the changes later
            original_text = text
        except wikipedia.IsRedirectPage:
            wikipedia.output(u'%s is a redirect to %s' % (refpl.linkname(), thispl.linkname()))
            choice = wikipedia.input(u'Do you want to work on pages linking to %s? [y|N]' % refpl.linkname())
            if choice == 'y':
                for ref_redir in getReferences(refpl):
                    refpl_redir=wikipedia.PageLink(wikipedia.mylang, ref_redir)
                    treat(refpl_redir, refpl)
                if solve_redirect:
                    choice2 = wikipedia.input(u'Do you want to make redirect %s point to %s? [y|N]' % (refpl.linkname(), target))
                    if choice2 == 'y':
                        redir_text = '#REDIRECT [[%s]]' % target
                        refpl.put(redir_text)
        else:
            n = 0
            curpos = 0
            edited = False
            # This loop will run until we have finished the current page
            while True:
                m=linkR.search(text, pos = curpos)
                if not m:
                    if n == 0:
                        wikipedia.output(u"No changes necessary in %s" % refpl.linkname())
                        return True
                    else:
                        # stop loop and save page
                        break
                # Make sure that next time around we will not find this same hit.
                curpos = m.start() + 1
                # Try to standardize the page.
                if wikipedia.isInterwikiLink(m.group(1)):
                    continue
                else:
                    linkpl=wikipedia.PageLink(thispl.code(), m.group(1),
                                              incode = refpl.code())
                # Check whether the link found is to thispl.
                if linkpl != thispl:
                    continue

                n += 1
                context = 30
                # This loop will run while the user doesn't choose an option
                # that will actually change the page
                while True:
                    print '\n'
                    wikipedia.output(u"== %s ==" % refpl.linkname())
                    wikipedia.output(text[max(0, m.start() - context):m.end()+context])
                    if always == None:
                        if edited:
                            choice=wikipedia.input(u"Option (#, r#, s=skip link, e=edit page, n=next page, u=unlink,\n"
                                               "        q=quit, m=more context, l=list, a=add new, x=save in this form):")
                        else:
                            choice=wikipedia.input(u"Option (#, r#, s=skip link, e=edit page, n=next page, u=unlink,\n"
                                               "        q=quit, m=more context, l=list, a=add new):")
                    else:
                        choice=always
                    if choice=='a':
                        ns=wikipedia.input(u'New alternative:')
                        alternatives.append(ns)
                    elif choice=='e':
                        import gui
                        edit_window = gui.EditBoxWindow()
                        newtxt = edit_window.edit(text)
                        # if user didn't press Cancel
                        if newtxt:
                            text = newtxt
                            break
                    elif choice=='m':
                        # show more text around the link we're working on
                        context*=2
                    elif choice=='l':
                        #########
                        # The GUI for the list is disabled because it doesn't
                        # work exactly as expected.
                        #########
                        #list in new window
                        #print '\n\t\t--> beachte neues Fenster <--'
                        #import gui
                        #list_window = gui.ListBoxWindow()
                        #mylist = list_window.list(alternatives)
                        ##########
                        print '\n'
                        for i in range(len(alternatives)):
                            wikipedia.output("%3d - %s" % (i, alternatives[i]))
                    else:
                        break
                
                if choice == 'e':
                    # user has edited the page and then pressed 'OK'
                    edited = True
                    curpos = 0
                    continue
                elif choice == 'n':
                    # skip this page
                    if primary:
                        # If run with the -primary argument, skip this occurence next time.
                        filename = 'disambiguations/' + thispl.urlname() + '.txt'
                        try:
                            # Open file for appending. If none exists yet, create a new one.
                            # The file is stored in the disambiguation/ subdir. Create if necessary.
                            f = open(makepath(filename), 'a')
                            f.write(refpl.urlname() + '\n')
                            f.close()
                        except IOError:
                            pass
                    return True
                elif choice=='q':
                    # quit the program
                    return False
                elif choice=='s':
                    # Next link on this page
                    n -= 1
                    continue
                elif choice=='x' and edited:
                    # Save the page as is
                    break

                # The link looks like this:
                # [[page_title|link_text]]trailing_chars
                page_title = m.group(1)
                link_text = m.group(2)

                if not link_text:
                    # or like this: [[page_title]]trailing_chars
                    link_text = page_title
                trailing_chars = m.group(3)
                if trailing_chars:
                    link_text += trailing_chars

                if choice=='u':
                    # unlink
                    text = text[:m.start()] + link_text + text[m.end():]
                    continue
                else:
                    if len(choice)>0 and choice[0] == 'r':
                    # we want to throw away the original link text
                        replaceit = 1
                        choice = choice[1:]
                    else:
                        replaceit = 0

                    try:
                        choice=int(choice)
                    except ValueError:
                        print '\nUnknown option'
                        continue
                    new_page_title = alternatives[choice]
                    reppl = wikipedia.PageLink(thispl.code(), new_page_title,
                                               incode = refpl.code())
                    new_page_title = reppl.linkname()
                    # There is a function that uncapitalizes the link target's first letter
                    # if the link description starts with a small letter. This is useful on
                    # nl: but annoying on de:.
                    # At the moment the de: exclusion is only a workaround because I don't
                    # know if other languages don't want this feature either.
                    # We might want to introduce a list of languages that don't want to use
                    # this feature.
                    if wikipedia.mylang != 'de' and link_text[0] in 'abcdefghijklmnopqrstuvwxyz':
                        new_page_title = new_page_title[0].lower() + new_page_title[1:]
                    if replaceit and trailing_chars: 
                        newlink = "[[%s]]%s" % (new_page_title, trailing_chars)
                    elif new_page_title == link_text or replaceit:
                        newlink = "[[%s]]" % new_page_title
                    # check if we can create a link with trailing characters instead of a pipelink
                    elif len(new_page_title) <= len(link_text) and link_text[:len(new_page_title)] == new_page_title and re.sub(trailR, '', link_text[len(new_page_title):]) == '':
                        newlink = "[[%s]]%s" % (new_page_title, link_text[len(new_page_title):])
                    else:
                        newlink = "[[%s|%s]]" % (new_page_title, link_text)
                    text = text[:m.start()] + newlink + text[m.end():]
                    continue

                wikipedia.output(text[max(0,m.start()-30):m.end()+30])
            if not debug:
                print '\nThe following changes have been made:\n'
                wikipedia.showDiff(original_text, text)
                print ''
                # save the page
                refpl.put(text)
        return True

    if wikipedia.mylang in link_trail:
        linktrail=link_trail[wikipedia.mylang]
    else:
        linktrail='[a-z]*'
    trailR=re.compile(linktrail)

    # The regular expression which finds links. Results consist of three groups:
    # group(1) is the target page title, that is, everything before | or ].
    # group(2) is the alternative link title, that's everything between | and ].
    # group(3) is the link trail, that's letters after ]] which are part of the word.
    # note that the definition of 'letter' varies from language to language.
    linkR=re.compile(r'\[\[([^\]\|]*)(?:\|([^\]]*))?\]\](' + linktrail + ')')

    def resafe(s):
        s=s.replace('(','\\(')
        s=s.replace(')','\\)')
        return s

    active=True

    for ref in getReferences(thispl):
        refpl=wikipedia.PageLink(wikipedia.mylang, ref)
        if active and not refpl.urlname() in skip_primary:
            if not treat(refpl, thispl):
                active=False

    # clear alternatives before working on next disambiguation page
    alternatives = []
