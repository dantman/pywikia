#!/usr/bin/python

import sys
import wikipedia
import time

def main():
    for pageinfo in wikipedia.newpages(5):
        sys.stdout.flush()
        print pageinfo["date"]
        print pageinfo["title"]
        print "Length:", pageinfo["length"],
        sys.stdout.flush()
        if pageinfo["length"] < 200 and pageinfo.get("user_anon"):
            print "SPAM SUSPECTED!"
            print
            try:
                content = pageinfo["title"].get()
                if '{{delete}}' in content or '{{speedy}}' in content:
                    raise wikipedia.NoPage
                print content
            except wikipedia.NoPage:
                print "Already gone (-:"
            print 
            answer = raw_input("Is it, or is it not, spam [y/n]?\a")
            if answer.lower().startswith('y'):
##                print "going to add {{delete}}!"
                time.sleep(10)
                newcontent = "{{delete}}\n" + content
                pageinfo["title"].put(newcontent, comment="user controlled bot declares: this is spam",
                                              minorEdit=True,
                                              watchArticle=False)
            # todo: ask response
            # if it is spam, add {{delete}}
        print
        print pageinfo.get("user_login") or pageinfo.get("user_anon")
        print pageinfo.get("comment") or "no comment"
        print '---'
        sys.stdout.flush()
if __name__ == "__main__":
    try:
        main()
    except:
        wikipedia.stopme()
        raise


