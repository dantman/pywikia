#!/usr/bin/python

import sys
import wikipedia
import datetime
import time
import traceback

__metaclass__ = type

question = """
\a
1) {{delete}}
2) {{stub}}
3) {{cleanup}}
q) quit cleaningbot
Enter) OK
What is it? """

messages = {
    "delete": "User controlled bot declares: this is spam. Contact [[User:Gerritholl]] and bot owner for problems.",
    "cleanup": "User controlled bot declares: this article needs cleanup. Contact [[User:Gerritholl]] and bot owner for problems.",
    "stub": "User controlled bot declares: this is a stub. Contact [[User:Gerritholl]] and bot owner for problems.",
    }

done = ["{{delete}}", "{{speedy}}", "{{VfD}}", "{{cleanup}}", "{{nonsense}}"] # do nothing if this is in it

class PageHandler:
    def __init__(self, page, date, length, loggedIn, user, comment):
        self.page = page
        self.date = date
        self.length = length
        self.loggedIn = loggedIn
        self.user = user
        self.comment = comment
    
    def showpageinfo(self):
        print self.date
        print self.page.title()
        print "Length: %i bytes" % self.length
        print "User: %s" % self.user
        if self.comment == None:
            print "no comment"
        else:
            print "Comment: %s" % self.comment

    def couldbebad(self):
        return self.length < 250 and not self.loggedIn


    def handlebadpage(self):
        self.content = self.page.get()
        for d in done:
            if d in self.content:
                print d, 'in content, nothing necessary'
                return
        print "-*- Start content -*-"
        print self.content
        print "-*- End of content -*-"
        answer = raw_input(question)
        if answer.startswith('1'): # cleanup: dispatch table
            self.handlespam()
        elif answer.startswith('2'):
            self.handlestub()
        elif answer.startswith('3'):
            self.handlecleanup()
        elif answer.startswith('q'):
            sys.exit("Exiting")
        else:
            print "Do nothing"

    def handlespam(self):
        print 'prepending {{delete}}...'
        newcontent = "{{delete}}\n" + self.content
        self.page.put(newcontent, comment=messages["delete"])

    def handlestub(self):
        print 'appending {{stub}}...'
        newcontent = self.content + "\n{{stub}}"
        self.page.put(newcontent, comment = messages["stub"])

    def handlecleanup(self):
        print 'prepending {{cleanup}}...'
        newcontent = "{{cleanup}}\n" + self.content
        self.page.put(newcontent, comment = messages["cleanup"])

    def run(self):
        self.showpageinfo()
        if self.couldbebad():
            print "Integrity of page doubtful..."
            try:
                self.handlebadpage()
            except wikipedia.NoPage:
                print 'seems already gone'
        print '----- Current time:', datetime.datetime.now()

                
class CleaningBot:
    def __init__(self, site=None):
        if site is None:
            site = wikipedia.getSite()
        self.site = site

    def run(self):
        for (page, date, length, loggedIn, username, comment) in wikipedia.newpages(100, repeat = True):
            handler = PageHandler(page, date, length, loggedIn, username, comment)
            handler.run()

if __name__ == "__main__":
    try:
        bot = CleaningBot()
        bot.run()
    except:
        wikipedia.stopme()
        raise


