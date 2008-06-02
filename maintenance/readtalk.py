#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Tool to read all your talk pages.

This tool will go through all the normal (not sysop) accounts configured in user-config and output the contents of the talk page.

TODO:
*Error checking
"""
import sys, re
sys.path.append(re.sub('/[^/]*$', '', sys.path[0])) #sys.path.append('..')
import wikipedia, config

def main():
    # Get a dictionary of all the usernames
    namedict = config.usernames
    for familyName in namedict.iterkeys():
        for lang in namedict[familyName].iterkeys():
            site = wikipedia.getSite(code=lang, fam=familyName)
            username = config.usernames[familyName][lang]
            page = wikipedia.Page(site, u'User_Talk:' + username)
            wikipedia.output(u'Reading talk page from ' + lang + u' ' + familyName)
            wikipedia.output(page.get (get_redirect=True))

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
