#!/usr/bin/python

import sys
import wikipedia
import datetime
import time
import traceback

__metaclass__ = type

question = """\a1) {{delete}}
2) {{stub}}
3) {{cleanup}}
q) quit cleaningbot
*) OK
What is it? """

messages = {
    "delete": "User controlled bot declares: this is spam. Contact [[User:Gerritholl]] and bot owner for problems.",
    "cleanup": "User controlled bot declares: this article needs cleanup. Contact [[User:Gerritholl]] and bot owner for problems.",
    "stub": "User controlled bot declares: this is a stub. Contact [[User:Gerritholl]] and bot owner for problems.",
    }

done = ["{{delete}}", "{{speedy}}", "{{VfD}}", "{{cleanup}}", "{{nonsense}}"] # do nothing if this is in it

class CleaningBot:
    trashhold = 250
    def __init__(self, site=None):
        if site is None:
            site = wikipedia.getSite()
        self.site = site

    def pages(self):
        for page in wikipedia.newpageslive(5):
            yield page

    def showpageinfo(self):
        print self.pageinfo["date"]
        print self.pageinfo["title"]
        print "Length:", self.pageinfo["length"]
        print "User:", self.pageinfo.get("user_login") or self.pageinfo.get("user_anon")
        comment = self.pageinfo.get("comment")
        if comment is not None:
            print "Comment:", comment
        else:
            print "no comment"


    def couldbebad(self):
        if self.pageinfo["length"] < self.trashhold and self.pageinfo.get("user_anon") is not None:
            return True
        return False

    def handlebadpage(self):
        self.content = self.pageinfo["title"].get()
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
        self.pageinfo["title"].put(newcontent, comment=messages["delete"], minorEdit=True, watchArticle=False)

    def handlestub(self):
        print 'appending {{stub}}...'
        newcontent = self.content + "\n{{stub}}"
        self.pageinfo["title"].put(newcontent, comment=messages["stub"], minorEdit=True, watchArticle=False)

    def handlecleanup(self):
        print 'prepending {{cleanup}}...'
        newcontent = "{{cleanup}}\n" + self.content
        self.pageinfo["title"].put(newcontent, comment=messages["cleanup"], minorEdit=True, watchArticle=False)

    def mainloop(self):
        gen = self.pages()
        while True:
            try:
                try:
                    page = gen.next()
                except StopIteration:
                    time.sleep(1)
                    continue
            except TypeError:
                traceback.print_exc()
                continue
            self.pageinfo = page
            self.showpageinfo()
            if self.couldbebad():
                print "Integrity of page doubtful..."
                try:
                    self.handlebadpage()
                except wikipedia.NoPage:
                    print 'seems already gone'
            print '----- Current time:', datetime.datetime.now()

def main():
    app = CleaningBot()
    app.mainloop()

if __name__ == "__main__":
    try:
        main()
    except:
        wikipedia.stopme()
        raise


