# -*- coding: utf8 -*-
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
    'en':'Robot-assisted disambiguation',
    'da':'Retter flertydigt link til',
    'de':'Bot-unterst\xfctzte Begriffskl\xe4rung',
    'nl':'Robot-geholpen doorverwijzing',
    'fr':'Homonymie r\xE9solue \xE0 l\'aide du robot'
    }

# Summary message when run with -redir parameter
msg_redir={
          'en':'Robot-assisted disambiguation',
          'da':'Retter flertydigt link til',
          'de':'Bot-unterst\xfctzte Redirectaufl\xf6sung',
          'nl':'Robot-geholpen doorverwijzing',
          'fr':'Correction de lien vers redirect'
          }

# disambiguation page name format for "primary topic" disambiguations
# (Begriffsklärungen nach Modell 2)
primary_topic_format={
          'de':'%s_(Begriffskl\xe4rung)',
          'en':'%s_(disambiguation)',
          'nl':'%s_(doorverwijspagina)'
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

ignore={
    'nl':('Wikipedia:Onderhoudspagina',
          'Wikipedia:Doorverwijspagina',
          'Wikipedia:Lijst van alle tweeletter-combinaties',
          'Gebruiker:Hooft/robot/Interwiki/lijst van problemen',
          'Wikipedia:Woorden die niet als zoekterm gebruikt kunnen worden',
          'Gebruiker:Puckly/Bijdragen',
          'Gebruiker:Waerth/bijdragen',
          "Wikipedia:Project aanmelding bij startpagina's",
          'Gebruiker:Gustar/aantekeningen denotatie annex connotatie'),
    'en':('Wikipedia:Links to disambiguating pages',
          'Wikipedia:Disambiguation pages with links',
          'Wikipedia:Multiple-place names \([A-Z]\)',
          'Wikipedia:Non-unique personal name',
          "User:Jerzy/Disambiguation Pages i've Editted",
          'User:Gareth Owen/inprogress',
          'TLAs from AAA to DZZ',
          'TLAs from EAA to HZZ',
          'TLAs from IAA to LZZ',
          'TLAs from MAA to PZZ',
          'TLAs from UAA to XZZ',
          'TLAs from YAA to ZZZ',
          'List of all two-letter combinations',
          'User:Daniel Quinlan/redirects.+',
          'User:Oliver Pereira/stuff',
          'Wikipedia:French Wikipedia language links',
          'Wikipedia:Polish language links',
          'Wikipedia:Undisambiguated abbreviations/CIA World Factbook',
          'Wikipedia:Undisambiguated abbreviations/Country codes',
          'Wikipedia:Undisambiguated abbreviations/Currency codes',
          'Wikipedia:Undisambiguated abbreviations/Elements',
          'Wikipedia:Undisambiguated abbreviations/State codes',
          'Wikipedia:Undisambiguated abbreviations/units of measurement',
          'Wikipedia:Undisambiguated abbreviations/file extensions',
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
    'fr':('Wikip\xE9dia:Liens aux pages d\'homonymie',
          'Wikip\xE9dia:Homonymie',
          'Wikip\xE9dia:Homonymie/Homonymes dynastiques',
  'Wikip\xE9dia:Prise de d\xE9cision\x2C noms des membres de dynasties/liste des dynastiens',
  'Liste de toutes les combinaisons de deux lettres',
  'STLs de AAA \xE0 DZZ',
          'STLs de EAA \xE0 HZZ',
          'STLs de IAA \xE0 LZZ',
          'STLs de MAA \xE0 PZZ',
          'STLs de QAA \xE0 TZZ',
  'STLs de UAA \xE0 XZZ',
  'STLs de YAA \xE0 ZZZ',
  'Wikip\xE9dia\x3APages sans interwiki\x2Ca',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cb',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cc',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cd',
  'Wikip\xE9dia\x3APages sans interwiki\x2Ce',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cf',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cg',
  'Wikip\xE9dia\x3APages sans interwiki\x2Ch',
  'Wikip\xE9dia\x3APages sans interwiki\x2Ci',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cj',
  'Wikip\xE9dia\x3APages sans interwiki\x2Ck',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cl',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cm',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cn',
  'Wikip\xE9dia\x3APages sans interwiki\x2Co',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cp',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cq',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cr',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cs',
  'Wikip\xE9dia\x3APages sans interwiki\x2Ct',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cu',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cv',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cw',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cx',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cy',
  'Wikip\xE9dia\x3APages sans interwiki\x2Cz'
  ),
    'de':(
          u'100 Wörter des 21. Jahrhunderts',
          u'Abkürzungen/[A-Z]',
          u'Benutzer\:Tsor/Begriffsklärungen',
          u'Benutzer Diskussion\:.+',
          u'Dreibuchstabenkürzel von [A-Z][A-Z][A-Z] bis [A-Z][A-Z][A-Z]',
          u'GISLexikon \([A-Z]\)',
          u'Lehnwort',
          u'Liste aller 2-Buchstaben-Kombinationen',
          u'Wikipedia:Begriffsklärung.*',
          u'Wikipedia\:Geographisch mehrdeutige Bezeichnungen',
          u'Wikipedia\:Liste mathematischer Themen\/BKS',
          u'Wikipedia\:WikiProjekt Altertumswissenschaft\/.+',
      )
    }



def getReferences(pl):
    x = wikipedia.getReferences(pl)
    # Remove ignorables
    if ignore.has_key(pl.code()):
        ignore_regexes =[]
        for ig in ignore[pl.code()]:
            ignore_regexes.append(re.compile(ig))
        for Rignore in ignore_regexes:
            for i in range(len(x)-1, -1, -1):
                if Rignore.match(x[i]):
                    wikipedia.output('Ignoring page ' + x[i], wikipedia.code2encoding(wikipedia.mylang))
                    del x[i]
    return x

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
            file = wikipedia.input('Please enter the list\'s filename: ')
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
                answer = wikipedia.input('Use it anyway? [y|N] ')
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
    pagename = wikipedia.input('Which page to check: ', encode = True)
    page_list.append(pagename)

for wrd in (page_list):
    # when run with -redir argument, there's another summary message
    if solve_redirect:
        wikipedia.setAction(msg_redir[wikipedia.chooselang(wikipedia.mylang,msg_redir)]+': '+wrd)
    else: 
        wikipedia.setAction(msg[wikipedia.chooselang(wikipedia.mylang,msg)]+': '+wrd)
    
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
            alternatives.append(str(thispl.getRedirectTo()))
        except wikipedia.NoPage:
            print "The specified page was not found."
            user_input = wikipedia.input("Please enter the name of the page where the redirect should have pointed at, or press enter to quit: ")
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
        print "%3d" % i, repr(alternatives[i])
    
    def treat(refpl, thispl):
        try:
            reftxt=refpl.get()
        except wikipedia.IsRedirectPage:
            pass
        else:
            n = 0
            curpos = 0
            while 1:
                m=linkR.search(reftxt, pos = curpos)
                if not m:
                    if n == 0:
                        print "Not found in %s"%refpl
                    elif not debug:
                        refpl.put(reftxt)
                    return True
                # Make sure that next time around we will not find this same hit.
                curpos = m.start() + 1 
                # Try to standardize the page.
                if wikipedia.isInterwikiLink(m.group(1)):
                    linkpl = None
                else:
                    linkpl=wikipedia.PageLink(thispl.code(), m.group(1),
                                              incode = refpl.code())
                # Check whether the link found is to thispl.
                if linkpl != thispl:
                    continue
    
                n += 1
                context = 30
                while 1:
                    print '\n'
                    wikipedia.output("== %s ==" % refpl.name())
                    wikipedia.output(reftxt[max(0,m.start()-context):m.end()+context])
                    if always == None:
                        choice=wikipedia.input("Option (#,r#,s=skip link,n=next page,u=unlink,q=quit,\n"
                                         "        m=more context,l=list,a=add new):")
                    else:
                        choice=always
                    if choice=='n':
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
                    elif choice=='s':
                        choice=-1
                        break
                    elif choice=='u':
                        choice=-2
                        break
                    elif choice=='a':
                        ns=wikipedia.input('New alternative:')
                        alternatives.append(ns)
                    elif choice=='q':
                        return False
                    elif choice=='m':
                        context*=2
                    elif choice=='l':
                        print '\n'
                        for i in range(len(alternatives)):
                            print "%3d" % i,repr(alternatives[i])
                    else:
                        if choice[0] == 'r':
                            replaceit = 1
                            choice = choice[1:]
                        else:
                            replaceit = 0
                        try:
                            choice=int(choice)
                        except ValueError:
                            pass
                        else:
                            break
                if choice==-1:
                    # Next link on this page
                    continue
                page_title = m.group(1)
                link_text = m.group(2)
                if not link_text:
                    link_text = page_title
                trailing_chars = m.group(3)
                if trailing_chars:
                    link_text += trailing_chars
                if choice==-2:
                    # unlink
                    reftxt = reftxt[:m.start()] + link_text + reftxt[m.end():]
                else:
                    # Normal replacement
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
                    if replaceit or new_page_title == link_text:
                        newlink = "[[%s]]" % new_page_title
                    # check if we can create a link with trailing characters instead of a pipelink
                    elif len(new_page_title) <= len(link_text) and link_text[:len(new_page_title)] == new_page_title and re.sub(trailR, '', link_text[len(new_page_title):]) == '':
                        newlink = "[[%s]]%s" % (new_page_title, link_text[len(new_page_title):])
                    else:
                        newlink = "[[%s|%s]]" % (new_page_title, link_text)
                    reftxt = reftxt[:m.start()] + newlink + reftxt[m.end():]
    
                wikipedia.output(reftxt[max(0,m.start()-30):m.end()+30])
            if not debug:
                refpl.put(reftxt)
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
