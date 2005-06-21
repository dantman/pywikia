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
two times, with a time lag of at least one week. Such links will be stored
in a .txt file in the deadlinks subdirectory.

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

    python weblinkchecker.py -sql:20050516.sql
        Checks all links found in an SQL cur dump.

"""

#
# (C) Daniel Herding, 2005
#
# Distributed under the terms of the PSF license.
#

import wikipedia, config, pagegenerators
import sys, re
import codecs, pickle
import httplib, socket, urlparse
import threading, time

class AllpagesPageContentGenerator:
    def __init__(self, start):
        self.start = start

    def generate(self):
        gen = pagegenerators.AllpagesPageGenerator(self.start)
        preloadingGen = pagegenerators.PreloadingGenerator(gen)
        for page in preloadingGen.generate():
            yield page.linkname(), page.get()

class SqlPageContentGenerator:
    '''
    Using an SQL dump file, retrieves all pages that are not redirects (doesn't
    load them from the live wiki), and yields title/text pairs.
    '''
    def __init__(self, sqlfilename):
        import sqldump
        self.dump = sqldump.SQLdump(sqlfilename, wikipedia.getSite().encoding())

    def generate(self):
        for entry in self.dump.entries():
            if not entry.redirect:
                yield entry.full_title(), entry.text

class SinglePageContentGenerator:
    '''Pseudo-generator'''
    def __init__(self, page):
        self.page = page

    def generate(self):
        yield self.page.linkname(), self.page.get(read_only = True)

class LinkChecker:
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
        self.redirectChain = redirectChain + [self.url]
        # we ignore the fragment
        self.scheme, self.host, self.path, self.query, self.fragment = urlparse.urlsplit(self.url)
        if not self.path:
            self.path = '/'
        if self.query:
            self.query = '?' + self.query
        self.protocol = url.split(':', 1)[0]
        #header = {'User-agent': 'PythonWikipediaBot/1.0'}
        # we fake being Opera because some webservers block
        # unknown clients
        self.header = {'User-agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.8) Gecko/20050511 Firefox/1.0.4 SUSE/1.0.4-0.3'}


    def resolveRedirect(self):
        '''
        Requests the header from the server. If the page is an HTTP redirect,
        returns the redirect target URL as a string. Otherwise returns None.
        '''
        conn = httplib.HTTPConnection(self.host)
        conn.request('HEAD', '%s%s' % (self.path, self.query), None, self.header)
        response = conn.getresponse()
        newURL = None
        if response.status >= 300 and response.status <= 399:
            redirTarget = response.getheader('Location')
            if redirTarget:
                if redirTarget.startswith('http://') or redirTarget.startswith('https://'):
                    newURL = redirTarget
                elif redirTarget.startswith('/'):
                    newURL = '%s://%s%s' % (self.protocol, self.host, redirTarget)
                else:
                    newURL = '%s://%s/%s' % (self.protocol, self.host, redirTarget)
            # wikipedia.output(u'%s is a redirect to %s' % (self.url, newURL))
            return newURL

        
    def check(self):
        """
        Returns True and the server status message if the page is alive.
        Otherwise returns false
        """
        try:
            url = self.resolveRedirect()
        except httplib.error, arg:
            return False, u'HTTP Error: %s' % arg
        except socket.error, arg:
            return False, u'Socket Error: %s' % arg
        except UnicodeEncodeError, arg:
            return False, u'Non-ASCII Characters in URL'
        if url:
            if url in self.redirectChain:
                return False, u'HTTP Redirect Loop: %s' % ' -> '.join(self.redirectChain + [url])
            elif len(self.redirectChain) >= 19:
                return False, u'Long Chain of Redirects: %s' % ' -> '.join(self.redirectChain + [url])
            else:
                redirChecker = LinkChecker(url, self.redirectChain)
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
                return False, u'Non-ASCII Characters in URL'
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
    def __init__(self, title, url, history):
        threading.Thread.__init__(self)
        self.title = title
        self.url = url
        self.history = history
        
    def run(self):
        linkChecker = LinkChecker(self.url)
        try:
            ok, message = linkChecker.check()
        except:
            wikipedia.output('Exception while processing URL %s in page %s' % (self.url, self.title))
            raise
        if ok:
            if self.history.setLinkAlive(self.url):
                wikipedia.output('*Link to %s in [[%s]] is back alive.' % (self.url, self.title))
        else:
            wikipedia.output('*[[%s]] links to %s - %s.' % (self.title, self.url, message))
            self.history.setLinkDead(self.url, message, self.title)

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
        # count the number of logged links, so that we can insert captions
        # from time to time
        self.logCount = 0
        try:
            datfile = open(self.datfilename, 'r')
            self.dict = pickle.load(datfile)
            datfile.close()
        except (IOError, EOFError):
            # no saved history exists yet, or history dump broken
            self.dict = {}

    def log(self, url, error, containingPage):
        site = wikipedia.getSite()
        wikipedia.output(u"** Logging page for deletion.")
        txtfilename = 'deadlinks/results-%s-%s.txt' % (site.family.name, site.lang)
        txtfile = codecs.open(txtfilename, 'a', 'utf-8')
        self.logCount += 1
        if self.logCount % 30 == 0:
            # insert a caption
            containingPageTitle = self.dict[url][0][0]
            txtfile.write('=== %s ===\n' % containingPageTitle[:3])
        txtfile.write("* %s\n" % url)
        for (title, date, error) in self.dict[url]:
            txtfile.write("** In [[%s]] on %s, %s\n" % (title, time.ctime(date), error))
        txtfile.close()
            
    def setLinkDead(self, url, error, containingPage):
        now = time.time()
        if self.dict.has_key(url):
            timeSinceFirstFound = now - self.dict[url][0][1]
            timeSinceLastFound= now - self.dict[url][-1][1]
            # if the last time we found this dead link is less than an hour
            # ago, we won't save it in the history this time.
            if timeSinceLastFound > 60 * 60:
                self.dict[url].append((containingPage, now, error))
            # if the first time we found this link longer than a week ago,
            # it should probably be fixed or removed. We'll list it in a file
            # so that it can be removed manually.
            if timeSinceFirstFound > 60 * 60 * 24 * 7:
                self.log(url, error, containingPage)
            
        else:
            self.dict[url] = [(containingPage, now, error)]

    def setLinkAlive(self, url):
        """
        If the link was previously found dead, removes it from the .dat file
        and returns True, else returns False.
        """
        if self.dict.has_key(url):
            del self.dict[url]
            return True
        else:
            return False
            
    def save(self):
        datfile = open(self.datfilename, 'w')
        self.dict = pickle.dump(self.dict, datfile)
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
        for (title, text) in self.generator.generate():
           self.checkLinksIn(title, text)
    
    def checkLinksIn(self, title, text):
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
        urls = linkR.findall(text)
        for url in urls:
            # Remove HTML comments in URLs
            url = re.sub('<!--.*?-->', '', url)
            # Limit the number of threads started at the same time. Each
            # thread will check one page, then die.
            while threading.activeCount() >= config.max_external_links:
                # wait 100 ms
                time.sleep(0.1)
            thread = LinkCheckThread(title, url, self.history)
            # thread dies when program terminates
            thread.setDaemon(True)
            thread.start()

def main():
    start = '!'
    source = None
    sqlfilename = None
    pageTitle = []
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'weblinkchecker')
        if arg:
            if arg.startswith('-sql'):
                if len(arg) == 4:
                    sqlfilename = wikipedia.input(u'Please enter the SQL dump\'s filename: ')
                else:
                    sqlfilename = arg[5:]
                source = 'sqldump'
            elif arg.startswith('-start:'):
                start = arg[7:]
            else:
                pageTitle.append(arg)
                source = 'page'

    if source == 'sqldump':
        # Bot will read all wiki pages from the dump and won't access the wiki.
        wikipedia.stopme()
        gen = SqlPageContentGenerator(sqlfilename)
    elif source == 'page':
        pageTitle = ' '.join(pageTitle)
        page = wikipedia.Page(wikipedia.getSite(), pageTitle)
        gen = SinglePageContentGenerator(page)
    else:
        gen = AllpagesPageContentGenerator(start)
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
            wikipedia.output(u"Killing remaining %i threads..." % (threading.activeCount() - 1))
            # Threads will die automatically because they are daemonic

        bot.history.save()
    
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
