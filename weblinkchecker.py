 #-*- coding: utf-8 -*-
import wikipedia
import sys, re
import httplib, socket
import urlparse
import threading, time
import pickle, time

class AllpagesPageGenerator:
    '''
    Using the Allpages special page, retrieves all articles, loads them (60 at
    a time) using XML export, and yields title/text pairs.
    '''
    def __init__(self, start ='!'):
        self.start = start
    
    def generate(self):
        while True:
            i = 0
            pls = []
            for pl in wikipedia.allpages(start = self.start):
                    pls.append(pl)
                    i += 1
                    if i >= 60:
                        self.start = pl.urlname() + '!'
                        break
            wikipedia.getall(wikipedia.getSite(), pls)
            for pl in pls:
                if not pl.isRedirectPage():
                    yield pl.linkname(), pl.get()

class SqlPageGenerator:
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
                    
class LinkChecker:
    '''
    Given a HTTP URL, tries to load the page from the Internet and checks if it
    is still online.
    
    Returns a (boolean, string) tuple saying if the page is online and including
    a status reason.
    
    Warning: Also returns false if your Internet connection isn't working
    correctly! (This will give a Socket Error)
    '''
    def __init__(self, url):
        self.url = url
        
    def check(self):
        # we ignore the fragment
        scheme, host, path, query, fragment = urlparse.urlsplit(self.url)
        if not path:
            path = '/'
        #print scheme, host, path, query, fragment
        # TODO: HTTPS
        try:
            conn = httplib.HTTPConnection(host)
        except httplib.error, arg:
            return False, u'HTTP Error: %s' % arg
        try:
            conn.request('GET', '%s?%s' % (path, query))
        except socket.error, arg:
            return False, u'Socket Error: %s' % arg
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
        ok, message = linkChecker.check()
        if ok:
            self.history.linkAlive(self.url)
            pass
        else:
            wikipedia.output('*[[%s]] links to %s - %s' % (self.title, self.url, message))
            self.history.linkDead(self.url, message, self.title)

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
        txtfilename = 'deadlinks/delete-%s-%s.txt' % (site.family.name, site.lang)
        txtfile = codecs.open(txtfilename, 'a', 'utf-8')
        txtfile.write("* %s\n" % url)
        for (title, date, error) in self.dict[url]:
            txtfile.write("** In [[%s]] on %s, %s\n" % (title, time.ctime(date), error))
        txtfile.close()
            
    def linkDead(self, url, error, containingPage):
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

    def linkAlive(self, url):
        if self.dict.has_key(url):
            del self.dict[url]
            
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
        try:
            for (title, text) in self.generator.generate():
                self.checkLinksIn(title, text)
        except:
            if threading.activeCount() > 1:
                wikipedia.output(u"Waiting for remaining %i threads to finish, please wait..." % threading.activeCount())
                # wait 5 seconds
                time.sleep(5)
            if threading.activeCount() > 1:
                wikipedia.output(u"Killing remaining %i threads..." % threading.activeCount())
                # Threads will die automatically because they are daemonic
    
    def checkLinksIn(self, title, text):
        #wikipedia.output(title)
        linkR = re.compile(r'http://[^ \]\r\n]+')
        urls = linkR.findall(text)
        for url in urls:
            # Don't start more than 50 threads at once. Each thread will check
            # one page, then die.
            # TODO: Make number of threads a config variable.
            while threading.activeCount() >= 50:
                # wait 100 ms
                time.sleep(0.1)
            thread = LinkCheckThread(title, url, self.history)
            # thread dies when program terminates
            thread.setDaemon(True)
            thread.start()

def main():
    start = '!'
    sqlfilename = None
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, logname = 'weblinkchecker.log')
        if arg:
            if arg.startswith('-sql'):
                if len(arg) == 4:
                    sqlfilename = wikipedia.input(u'Please enter the SQL dump\'s filename: ')
                else:
                    sqlfilename = arg[5:]
                source = sqlfilename
            elif arg.startswith('-start:'):
                start = arg[7:]
            else:
                print 'Unknown argument: %s' % arg

    if sqlfilename:
        gen = SqlPageGenerator(sqlfilename)
    else:
        gen = AllpagesPageGenerator(start)
    bot = WeblinkCheckerRobot(gen)
    try:
        bot.run()
    finally:
        bot.history.save()
    
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
