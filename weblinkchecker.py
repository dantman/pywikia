# -*- coding: utf-8 -*-
import wikipedia
import sys, re
import httplib, socket
import urlparse
import threading, time

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
        response = conn.getresponse()
        #wikipedia.output('%s: %s' % (self.url, response.status))
        # site down if the server status is between 400 and 499
        siteDown = response.status in range(400, 500)
        return not siteDown, '%s %s' % (response.status, response.reason)  

class LinkCheckThread(threading.Thread):
    '''
    A thread responsible for checking one page. After checking the page, it
    will die.
    '''
    def __init__(self, title, url):
        threading.Thread.__init__(self)
        self.title = title
        self.url = url

    def run(self):
        linkChecker = LinkChecker(self.url)
        ok, message = linkChecker.check()
        if not ok:
            wikipedia.output('WARNING: %s links to %s: %s' % (self.title, self.url, message))
    
class WeblinkCheckerRobot:
    '''
    Robot which will use several LinkCheckThreads at once to search for dead
    weblinks on pages provided by the given generator.
    '''
    def __init__(self, generator, start ='!'):
        self.generator = generator
        self.start = start
    
    def run(self):
        for (title, text) in self.generator.generate():
            self.checkLinksIn(title, text)
    
    def checkLinksIn(self, title, text):
        #wikipedia.output(title)
        linkR = re.compile(r'http://[^ \]\r\n]+')
        urls = linkR.findall(text)
        for url in urls:
            # Don't start more than 10 threads at once. Each thread will check
            # one page, then die.
            # TODO: Make number of threads a config variable.
            while threading.activeCount() >= 10:
                # wait 100 ms
                time.sleep(0.1)
            thread = LinkCheckThread(title, url)
            thread.start()

def main():
    start = '!'
    sqlfilename = None
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg)
        if arg:
            if arg.startswith('-sql'):
                if len(arg) == 4:
                    sqlfilename = wikipedia.input(u'Please enter the SQL dump\'s filename: ')
                else:
                    sqlfilename = arg[5:]
                source = sqlfilename
            elif arg.startswith('-start:'):
                start = int(arg[7:])
            else:
                print 'Unknown argument: %s' % arg

    if sqlfilename:
        gen = SqlPageGenerator(sqlfilename)
    else:
        gen = AllpagesPageGenerator(start)
    bot = WeblinkCheckerRobot(gen)
    bot.run()
    
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
