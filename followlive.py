#!/usr/bin/python

import sys
import wikipedia

def main():
    for pageinfo in wikipedia.newpages():
        sys.stdout.flush()
        print pageinfo["date"]
        print pageinfo["title"]
        print "Length:", pageinfo["length"],
        sys.stdout.flush()
        if pageinfo["length"] < 200 and pageinfo.get("user_anon"):
            print "SPAM SUSPECTED!"
            print
            print pageinfo["title"].get()
            print 
            print "Is it, or is it not, spam?"
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


