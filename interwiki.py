#coding: iso-8859-1
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
                   useful if you specify a single page to work on.
                   
    -same:         try to translate the page to other languages by
                   testing whether a page with the same name exists on each of
                   the other known wikipedias

    -name:         similar to -same, but UPPERCASE the last name for eo:

    -untranslated: untranslated pages are not skipped; instead in those
                   cases interactively a translation hint is asked of the user.

    -confirm:      ask for confirmation before any page is changed on the
                   live wikipedia. Without this argument, additions and
                   unambiguous modifications are made without confirmation.

    -autonomous:   run automatically, do not ask any questions. If a question
                   to an operator is needed, write the name of the page
                   to autonomous_problems.dat and continue on the next page.

    -test:         run on three pages named "Scheikunde", "Natuurkunde",
                   and "Wiskunde". This is a trivial test of the functionality.

    -nobell:       do not use the terminal bell to announce a question

    -nolog:        switch off the log file

    -nobacklink:   switch off the backlink warnings

    -start:        used as -start:pagename, specifies that the robot should
                   go alphabetically through all pages on the home wikipedia,
                   starting at the named page.

    -number:       used as -number:#, specifies that the robot should process
                   that amount of pages and then stop. This is only useful in
                   combination with -start. The default is not to stop.
                   
    Arguments that are interpreted by more bots:

    -lang:         specifies the language the bot is run on (e.g. -lang:de).
                   Overwrites the settings in username.dat


Two configuration options can be used to change the workings of this robot:

treelang_backlink: if set to True, all problems in foreign wikipedias will
                   be reported
treelang_log:      if set to True, all messages will be logged to a file
                   as well as being displayed to the screen.

Both these options are set to True by default. They can be changed through
the user-config.py configuration file.

"""
#
# (C) Rob W.W. Hooft, 2003
#
# Distribute under the terms of the PSF license.
#
__version__ = '$Id$'
#
import sys, copy, re

import wikipedia, config, unequal

msg = {
    'en':('Adding','Removing','Modifying'),
    'nl':('Erbij','Eraf','Anders'),
    'da':('Tilføjer','Fjerner','Ændrer'),
    'fr':('Ajoute','Retire','Modifie'),
    'de':('Ergänze','Entferne','Ändere'),
    }

class Global:
    """Container class for global settings.
       Use of globals outside of this is to be avoided."""
    always = False
    autonomous = False
    backlink = config.treelang_backlink
    bell = True
    confirm = False
    debug = True
    force = False
    forreal = True
    log = config.treelang_log
    minquerysize = 10
    maxquerysize = 60
    same = False
    untranslated = False
    
class Subject:
    """Class to follow the progress of a single 'subject' (i.e. a page with
       all its translations)"""
    def __init__(self, pl, hints = None):
        """Constructor. Takes as arguments the PageLink on the home wikipedia
           plus optionally a list of hints for translation"""
        # Remember the "origin page"
        self.inpl = pl
        # Mark the origin page as todo.
        self.todo = {pl:pl.code()}
        # Nothing has been done yet
        self.done = {}
        # Add the translations given in the hints.
        self.translate(hints)
        if globalvar.confirm:
            self.confirm = 1
        else:
            self.confirm = 0

    def pl(self):
        """Return the PageLink on the home wikipedia"""
        return self.inpl
    
    def translate(self, hints = None):
        """Add the translation hints given to the todo list"""
        import titletranslate
        arr = {}
        titletranslate.translate(self.inpl, arr, same = globalvar.same, hints = hints)
        for pl in arr.iterkeys():
            self.todo[pl] = pl.code()

    def openCodes(self):
        """Return a list of language codes for all things we still need to do"""
        return self.todo.values()

    def willWorkOn(self, code):
        """By calling this method, you 'promise' this instance that you will
           work on any todo items in the language given by 'code'. This routine
           will return a list of pages that can be treated."""
        # Bug-check: Isn't there any work still in progress?
        if hasattr(self,'pending'):
            raise 'Cant start on %s; still working on %s'%(code,self.pending)
        # Prepare a list of suitable pages
        self.pending=[]
        for pl in self.todo.keys():
            if pl.code() == code:
                self.pending.append(pl)
                del self.todo[pl]
        # If there are any, return them. Otherwise, nothing is in progress.
        if self.pending:
            return self.pending
        else:
            del self.pending
            return None

    def conditionalAdd(self, pl, counter):
        """Add the pagelink given to the todo list, but only if we didn't know
           it before. If it is added, update the counter accordingly."""
        if (pl not in self.done and
            pl not in self.todo and
            pl not in self.pending):
            self.todo[pl] = pl.code()
            counter.plus(pl.code())
            #print "DBG> Found new to do:",pl.asasciilink()
        
    def workDone(self, counter):
        """This is called by a worker to tell us that the promised work
           was completed as far as possible. The only argument is an instance
           of a counter class, that has methods minus() and plus() to keep
           counts of the total work todo."""
        # Loop over all the pages that should have been taken care of
        for pl in self.pending:
            # Mark the page as done
            self.done[pl] = pl.code()
            # Register this fact at the todo-counter.
            counter.minus(pl.code())
            # Now check whether any interwiki links should be added to the
            # todo list.
            if unequal.bigger(pl, self.inpl):
                print "NOTE: %s is bigger than %s, not following references" % (pl, self.inpl)
            else:
                try:
                    iw = pl.interwiki()
                except wikipedia.IsRedirectPage,arg:
                    pl3 = wikipedia.PageLink(pl.code(),arg.args[0])
                    print "NOTE: %s is redirect to %s"% (pl.asasciilink(), pl3.asasciilink())
                    self.conditionalAdd(pl3, counter)
                except wikipedia.NoPage:
                    pass
                else:
                    for pl2 in iw:
                        self.conditionalAdd(pl2, counter)
        # These pages are no longer 'in progress'
        del self.pending
        # Check whether we need hints and the user offered to give them
        if len(self.done) == 1 and len(self.todo) == 0 and globalvar.untranslated:
            if globalvar.bell:
                sys.stdout.write('\07')
            print "%s does not have any interwiki links"%self.inpl.asasciilink()
            newhint = raw_input("Hint:")
            if newhint:
                arr = {}
                titletranslate.translate(pl, arr, same = False,
                                         hints = [newhint])
                for pl in arr.iterkeys():
                    self.todo[pl] = pl.code()

    def isDone(self):
        """Return True if all the work for this subject has completed."""
        return len(self.todo) == 0

    def problem(self, txt):
        """Report a problem with the resolution of this subject."""
        print "ERROR: %s"%txt
        self.confirm += 1
        if globalvar.autonomous:
            f=open('autonomous_problem.dat', 'a')
            f.write("%s {%s}\n" % (self.inpl, txt))
            f.close()
            
    def finish(self):
        """Round up the subject, making any necessary changes. This method
           should be called exactly once after the todo list has gone empty."""
        if self.inpl.isRedirectPage():
            return
        if not self.isDone():
            raise "Bugcheck: finish called before done"
        print "======Post-processing %s======"%(self.inpl.asasciilink())
        # Assemble list of accepted interwiki links
        new = {}
        for pl in self.done.keys():
            code = pl.code()
            if code == wikipedia.mylang and self.done[pl] is not None:
                if pl != self.inpl:
                    self.problem('Someone refers to %s with us' % pl.asasciilink())
            elif pl.exists() and not pl.isRedirectPage():
                if new.has_key(code) and new[code] != pl:
                    self.problem("'%s' as well as '%s'" % (new[code].asasciilink(), pl.asasciilink()))
                    if globalvar.autonomous:
                        return
                    while 1:
                        if globalvar.bell:
                            sys.stdout.write('\07')
                        answer = raw_input("Use (f)ormer or (l)atter or (n)either or (g)ive up?")
                        if answer.startswith('f'):
                            break
                        elif answer.startswith('l'):
                            new[pl.code()] = pl
                            break
                        elif answer.startswith('n'):
                            new[pl.code()] = None
                            break
                        elif answer.startswith('g'):
                            # Give up
                            return
                elif code in ('zh-tw','zh-cn') and new.has_key('zh') and new['zh'] is not None:
                    print "NOTE: Ignoring %s, using %s"%(new['zh'].asasciilink(),pl.asasciilink())
                    new['zh'] = None # Remove the global zh link
                    new[code] = pl # Add the more precise one
                elif code == 'zh' and (
                    (new.has_key('zh-tw') and new['zh-tw'] is not None) or
                    (new.has_key('zh-cn') and new['zh-cn'] is not None)):
                    print "NOTE: Ignoring %s"%(pl.asasciilink())
                    pass # do not add global zh if there is a specific zh-tw or zh-cn
                elif code not in new:
                    new[code] = pl

        # Remove the neithers
        for k,v in new.items():
            if v is None:
                del new[k]

        print "==status=="
        old={}
        try:
            for pl in self.inpl.interwiki():
                old[pl.code()] = pl
        except wikipedia.NoPage:
            print "BUG:", self.inpl.asasciilink(), "No longer exists?"
        ####
        mods, removing = compareLanguages(old, new)
        if not mods and not globalvar.always:
            print "No changes needed"
        else:
            if mods:
                print "Changes to be made:",mods
            oldtext = self.inpl.get()
            newtext = wikipedia.replaceLanguageLinks(oldtext, new)
            if globalvar.debug:
                import difflib
                for line in difflib.ndiff(oldtext.split('\r\n'),newtext.split('\r\n')):
                    if line[0] in ['+','-']:
                        print repr(line)[2:-1]
            if newtext != oldtext:
                print "NOTE: Replace %s" % self.inpl.asasciilink()
                if globalvar.forreal:
                    if removing and not globalvar.force:
                        self.problem('removing: %s'%(",".join(removing)))
                        if not globalvar.autonomous:
                            if globalvar.bell:
                                sys.stdout.write('\07')
                            answer = raw_input('submit y/n ?')
                        else:
                            answer = 'n'
                    else:
                        answer = 'y'
                    if answer == 'y':
                        print "NOTE: Updating live wikipedia..."
                        status, reason, data = self.inpl.put(newtext,
                                                             comment='robot '+mods)
                        if str(status) != '302':
                            print status, reason
                        else:
                            if globalvar.backlink:
                                self.reportBacklinks(new)

    def reportBacklinks(self, new):
        """Report missing back links. This will be called from finish() if
           needed."""
        for code in new.keys():
            pl = new[code]
            if not unequal.bigger(self.inpl, pl):
                shouldlink = new.values() + [self.inpl]
                linked = pl.interwiki()
                for xpl in shouldlink:
                    if xpl != pl and not xpl in linked:
                        for l in linked:
                            if l.code() == xpl.code():
                                print "WARNING:", pl.asasciiselflink(), "does not link to", xpl.asasciilink(), "but to", l.asasciilink()
                                break
                        else:
                            print "WARNING:", pl.asasciiselflink(), "does not link to", xpl.asasciilink()
                # Check for superfluous links
                for xpl in linked:
                    if not xpl in shouldlink:
                        # Check whether there is an alternative page on that language.
                        for l in shouldlink:
                            if l.code() == xpl.code():
                                # Already reported above.
                                break
                        else:
                            # New warning
                            print "WARNING:", pl.asasciiselflink(), "links to incorrect", xpl.asasciilink()
    
class SubjectArray:
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
        for code in subj.openCodes():
            # Keep correct counters
            self.plus(code)

    def setGenerator(self, generator):
        """Add a generator of subjects. Once the list of subjects gets
           too small, this generator is called to produce more PageLinks"""
        self.generator = generator

    def generateMore(self, number):
        """Generate more subjects. This is called internally when the
           list of subjects becomes to small, but only if there is a
           generator"""
        fs = self.firstSubject()
        if fs:
            print "NOTE: The first unfinished subject is:", fs.pl().asasciilink()
        print "NOTE: Number of pages queued is %d, trying to add %d more."%(
            len(self.subjects), number)
        for i in range(number):
            try:
                self.add(self.generator.next())
            except StopIteration:
                self.generator = None
                break

    def firstSubject(self):
        """Return the first subject that is still being worked on"""
        if self.subjects:
            return self.subjects[0]
        
    def maxOpenCode(self):
        """Return the code of the foreign language that has the most
           open queries plus the number. If there is nothing left, return
           None, 0"""
        max = 0
        maxlang = None
        for lang, count in self.counts.iteritems():
            if lang != wikipedia.mylang:
                if count > max:
                    max = count
                    maxlang = lang
        return maxlang, max

    def selectQueryCode(self):
        """Select the language code the next query should go out for."""
        # First see how many foreign page queries we can find.
        maxlang, max = self.maxOpenCode()
        # If that number is too small, we need drastic measures.
        if max >= globalvar.minquerysize:
            return maxlang
        # How many home-language queries we still have?
        mycount = self.counts.get(wikipedia.mylang,0)
        # Can we make more home-language queries by adding subjects?
        if self.generator and mycount < globalvar.maxquerysize:
            self.generateMore(globalvar.maxquerysize - mycount)
        # If we have any, getting the home language is a good thing.
        if self.counts[wikipedia.mylang] > 0:
            return wikipedia.mylang
        # Otherwise go for the foreign language anyway
        return maxlang
    
    def queryStep(self):
        """Perform one step in the solution process"""
        # First find the best language to work on
        code = self.selectQueryCode()
        # Now assemble a reasonable list of pages to get
        group = []
        plgroup = []
        for subj in self.subjects:
            # Promise the subject that we will work on the code language
            # We will get a list of pages we can do.
            x = subj.willWorkOn(code)
            if x:
                plgroup.extend(x)
                group.append(subj)
                if len(plgroup)>=globalvar.maxquerysize:
                    break
        # Get the content of the assembled list in one blow
        wikipedia.getall(code, plgroup)
        # Tell all of the subjects that the promised work is done
        for subj in group:
            subj.workDone(self)
        # Delete the ones that are done now.
        for i in range(len(self.subjects)-1, -1, -1):
            subj = self.subjects[i]
            if subj.isDone():
                subj.finish()
                del self.subjects[i]

    def isDone(self):
        """Check whether there is still more work to do"""
        return len(self.subjects) == 0 and self.generator is None

    def plus(self, code):
        """This is a routine that the Subject class expects in a counter"""
        try:
            self.counts[code] += 1
        except KeyError:
            self.counts[code] = 1

    def minus(self, code):
        """This is a routine that the Subject class expects in a counter"""
        self.counts[code] -= 1
        
    def run(self):
        """Start the process until finished"""
        while not self.isDone():
            self.queryStep()
    
def compareLanguages(old, new):
    removing = []
    adding = []
    modifying = []
    for code in old.keys():
        if code not in new.keys():
            removing.append(code)
        elif old[code] != new[code]:
            modifying.append(code)

    for code2 in new.keys():
        if code2 not in old.keys():
            adding.append(code2)
    s = ""
    if adding:
        s = s + " %s:" % (msg[msglang][0]) + ",".join(adding)
    if removing: 
        s = s + " %s:" % (msg[msglang][1]) + ",".join(removing)
    if modifying:
        s = s + " %s:" % (msg[msglang][2]) + ",".join(modifying)
    return s,removing

#===========
        
globalvar=Global()
    
if __name__ == "__main__":
    inname = []
    hints = []
    mode = 1
    start = None
    number = None
    for arg in sys.argv[1:]:
        if wikipedia.argHandler(arg):
            pass
        elif arg == '-force':
            globalvar.force = True
        elif arg == '-always':
            globalvar.always = True
        elif arg == '-same':
            globalvar.same = True
        elif arg == '-untranslated':
            globalvar.untranslated = True
        elif arg.startswith('-hint:'):
            hints.append(arg[6:])
        elif arg == '-name':
            globalvar.same = 'name'
        elif arg == '-confirm':
            globalvar.confirm = True
        elif arg == '-autonomous':
            globalvar.autonomous = True
        elif arg == '-nolog':
            globalvar.log = False
        elif arg == '-nobacklink':
            globalvar.backlink = False
        elif arg == '-nobell':
            globalvar.bell = False
        elif arg == '-test':
            mode = 2
        elif arg.startswith('-start:'):
            mode = 3
            start = arg[7:]
        elif arg.startswith('-number:'):
            number = int(arg[8:])
        else:
            inname.append(arg)

    if msg.has_key(wikipedia.mylang):
        msglang = wikipedia.mylang
    else:
        msglang = 'en'

    if globalvar.log:
        import logger
        sys.stdout = logger.Logger(sys.stdout, filename = 'treelang.log')

    unequal.read_exceptions()
    
    sa=SubjectArray()

    if mode == 1:
        inname = '_'.join(inname)
        if not inname:
            inname = raw_input('Which page to check:')

        inpl = wikipedia.PageLink(wikipedia.mylang, inname)

        sa.add(inpl, hints = hints)
    elif mode == 2:
        sa.add(wikipedia.PageLink(wikipedia.mylang, 'Scheikunde'))
        sa.add(wikipedia.PageLink(wikipedia.mylang, 'Wiskunde'))
        sa.add(wikipedia.PageLink(wikipedia.mylang, 'Natuurkunde'))
    elif mode == 3 and number:
        print "Treating %d pages starting at %s" % (number, start)
        i = 0
        for pl in wikipedia.allpages(start = start):
            sa.add(pl)
            i += 1
            if i >= number:
                break
    elif mode == 3 and not number:
        print "Treating pages starting at %s" % start
        sa.setGenerator(wikipedia.allpages(start = start))
        
    try:
        sa.run()
    except KeyboardInterrupt:
        print "Process was interrupted."
        print "The first unfinished subject is:",sa.firstSubject().pl().asasciilink()
        
