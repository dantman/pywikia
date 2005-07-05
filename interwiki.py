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
                   
    -same:         looks over all 'serious' languages for the same title.
                   -same is equivalent to -hint:all:

    -name:         similar to -same, but UPPERCASE the last name for eo:

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

    -showpage      when asking for hints, show the first bit of the text
                   of the page always, rather than doing so only when being
                   asked for (by typing '?'). Only useful in combination
                   with a hint-asking option like -untranslated, -askhints
                   or -untranslatedonly
                   
A configuration option can be used to change the working of this robot:

interwiki_backlink: if set to True, all problems in foreign wikis will
                    be reported

Both these options are set to True by default. They can be changed through
the user-config.py configuration file.

If interwiki.py is terminated before it is finished, it will write a file
"interwiki.dump"; the program will read it if invoked with the
"-restore" or "-continue" option, and finish all the subjects in that list.
To run the interwiki-bot on all pages on a language, run it with option
"-start:!", and if it takes so long you have to break it off, use "-continue"
next time.
"""
#
# (C) Rob W.W. Hooft, 2003
# (C) Daniel Herding, 2004
# (C) Yuri Astrakhan, 2005
#
# Distribute under the terms of the PSF license.
#
__version__ = '$Id$'
#
import sys, copy, re
import time, date
import codecs
import socket
try:
    set # introduced in Python 2.4: faster and future
except NameError:
    from sets import Set as set

import wikipedia, config, pagegenerators
import titletranslate
import vertexgen

msg = {
    'af':(u'Bygevoeg', u'Verwyder', u'Verander'),
    'cs':(u'přidal', u'odebral', u'změnil'),
    'csb':(u'dodôwô', u'rëmô', u'pòprôwiô'),
    'da':(u'Tilføjer', u'Fjerner', u'Ændrer'),
    'de':(u'Ergänze', u'Entferne', u'Ändere'),
    'en':(u'Adding', u'Removing', u'Modifying'),
    'es':(u'Añadido', u'Eliminado', u'Modificado'),
    'fr':(u'Ajoute', u'Retire', u'Modifie'),
    'is':(u'Bæti við', u'Fjarlægi', u'Breyti'),
    'nl':(u'Erbij', u'Eraf', u'Anders'),
    'nn':(u'la til', u'fjerna', u'endra'),
    'no':(u'Tilføyer', u'Fjerner', u'Endrer'),
    'pl':(u'dodaje', u'usuwa', u'poprawia'),
    'pt':(u'Adicionando', u'Removendo',u'Modificando'),
    'sk':(u'Pridal', u'Odobral',u'Zmenil' ),
    'sv':(u'Lägger till', u'Tar bort', u'Ändrar'),
    }

class Global(object):
    """Container class for global settings.
       Use of globals outside of this is to be avoided."""
    always = False
    autonomous = False
    backlink = config.interwiki_backlink
    confirm = False
    debug = True
    followredirect = True
    force = False
    minarraysize = 100
    maxquerysize = 60
    same = False
    shownew = True
    skip = set()
    untranslated = False
    untranslatedonly = False
    askhints = False
    auto = True
    neverlink = []
    showtextlink = 0
    showtextlinkadd = 300

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
        titletranslate.translate(self.inpl, arr, same = globalvar.same, hints = hints, auto = globalvar.auto)
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
                except wikipedia.IsRedirectPage,arg:
                    pl3 = wikipedia.Page(pl.site(),arg.args[0])
                    wikipedia.output(u"NOTE: %s is redirect to %s" % (pl.aslink(), pl3.aslink()))
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
                        if self.conditionalAdd(pl3, counter, pl):
                            if globalvar.shownew:
                                wikipedia.output(u"%s: %s gives new redirect %s" %  (self.inpl.aslink(), pl.aslink(forceInterwiki = True), pl3.aslink(forceInterwiki = True)))
                except wikipedia.NoPage:
                    wikipedia.output(u"NOTE: %s does not exist" % pl.aslink())
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
                    if not globalvar.autonomous:
                        if self.inpl.isDisambig() and not pl.isDisambig():
                            choice = wikipedia.inputChoice('WARNING: %s is a disambiguation page, but %s doesn\'t seem to be one. Follow it anyway?' % (self.inpl.aslink(), pl.aslink()), ['Yes', 'No'], ['y', 'N'], 'N')
                        elif not self.inpl.isDisambig() and pl.isDisambig():
                            choice = wikipedia.inputChoice('WARNING: %s doesn\'t seem to be a disambiguation page, but %s is one. Follow it anyway?' % (self.inpl.aslink(), pl.aslink()), ['Yes', 'No'], ['y', 'N'], 'N')
                        else:
                            choice = 'y'
                        if choice not in ['y', 'Y']:
                            wikipedia.output(u"NOTE: ignoring %s and its interwiki links" % pl.aslink())
                            del self.done[pl]
                            iw = ()
                    if self.inpl == pl:
                        self.untranslated = (len(iw) == 0)
                        if globalvar.untranslatedonly:
                            # Ignore the interwiki links.
                            iw = ()
                    elif pl.isEmpty():
                        if not pl.isCategory():
                            wikipedia.output(u"NOTE: %s is empty; ignoring it and its interwiki links" % pl.aslink())
                            # Ignore the interwiki links
                            iw = ()
                    for page2 in iw:
                        if page2.site().language() in globalvar.neverlink:
                            print "Skipping link %s to an ignored language"% page2
                            continue
                        if globalvar.same=='wiktionary' and page2.linkname().lower()!=self.inpl.linkname().lower():
                            print "NOTE: Ignoring %s for %s in wiktionary mode"% (page2, self.inpl)
                            continue
                        if not globalvar.autonomous:
                            if self.inpl.namespace() != page2.namespace():
                                choice = wikipedia.inputChoice('WARNING: %s is in namespace %i, but %s is in namespace %i. Follow it anyway?' % (self.inpl.aslink(), self.inpl.namespace(), page2.aslink(), page2.namespace()), ['Yes', 'No'], ['y', 'N'], 'N')
                                if choice not in ['y', 'Y']:
                                    continue
                        if self.conditionalAdd(page2, counter, pl):
                            if globalvar.shownew:
                                wikipedia.output(u"%s: %s gives new interwiki %s"% (self.inpl.aslink(), pl.aslink(), page2.aslink()))
                              
        # These pages are no longer 'in progress'
        del self.pending
        # Check whether we need hints and the user offered to give them
        if self.untranslated and not self.hintsasked:
            wikipedia.output(u"NOTE: %s does not have any interwiki links" % self.inpl.aslink())
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
                        titletranslate.translate(pl, arr, same = False,
                                                 hints = [newhint], auto = globalvar.auto)
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
            f = codecs.open('autonomous_problem.dat', 'a', 'utf-8')
            f.write("* %s {%s}\n" % (self.inpl.aslink(), txt))
            f.close()

    def whereReport(self, pl, indent=4):
        for pl2 in self.foundin[pl]:
            if pl2 is None:
                wikipedia.output(u" "*indent + "Given as a hint.")
            else:
                wikipedia.output(u" "*indent + pl2.aslink())

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
                    self.problem("Found link to %s" % pl.aslink(forceInterwiki = True) )
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
        if nerr == 0 and len( self.foundin[self.inpl] ) == 0 and len(new) != 0:
            self.problem(u'None of %i other languages refers back to %s' % (len(new), self.inpl.aslink()))
        # If there are any errors, we need to go through all
        # items manually.
        if nerr > 0:

            # Save all the found interwikies as a "article  from  to"  file
            if vertexgen.vertfile:
                for k,v in new.items():
                    for pl2 in v:
                        for pl3 in self.foundin[pl2]:
                            if pl3 is None:
                                vertexgen.add( self.formatPl(self.inpl), u':hint:', self.formatPl(pl2) )
                            else:
                                vertexgen.add( self.formatPl(self.inpl), self.formatPl(pl3), self.formatPl(pl2) )
                    
            # First loop over the ones that have more solutions
            for k,v in new.items():
                if len(v) > 1:
                    print "="*30
                    print "Links to %s"%k
                    i = 0
                    for page2 in v:
                        i += 1
                        wikipedia.output(u"  (%d) Found link to %s in:" % (i, page2.aslink(forceInterwiki = True)))
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
                    print "="*30
                    pl2 = v[0]
                    wikipedia.output(u"Found link to %s in:" % pl2.aslink())
                    self.whereReport(pl2, indent=4)
                    while 1:
                        if acceptall: 
                            answer = 'a'
                        else: 
                            answer = wikipedia.inputChoice(u'What should be done?', ['accept', 'reject', 'give up', 'accept all'], ['a', 'r', 'G', 'l'], 'G')
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
    
    def finish(self, sa = None):
        """Round up the subject, making any necessary changes. This method
           should be called exactly once after the todo list has gone empty.

           This contains a shortcut: if a subject array is given in the argument
           sa, just before submitting a page change to the live wiki it is
           checked whether we will have to wait. If that is the case, the sa will
           be told to make another get request first."""
        if not self.isDone():
            raise "Bugcheck: finish called before done"
        if self.inpl.isRedirectPage():
            return
        if not self.untranslated and globalvar.untranslatedonly:
            return
        if len(self.done) == 1:
            # No interwiki at all
            return
        wikipedia.output(u"======Post-processing %s======" % self.inpl.aslink())
        # Assemble list of accepted interwiki links
        new = self.assemble()
        if new == None: # User said give up or autonomous with problem
            return
        
        # Make sure new contains every page link, including the page we are processing
        # replaceLinks will skip the site it's working on.
        if not new.has_key(self.inpl.site()):
            new[self.inpl.site()] = self.inpl

        #self.replaceLinks(self.inpl, new, True, sa)

        updatedSites = []
        # Process all languages here
        for (site, page) in new.iteritems():
            # if we have an account for this site
            if config.usernames.has_key(site.family.name) and config.usernames[site.family.name].has_key(site.lang):
                if self.inpl.isDisambig() != page.isDisambig():
                    wikipedia.output(u"Cannot update %s, disambiguation flag doesn't match." % site.lang)
                else:
                    # Try to do the changes
                    if self.replaceLinks(page, new, sa):
                        # Changes were successful
                        updatedSites.append(site)
        for site in updatedSites:
            # don't report backlinks for pages we already changed
            del new[site]
        self.reportBacklinks(new)

    def replaceLinks(self, pl, new, sa):
        """
        Returns True if saving was successful.
        """
        wikipedia.output(u"Updating links on page %s." % pl.aslink(forceInterwiki = True))

        # sanity check - the page we are fixing must be the only one for that site.
        pltmp = new[pl.site()]
        if pltmp != pl:
            wikipedia.output(u"BUG: %s is not in the list of new links!" % pl.aslink())
            return False
            
        # Avoid adding a iw link back to itself
        # It must be added back on before exiting this method.
        del new[pl.site()]
        try:
            # Put interwiki links into a map
            old={}
            try:
                for pl2 in pl.interwiki():
                    old[pl2.site()] = pl2
            except wikipedia.NoPage:
                wikipedia.output(u"BUG: %s no longer exists?" % pl.aslink())
                return False

            # Check what needs to get done
            mods, removing = compareLanguages(old, new, insite = pl.site())
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
                    if removing:
                        self.problem('removing: %s'%(",".join([x.lang for x in removing])))
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
                            answer = wikipedia.inputChoice(u'Submit?', ['Yes', 'No'], ['y', 'N'], 'N')
                    else:
                        # If we do not need to ask, allow
                        answer = 'y'
                    # If we got permission to submit, do so
                    if answer == 'y':
                        # Check whether we will have to wait for wikipedia. If so, make
                        # another get-query first.
                        if sa:
                            while wikipedia.get_throttle.waittime() + 2.0 < wikipedia.put_throttle.waittime():
                                print "NOTE: Performing a recursive query first to save time...."
                                qdone = sa.oneQuery()
                                if not qdone:
                                    # Nothing more to do
                                    break
                        print "NOTE: Updating live wiki..."
                        timeout=60
                        while 1:
                            try:
                                # print "DBG> updating ", pl
                                status, reason, data = pl.put(newtext, comment=u'robot '+mods)
                            except (socket.error, IOError):
                                if timeout>3600:
                                    raise
                                wikipedia.output(u"ERROR putting page. Sleeping %i seconds before trying again" % timeout)
                                timeout *= 2
                                time.sleep(timeout)
                            else:
                                break
                        if str(status) == '302':
                            return True
                        else:
                            print status, reason

                return False
        finally:
            # re-add the pl back to the new links list.
            new[pl.site()] = pl

    def reportBacklinks(self, new):
        """Report missing back links. This will be called from finish() if
           needed."""
        try:
            for site, page in new.iteritems():
                if not page.section():
                    shouldlink = new.values() + [self.inpl]
                    linked = page.interwiki()
                    for xpage in shouldlink:
                        if xpage != page and not xpage in linked:
                            for l in linked:
                                if l.site() == xpage.site():
                                    wikipedia.output(u"WARNING: %s: %s does not link to %s but to %s" % (page.site().family.name, page.aslink(forceInterwiki = True), xpage.aslink(forceInterwiki = True), l.aslink(forceInterwiki = True)))
                                    break
                            else:
                                wikipedia.output(u"WARNING: %s: %s does not link to %s" % (page.site().family.name, page.aslink(forceInterwiki = True), xpage.aslink(forceInterwiki = True)))
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
                                wikipedia.output(u"WARNING: %s: %s links to incorrect %s" % (page.site().family.name, page.aslink(forceInterwiki = True), xpage.aslink(forceInterwiki = True)))
        except (socket.error, IOError):
            wikipedia.output(u'ERROR: could not report backlinks')
    
class SubjectArray(object):
    """A class keeping track of a list of subjects, controlling which pages
       are queried from which languages when."""
    
    def __init__(self):
        """Constructor. We always start with empty lists."""
        self.subjects = []
        self.counts = {}
        self.generator = None

    def add(self, pl, hints = None):
        """Add a single subject to the list"""
        subj = Subject(pl, hints = hints)
        self.subjects.append(subj)
        for site in subj.openSites():
            # Keep correct counters
            self.plus(site)

    def setGenerator(self, generator):
        """Add a generator of subjects. Once the list of subjects gets
           too small, this generator is called to produce more Pages"""
        self.generator = generator

    def dump(self, fn):
        f = codecs.open(fn, 'w', 'utf-8')
        for subj in self.subjects:
            f.write(subj.pl().aslink(None)+'\n')
        f.close()
        
    def generateMore(self, number):
        """Generate more subjects. This is called internally when the
           list of subjects becomes to small, but only if there is a
           generator"""
        fs = self.firstSubject()
        if fs:
            wikipedia.output(u"NOTE: The first unfinished subject is " + fs.pl().aslink())
        print "NOTE: Number of pages queued is %d, trying to add %d more."%(len(self.subjects), number)
        for i in range(number):
            try:
                pl=self.generator.next()
                while pl in globalvar.skip:
                    pl=self.generator.next()
                self.add(pl, hints = hints)
            except StopIteration:
                self.generator = None
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
            if self.generator and mycount < globalvar.maxquerysize:
                timeout = 60
                while timeout<3600:
                    try:
                        self.generateMore(globalvar.maxquerysize - mycount)
                    except wikipedia.NoPage:
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
        try:
            wikipedia.getall(site, plgroup)
        except wikipedia.SaxError:
            # Ignore this error, and get the pages the traditional way.
            pass
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
        return len(self) == 0 and self.generator is None

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
            removing.append(site)
        elif old[site] != new[site]:
            modifying.append(site)

    for site2 in new.keys():
        if site2 not in old:
            adding.append(site2)
    s = ""
    if adding:
        s = s + " %s:" % (wikipedia.translate(insite.lang, msg)[0]) + " " + ", ".join([x.lang for x in adding])
    if removing: 
        s = s + " %s:" % (wikipedia.translate(insite.lang, msg)[1]) + " " + ", ".join([x.lang for x in removing])
    if modifying:
        s = s + " %s:" % (wikipedia.translate(insite.lang, msg)[2]) + " " + ", ".join([x.lang for x in modifying])
    return s,removing

def readWarnfile(filename, sa):
    import warnfile
    reader = warnfile.WarnfileReader(filename)
    # we won't use removeHints
    (hints, removeHints) = reader.getHints()
    for page in hints.iterkeys():
        # The WarnfileReader gives us a list of pagelinks, but titletranslate.py expects a list of strings, so we convert it back.
        # TODO: This is a quite ugly hack, in the future we should maybe make titletranslate expect a list of pagelinks.
        hintStrings = []
        for hintedPage in hints[page]:
            #lang = 
            hintStrings.append('%s:%s' % (hintedPage.site().language(), hintedPage.linkname()))
        sa.add(page, hints = hintStrings)

#===========
        
globalvar=Global()
    
if __name__ == "__main__":
    try:
        inname = []
        hints = []
        start = None
        number = None
        warnfile = None
        # a page generator which doesn't give hints
        hintlessPageGen = None
        
        sa=SubjectArray()
        
        if not config.never_log:
            wikipedia.activateLog('interwiki.log')

        for arg in sys.argv[1:]:
            arg = wikipedia.argHandler(arg, 'interwiki')
            if arg:
                if arg == '-noauto':
                    globalvar.auto = False
                elif arg.startswith('-vertfile:'):
                    vertexgen.openFile(arg[10:])
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
                elif arg.startswith('-hint:'):
                    pass
                elif arg.startswith('-warnfile:'):
                    warnfile = arg[10:]
                elif arg == '-name':
                    globalvar.same = 'name'
                elif arg == '-confirm':
                    globalvar.confirm = True
                elif arg == '-autonomous':
                    globalvar.autonomous = True
                elif arg == '-noshownew':
                    globalvar.shownew = False
                elif arg == '-nobacklink':
                    globalvar.backlink = False
                elif arg == '-noredirect':
                    globalvar.followredirect = False
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
                    for page in skipPageGen():
                        globalvar.skip.add(page)
                elif arg == '-restore':
                    hintlessPageGen = pagegenerators.TextfilePageGenerator('interwiki.dump')
                elif arg == '-continue':
                    hintlessPageGen = pagegenerators.TextfilePageGenerator('interwiki.dump')
                    # We waste this generator to find out the last page's title
                    # This is an ugly workaround.
                    for page in hintlessPageGen():
                        pass
                    try:
                        start = page.linkname()
                    except NameError:
                        print "Dump file is empty?! Starting at the beginning."
                        start = "!"
                    # old generator is used up, create a new one
                    hintlessPageGen = pagegenerators.TextfilePageGenerator('interwiki.dump')
                elif arg.startswith('-file:'):
                    hintlessPageGen = pagegenerators.TextfilePageGenerator(arg[6:])
                elif arg == '-start':
                    start = '_'                     # start page will be entered interactively
                elif arg.startswith('-start:'):
                    if len(arg) == 7:
                        start = '_'                 # start page will be entered interactively
                    else:
                        start = arg[7:]
                elif arg.startswith('-number:'):
                    number = int(arg[8:])
                elif arg.startswith('-array:'):
                    globalvar.minarraysize = int(arg[7:])
                    if globalvar.minarraysize < globalvar.maxquerysize:
                        globalvar.maxquerysize = globalvar.minarraysize
                elif arg.startswith('-neverlink:'):
                    globalvar.neverlink += arg[11:].split(",")
                elif arg.startswith('-showpage'):
                    globalvar.showtextlink += globalvar.showtextlinkadd
                else:
                    inname.append(arg)

        if hintlessPageGen:
            for page in hintlessPageGen():
                sa.add(page, hints=hints)

        if warnfile:
            readWarnfile(warnfile, sa)

        if start:
            if start == '_':
                start = wikipedia.input(u'Which page to start from: ')

            namespace = wikipedia.Page(wikipedia.getSite(),start).namespace()
            if number:
                wikipedia.output(u"Treating %d pages starting at %s" % (number, start))
                if namespace != 0:
                    start = ':'.join(start.split(':')[1:])
                i = 0
                for pl in wikipedia.allpages(start = start, namespace = namespace):
                    sa.add(pl,hints=hints)
                    i += 1
                    if i >= number:
                        break
            else:
                print "Treating pages starting at %s" % start
                if namespace != 0:
                    start = ':'.join(start.split(':')[1:])
                sa.setGenerator(wikipedia.allpages(start = start, namespace = namespace))

        inname = '_'.join(inname)
        if sa.isDone() and not inname:
            inname = wikipedia.input(u'Which page to check: ')

        if inname:
            inpl = wikipedia.Page(wikipedia.getSite(), inname)
            sa.add(inpl, hints = hints)

        try:
            sa.run()
        except KeyboardInterrupt:
            sa.dump('interwiki.dump')
        except:
            sa.dump('interwiki.dump')
            raise

    finally:
        wikipedia.stopme()
