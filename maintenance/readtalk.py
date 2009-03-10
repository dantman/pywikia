#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Tool to read all your talk pages.

This tool will go through all the normal (not sysop) accounts configured in user-config and output the contents of the talk page.

TODO:
*Error checking
"""
import sys, re
sys.path.append(re.sub('/[^/]*$', '', sys.path[0])) 
sys.path.append('..')
import wikipedia, config


def readtalk(lang, familyName):
    site = wikipedia.getSite(code=lang, fam=familyName)
    site.forceLogin();
    page = wikipedia.Page(site, u'User_Talk:' + config.usernames[familyName][lang])
    wikipedia.output(u'Reading talk page from %s:%s'% (lang,familyName))
    try:
        wikipedia.output(page.get (get_redirect=True)+"\n")
    except wikipedia.NoPage:
        wikipedia.output("WARNING: Account talk page is not exist.\n")
    except wikipedia.UserBlocked:
        wikipedia.output("WARNING: Account in %s:%s is blocked.\n"% (familyName,lang))

def main():
    # Get a dictionary of all the usernames
    all =  False
    
    for arg in wikipedia.handleArgs():
        if arg.startswith('-all'):
            all = True
    
    if all == True:
        namedict = config.usernames
        for familyName in namedict.iterkeys():
            for lang in namedict[familyName].iterkeys():
                readtalk(lang,familyName)
    else:
        readtalk(wikipedia.default_code,wikipedia.default_family)

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()

