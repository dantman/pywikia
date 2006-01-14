# -*- coding: utf-8  -*-
"""
This bot is used for checking external links found at the wiki. It checks
several pages at once, with a limit set by the config variable
max_external_links.

The bot won't change any wiki pages, it will only report dead links such that
people can fix or remove the links themselves.

The bot will store all links found dead in a .dat file in the deadlinks
subdirectory. To avoid the removing of links which are only temporarily
unavailable, the bot only reports links which were reported dead at least
two times, with a time lag of at least one week. Such links will be logged to a .txt file in the deadlinks subdirectory.

In addition to the logging step, it is possible to automatically report dead links to the talk page of the article where the link was found.

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
}

talk_report = {
    'de': u'\n\n== Toter Weblink ==\n\nBei mehreren automatisierten Botläufen wurde der folgende Weblink als nicht verfügbar erkannt. Bitte überprüfe, ob der Link tatsächlich down ist, und korrigiere oder entferne ihn in diesem Fall!\n\n%s\n\n--~~~~',
    'en': u'\n\n== Dead link ==\n\nDuring several automated bot runs the following external link was found to be unavailable. Please check if the link is in fact down and fix or remove it in that case!\n\n%s\n\n--~~~~',
}

ignorelist = [
    re.compile('.*[\./@]example.com(/.*)?'),
    re.compile('.*[\./@]example.net(/.*)?'),
    re.compile('.*[\./@]example.org(/.*)?'),
]

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
        #header = {'User-agent': 'PythonWikipediaBot/1.0'}
        # we fake being Firefox because some webservers block
        # unknown clients
        self.header = {'User-agent': 'Mozilla/5.0 (X11; U; Linux i686; de; rv:1.8) Gecko/20051128 SUSE/1.5-0.1 Firefox/1.5'}

    def changeUrl(self, url):
        self.url = url
        # we ignore the fragment
        self.scheme, self.host, self.path, self.query, self.fragment = urlparse.urlsplit(self.url)
        if not self.path:
            self.path = '/'
        if self.query:
            self.query = '?' + self.query
        self.protocol = url.split(':', 1)[0]
        

    def resolveRedirect(self):
        '''
        Requests the header from the server. If the page is an HTTP redirect,
        returns the redirect target URL as a string. Otherwise returns None.
        '''
        conn = httplib.HTTPConnection(self.host)
        conn.request('HEAD', '%s%s' % (self.path, self.query), None, self.header)
        response = conn.getresponse()
        if response.status >= 300 and response.status <= 399:
            redirTarget = response.getheader('Location')
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
            
    def check(self):
        """
        Returns True and the server status message if the page is alive.
        Otherwise returns false
        """
        try:
            wasRedirected = self.resolveRedirect()
        except httplib.error, arg:
            return False, u'HTTP Error: %s' % arg
        except socket.error, arg:
            return False, u'Socket Error: %s' % arg
        except UnicodeEncodeError, arg:
            return False, u'Non-ASCII Characters in URL: %s' % arg
        if wasRedirected:
            if self.url in self.redirectChain:
                return False, u'HTTP Redirect Loop: %s' % ' -> '.join(self.redirectChain + [self.url])
            elif len(self.redirectChain) >= 19:
                return False, u'Long Chain of Redirects: %s' % ' -> '.join(self.redirectChain + [self.url])
            else:
                redirChecker = LinkChecker(self.url, self.redirectChain)
                return redirChecker.check()
        else:
            try:
                conn = httplib.HTTPConnection(self.host)
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
    The URLs are dict's keys, and values are lists of tuples where each tuple
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
   
    def __init__(self):
        site = wikipedia.getSite()
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

    def report(self, url, errorReport, containingPage):
        """
        Tries to add an error report to the talk page belonging to the page containing the dead link.
        """
        if config.report_dead_links_on_talk and not containingPage.isTalkPage():
            wikipedia.output(u"** Reporting dead link on talk page...")
            talk = containingPage.switchTalkPage()
            try:
                content = talk.get()
                if url in content:
                    wikipedia.output(u"** Dead link seems to have already been reported.")
                    return
            except (wikipedia.NoPage, wikipedia.IsRedirectPage):
                content = u''
            content += wikipedia.translate(wikipedia.getSite(), talk_report) % errorReport
            talk.put(content)
        
    def log(self, url, error, containingPage):
        """
        Logs an error report to a text file in the deadlinks subdirectory.
        """
        site = wikipedia.getSite()
        errorReport = u'* %s\n' % url
        for (pageTitle, date, error) in self.historyDict[url]:
            errorReport += "** In [[%s]] on %s, %s\n" % (pageTitle, time.ctime(date), error)
        wikipedia.output(u"** Logging page for deletion.")
        txtfilename = 'deadlinks/results-%s-%s.txt' % (site.family.name, site.lang)
        txtfile = codecs.open(txtfilename, 'a', 'utf-8')
        self.logCount += 1
        if self.logCount % 30 == 0:
            # insert a caption
            txtfile.write('=== %s ===\n' % containingPage.title()[:3])
        txtfile.write(errorReport)
        txtfile.close()
        self.report(url, errorReport, containingPage)
    
            
    def setLinkDead(self, url, error, page):
        """
        Adds the fact that the link was found dead to the .dat file.
        """
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

    def setLinkAlive(self, url):
        """
        If the link was previously found dead, removes it from the .dat file
        and returns True, else returns False.
        """
        if self.historyDict.has_key(url):
            del self.historyDict[url]
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

                        
class WeblinkCheckerRobot:
    '''
    Robot which will use several LinkCheckThreads at once to search for dead
    weblinks on pages provided by the given generator.
    '''
    def __init__(self, generator, start ='!'):
        self.generator = generator
        self.start = start
        self.history = History()
        
    def run(self):
        comment = wikipedia.translate(wikipedia.getSite(), talk_report_msg)
        wikipedia.setAction(comment)
        
        for page in self.generator:
           self.checkLinksIn(page)
    
    def checkLinksIn(self, page):
        text = page.get()
        # RFC 2396 says that URLs may only contain certain characters.
        # For this regex we also accept non-allowed characters, so that the bot
        # will later show these links as broken ('Non-ASCII Characters in URL').
        # Note: While allowing parenthesis inside URLs, MediaWiki will regard
        # right parenthesis at the end of the URL as not part of that URL.
        # The same applies to dot, comma, colon and some other characters.
        # So characters inside the URL can be anything except whitespace,
        # closing squared brackets, quotation marks, greater than and less
        # than, and the last character also can't be parenthesis or another
        # character disallowed by MediaWiki.
        # MediaWiki allows closing curly braces inside links, but such braces
        # often come from templates where URLs are parameters, so as a
        # workaround we won't allow them inside links here.
        linkR = re.compile(r'http[s]?://[^\]\s<>}"]*[^\]\s\)\.:;,<>}"]')
        # Remove HTML comments in URLs as well as URLs in HTML comments.
        # Also remove text inside nowiki links
        text = re.sub('(?s)<nowiki>.*?</nowiki>|<!--.*?-->', '', text)
        urls = linkR.findall(text)
        for url in urls:
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
    start = u'!'
    pageTitle = []
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'weblinkchecker')
        if arg:
            if arg.startswith('-start:'):
                start = arg[7:]
            else:
                pageTitle.append(arg)

    if pageTitle == []:
        gen = pagegenerators.AllpagesPageGenerator(start)
    else:
        pageTitle = ' '.join(pageTitle)
        page = wikipedia.Page(wikipedia.getSite(), pageTitle)
        gen = iter([page])
    gen = pagegenerators.PreloadingGenerator(gen, pageNumber = 240)
    gen = pagegenerators.RedirectFilterPageGenerator(gen)
    bot = WeblinkCheckerRobot(gen)
    try:
        bot.run()
    finally:
        i = 0
        # Don't wait longer than 30 seconds for threads to finish.
        while threading.activeCount() > 1 and i < 30:
            wikipedia.output(u"Waiting for remaining %i threads to finish, please wait..." % (threading.activeCount() - 1)) # don't count the main thread
            # wait 1 second
            time.sleep(1)
            i += 1
        if threading.activeCount() > 1:
            wikipedia.output(u"Killing remaining %i threads, please wait..." % (threading.activeCount() - 1))
            # Threads will die automatically because they are daemonic. But the
            # killing might lag, so we wait 1 second.
            time.sleep(1)

        bot.history.save()
    
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
