#!/usr/bin/python
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

   -main       only check pages in the main namespace, not in the talk,
               wikipedia, user, etc. namespaces.

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
import re, sys, math

# This is a purely interactive robot. We set the delays lower.
wikipedia.put_throttle.setDelay(4)

# Summary message when run without -redir parameter
msg={
    'en':u'Robot-assisted disambiguation: %s',
    'da':u'Retter flertydigt link til: %s',
    'de':u'Bot-unterstützte Begriffsklärung: %s',
    'nl':u'Robot-geholpen doorverwijzing: %s',
    'fr':u'Homonymie résolue à l\'aide du robot: %s',
    'pt':u'Desambiguação assistida por bot: %s'
    }

# Summary message when run with -redir parameter
msg_redir={
          'en':u'Robot-assisted disambiguation: %s',
          'da':u'Retter flertydigt link til: %s',
          'de':u'Bot-unterstützte Redirectauflösung: %s',
          'nl':u'Robot-geholpen doorverwijzing: %s',
          'fr':u'Correction de lien vers redirect: %s',
          'pt':u'Desambiguação assistida por bot: %s'
          }

# disambiguation page name format for "primary topic" disambiguations
# (Begriffsklärungen nach Modell 2)
primary_topic_format={
          'de':u'%s_(Begriffsklärung)',
          'en':u'%s_(disambiguation)',
          'nl':u'%s_(doorverwijspagina)',
          'pt':u'%s_(Desambuigração)'
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
   'nl':u'[a-z|ä|ö|ü|ï|ë|é|è|é|à|ç]*',
   'pt':u'[a-z|á|â|à|ã|é|ê|í|ó|ô|õ|ú|ü|ç]*'
   }

# List pages that will be ignored if they got a link to a disambiguation
# page. An example is a page listing disambiguations articles.
# Special chars should be encoded with unicode (\x##) and space used
# instead of _

ignore_title = {
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
          'Gebruiker:Pven/Romeinse cijfers',
          'Categorie:Doorverwijspagina',
          'Wikipedia:Ongelijke redirects',
          'Gebruiker:Cars en travel',
          'Wikipedia:Archief*',
          'Overleg Wikipedia:Logboek*'
          ),
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
    'fr':(u'Wikipédia:Liens aux pages d\'homonymie',
          u'Wikipédia:Homonymie',
          u'Wikipédia:Homonymie/Homonymes dynastiques',
          u'Wikipédia:Prise de décision, noms des membres de dynasties/liste des dynastiens',
          u'Liste de toutes les combinaisons de deux lettres',
          u'STLs de [A-Z]AA à [A-Z]ZZ',
          u'Wikipédia:Pages sans interwiki,.'
          ),
    'de':(
          u'100 Wörter des 21. Jahrhunderts',
          u'Abkürzungen/[A-Z]',
          u'Benutzer:Zwobot/Probleme',
          u'Benutzer:Katharina/Begriffsklärungen',
          u'Benutzer:Tsor/Begriffsklärungen',
          u'Benutzer:SirJective/Klammerzusatz',
          u'Benutzer Diskussion:.+',
          u'GISLexikon \([A-Z]\)',
          u'Lehnwort',
          u'Liste aller 2-Buchstaben-Kombinationen',
          u'Wikipedia:Archiv:.+',
          u'Wikipedia:Artikelwünsche/Ding-Liste/[A-Z]',
          u'Wikipedia:Begriffsklärung.*',
          u'Wikipedia:Dreibuchstabenkürzel von [A-Z][A-Z][A-Z] bis [A-Z][A-Z][A-Z]',
          u'Wikipedia:Geographisch mehrdeutige Bezeichnungen',
          u'Wikipedia:Kurze Artikel',
          u'Wikipedia:Liste mathematischer Themen/BKS',
          u'Wikipedia:Liste mathematischer Themen/Redirects',
          u'Wikipedia:Qualitätsoffensive/UNO', #requested by Benutzer:Addicted 
          u'Wikipedia:WikiProjekt Altertumswissenschaft/.+'
          ),
    'pt':(
          u'Categoria:Desambiguação',
          u'Wikipedia:Links para desambiguar páginas',
          u'Wikipedia:Desambiguação',
          )
    }

class ReferringPageGenerator:
    def __init__(self, disambPl, primary = False):
        self.disambPl = disambPl
        # if run with the -primary argument, enable the ignore manager
        self.primaryIgnoreManager = PrimaryIgnoreManager(disambPl, enabled = primary)
        
    def getReferences(self):
        refs = wikipedia.getReferences(self.disambPl, follow_redirects = False)
        wikipedia.output(u"Found %d references." % len(refs))
        # Remove ignorables
        if ignore_title.has_key(self.disambPl.site().lang):
            ignore_title_regexes = []
            for ig in ignore_title[self.disambPl.site().lang]:
                ig = ig.encode(wikipedia.myencoding())
                ignore_title_regexes.append(re.compile(ig))
            for Rignore in ignore_title_regexes:
                # run backwards because we might remove list items
                for i in range(len(refs)-1, -1, -1):
                    if Rignore.match(refs[i]):
                        wikipedia.output('Ignoring page ' + refs[i], wikipedia.myencoding())
                        del refs[i]
        refpls = []
        for ref in refs:
            refpl = wikipedia.PageLink(self.disambPl.site(), ref)
            if not self.primaryIgnoreManager.isIgnored(refpl):
                refpls.append(refpl)

        wikipedia.output(u"Will work on %d pages." % len(refpls))
        return refpls
    
    def generate(self):
        refpls = self.getReferences()
        while refpls:
            # We don't want to load too many pages at once using XML export.
            # We only get 20 at a time.
            someRefPls = []
            for i in range(0, 20):
                try:
                    someRefPls.append(refpls.pop(0))
                # Nothing left to do?
                except IndexError:
                    break
            try:
                wikipedia.getall(self.disambPl.site(), someRefPls, throttle=False)
            except wikipedia.SaxError:
                # Ignore this error, and get the pages the traditional way later.
                pass
            for refpl in someRefPls:
                yield refpl

class PrimaryIgnoreManager:
    '''
    If run with the -primary argument, reads from a file which pages should
    not be worked on; these are the ones where the user pressed n last time.
    If run without the -primary argument, doesn't ignore any pages.
    '''
    def __init__(self, disambPl, enabled = False):
        self.disambPl = disambPl
        self.enabled = enabled
        
        self.ignorelist = []
        filename = 'disambiguations/' + self.disambPl.urlname() + '.txt'
        try:
            # The file is stored in the disambiguation/ subdir. Create if necessary.
            f = open(self.makepath(filename), 'r')
            for line in f.readlines():
                # remove trailing newlines and carriage returns
                while line[-1] in ['\n', '\r']:
                    line = line[:-1]
                #skip empty lines
                if line != '':
                    self.ignorelist.append(line)
            f.close()
        except IOError:
            pass

    def isIgnored(self, refpl):
        return self.enabled and refpl.urlname() in self.ignorelist
        
    def ignore(self, refpl):
        if self.enabled:
            # Skip this occurence next time.
            filename = 'disambiguations/' + self.disambPl.urlname() + '.txt'
            try:
                # Open file for appending. If none exists yet, create a new one.
                # The file is stored in the disambiguation/ subdir. Create if necessary.
                f = open(self.makepath(filename), 'a')
                f.write(refpl.urlname() + '\n')
                f.close()
            except IOError:
                pass

    def makepath(self, path):
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
    

class DisambiguationRobot:
    ignore_contents = {
        'de':(u'{{[Ii]nuse}}',
              u'{{[Ll]öschen}}',
            )
    }
    
    def __init__(self, always, alternatives, getAlternatives, solve_redirect, page_list, primary, main_only):
        self.always = always
        self.alternatives = alternatives
        self.getAlternatives = getAlternatives
        self.solve_redirect = solve_redirect
        self.page_list = page_list
        self.primary = primary
        self.main_only = main_only

        self.mysite = wikipedia.getSite()
        self.mylang = self.mysite.language()

        # compile regular expressions
        self.ignore_contents_regexes = []
        if self.ignore_contents.has_key(self.mylang):
            for ig in self.ignore_contents[self.mylang]:
                self.ignore_contents_regexes.append(re.compile(ig))
        
    def checkContents(self, text):
        '''
        For a given text, returns False if none of the regular
        expressions given in the dictionary at the top of this class
        matches a substring of the text.
        Otherwise returns the substring which is matched by one of
        the regular expressions.
        '''
        for ig in self.ignore_contents_regexes:
            match = ig.search(text)
            if match:
                return match.group()
        return None
    
    def makeAlternativesUnique(self):
        # remove duplicate entries
        result={}
        for i in self.alternatives:
            result[i]=None
        self.alternatives = result.keys()
    
    
    def listAlternatives(self):
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
        for i in range(len(self.alternatives)):
            wikipedia.output(u"%3d - %s" % (i, self.alternatives[i]))
    
    def treat(self, refpl, disambPl):
        """
        Parameters:
            disambPl - The disambiguation page or redirect we don't want anything
                     to link on
            refpl - A page linking to disambPl
        Returns False if the user pressed q to completely quit the program.
        Otherwise, returns True.
        """
        if self.mylang in link_trail:
            linktrail=link_trail[self.mylang]
        else:
            linktrail='[a-z]*'
        trailR=re.compile(linktrail)
        # The regular expression which finds links. Results consist of three groups:
        # group(1) is the target page title, that is, everything before | or ].
        # group(2) is the alternative link title, that's everything between | and ].
        # group(3) is the link trail, that's letters after ]] which are part of the word.
        # note that the definition of 'letter' varies from language to language.
        linkR=re.compile(r'\[\[([^\]\|]*)(?:\|([^\]]*))?\]\](' + linktrail + ')')

        include = False
        try:
            text=refpl.get(throttle=False)
            ignoreReason = self.checkContents(text)
            if ignoreReason:
                wikipedia.output('\n\nSkipping %s because it contains %s.\n\n' % (refpl.linkname(), ignoreReason))
            else:
                include = True
        except wikipedia.IsRedirectPage:
            wikipedia.output(u'%s is a redirect to %s' % (refpl.linkname(), disambPl.linkname()))
            if self.solve_redirect:
                choice = wikipedia.input(u'Do you want to make redirect %s point to %s? [y|N]' % (refpl.linkname(), target))
                if choice2 == 'y':
                    redir_text = '#REDIRECT [[%s]]' % target
                    refpl.put(redir_text)
            else:
                choice = wikipedia.input(u'Do you want to work on pages linking to %s? [y|N|c(hange redirect)]' % refpl.linkname())
                if choice == 'y':
                    gen = ReferringPageGenerator(refpl, self.primary)
                    for refpl2 in gen.generate():
                        # run until the user selected 'quit'
                        if not self.treat(refpl2, refpl):
                            break
                elif choice == 'c':
                    text="#%s [[%s]]"%(self.mysite.redirect(default=True), disambPl.linkname())
                    include = "redirect"
        if include in [True,"redirect"]:
            # make a backup of the original text so we can show the changes later
            original_text=text
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
                    linkpl=wikipedia.PageLink(disambPl.site(), m.group(1))
                # Check whether the link found is to disambPl.
                if linkpl != disambPl:
                    continue
    
                n += 1
                # how many bytes should be displayed around the current link
                context = 30
                # This loop will run while the user doesn't choose an option
                # that will actually change the page
                while True:
                    print '\n'
                    wikipedia.output(u">>> %s <<<" % refpl.linkname())
                    # at the beginning of the link, start red color.
                    # at the end of the link, reset the color to default
                    displayedText = text[max(0, m.start() - context):m.start()] + wikipedia.colorize(text[m.start():m.end()], '91') + text[m.end():m.end()+context]
                    wikipedia.output(displayedText)
                    if not self.always:
                        if edited:
                            choice=wikipedia.input(u"Option (#, r#, s=skip link, e=edit page, n=next page, u=unlink,\n"
                                               "        q=quit, m=more context, l=list, a=add new, x=save in this form):")
                        else:
                            choice=wikipedia.input(u"Option (#, r#, s=skip link, e=edit page, n=next page, u=unlink,\n"
                                               "        q=quit, m=more context, l=list, a=add new):")
                    else:
                        choice = self.always
                    if choice=='a':
                        newAlternative = wikipedia.input(u'New alternative:')
                        self.alternatives.append(newAlternative)
                        self.listAlternatives()
                    elif choice=='e':
                        import gui
                        edit_window = gui.EditBoxWindow()
                        newtxt = edit_window.edit(text)
                        # if user didn't press Cancel
                        if newtxt:
                            text = newtxt
                            break
                    elif choice=='l':
                        self.listAlternatives()
                    elif choice=='m':
                        # show more text around the link we're working on
                        context*=2
                    else:
                        break
            
                if choice == 'e':
                    # user has edited the page and then pressed 'OK'
                    edited = True
                    curpos = 0
                    continue
                elif choice == 'n':
                    # skip this page
                    if self.primary:
                        # If run with the -primary argument, skip this occurence next time.
                        self.primaryIgnoreManager.ignore(refpl)
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
                    elif include == "redirect":
                        replaceit = 1
                    else:
                        replaceit = 0
    
                    try:
                        choice=int(choice)
                    except ValueError:
                        print '\nUnknown option'
                        # step back to ask the user again what to do with the current link
                        curpos -= 1
                        continue
                    if choice >= len(self.alternatives) or choice < 0:
                        print '\nChoice out of range. Please select a number between 0 and %d.' % (len(self.alternatives) - 1)
                        # show list of possible choices
                        self.listAlternatives()
                        # step back to ask the user again what to do with the current link
                        curpos -= 1
                        continue
                    new_page_title = self.alternatives[choice]
                    reppl = wikipedia.PageLink(disambPl.site(), new_page_title)
                    new_page_title = reppl.linkname()
                    # There is a function that uncapitalizes the link target's first letter
                    # if the link description starts with a small letter. This is useful on
                    # nl: but annoying on de:.
                    # At the moment the de: exclusion is only a workaround because I don't
                    # know if other languages don't want this feature either.
                    # We might want to introduce a list of languages that don't want to use
                    # this feature.
                    if self.mylang != 'de' and link_text[0] in 'abcdefghijklmnopqrstuvwxyz':
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
            print '\nThe following changes have been made:\n'
            wikipedia.showColorDiff(original_text, text)
            print ''
            # save the page
            refpl.put(text)
        return True
    
    
    def run(self):
        if self.main_only:
            if ignore_title.has_key(self.mylang):
                ignore_title[self.mylang] += self.mysite.namespaces()
            else:
                ignore_title[self.mylang] = self.mysite.namespaces()
    
        for disambTitle in self.page_list:
            # when run with -redir argument, there's another summary message
            if self.solve_redirect:
                wikipedia.setAction(wikipedia.translate(self.mysite,msg_redir) % disambTitle)
            else:
                wikipedia.setAction(wikipedia.translate(self.mysite,msg) % disambTitle)
    
            disambPl = wikipedia.PageLink(self.mysite, disambTitle)
            
            self.primaryIgnoreManager = PrimaryIgnoreManager(disambPl, enabled = self.primary)
    
            if self.solve_redirect:
                try:
                    target = disambPl.getRedirectTo()
                    target = unicode(target, wikipedia.myencoding()) 
                    self.alternatives.append(target)
                except wikipedia.NoPage:
                    print "The specified page was not found."
                    user_input = wikipedia.input(u"Please enter the name of the page where the redirect should have pointed at, or press enter to quit:")
                    if user_input == "":
                        sys.exit(1)
                    else:
                        self.alternatives.append(user_input)
                except wikipedia.IsNotRedirectPage:
                    print "The specified page is not a redirect."
                    sys.exit(1)
            elif self.getAlternatives:
                try:
                    if self.primary:
                        disamb_pl = wikipedia.PageLink(self.mysite, primary_topic_format[self.mylang] % disambTitle)
                        thistxt = disamb_pl.get(throttle=False)
                    else:
                        thistxt = disambPl.get(throttle=False)
                except wikipedia.IsRedirectPage,arg:
                    thistxt = wikipedia.PageLink(self.mysite, str(arg)).get(throttle=False)
                except wikipedia.NoPage:
                    print "Page does not exist?!"
                    thistxt = ""
                thistxt = wikipedia.removeLanguageLinks(thistxt)
                thistxt = wikipedia.removeCategoryLinks(thistxt, self.mysite)
                # regular expression matching a wikilink
                w = r'([^\]\|]*)'
                Rlink = re.compile(r'\[\['+w+r'(\|'+w+r')?\]\]')
                for matchObj in Rlink.findall(thistxt):
                    self.alternatives.append(matchObj[0])
    
            self.makeAlternativesUnique()
            # sort possible choices
            self.alternatives.sort()
            self.listAlternatives()
    
            gen = ReferringPageGenerator(disambPl, self.primary)
            for refpl in gen.generate():
                if not self.primaryIgnoreManager.isIgnored(refpl):
                    # run until the user selected 'quit'
                    if not self.treat(refpl, disambPl):
                        break
    
            # clear alternatives before working on next disambiguation page
            self.alternatives = []

def main():
    # the option that's always selected when the bot wonders what to do with
    # a link. If it's None, the user is prompted (default behaviour).
    always = None
    alternatives = []
    getAlternatives = True
    solve_redirect = False
    # if the -file argument is used, page titles are dumped in this array.
    # otherwise it will only contain one page.
    page_list = []
    # if -file is not used, this temporary array is used to read the page title.
    page_title = []
    primary = False
    main_only = False

    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg)
        if arg:
            if arg.startswith('-primary:'):
                primary = True
                getAlternatives = False
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
                    mysite = wikipedia.getSite()
                    pl=wikipedia.PageLink(mysite, arg[5:])
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
                getAlternatives = False
            elif arg=='-redir':
                solve_redirect = True
            elif arg=='-main':
                main_only = True
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
                
    bot = DisambiguationRobot(always, alternatives, getAlternatives, solve_redirect, page_list, primary, main_only)
    bot.run()

            
try:
    main()
except:
    wikipedia.stopme()
    raise
else:
    wikipedia.stopme()
