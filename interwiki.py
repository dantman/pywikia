#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Script to check language links for general pages. This works by downloading the
page, and using existing translations plus hints from the command line to
download the equivalent pages from other languages. All of such pages are
downloaded as well and checked for interwiki links recursively until there are
no more links that are encountered. A rationalization process then selects the
right interwiki links, and if this is unambiguous, the interwiki links in the
original page will be automatically updated and the modified page uploaded.

This script understands various command-line arguments:
    -force:        do not ask permission to make "controversial" changes,
                   like removing a language because none of the found
                   alternatives actually exists.

    -always:       make changes even when a single byte is changed in
                   the page, not only when one of the links has a significant
                   change.

    -hint:         used as -hint:de:Anweisung to give the robot a hint
                   where to start looking for translations. This is only
                   useful if you specify a single page to work on. If no
                   text is given after the second ':', the name of the page
                   itself is used as the title for the hint.

    There are some special hints, trying a number of languages at once:
    all:    Provides the hint for all languages with at least ca. 100 pages
    10:     Provides the hint for ca. 10 of the largest languages
    20:, 30:, 50: Analogous to 10: with ca. 20, 30 and 50 languages 
    cyril:  Provides the hint for all languages that use the cyrillic alphabet

    -cat           Work on all pages which are in a specific category.
                   Argument can also be given as "-cat:categoryname".

    -ref           Work on all pages that link to a certain page.
                   Argument can also be given as "-ref:referredpagetitle".

    -link          Work on all pages that are linked from a certain page.
                   Argument can also be given as "-link:linkingpagetitle".

    -new           Work on the most recent new pages on the wiki

    -subcat        When the pages to work on have been chosen by -cat, pages in
                   subcategories of the selected category are also included.
                   When -cat has not been selected, this has no effect.
    
    -same:         looks over all 'serious' languages for the same title.
                   -same is equivalent to -hint:all:

    -wiktionary:   similar to -same, but will ONLY accept names that are
                   identical to the original. Also, if the title is not
                   capitalized, it will only go through other wikis without
                   automatic capitalization.
                   
    -askhints:     for each page one or more hints are asked. See hint: above
                   for the format, one can for example give "en:something" or
                   "20:" as hint.

    -untranslated: works normally on pages with at least one interlanguage
                   link; asks hints for pages that have none.

    -untranslatedonly: same as -untranslated, but pages which already have a
                   translation are skipped. Hint: do NOT use this in
                   combination with -start without a -number limit, because
                   you will go through the whole alphabet before any queries
                   are performed!

    -file:         used as -file:filename, read a list of pages to treat
                   from the named file
                   
    -confirm:      ask for confirmation before any page is changed on the
                   live wiki. Without this argument, additions and
                   unambiguous modifications are made without confirmation.

    -select:       ask for each link whether it should be include before
                   changing any page. This is useful if you want to remove
                   invalid interwiki and if you do multiple hints of which
                   some might be correct and others incorrect. Combining
                   -select and -confirm is possible, but seems like overkill.

    -autonomous:   run automatically, do not ask any questions. If a question
                   to an operator is needed, write the name of the page
                   to autonomous_problems.dat and continue on the next page.

    -nobacklink:   switch off the backlink warnings

    -start:        used as -start:pagename, specifies that the robot should
                   go alphabetically through all pages on the home wiki,
                   starting at the named page.

    -number:       used as -number:#, specifies that the robot should process
                   that amount of pages and then stop. This is only useful in
                   combination with -start. The default is not to stop.

    -array:        used as -array:#, specifies that the robot should process
                   that amount of pages at once, only starting to load new
                   pages in the original language when the total falls below
                   that number. Default is to process (at least) 100 pages at
                   once. The number of new ones loaded is equal to the number
                   that is loaded at once from another language (default 60)

    -years:        run on all year pages in numerical order. Stop at year 2050.
                   If the argument is given in the form -years:XYZ, it
                   will run from [[XYZ]] through [[2050]]. If XYZ is a
                   negative value, it is interpreted as a year BC. If the
                   argument is simply given as -years, it will run from 1
                   through 2050.
                   
                   This implies -noredirect.

    -noauto:       Do not use the automatic translation feature for years and
                   dates, only use found links and hits.

    -days:         Like -years, but runs through all date pages. Stops at
                   Dec 31.  If the argument is given in the form -days:X,
                   it will start at month no. X through Dec 31. If the
                   argument is simply given as -days, it will run from
                   Jan 1 through Dec 31.  E.g. for -days:9 it will run
                   from Sep 1 through Dec 31.
    
    -skipfile:     used as -skipfile:filename, skip all links mentioned in
                   the given file from the list generated by -start. This
                   does not work with -number!
                   
    -skipauto:     use to skip all pages that can be translated automatically,
                   like dates, centuries, months, etc.

    -restore:      restore a set of "dumped" pages the robot was working on
                   when it terminated.

    -continue:     as restore, but after having gone through the dumped pages,
                   continue alphabetically starting at the last of the dumped
                   pages.

    -warnfile:     used as -warnfile:filename, reads all warnings from the
                   given file that apply to the home wiki language,
                   and read the rest of the warning as a hint. Then
                   treats all the mentioned pages. A quicker way to
                   implement warnfile suggestions without verifying them
                   against the live wiki is using the warnfile.py
                   robot.

    -noredirect    do not follow redirects (note: without ending columns).

    -noshownew:    don't show the source of every new pagelink found.

    -neverlink:    used as -neverlink:xx where xx is a language code:
                   Disregard any links found to language xx. You can also
                   specify a list of languages to disregard, separated by
                   commas.

    -ignore:       used as -ignore:xx:aaa where xx is a language code, and
                   aaa is a page title to be ignored.

    -ignorefile:   similar to -ignore, except that the pages are taken from
                   the given file instead of the command line.
    
    -showpage      when asking for hints, show the first bit of the text
                   of the page always, rather than doing so only when being
                   asked for (by typing '?'). Only useful in combination
                   with a hint-asking option like -untranslated, -askhints
                   or -untranslatedonly

    -localonly     only work on the local wiki, not on other wikis in the family
                   I have a login at
                   
    -limittwo      only update two pages - one in the local wiki (if loged-in),
                   and one in the top available one.
                   For example, if the local page has links to de and fr,
                   this option will make sure that only local and de: (larger)
                   site is updated. This option is useful to quickly set two way
                   links without updating all of wiki's sites.

    -whenneeded    works like limittwo, but other languages are changed in the
                   following cases:
                   * If there are no interwiki at all on the page
                   * If an interwiki must be removed
                   * If an interwiki must be changed, where the old interwiki
                     does not go to a non-existing or redirect page (although
                     some cases where it is are included too)
                   
    -bracket       only work on pages that have (in the home language) a bracket
                   in their title. All other pages are skipped.

Some configuration option can be used to change the working of this robot:

interwiki_backlink: if set to True, all problems in foreign wikis will
                    be reported


interwiki_shownew:  should interwiki.py display every new link it discovers?

interwiki_graph:    output a graph PNG file on conflicts? You need pydot for
                    this: http://dkbza.org/pydot.html

interwiki_graph_format: the file format for interwiki graphs 

without_interwiki:  save file with local articles without interwikis

All these options can be changed through the user-config.py configuration file.

If interwiki.py is terminated before it is finished, it will write a dump file
to the interwiki-dumps subdirectory. The program will read it if invoked with
the "-restore" or "-continue" option, and finish all the subjects in that list.
To run the interwiki-bot on all pages on a language, run it with option
"-start:!", and if it takes so long you have to break it off, use "-continue"
next time.
"""
#
# (C) Rob W.W. Hooft, 2003
# (C) Daniel Herding, 2004
# (C) Yuri Astrakhan, 2005-2006
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#
import sys, copy, re
import time
import codecs
import socket

try:
    set # introduced in Python 2.4: faster and future
except NameError:
    from sets import Set as set

try: sorted ## Introduced in 2.4
except NameError:
    def sorted(seq, cmp=None, key=None, reverse=False):
        """Copy seq and sort and return it.
        >>> sorted([3, 1, 2])
        [1, 2, 3]
        """
        seq2 = copy.copy(seq)
        if key:
            if cmp == None:
                cmp = __builtins__.cmp
            seq2.sort(lambda x,y: cmp(key(x), key(y)))
        else:
            if cmp == None:
                seq2.sort()
            else:
                seq2.sort(cmp)
        if reverse:
            seq2.reverse()
        return seq2

import wikipedia, config, pagegenerators, catlib
import titletranslate

class LinkMustBeRemoved(wikipedia.Error):
    """
    An interwiki link has to be removed, but this can't be done because of user
    preferences or because the user chose not to change the page.
    """

msg = {
    'af': (u'robot ', u'Bygevoeg', u'Verwyder', u'Verander'),
    'ar': (u'روبوت ', u'إضافة', u'مسح', u'تعديل'),
    'br': (u'Robot ', u'Ouzhpennet', u'Kemmet', u'Tennet'),
    'ca': (u'Robot ', u'afegeix', u'esborra', u'modifica'),
    'cs': (u'robot ', u'přidal', u'odebral', u'změnil'),
    'csb':(u'robot ', u'dodôwô', u'rëmô', u'pòprôwiô'),
    'da': (u'robot ', u'Tilføjer', u'Fjerner', u'Ændrer'),
    'de': (u'Bot: ', u'Ergänze', u'Entferne', u'Ändere'),
    'en': (u'robot ', u'Adding', u'Removing', u'Modifying'),
    'es': (u'robot ', u'Añadido', u'Eliminado', u'Modificado'),
    'eu': (u'robota ', u'Erantsia', u'Ezabatua', u'Aldatua'),
    'fa': (u'ربات ', u'افزودن', u'حذف', u'اصلاح'),
    'fi': (u'Botti ', u'lisäsi', u'poisti', u'muokkasi'),
    'fr': (u'robot ', u'Ajoute', u'Retire', u'Modifie'),
    'he': (u'רובוט ', u'מוסיף', u'מסיר', u'משנה'),
    'hr': (u'robot', u'Dodaje', u'Uklanja', u'Mijenja'),
    'ia': (u'Robot: ', u'Addition de', u'Elimination de', u'Modification de'),
    'is': (u'robot ', u'Bæti við', u'Fjarlægi', u'Breyti'),
    'it': (u'robot ', u'Aggiungo', u'Tolgo', u'Modifico'),
    'ka': (u'რობოტი ', u'დამატება', u'წაშლა', u'შეცვლა'),
    'ksh': (u'Bot: ', u'dobëijedonn', u'erußjenumme', u'ußjewääßelt'),
    'lt': (u'robotas ', u'Pridedama', u'Šalinama', u'Keičiama'),
    'nl': (u'robot ', u'Erbij', u'Eraf', u'Anders'),
    'nn': (u'robot ', u'la til', u'fjerna', u'endra'),
    'no': (u'robot ', u'Tilføyer', u'Fjerner', u'Endrer'),
    'os': (u'Робот', u'баххæст кодта', u'Баивта', u'Аиуварс'),
    'pl': (u'robot ', u'dodaje', u'usuwa', u'poprawia'),
    'pt': (u'Bot: ', u'Adicionando', u'Removendo',u'Modificando'),
    'sk': (u'robot ', u'Pridal', u'Odobral',u'Zmenil' ),
    'sl': (u'robot ', u'Dodajanje', u'Odstranjevanje', u'Spreminjanje'),
    'sr': (u'Бот', u'Додаје', u'Брише', u'Мења'),
    'sv': (u'robot ', u'Lägger till', u'Tar bort', u'Ändrar'),
    }

class Global(object):
    """Container class for global settings.
       Use of globals outside of this is to be avoided."""
    always = False
    autonomous = False
    backlink = config.interwiki_backlink
    confirm = False
    select = False
    debug = True
    followredirect = True
    force = False
    minarraysize = 100
    maxquerysize = 60
    same = False
    shownew = config.interwiki_shownew
    skip = set()
    skipauto = False
    untranslated = False
    untranslatedonly = False
    askhints = False
    auto = True
    neverlink = []
    showtextlink = 0
    showtextlinkadd = 300
    localonly = False
    limittwo = False
    strictlimittwo = False
    ignore = []
    bracketonly = False

class Subject(object):
    """Class to follow the progress of a single 'subject' (i.e. a page with
       all its translations)"""
    def __init__(self, pl, hints = None):
        """Constructor. Takes as arguments the Page on the home wiki
           plus optionally a list of hints for translation"""
        # Remember the "origin page"
        self.inpl = pl
        # Mark the origin page as todo.
        self.todo = {pl:pl.site()}
        # Nothing has been done yet
        self.done = {}
        # Add the translations given in the hints.
        self.foundin = {self.inpl:[]}
        self.translate(hints)
        if globalvar.confirm:
            self.confirm = 1
        else:
            self.confirm = 0
        self.problemfound = False
        self.untranslated = None
        self.hintsasked = False
        
    def pl(self):
        """Return the Page on the home wiki"""
        return self.inpl
    
    def translate(self, hints = None):
        """Add the translation hints given to the todo list"""
        arr = {}
        if globalvar.same:
            if hints:
                titletranslate.translate(self.inpl, arr, hints = hints + ['all:'], auto = globalvar.auto)
            else:
                titletranslate.translate(self.inpl, arr, hints = ['all:'], auto = globalvar.auto)
        else:
            titletranslate.translate(self.inpl, arr, hints = hints, auto = globalvar.auto)
        for pl in arr.iterkeys():
            self.todo[pl] = pl.site()
            self.foundin[pl] = [None]

    def openSites(self):
        """Return a list of sites for all things we still need to do"""
        return self.todo.values()

    def willWorkOn(self, site):
        """By calling this method, you 'promise' this instance that you will
           work on any todo items for the wiki indicated by 'site'. This routine
           will return a list of pages that can be treated."""
        # Bug-check: Isn't there any work still in progress?
        if hasattr(self,'pending'):
            raise 'Cant start on %s; still working on %s'%(repr(site),self.pending)
        # Prepare a list of suitable pages
        self.pending=[]
        for pl in self.todo.keys():
            if pl.site() == site:
                self.pending.append(pl)
                del self.todo[pl]
        # If there are any, return them. Otherwise, nothing is in progress.
        if self.pending:
            return self.pending
        else:
            del self.pending
            return None

    def conditionalAdd(self, pl, counter, foundin):
        """Add the pagelink given to the todo list, but only if we didn't know
           it before. If it is added, update the counter accordingly."""
        # For each pl remember where it was found
        if self.foundin.has_key(pl):
            self.foundin[pl].append(foundin)
            return False
        else:
            self.foundin[pl]=[foundin]
            self.todo[pl] = pl.site()
            counter.plus(pl.site())
            # wikipedia.output("DBG> Found new to do: %s" % pl.aslink())
            return True
        
    def workDone(self, counter):
        """This is called by a worker to tell us that the promised work
           was completed as far as possible. The only argument is an instance
           of a counter class, that has methods minus() and plus() to keep
           counts of the total work todo."""
        # Loop over all the pages that should have been taken care of
        for pl in self.pending:
            # Mark the page as done
            self.done[pl] = pl.site()

            # make sure that none of the linked items is an auto item
            if globalvar.skipauto:
                dictName, year = pl.autoFormat()
                if dictName != None:
                    wikipedia.output(u'WARNING: %s:%s relates to %s:%s, which is an auto entry %s(%s)' % (self.inpl.site().language(), self.inpl.title(), pl.site().language(),pl.title(),dictName,year))                

            # Register this fact at the todo-counter.
            counter.minus(pl.site())
            # Assume it's not a redirect
            isredirect = 0
            # Now check whether any interwiki links should be added to the
            # todo list.
            if pl.section():
                # We have been referred to a part of a page, not the whole page. Do not follow references.
                pass
            else:
                try:
                    iw = pl.interwiki()
                except UnicodeDecodeError, arg:
                    wikipedia.output(u"BUG>>> UnicodeDecodeError exception processing %s: %s" % (pl.aslink(forceInterwiki=True), arg))
                    print arg.args[1]
                except ValueError, arg:
                    wikipedia.output(u"BUG>>> ValueError exception processing %s: %s" % (pl.aslink(forceInterwiki=True), arg))
                except wikipedia.IsRedirectPage,arg:
                    try:
                        pl3 = wikipedia.Page(pl.site(),arg.args[0])
                        wikipedia.output(u"NOTE: %s is redirect to %s" % (pl.aslink(True), pl3.aslink(True)))
                        if pl == self.inpl:
                            # This is a redirect page itself. We don't need to
                            # follow the redirection.
                            isredirect = 1
                            # In this case we can also stop all hints!
                            for pl2 in self.todo:
                                counter.minus(pl2.site())
                            self.todo = {}
                            pass
                        elif not globalvar.followredirect:
                            print "NOTE: not following redirects."
                        else:
                            if globalvar.same=='wiktionary':
                                # In this case only follow the redirect if we would have
                                # followed an interwiki to that same page
                                if pl3.title().lower()!=self.inpl.title().lower():
                                    print "NOTE: Ignoring %s for %s in wiktionary mode"% (pl3, self.inpl)
                                    continue
                                elif pl3.title() != self.inpl.title() and self.inpl.site().nocapitalize and pl3.site().nocapitalize:
                                    print "NOTE: Ignoring %s for %s in wiktionary mode because both languages are uncapitalized."% (pl3, self.inpl)
                                    continue
                            if self.conditionalAdd(pl3, counter, pl):
                                if globalvar.shownew:
                                    wikipedia.output(u"%s: %s gives new redirect %s" %  (self.inpl.aslink(), pl.aslink(True), pl3.aslink(True)))
                    except UnicodeDecodeError:
                        wikipedia.output(u"BUG>>> processing %s: could not decode redirect to %s:%s" % (pl.aslink(forceInterwiki=True),pl.site(),arg.args[0]))
                    except (KeyError, ValueError):
                        wikipedia.output(u"WARNING>>> processing %s: redirect to %s:%s, possibly unsuported family" % (pl.aslink(forceInterwiki=True),pl.site(),arg.args[0]))
                except wikipedia.NoPage:
                    wikipedia.output(u"NOTE: %s does not exist" % pl.aslink(True))
                    #print "DBG> ",pl.urlname()
                    if pl == self.inpl:
                        # This is the home subject page.
                        # In this case we can stop all hints!
                        for pl2 in self.todo:
                            counter.minus(pl2.site())
                        self.todo = {}
                        self.done = {} # In some rare cases it might be we already did check some 'automatic' links
                        pass
                #except wikipedia.SectionError:
                #    wikipedia.output(u"NOTE: section %s does not exist" % pl.aslink())
                else:
                    if globalvar.autonomous:
                        if self.inpl.isDisambig() and not pl.isDisambig():
                            wikipedia.output(u"NOTE: Ignoring link from disambiguation page %s to non-disambiguation %s" % (self.inpl.aslink(True), pl.aslink(True)))
                            del self.done[pl]
                        elif not self.inpl.isDisambig() and pl.isDisambig():
                            wikipedia.output(u"NOTE: Ignoring link from non-disambiguation page %s to disambiguation %s" % (self.inpl.aslink(True), pl.aslink(True)))
                            del self.done[pl]
                    else:
                        if self.inpl.isDisambig() and not pl.isDisambig():
                            choice = wikipedia.inputChoice('WARNING: %s is a disambiguation page, but %s doesn\'t seem to be one. Follow it anyway?' % (self.inpl.aslink(True), pl.aslink(True)), ['Yes', 'No', 'Add a hint'], ['y', 'n', 'a'])
                        elif not self.inpl.isDisambig() and pl.isDisambig():
                            choice = wikipedia.inputChoice('WARNING: %s doesn\'t seem to be a disambiguation page, but %s is one. Follow it anyway?' % (self.inpl.aslink(True), pl.aslink(True)), ['Yes', 'No', 'Add a hint'], ['y', 'n', 'a'])
                        else:
                            choice = 'y'
                        if choice not in ['y', 'Y']:
                            wikipedia.output(u"NOTE: ignoring %s and its interwiki links" % pl.aslink(True))
                            del self.done[pl]
                            iw = ()
                            if choice in ['a', 'A']:
                                newhint = wikipedia.input(u'Give a hint for language %s, not using a language code:'%pl.site().language())
                                if newhint:
                                    page2 = wikipedia.Page(pl.site(),newhint)
                                    self.conditionalAdd(page2, counter, None)
                    if self.inpl == pl:
                        self.untranslated = (len(iw) == 0)
                        if globalvar.untranslatedonly:
                            # Ignore the interwiki links.
                            iw = ()
                    elif pl.isEmpty():
                        if not pl.isCategory():
                            wikipedia.output(u"NOTE: %s is empty; ignoring it and its interwiki links" % pl.aslink(True))
                            # Ignore the interwiki links
                            iw = ()
                    for page2 in iw:
                        if page2.site().language() in globalvar.neverlink:
                            print("Skipping link %s to an ignored language"%page2)
                            continue
                        if page2 in globalvar.ignore:
                            print("Skipping link %s to an ignored page"%page2)
                            continue                            
                        if globalvar.same=='wiktionary':
                            if page2.title().lower()!=self.inpl.title().lower():
                                wikipedia.output(self.inpl.title())
                                wikipedia.output(page2.title())
                                try:
                                    wikipedia.output(u"NOTE: Ignoring %s for %s in wiktionary mode" % (page2, self.inpl))
                                except UnicodeDecodeError:
                                    print("NOTE: Ignoring %s for %s in wiktionary mode" % (page2, self.inpl))
                                continue
                            elif page2.title() != self.inpl.title() and self.inpl.site().nocapitalize and page2.site().nocapitalize:
                                wikipedia.output(u"NOTE: Ignoring %s for %s in wiktionary mode because both languages are uncapitalized." % (page2, self.inpl))
                                continue
                        if not globalvar.autonomous:
                            if self.inpl.namespace() != page2.namespace():
                                if not self.foundin.has_key(page2):
                                    choice = wikipedia.inputChoice('WARNING: %s is in namespace %i, but %s is in namespace %i. Follow it anyway?' % (self.inpl.aslink(True), self.inpl.namespace(), page2.aslink(True), page2.namespace()), ['Yes', 'No'], ['y', 'n'])
                                    if choice not in ['y', 'Y']:
                                        # Fill up foundin, so that we will not ask again
                                        self.foundin[page2] = [pl]
                                        wikipedia.output(u"NOTE: ignoring %s and its interwiki links" % page2.aslink(True))
                                        continue
                        if self.conditionalAdd(page2, counter, pl):
                            if globalvar.shownew:
                                wikipedia.output(u"%s: %s gives new interwiki %s"% (self.inpl.aslink(), pl.aslink(True), page2.aslink(True)))
                              
        # These pages are no longer 'in progress'
        del self.pending
        # Check whether we need hints and the user offered to give them
        if self.untranslated and not self.hintsasked:
            wikipedia.output(u"NOTE: %s does not have any interwiki links" % self.inpl.aslink(True))
            if config.without_interwiki:
                f = codecs.open('without_interwiki.txt', 'a', 'utf-8')
                f.write("# %s \n" % pl.aslink())
                f.close()
        if (self.untranslated or globalvar.askhints) and not self.hintsasked and not isredirect:
            # Only once! 
            self.hintsasked = True
            if globalvar.untranslated:
                newhint = None
                t = globalvar.showtextlink
                if t:
                    wikipedia.output(pl.get()[:t])
                while 1:
                    newhint = wikipedia.input(u'Give a hint (? to see pagetext):')
                    if newhint == '?':
                        t += globalvar.showtextlinkadd
                        wikipedia.output(pl.get()[:t])
                    elif newhint and not ':' in newhint:
                        print "Please enter a hint like language:pagename"
                        print "or type nothing if you do not have a hint"
                    elif not newhint:
                        break
                    else:
                        arr = {}
                        titletranslate.translate(pl, arr, hints = [newhint], auto = globalvar.auto)
                        for pl2 in arr.iterkeys():
                            self.todo[pl2] = pl2.site()
                            counter.plus(pl2.site())
                            self.foundin[pl2] = [None]
                            

    def isDone(self):
        """Return True if all the work for this subject has completed."""
        return len(self.todo) == 0

    def problem(self, txt):
        """Report a problem with the resolution of this subject."""
        wikipedia.output(u"ERROR: %s" % txt)
        self.confirm += 1
        self.problemfound = True
        if globalvar.autonomous:
            try:
                f = codecs.open('autonomous_problem.dat', 'a', 'utf-8')
                f.write("* %s {%s}\n" % (self.inpl.aslink(True), txt))
                f.close()
            except:
                print 'File of autonomous_problem.dat open or corrupted! Try again with -restore.'
                sys.exit()

    def whereReport(self, pl, indent=4):
        for pl2 in sorted(self.foundin[pl]):
            if pl2 is None:
                wikipedia.output(u" "*indent + "Given as a hint.")
            else:
                wikipedia.output(u" "*indent + pl2.aslink(True))

    def createGraph(self):
        """
        See http://meta.wikimedia.org/wiki/Interwiki_graphs
        """
        wikipedia.output(u'Preparing graph for %s' % self.inpl.title())
        import pydot
        # create empty graph
        graph = pydot.Dot()
        graph.add_node(pydot.Node('start', shape = 'point'))
#        graph.set('concentrate', 'true')
        for page in self.foundin.iterkeys():
            # a node for each found page
            node = pydot.Node('"%s:%s"' % (page.site().language(), wikipedia.unicode2html(page.title(), 'ascii')), shape = 'rectangle')
            node.set_URL('http://%s%s' % (page.site().hostname(), page.site().get_address(page.urlname())))
            node.set_style('filled')
            node.set_fillcolor('white')
            node.set_fontsize('11')
            if not page.exists():
                node.set_fillcolor('red')
            elif page.isRedirectPage():
                node.set_fillcolor('blue')
            elif page.isDisambig():
                node.set_fillcolor('orange')
            if page.namespace() != self.inpl.namespace():
                node.set_color('green')
                node.set_style('filled,bold')
            # if we found more than one valid page for this language:
            if len(filter(lambda p: p.site() == page.site() and p.exists() and not p.isRedirectPage(), self.foundin.keys())) > 1:
                # mark conflict by octagonal node
                node.set_shape('octagon')
            graph.add_node(node)
        # mark start node
        firstLabel = '"%s:%s"' % (self.inpl.site().language(), wikipedia.unicode2html(self.inpl.title(), 'ascii'))
        graph.add_edge(pydot.Edge('start', firstLabel))
        for page, referrers in self.foundin.iteritems():
            for refPage in referrers:
                # if page was given as a hint, referrers would be [None]
                if refPage is not None:
                    sourceLabel = '"%s:%s"' % (refPage.site().language(), wikipedia.unicode2html(refPage.title(), 'ascii'))
                    targetLabel = '"%s:%s"' % (page.site().language(), wikipedia.unicode2html(page.title(), 'ascii'))
                    edge = pydot.Edge(sourceLabel, targetLabel)
                    oppositeEdge = graph.get_edge(targetLabel, sourceLabel)
                    if oppositeEdge:
                        #oppositeEdge.set_arrowtail('normal')
                        oppositeEdge.set_dir('both')
                    else:
                        # add edge
                        if refPage.site() == page.site():
                            edge.set_color('blue')
                        elif not page.exists():
                            # mark dead links
                            edge.set_color('red')
                        elif refPage.isDisambig() != page.isDisambig():
                            # mark links between disambiguation and non-disambiguation
                            # pages
                            edge.set_color('orange')
                        if refPage.namespace() != page.namespace():
                            edge.set_color('green')
                        graph.add_edge(edge)

        filename = '%s-%s-%s.%s' % (self.inpl.site().family.name, self.inpl.site().language(), self.inpl.title(), config.interwiki_graph_format)
        for forbiddenChar in ':*?/\\':
            filename = filename.replace(forbiddenChar, '_')
        filename = 'interwiki-graphs/' + filename
        if config.interwiki_graph_dumpdot:
            if graph.write(filename + '.dot', prog = 'dot' , format ='raw'):
                wikipedia.output(u'Dot file saved as %s' % filename)
            else:
                wikipedia.output(u'Dot file could not be saved as %s' % filename)
        if graph.write(filename, prog = 'dot', format = config.interwiki_graph_format):
            wikipedia.output(u'Graph saved as %s' % filename)
        else:
            wikipedia.output(u'Graph could not be saved as %s' % filename)

    def assemble(self):
        # No errors have been seen so far
        nerr = 0
        # Build up a dictionary of all links found, with the site as key.
        # Each value will be a list.
        mysite = wikipedia.getSite()
        
        new = {}
        for pl in self.done.keys():
            site = pl.site()
            if site == mysite and pl.exists() and not pl.isRedirectPage():
                if pl != self.inpl:
                    self.problem("Found link to %s" % pl.aslink(True) )
                    self.whereReport(pl)
                    nerr += 1
            elif pl.exists() and not pl.isRedirectPage():
                if site in new:
                    new[site].append(pl)
                else:
                    new[site] = [pl]
        # See if new{} contains any problematic values
        result = {}
        for k, v in new.items():
            if len(v) > 1:
                nerr += 1
                self.problem("Found more than one link for %s"%k)
        # The following two lines are no longer correct since multi-site
        # editing is now possible
        # if nerr == 0 and len( self.foundin[self.inpl] ) == 0 and len(new) != 0:
        #    self.problem(u'None of %i other languages refers back to %s' % (len(new), self.inpl.aslink()))
        # If there are any errors, we need to go through all
        # items manually.
        if nerr > 0 or globalvar.select:

            if config.interwiki_graph:
                self.createGraph()
            
            # We don't need to continue with the rest if we're in autonomous
            # mode.
            if globalvar.autonomous:
                return None

            # First loop over the ones that have more solutions
            for k,v in new.items():
                if len(v) > 1:
                    print "="*30
                    print "Links to %s"%k
                    i = 0
                    for page2 in v:
                        i += 1
                        wikipedia.output(u"  (%d) Found link to %s in:" % (i, page2.aslink(True)))
                        self.whereReport(page2, indent=8)
                    if not globalvar.autonomous:
                        while 1:
                            answer = wikipedia.input(u"Which variant should be used [number, (n)one, (g)ive up] :")
                            if answer:
                                if answer in 'gG':
                                    return None
                                elif answer in 'nN':
                                    # None acceptable
                                    break
                                elif answer[0] in '0123456789':
                                    answer = int(answer)
                                    try:
                                        result[k] = v[answer-1]
                                    except IndexError:
                                        # user input is out of range
                                        pass
                                    else:
                                        break
            # We don't need to continue with the rest if we're in autonomous
            # mode.
            if globalvar.autonomous:
                return None
            # Loop over the ones that have one solution, so are in principle
            # not a problem.
            acceptall = False
            for k,v in new.items():
                if len(v) == 1:
                    if not acceptall:
                        print "="*30
                        pl2 = v[0]
                        wikipedia.output(u"Found link to %s in:" % pl2.aslink(True))
                        self.whereReport(pl2, indent=4)
                    while 1:
                        if acceptall: 
                            answer = 'a'
                        else: 
                            answer = wikipedia.inputChoice(u'What should be done?', ['accept', 'reject', 'give up', 'accept all'], ['a', 'r', 'g', 'l'])
                            if not answer:
                                answer = 'a'
                        if answer in 'lL': # accept all
                            acceptall = True
                            answer = 'a'
                        if answer in 'aA': # accept this one
                            result[k] = v[0]
                            break
                        elif answer in 'gG': # give up
                            return None
                        elif answer in 'rR': # reject
                            # None acceptable
                            break
        else: # nerr <= 0, hence there are no lists longer than one.
            for k,v in new.items():
                result[k] = v[0]
        return result
    
    def finish(self, bot = None):
        """Round up the subject, making any necessary changes. This method
           should be called exactly once after the todo list has gone empty.

           This contains a shortcut: if a subject array is given in the argument
           bot, just before submitting a page change to the live wiki it is
           checked whether we will have to wait. If that is the case, the bot will
           be told to make another get request first."""
        if not self.isDone():
            raise "Bugcheck: finish called before done"
        if self.inpl.isRedirectPage():
            return
        if not self.untranslated and globalvar.untranslatedonly:
            return
        # The following check is not always correct and thus disabled.
        # self.done might contain no interwiki links because of the -neverlink
        # argument or because of disambiguation conflicts.
#         if len(self.done) == 1:
#             # No interwiki at all
#             return
        wikipedia.output(u"======Post-processing %s======" % self.inpl.aslink(True))
        # Assemble list of accepted interwiki links
        new = self.assemble()
        if new == None: # User said give up or autonomous with problem
            wikipedia.output(u"======Aborted processing %s======" % self.inpl.aslink(True))
            return
        
        # Make sure new contains every page link, including the page we are processing
        # replaceLinks will skip the site it's working on.
        if not new.has_key(self.inpl.site()):
            new[self.inpl.site()] = self.inpl

        #self.replaceLinks(self.inpl, new, True, bot)

        updatedSites = []
        notUpdatedSites = []
        # Process all languages here

        if globalvar.limittwo:
            lclSite = self.inpl.site()
            lclSiteDone = False
            frgnSiteDone = False
            for siteCode in lclSite.family.languages_by_size + [self.inpl.site().lang]:   #make sure there is always this site's code
                site = wikipedia.getSite(code = siteCode)
#                wikipedia.output(u"DBG> Searching for %s (code=%s)" % (site,siteCode))
                if (not lclSiteDone and site == lclSite) or (not frgnSiteDone and site != lclSite and new.has_key(site)):
                    if site == lclSite:
                        lclSiteDone = True   # even if we fail the update

                    if config.usernames.has_key(site.family.name) and config.usernames[site.family.name].has_key(site.lang):
                        if site != lclSite:
                            wikipedia.output(u"Found pair match between %s and %s" % (lclSite, site))
                        try:
                            if self.replaceLinks(new[site], new, bot):
                                updatedSites.append(site)
                            if site != lclSite:
                                frgnSiteDone = True
                        except LinkMustBeRemoved:
                            notUpdatedSites.append(site)
                elif not globalvar.strictlimittwo and new.has_key(site) and site != lclSite:
                    old={}
                    try:
                        for pl in new[site].interwiki():
                            old[pl.site()] = pl
                    except wikipedia.NoPage:
                        wikipedia.output(u"BUG>>> %s no longer exists?" % new[site].aslink(True))
                        continue
                    mods, adding, removing, modifying = compareLanguages(old, new, insite = lclSite)
                    if len(removing) > 0 or (len(modifying) > 0 and self.problemfound) or len(old.keys()) == 0:
                        try:
                            if self.replaceLinks(new[site], new, bot):
                                updatedSites.append(site)
                        except LinkMustBeRemoved:
                            notUpdatedSites.append(site)
                        
            else:
                wikipedia.output(u"Unable to find a suitable pair")
        else:
            for (site, page) in new.iteritems():
                # if we have an account for this site
                if config.usernames.has_key(site.family.name) and config.usernames[site.family.name].has_key(site.lang):
                    # Try to do the changes
                    try:
                        if self.replaceLinks(page, new, bot):
                            # Page was changed
                            updatedSites.append(site)
                    except LinkMustBeRemoved:
                        notUpdatedSites.append(site)
        
        # disabled graph drawing for minor problems: it just takes too long 
        #if notUpdatedSites != [] and config.interwiki_graph:
        #    # at least one site was not updated, save a conflict graph
        #    self.createGraph()
            
        # don't report backlinks for pages we already changed
        if globalvar.backlink:
            self.reportBacklinks(new, updatedSites)

    def replaceLinks(self, pl, newPages, bot):
        """
        Returns True if saving was successful.
        """
        if globalvar.localonly:
            # In this case only continue on the Page we started with
            if pl != self.pl():
                return False

        if pl.title() != pl.sectionFreeTitle():
            # This is not a page, but a subpage. Do not edit it.
            wikipedia.output(u"Not editing %s: not doing interwiki on subpages" % pl.aslink(True))
            return False
        wikipedia.output(u"Updating links on page %s." % pl.aslink(True))

        # clone original newPages dictionary, so that we can modify it to the local page's needs
        new = dict(newPages)
        
        # sanity check - the page we are fixing must be the only one for that site.
        pltmp = new[pl.site()]
        if pltmp != pl:
            s = "None"
            if pltmp != None: s = pltmp.aslink(True)
            wikipedia.output(u"BUG>>> %s is not in the list of new links! Found %s." % (pl.aslink(True), s))
            return False
        
        # Avoid adding an iw link back to itself
        del new[pl.site()]

        # Put interwiki links into a map
        old={}
        try:
            for pl2 in pl.interwiki():
                old[pl2.site()] = pl2
        except wikipedia.NoPage:
            wikipedia.output(u"BUG>>> %s no longer exists?" % pl.aslink(True))
            return False

        # Check what needs to get done
        mods, adding, removing, modifying = compareLanguages(old, new, insite = pl.site())

        # When running in autonomous mode without -force switch, make sure we don't remove any items, but allow addition of the new ones
        if globalvar.autonomous and not globalvar.force and len(removing) > 0:
            for rmpl in removing:
                if rmpl.site() != pl.site():   # Sometimes sites have an erroneous link to itself as an interwiki
                    new[rmpl.site()] = old[rmpl.site()]
                    wikipedia.output(u"WARNING: %s is either deleted or has a mismatching disambiguation state." % rmpl.aslink(True))
            # Re-Check what needs to get done
            mods, adding, removing, modifying = compareLanguages(old, new, insite = pl.site())

        if not mods and not globalvar.always:
            wikipedia.output(u'No changes needed' )
        else:
            if mods:
                wikipedia.output(u"Changes to be made: %s" % mods)
            oldtext = pl.get()
            newtext = wikipedia.replaceLanguageLinks(oldtext, new, site = pl.site())
            if globalvar.debug:
                wikipedia.showDiff(oldtext, newtext)
            if newtext != oldtext:
                # wikipedia.output(u"NOTE: Replace %s" % pl.aslink())
                # Determine whether we need permission to submit
                ask = False
                if removing and removing != [pl]:   # Allow for special case of a self-pointing interwiki link
                    self.problem('Found incorrect link to %s in %s'% (",".join([x.site().lang for x in removing]), pl.aslink(True)))
                    ask = True
                if globalvar.force:
                    ask = False
                if globalvar.confirm:
                    ask = True
                # If we need to ask, do so
                if ask:
                    if globalvar.autonomous:
                        # If we cannot ask, deny permission
                        answer = 'n'
                    else:
                        answer = wikipedia.inputChoice(u'Submit?', ['Yes', 'No'], ['y', 'n'])
                else:
                    # If we do not need to ask, allow
                    answer = 'y'
                # If we got permission to submit, do so
                if answer == 'y':
                    # Check whether we will have to wait for wikipedia. If so, make
                    # another get-query first.
                    if bot:
                        while wikipedia.get_throttle.waittime() + 2.0 < wikipedia.put_throttle.waittime():
                            print "NOTE: Performing a recursive query first to save time...."
                            qdone = bot.oneQuery()
                            if not qdone:
                                # Nothing more to do
                                break
                    print "NOTE: Updating live wiki..."
                    timeout=60
                    while 1:
                        try:
                            status, reason, data = pl.put(newtext, comment = wikipedia.translate(pl.site().lang, msg)[0] + mods)
                        except wikipedia.LockedPage:
                            wikipedia.output(u'Page %s is locked. Skipping.' % pl.title())
                            return False
                        except (wikipedia.EditConflict, wikipedia.SpamfilterError), error:
                            # we can't resolve edit conflicts and spamfilter triggerings
                            # automatically.
                            wikipedia.output(u'ERROR putting page: %s. Giving up.' % error)
                            return False
                        except (socket.error, IOError, wikipedia.PageNotSaved), error:
                            if timeout>3600:
                                raise
                            wikipedia.output(u'ERROR putting page: %s' % error)
                            wikipedia.output(u'Sleeping %i seconds before trying again.' % timeout)
                            timeout *= 2
                            time.sleep(timeout)
                        else:
                            break
                    if str(status) == '302':
                        return True
                    else:
                        print status, reason
                else:
                    raise LinkMustBeRemoved('Found incorrect link to %s in %s'% (",".join([x.site().lang for x in removing]), pl.aslink(True)))
            return False

    def reportBacklinks(self, new, updatedSites):
        """
        Report missing back links. This will be called from finish() if needed.

        updatedSites is a list that contains all sites we changed, to avoid
        reporting of missing backlinks for pages we already fixed

        """
        try:
            for site, page in new.iteritems():
                if site not in updatedSites and not page.section():
                    shouldlink = new.values() + [self.inpl]
                    try:
                        linked = page.interwiki()
                    except wikipedia.NoPage:
                        wikipedia.output(u"WARNING: Page %s does no longer exist?!" % page.title())
                        break
                    for xpage in shouldlink:
                        if xpage != page and not xpage in linked:
                            for l in linked:
                                if l.site() == xpage.site():
                                    wikipedia.output(u"WARNING: %s: %s does not link to %s but to %s" % (page.site().family.name, page.aslink(True), xpage.aslink(True), l.aslink(True)))
                                    break
                            else:
                                wikipedia.output(u"WARNING: %s: %s does not link to %s" % (page.site().family.name, page.aslink(True), xpage.aslink(True)))
                    # Check for superfluous links
                    for xpage in linked:
                        if not xpage in shouldlink:
                            # Check whether there is an alternative page on that language.
                            for l in shouldlink:
                                if l.site() == xpage.site():
                                    # Already reported above.
                                    break
                            else:
                                # New warning
                                wikipedia.output(u"WARNING: %s: %s links to incorrect %s" % (page.site().family.name, page.aslink(True), xpage.aslink(True)))
        except (socket.error, IOError):
            wikipedia.output(u'ERROR: could not report backlinks')
    
class InterwikiBot(object):
    """A class keeping track of a list of subjects, controlling which pages
       are queried from which languages when."""
    
    def __init__(self):
        """Constructor. We always start with empty lists."""
        self.subjects = []
        self.counts = {}
        self.pageGenerator = None
        self.generated = 0

    def add(self, pl, hints = None):
        """Add a single subject to the list"""
        subj = Subject(pl, hints = hints)
        self.subjects.append(subj)
        for site in subj.openSites():
            # Keep correct counters
            self.plus(site)

    def setPageGenerator(self, pageGenerator, number = None):
        """Add a generator of subjects. Once the list of subjects gets
           too small, this generator is called to produce more Pages"""
        self.pageGenerator = pageGenerator
        self.generateNumber = number

    def dump(self):
        site = wikipedia.getSite()
        f = codecs.open(u'interwiki-dumps/interwikidump-%s-%s.txt' % (site.family.name, site.lang), 'w', 'utf-8')
        for subj in self.subjects:
            f.write(subj.pl().aslink(None)+'\n')
        f.close()
        wikipedia.output(u'Dump %s (%s) saved' % (site.lang, site.family.name))
        
    def generateMore(self, number):
        """Generate more subjects. This is called internally when the
           list of subjects becomes too small, but only if there is a
           PageGenerator"""
        fs = self.firstSubject()
        if fs:
            wikipedia.output(u"NOTE: The first unfinished subject is " + fs.pl().aslink(True))
        print "NOTE: Number of pages queued is %d, trying to add %d more."%(len(self.subjects), number)
        for i in range(number):
            try:
                while True:
                    page = self.pageGenerator.next()
                    if page in globalvar.skip:
                        wikipedia.output(u'Skipping: %s is in the skip list' % page.title())
                        continue
                    if globalvar.skipauto:
                        dictName, year = page.autoFormat()
                        if dictName != None:
                            wikipedia.output(u'Skipping: %s is an auto entry %s(%s)' % (page.title(),dictName,year))
                            continue
                    if globalvar.bracketonly:
                        if page.title().find("(") == -1:
                            continue
                    break

                self.add(page, hints = hints)
                self.generated += 1
                if self.generateNumber:
                    if self.generated == self.generateNumber:
                        self.pageGenerator = None
                        break
            except StopIteration:
                self.pageGenerator = None
                break

    def firstSubject(self):
        """Return the first subject that is still being worked on"""
        if self.subjects:
            return self.subjects[0]
        
    def maxOpenSite(self):
        """Return the site that has the most
           open queries plus the number. If there is nothing left, return
           None, 0. Only languages that are TODO for the first Subject
           are returned."""
        max = 0
        maxlang = None
        oc = self.firstSubject().openSites()
        if not oc:
            # The first subject is done. This might be a recursive call made because we
            # have to wait before submitting another modification to go live. Select
            # any language from counts.
            oc = self.counts.keys()
        if wikipedia.getSite() in oc:
            return wikipedia.getSite()
        for lang in oc:
            count = self.counts[lang]
            if count > max:
                max = count
                maxlang = lang
        return maxlang

    def selectQuerySite(self):
        """Select the site the next query should go out for."""
        # How many home-language queries we still have?
        mycount = self.counts.get(wikipedia.getSite(),0)
        # Do we still have enough subjects to work on for which the
        # home language has been retrieved? This is rough, because
        # some subjects may need to retrieve a second home-language page!
        if len(self.subjects) - mycount < globalvar.minarraysize:
            # Can we make more home-language queries by adding subjects?
            if self.pageGenerator and mycount < globalvar.maxquerysize:
                timeout = 60
                while timeout<3600:
                    try:
                        self.generateMore(globalvar.maxquerysize - mycount)
                    except wikipedia.ServerError:
                        # Could not extract allpages special page?
                        wikipedia.output(u'ERROR: could not retrieve more pages. Will try again in %d seconds'%timeout)
                        time.sleep(timeout)
                        timeout *= 2
                    else:
                        break
            # If we have a few, getting the home language is a good thing.
            if self.counts[wikipedia.getSite()] > 4:
                return wikipedia.getSite()
        # If getting the home language doesn't make sense, see how many 
        # foreign page queries we can find.
        return self.maxOpenSite()
    
    def oneQuery(self):
        """Perform one step in the solution process"""
        # First find the best language to work on
        site = self.selectQuerySite()
        if site == None:
            print "NOTE: Nothing left to do"
            return False
        # Now assemble a reasonable list of pages to get
        group = []
        plgroup = []
        for subj in self.subjects:
            # Promise the subject that we will work on the site
            # We will get a list of pages we can do.
            x = subj.willWorkOn(site)
            if x:
                plgroup.extend(x)
                group.append(subj)
                if len(plgroup)>=globalvar.maxquerysize:
                    break
        if len(plgroup) == 0:
            print "NOTE: Nothing left to do 2"
            return False
        # Get the content of the assembled list in one blow
        retryCount = 2
        timeout = 30
        while True:
            try:
                wikipedia.getall(site, plgroup)
            except wikipedia.SaxError:
                if retryCount > 0:
                    retryCount = retryCount - 1
                    wikipedia.output(u'Sleeping %i seconds before trying again.' % timeout)
                    time.sleep(timeout)
                    timeout = timeout * 2
                else:
                    # Ignore this error, and get the pages the traditional way.
                    break
            else:
                break
        # Tell all of the subjects that the promised work is done
        for subj in group:
            subj.workDone(self)
        return True
        
    def queryStep(self):
        self.oneQuery()
        # Delete the ones that are done now.
        for i in range(len(self.subjects)-1, -1, -1):
            subj = self.subjects[i]
            if subj.isDone():
                subj.finish(self)
                del self.subjects[i]
    
    def isDone(self):
        """Check whether there is still more work to do"""
        return len(self) == 0 and self.pageGenerator is None

    def plus(self, site): 
        """This is a routine that the Subject class expects in a counter"""
        try:
            self.counts[site] += 1
        except KeyError:
            self.counts[site] = 1

    def minus(self, site):
        """This is a routine that the Subject class expects in a counter"""
        self.counts[site] -= 1
        
    def run(self):
        """Start the process until finished"""
        while not self.isDone():
            self.queryStep()

    def __len__(self):
        return len(self.subjects)
    
def compareLanguages(old, new, insite):
    removing = []
    adding = []
    modifying = []
    for site in old.keys():
        if site not in new:
            removing.append(old[site])
        elif old[site] != new[site]:
            modifying.append(new[site])

    for site2 in new.keys():
        if site2 not in old:
            adding.append(new[site2])
    mods = ""
    # sort by language code
    adding.sort()
    modifying.sort()
    removing.sort()
    
    if len(adding) + len(removing) + len(modifying) <= 3:
        # Use an extended format for the string linking to all added pages.
        fmt = lambda pl: pl.aslink(forceInterwiki=True)
    else:
        # Use short format, just the language code
        fmt = lambda pl: pl.site().lang
    
    if adding:
        mods += " %s: %s" % (wikipedia.translate(insite.lang, msg)[1], ", ".join([fmt(x) for x in adding]))
    if removing: 
        mods += " %s: %s" % (wikipedia.translate(insite.lang, msg)[2], ", ".join([fmt(x) for x in removing]))
    if modifying:
        mods += " %s: %s" % (wikipedia.translate(insite.lang, msg)[3], ", ".join([fmt(x) for x in modifying]))
    return mods, adding, removing, modifying

def readWarnfile(filename, bot):
    import warnfile
    reader = warnfile.WarnfileReader(filename)
    # we won't use removeHints
    (hints, removeHints) = reader.getHints()
    pages = hints.keys()
    for page in pages:
        # The WarnfileReader gives us a list of pagelinks, but titletranslate.py expects a list of strings, so we convert it back.
        # TODO: This is a quite ugly hack, in the future we should maybe make titletranslate expect a list of pagelinks.
        hintStrings = ['%s:%s' % (hintedPage.site().language(), hintedPage.title()) for hintedPage in hints[page]]
        bot.add(page, hints = hintStrings)

#===========
        
globalvar=Global()
    
if __name__ == "__main__":
    try:
        singlePageTitle = []
        hints = []
        start = None
        number = None
        # the category name which will be used when source is 'category'.
        categoryName = None
        # a page whose referrers will be processed when the -ref parameter is used
        referredPageTitle = None
        linkingPageTitle = None
        warnfile = None
        # a PageGenerator (which doesn't give hints, only Pages)
        hintlessPageGen = None
        optContinue = False
        optRestore = False
        workNew = False
        catrecurse = False
        
        bot=InterwikiBot()
        
        if not config.never_log:
            wikipedia.activateLog('interwiki.log')

        for arg in sys.argv[1:]:
            # This code needs to be cleaned up to allow file name passage, and documented at the top
            if arg == "-mult":
                f = file("codelist.txt")
                lang = f.readline().strip()
                if len(lang) < 2:
                    raise u"No more items in the list"
                print "Processing " + lang
                f2 = file("codelist2.txt", "w")
                for s in f:
                    f2.write(s)
                f.close()
                f2.close()
                import os
                os.remove("codelist.txt")
                os.rename("codelist2.txt", "codelist.txt")
                
                wikipedia.argHandler("-lang:" + lang, 'interwiki')
                wikipedia.argHandler("-log:mult_%s.log" % lang, 'interwiki')
                continue

            arg = wikipedia.argHandler(arg, 'interwiki')
            if arg:
                if arg == '-noauto':
                    globalvar.auto = False
                elif arg.startswith('-hint:'):
                    hints.append(arg[6:])
                elif arg == '-force':
                    globalvar.force = True
                elif arg == '-always':
                    globalvar.always = True
                elif arg == '-same':
                    globalvar.same = True
                elif arg == '-wiktionary':
                    globalvar.same = 'wiktionary'
                elif arg == '-untranslated':
                    globalvar.untranslated = True
                elif arg == '-untranslatedonly':
                    globalvar.untranslated = True
                    globalvar.untranslatedonly = True
                elif arg == '-askhints':
                    globalvar.untranslated = True
                    globalvar.untranslatedonly = False
                    globalvar.askhints = True    
                elif arg == '-noauto':
                    pass
                elif arg.startswith('-warnfile:'):
                    warnfile = arg[10:]
                elif arg == '-confirm':
                    globalvar.confirm = True
                elif arg == '-select':
                    globalvar.select = True
                elif arg == '-autonomous':
                    globalvar.autonomous = True
                elif arg == '-noshownew':
                    globalvar.shownew = False
                elif arg == '-nobacklink':
                    globalvar.backlink = False
                elif arg == '-noredirect':
                    globalvar.followredirect = False
                elif arg == '-localonly':
                    globalvar.localonly = True
                elif arg == '-limittwo':
                    globalvar.limittwo = True
                    globalvar.strictlimittwo = True
                elif arg == '-whenneeded':
                    globalvar.limittwo = True
                    globalvar.strictlimittwo = False
                elif arg.startswith('-years'):
                    # Look if user gave a specific year at which to start
                    # Must be a natural number or negative integer.
                    if len(arg) > 7 and (arg[7:].isdigit() or (arg[7] == "-" and arg[8:].isdigit())):
                        startyear = int(arg[7:])
                    else:
                        startyear = 1
                    # avoid problems where year pages link to centuries etc.
                    globalvar.followredirect = False
                    hintlessPageGen = pagegenerators.YearPageGenerator(startyear)
                elif arg.startswith('-days'):
                    if len(arg) > 6 and arg[5] == ':' and arg[6:].isdigit():
                        # Looks as if the user gave a specific month at which to start
                        # Must be a natural number.
                        startMonth = int(arg[6:])
                    else:
                        startMonth = 1
                    hintlessPageGen = pagegenerators.DayPageGenerator(startMonth)
                elif arg.startswith('-skipfile:'):
                    skipfile = arg[10:]
                    skipPageGen = pagegenerators.TextfilePageGenerator(skipfile)
                    for page in skipPageGen:
                        globalvar.skip.add(page)
                elif arg == '-skipauto':
                    globalvar.skipauto = True
                elif arg == '-restore':
                    optRestore = True
                elif arg == '-continue':
                    optContinue = True
                elif arg.startswith('-file:'):
                    hintlessPageGen = pagegenerators.TextfilePageGenerator(arg[6:])
                elif arg == '-start':
                    start = wikipedia.input(u'Which page to start from: ')
                elif arg.startswith('-start:'):
                    if len(arg) == 7:
                        start = wikipedia.input(u'Which page to start from: ')
                    else:
                        start = arg[7:]
                elif arg.startswith('-ref'):
                    if len(arg) == 4:
                        referredPageTitle = wikipedia.input(u'Links to which page should be processed?')
                    else:
                        referredPageTitle = arg[5:]
                elif arg.startswith('-cat'):
                    if len(arg) == 4:
                        categoryName = wikipedia.input(u'Please enter the category name:')
                    else:
                        categoryName = arg[5:]
                elif arg.startswith('-subcat'):
                    catrecurse = True
                elif arg.startswith('-link'):
                    if len(arg) == 5:
                        linkingPageTitle = wikipedia.input(u'Links from which page should be processed?')
                    else:
                        linkingPageTitle = arg[6:]
                elif arg.startswith('-number:'):
                    number = int(arg[8:])
                elif arg.startswith('-array:'):
                    globalvar.minarraysize = int(arg[7:])
                    if globalvar.minarraysize < globalvar.maxquerysize:
                        globalvar.maxquerysize = globalvar.minarraysize
                elif arg.startswith('-neverlink:'):
                    globalvar.neverlink += arg[11:].split(",")
                elif arg.startswith('-ignore:'):
                    globalvar.ignore += [wikipedia.Page(None,p) for p in arg[8:].split(",")]
                elif arg.startswith('-ignorefile:'):
                    ignorefile = arg[12:]
                    ignorePageGen = pagegenerators.TextfilePageGenerator(ignorefile)
                    for page in ignorePageGen:
                        globalvar.ignore.append(page)
                elif arg == '-showpage':
                    globalvar.showtextlink += globalvar.showtextlinkadd
                elif arg == '-graph':
                    # override configuration
                    config.interwiki_graph = True
                elif arg == '-bracket':
                    globalvar.bracketonly = True
                elif arg == '-new':
                    workNew = True
                else:
                    singlePageTitle.append(arg)
        
        # ensure that we don't try to change main page
        try:
            site = wikipedia.getSite()
            mainpagename = site.family.mainpages[site.language()]
            globalvar.skip.add(wikipedia.Page(site, mainpagename))
        except:
            wikipedia.output(u'Missing main page name')

        # We need to know what language we are processing before invoking getSite()
        if optRestore or optContinue:
            site = wikipedia.getSite()
            dumpFileName = u'interwiki-dumps/interwikidump-%s-%s.txt' % (site.family.name, site.lang)
            hintlessPageGen = pagegenerators.TextfilePageGenerator(dumpFileName)
            if optContinue:
                # We waste this generator to find out the last page's title
                # This is an ugly workaround.
                for page in hintlessPageGen:
                    pass
                try:
                    nextPage = page.titleWithoutNamespace() + '!'
                    namespace = page.namespace()
                except NameError:
                    print "Dump file is empty?! Starting at the beginning."
                    nextPage = "!"
                    namespace = 0
                # old generator is used up, create a new one
                hintlessPageGen = pagegenerators.CombinedPageGenerator([pagegenerators.TextfilePageGenerator(dumpFileName), pagegenerators.AllpagesPageGenerator(nextPage, namespace)])

        if start:
            namespace = wikipedia.Page(wikipedia.getSite(), start).namespace()
            start = wikipedia.Page(wikipedia.getSite(), start).titleWithoutNamespace()
            hintlessPageGen = pagegenerators.AllpagesPageGenerator(start, namespace)
        elif referredPageTitle:
            referredPage = wikipedia.Page(wikipedia.getSite(), referredPageTitle)
            hintlessPageGen = pagegenerators.ReferringPageGenerator(referredPage)
        elif linkingPageTitle:
            linkingPage = wikipedia.Page(wikipedia.getSite(), linkingPageTitle)
            hintlessPageGen = pagegenerators.LinkedPageGenerator(linkingPage)
        elif categoryName:
            cat = catlib.Category(wikipedia.getSite(), 'Category:%s' % categoryName)
            hintlessPageGen = pagegenerators.CategorizedPageGenerator(cat, recurse = catrecurse)
        elif workNew:
            if not number:
                number = config.special_page_limit 
            hintlessPageGen = pagegenerators.NewpagesPageGenerator(number = number)

        if hintlessPageGen:
            # we'll use iter() to create make a next() function available.
            bot.setPageGenerator(iter(hintlessPageGen),number = number)
        elif warnfile:
            readWarnfile(warnfile, bot)
        else:
            singlePageTitle = ' '.join(singlePageTitle)
            if not singlePageTitle:
                singlePageTitle = wikipedia.input(u'Which page to check:')
            singlePage = wikipedia.Page(wikipedia.getSite(), singlePageTitle)
            bot.add(singlePage, hints = hints)
        
        try:
            bot.run()
        except KeyboardInterrupt:
            bot.dump()
        except:
            bot.dump()
            raise

    finally:
        wikipedia.stopme()
