# -*- coding: utf-8  -*-
"""
This bot is used for checking external links found at the wiki. It checks
several pages at once, with a limit set by the config variable
max_external_links, which defaults to 50.

The bot won't change any wiki pages, it will only report dead links such that
people can fix or remove the links themselves.

The bot will store all links found dead in a .dat file in the deadlinks
subdirectory. To avoid the removing of links which are only temporarily
unavailable, the bot only reports links which were reported dead at least
two times, with a time lag of at least one week. Such links will be logged to a
.txt file in the deadlinks subdirectory.

In addition to the logging step, it is possible to automatically report dead
links to the talk page of the article where the link was found. To use this
feature, set report_dead_links_on_talk = True in your user-config.py, or
specify "-talk" on the command line. Adding "-notalk" switches this off
irrespective of the configuration variable.

When a link is found alive, it will be removed from the .dat file.

Syntax examples:
    python weblinkchecker.py
        Loads all wiki pages in alphabetical order using the Special:Allpages
        feature.

    python weblinkchecker.py -start:Example_page
        Loads all wiki pages using the Special:Allpages feature, starting at
        "Example page"
    
    python weblinkchecker.py Example page
        Only checks links found in the wiki page "Example page"
"""

#
# (C) Daniel Herding, 2005
#
# Distributed under the terms of the MIT license.
#
__version__='$Id$'

import wikipedia, config, pagegenerators
import sys, re
import codecs, pickle
import httplib, socket, urlparse
import threading, time

talk_report_msg = {
    'de': u'Bot: Berichte nicht verfügbaren Weblink',
    'en': u'robot: Reporting unavailable external link',
    'he': u'רובוט: מדווח על קישור חיצוני בלתי זמין',
    'ia': u'Robot: Reporto de un ligamine externe non functionante',
    'pt': u'Bot: Checando links externos',
    'sr': u'Бот: Пријављивање непостојећих спољашњих повезница',
}

talk_report = {
    'de': u'== Toter Weblink ==\n\nBei mehreren automatisierten Botläufen wurde der folgende Weblink als nicht verfügbar erkannt. Bitte überprüfe, ob der Link tatsächlich unerreichbar ist, und korrigiere oder entferne ihn in diesem Fall!\n\n%s\n--~~~~',
    'en': u'== Dead link ==\n\nDuring several automated bot runs the following external link was found to be unavailable. Please check if the link is in fact down and fix or remove it in that case!\n\n%s\n--~~~~',
    'he': u'== קישור שבור ==\n\nבמהלך מספר ריצות אוטומטיות של הבוט, נמצא שהקישור החיצוני הבא אינו זמין. אנא בדקו אם הקישור אכן שבור, ותקנו אותו או הסירו את הפיסקאות הללו במקרה זה!\n\n%s\n--~~~~',
    'ia': u'== Ligamine defuncte ==\n\nDurante plure sessiones automatic, le robot ha constatate que le sequente ligamine externe non es disponibile. Per favor confirma que le ligamine de facto es defuncte, e in caso de si, repara o elimina lo!\n\n%s\n--~~~~',
    'pt': u'== Link quebrado ==\n\nFoi checado os links externos deste artigo por vários minutos. Verifique por favor se a ligação estiver fora do ar e tente arrumá-lo ou removê-la!\n\n%s\n --~~~~ ',
    'sr': u'== Покварене спољашње повезнице ==\n\nТоком неколико аутоматски провера, бот је пронашао покварене спољашње повезнице. Молимо вас проверите да ли је повезница добра, поправите је или је уклоните!\n\n%s\n--~~~~',
}

ignorelist = [
    re.compile('.*[\./@]example.com(/.*)?'), # reserved for documentation
    re.compile('.*[\./@]example.net(/.*)?'), # reserved for documentation
    re.compile('.*[\./@]example.org(/.*)?'), # reserved for documentation
    re.compile('.*[\./@]gso.gbv.de(/.*)?'),  # bot somehow can't handle their redirects 
    re.compile('.*[\./@]berlinonline.de(/.*)?'), # a de: user wants to fix them by hand and doesn't want them to be deleted, see [[de:Benutzer:BLueFiSH.as/BZ]].
]

class Global(object):
    talk = config.report_dead_links_on_talk

    def handleArgs(self, args):
        unhandledArguments = []
        for arg in args:
            if arg == '-talk':
                self.talk = True
            elif arg == '-notalk':
                self.talk = False
            else:
                unhandledArguments.append(arg)
        return unhandledArguments

globalvar = Global()

def weblinksIn(text, withoutBracketed = False, onlyBracketed = False):
    # RFC 2396 says that URLs may only contain certain characters.
    # For this regex we also accept non-allowed characters, so that the bot
    # will later show these links as broken ('Non-ASCII Characters in URL').
    # Note: While allowing parenthesis inside URLs, MediaWiki will regard
    # right parenthesis at the end of the URL as not part of that URL.
    # The same applies to dot, comma, colon and some other characters.
    # MediaWiki allows closing curly braces inside links, but such braces
    # often come from templates where URLs are parameters, so as a
    # workaround we won't allow them inside links here. The same is true
    # for the vertical bar.
    notAtEnd = '\]\s\)\.:;,<>}\|"'
    # So characters inside the URL can be anything except whitespace,
    # closing squared brackets, quotation marks, greater than and less
    # than, and the last character also can't be parenthesis or another
    # character disallowed by MediaWiki.
    notInside = '\]\s<>}"'
    # The first half of this regular expression is required because '' is
    # not allowed inside links. For example, in this wiki text:
    #       ''Please see http://www.example.org.''
    # .'' shouldn't be considered as part of the link.
    regex = r'(?P<url>http[s]?://[^' + notInside + ']*?[^' + notAtEnd + '](?=[' + notAtEnd+ ']*\'\')|http[s]?://[^' + notInside + ']*[^' + notAtEnd + '])'
    
    if withoutBracketed:
        regex = r'(?<!\[)' + regex
    elif onlyBracketed:
        regex = r'\[' + regex
    linkR = re.compile(regex)
    # Remove HTML comments in URLs as well as URLs in HTML comments.
    # Also remove text inside nowiki links
    text = re.sub('(?s)<nowiki>.*?</nowiki>|<!--.*?-->', '', text)
    for m in linkR.finditer(text):
        yield m.group('url')

class LinkChecker(object):
    '''
    Given a HTTP URL, tries to load the page from the Internet and checks if it
    is still online.
    
    Returns a (boolean, string) tuple saying if the page is online and including
    a status reason.
    
    Warning: Also returns false if your Internet connection isn't working
    correctly! (This will give a Socket Error)
    '''
    def __init__(self, url, redirectChain = []):
        """
        redirectChain is a list of redirects which were resolved by
        resolveRedirect(). This is needed to detect redirect loops.
        """
        self.url = url
        self.redirectChain = redirectChain + [url]
        self.changeUrl(url)
        self.header = {
            # 'User-agent': wikipedia.useragent,
            # we fake being Firefox because some webservers block unknown
            # clients, e.g. http://images.google.de/images?q=Albit gives a 403
            # when using the PyWikipediaBot user agent.
            'User-agent': 'Mozilla/5.0 (X11; U; Linux i686; de; rv:1.8) Gecko/20051128 SUSE/1.5-0.1 Firefox/1.5',
            'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
            'Accept-Language': 'de-de,de;q=0.8,en-us;q=0.5,en;q=0.3',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '30',
            'Connection': 'keep-alive',
            }

    def changeUrl(self, url):
        self.url = url
        # we ignore the fragment
        self.scheme, self.host, self.path, self.query, self.fragment = urlparse.urlsplit(self.url)
        if not self.path:
            self.path = '/'
        if self.query:
            self.query = '?' + self.query
        self.protocol = url.split(':', 1)[0]
        

    def resolveRedirect(self, useHEAD = True):
        '''
        Requests the header from the server. If the page is an HTTP redirect,
        returns the redirect target URL as a string. Otherwise returns None.
        
        If useHEAD is true, uses the HTTP HEAD method, which saves bandwidth
        by not downloading the body. Otherwise, the HTTP GET method is used.
        '''
        if self.scheme == 'http':
            conn = httplib.HTTPConnection(self.host)
        elif self.scheme == 'https':
            conn = httplib.HTTPSConnection(self.host)
        try:
            if useHEAD:
                conn.request('HEAD', '%s%s' % (self.path, self.query), None, self.header)
            else:
                conn.request('GET', '%s%s' % (self.path, self.query), None, self.header)
            response = conn.getresponse()
        except httplib.BadStatusLine:
            # Some servers don't seem to handle HEAD requests properly,
            # e.g. http://www.radiorus.ru/ which is running on a very old
            # Apache server. Using GET instead works on these (but it uses
            # more bandwidth).
            return self.resolveRedirect(useHEAD = False)
        if response.status >= 300 and response.status <= 399:
            #print response.getheaders()
            redirTarget = response.getheader('Location')
            #print "redirTarget:", redirTarget
            if redirTarget:
                if redirTarget.startswith('http://') or redirTarget.startswith('https://'):
                    self.changeUrl(redirTarget)
                    return True
                elif redirTarget.startswith('/'):
                    self.changeUrl('%s://%s%s' % (self.protocol, self.host, redirTarget))
                    return True
                else: # redirect to relative position
                    # cut off filename
                    directory = self.path[:self.path.rindex('/') + 1]
                    # handle redirect to parent directory
                    while redirTarget.startswith('../'):
                        redirTarget = redirTarget[3:]
                        # change /foo/bar/ to /foo/
                        directory = directory[:-1]
                        directory = directory[:directory.rindex('/') + 1]
                    self.changeUrl('%s://%s%s%s' % (self.protocol, self.host, directory, redirTarget))
                    return True
        else:
            return False # not a redirect
            
    def check(self, useHEAD = True):
        """
        Returns True and the server status message if the page is alive.
        Otherwise returns false
        """
        try:
            wasRedirected = self.resolveRedirect(useHEAD = useHEAD)
        except httplib.error, arg:
            return False, u'HTTP Error: %s' % arg
        except socket.error, arg:
            return False, u'Socket Error: %s' % arg
        #except UnicodeEncodeError, arg:
        #    return False, u'Non-ASCII Characters in URL: %s' % arg
        if wasRedirected:
            if self.url in self.redirectChain:
                if useHEAD:
                    # Some servers don't seem to handle HEAD requests properly,
                    # which leads to a cyclic list of redirects.
                    # We simply start from the beginning, but this time,
                    # we don't use HEAD, but GET requests.
                    redirChecker = LinkChecker(self.redirectChain[0])
                    return redirChecker.check(useHEAD = False)
                else:
                    return False, u'HTTP Redirect Loop: %s' % ' -> '.join(self.redirectChain + [self.url])
            elif len(self.redirectChain) >= 19:
                if useHEAD:
                    # Some servers don't seem to handle HEAD requests properly,
                    # which leads to a long (or infinite) list of redirects.
                    # We simply start from the beginning, but this time,
                    # we don't use HEAD, but GET requests.
                    redirChecker = LinkChecker(self.redirectChain[0])
                    return redirChecker.check(useHEAD = False)
                else:
                    return False, u'Long Chain of Redirects: %s' % ' -> '.join(self.redirectChain + [self.url])
            else:
                redirChecker = LinkChecker(self.url, self.redirectChain)
                return redirChecker.check(useHEAD = useHEAD)
        else:
            try:
                if self.scheme == 'http':
                    conn = httplib.HTTPConnection(self.host)
                elif self.scheme == 'https':
                    conn = httplib.HTTPSConnection(self.host)
            except httplib.error, arg:
                return False, u'HTTP Error: %s' % arg
            try:
                conn.request('GET', '%s%s' % (self.path, self.query), None, self.header)
            except socket.error, arg:
                return False, u'Socket Error: %s' % arg
            except UnicodeEncodeError, arg:
                return False, u'Non-ASCII Characters in URL: %s' % arg
            try:
                response = conn.getresponse()
            except Exception, arg:
                return False, u'Error: %s' % arg
            #wikipedia.output('%s: %s' % (self.url, response.status))
            # site down if the server status is between 400 and 499
            siteDown = response.status in range(400, 500)
            return not siteDown, '%s %s' % (response.status, response.reason)

class LinkCheckThread(threading.Thread):
    '''
    A thread responsible for checking one page. After checking the page, it
    will die.
    '''
    def __init__(self, page, url, history):
        threading.Thread.__init__(self)
        self.page = page
        self.url = url
        self.history = history
        
    def run(self):
        linkChecker = LinkChecker(self.url)
        try:
            ok, message = linkChecker.check()
        except:
            wikipedia.output('Exception while processing URL %s in page %s' % (self.url, self.page.title()))
            raise
        if ok:
            if self.history.setLinkAlive(self.url):
                wikipedia.output('*Link to %s in [[%s]] is back alive.' % (self.url, self.page.title()))
        else:
            wikipedia.output('*[[%s]] links to %s - %s.' % (self.page.title(), self.url, message))
            self.history.setLinkDead(self.url, message, self.page)

class History:
    '''
    Stores previously found dead links.
    The URLs are dictionary keys, and values are lists of tuples where each tuple
    represents one time the URL was found dead. Tuples have the form
    (title, date, error) where title is the wiki page where the URL was found,
    date is an instance of time, and error is a string with error code and
    message.

    We assume that the first element in the list represents the first time we
    found this dead link, and the last element represents the last time.
    
    Example:
            
    dict = {
        'http://www.example.org/page': [
            ('WikiPageTitle', DATE, '404: File not found'),
            ('WikiPageName2', DATE, '404: File not found'),
        ]
    '''
   
    def __init__(self, reportThread):
        self.reportThread = reportThread
        site = wikipedia.getSite()
        self.semaphore = threading.Semaphore()
        self.datfilename = 'deadlinks/deadlinks-%s-%s.dat' % (site.family.name, site.lang)
        # Count the number of logged links, so that we can insert captions
        # from time to time
        self.logCount = 0
        try:
            datfile = open(self.datfilename, 'r')
            self.historyDict = pickle.load(datfile)
            datfile.close()
        except (IOError, EOFError):
            # no saved history exists yet, or history dump broken
            self.historyDict = {}

    def log(self, url, error, containingPage):
        """
        Logs an error report to a text file in the deadlinks subdirectory.
        """
        site = wikipedia.getSite()
        errorReport = u'* %s\n' % url
        for (pageTitle, date, error) in self.historyDict[url]:
            # ISO 8601 formulation
            isoDate = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(date))
            errorReport += "** In [[%s]] on %s, %s\n" % (pageTitle, isoDate, error)
        wikipedia.output(u"** Logging link for deletion.")
        txtfilename = 'deadlinks/results-%s-%s.txt' % (site.family.name, site.lang)
        txtfile = codecs.open(txtfilename, 'a', 'utf-8')
        self.logCount += 1
        if self.logCount % 30 == 0:
            # insert a caption
            txtfile.write('=== %s ===\n' % containingPage.title()[:3])
        txtfile.write(errorReport)
        txtfile.close()
        if self.reportThread and not containingPage.isTalkPage():
            self.reportThread.report(url, errorReport, containingPage)
    
            
    def setLinkDead(self, url, error, page):
        """
        Adds the fact that the link was found dead to the .dat file.
        """
        self.semaphore.acquire()
        now = time.time()
        if self.historyDict.has_key(url):
            timeSinceFirstFound = now - self.historyDict[url][0][1]
            timeSinceLastFound= now - self.historyDict[url][-1][1]
            # if the last time we found this dead link is less than an hour
            # ago, we won't save it in the history this time.
            if timeSinceLastFound > 60 * 60:
                self.historyDict[url].append((page.title(), now, error))
            # if the first time we found this link longer than a week ago,
            # it should probably be fixed or removed. We'll list it in a file
            # so that it can be removed manually.
            if timeSinceFirstFound > 60 * 60 * 24 * 7:
                self.log(url, error, page)
        else:
            self.historyDict[url] = [(page.title(), now, error)]
        self.semaphore.release()

    def setLinkAlive(self, url):
        """
        If the link was previously found dead, removes it from the .dat file
        and returns True, else returns False.
        """
        if self.historyDict.has_key(url):
            self.semaphore.acquire()
            try:
                del self.historyDict[url]
            except KeyError:
                # Not sure why this can happen, but I guess we can ignore this...
                pass
            self.semaphore.release()
            return True
        else:
            return False
        
    def save(self):
        """
        Saves the .dat file to disk.
        """
        datfile = open(self.datfilename, 'w')
        self.historyDict = pickle.dump(self.historyDict, datfile)
        datfile.close()

class DeadLinkReportThread(threading.Thread):
    '''
    A Thread that is responsible for posting error reports on talk pages. There
    will only be one DeadLinkReportThread, and it is using a semaphore to make
    sure that two LinkCheckerThreads can not access the queue at the same time.
    '''
    def __init__(self):
        threading.Thread.__init__(self)
        self.semaphore = threading.Semaphore()
        self.queue =  [];
        self.finishing = False
        self.killed = False
    
    def report(self, url, errorReport, containingPage):
        """
        Tries to add an error report to the talk page belonging to the page containing the dead link.
        """
        self.semaphore.acquire()
        self.queue.append((url, errorReport, containingPage))
        self.semaphore.release()

    def shutdown(self):
        self.finishing = True
    
    def kill(self):
        # TODO: remove if unneeded
        self.killed = True
    
    def run(self):
        while not self.killed:
            # print 'RUN, queue length: %i' % len(self.queue)
            if len(self.queue) == 0:
                if self.finishing:
                    break
                else:
                    time.sleep(0.1)
            else:
                self.semaphore.acquire()
                (url, errorReport, containingPage) = self.queue[0]
                self.queue = self.queue[1:]
                message = u'** Reporting dead link on ' + containingPage.switchTalkPage().aslink() + '...'
                wikipedia.output(message, colors = [11] * len(message))
                talk = containingPage.switchTalkPage()
                try:
                    content = talk.get() + "\n\n"
                    if url in content:
                        message = u'** Dead link seems to have already been reported on ' + containingPage.switchTalkPage().aslink() + '.'
                        wikipedia.output(message, colors = [11] * len(message))
                        self.semaphore.release()
                        continue
                except (wikipedia.NoPage, wikipedia.IsRedirectPage):
                    content = u''
                content += wikipedia.translate(wikipedia.getSite(), talk_report) % errorReport
                try:
                    talk.put(content)
                except wikipedia.SpamfilterError, url:
                    message = u'** SpamfilterError while trying to change %s: %s' % (containingPage.switchTalkPage().aslink(), url)
                    wikipedia.output(message, colors = [11] * len(message))
                    
                self.semaphore.release()

class WeblinkCheckerRobot:
    '''
    Robot which will use several LinkCheckThreads at once to search for dead
    weblinks on pages provided by the given generator.
    '''
    def __init__(self, generator, start ='!'):
        self.generator = generator
        self.start = start
        if globalvar.talk:
            #wikipedia.output("Starting talk page thread")
            reportThread = DeadLinkReportThread()
            # thread dies when program terminates
            # reportThread.setDaemon(True)
            reportThread.start()
        else:
            reportThread = None
        self.history = History(reportThread)

    def run(self):
        comment = wikipedia.translate(wikipedia.getSite(), talk_report_msg)
        wikipedia.setAction(comment)
        
        for page in self.generator:
           self.checkLinksIn(page)
    
    def checkLinksIn(self, page):
        try:
            text = page.get()
        except wikipedia.NoPage:
            wikipedia.output(u'%s does not exist.' % page.title())
            return
        for url in weblinksIn(text):
            ignoreUrl = False
            for ignoreR in ignorelist:
                if ignoreR.match(url):
                    ignoreUrl = True
            if not ignoreUrl:
                # Limit the number of threads started at the same time. Each
                # thread will check one page, then die.
                while threading.activeCount() >= config.max_external_links:
                    # wait 100 ms
                    time.sleep(0.1)
                thread = LinkCheckThread(page, url, self.history)
                # thread dies when program terminates
                thread.setDaemon(True)
                thread.start()

def main():
    gen = None
    pageTitle = []
    args = wikipedia.handleArgs()
    args = globalvar.handleArgs(args)
    
    for arg in args:
        if arg.startswith('-start:'):
            start = arg[7:]
            gen = pagegenerators.AllpagesPageGenerator(start)
        else:
            pageTitle.append(arg)

    if pageTitle:
        pageTitle = ' '.join(pageTitle)
        page = wikipedia.Page(wikipedia.getSite(), pageTitle)
        gen = iter([page])

    if gen:
        gen = pagegenerators.PreloadingGenerator(gen, pageNumber = 240)
        gen = pagegenerators.RedirectFilterPageGenerator(gen)
        bot = WeblinkCheckerRobot(gen)
        try:
            bot.run()
        finally:
            waitTime = 0
            # Don't wait longer than 30 seconds for threads to finish.
            while threading.activeCount() > 2 and waitTime < 30:
                wikipedia.output(u"Waiting for remaining %i threads to finish, please wait..." % (threading.activeCount() - 2)) # don't count the main thread and report thread
                # wait 1 second
                time.sleep(1)
                waitTime += 1
            if threading.activeCount() > 2:
                wikipedia.output(u'Remaining %i threads will be killed.' % (threading.activeCount() - 2))
                # Threads will die automatically because they are daemonic.
            wikipedia.output(u'Saving history...')
            bot.history.save()
            if bot.history.reportThread:
                bot.history.reportThread.shutdown()
                # wait until the report thread is shut down; the user can interrupt
                # it by pressing CTRL-C.
                #try:
                try:
                    while bot.history.reportThread.isAlive():
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    print 'INTERRUPT'
                    bot.history.reportThread.kill()
    else:
        wikipedia.showHelp()
    
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
