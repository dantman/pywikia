# -*- coding: utf-8 -*-
"""

"""
#
# (C) Daniel Herding, 2004
#
# Distributed under the terms of the PSF license.
#
#
import wikipedia
import re, sys, pickle, codecs

def get(key):
    import os.path
    if not os.path.exists('mediawiki-messages-%s.dat' % wikipedia.mylang):
        refresh_messages()
    # TODO: It's quite inefficient to reload the file every time this function
    # is used. Maybe we can save its content the first time the function is
    # called.
    f = open('mediawiki-messages-%s.dat' % wikipedia.mylang, 'r')
    dictionary = pickle.load(f)
    f.close()
    key = key[0].lower() + key[1:]
    if dictionary.has_key(key):
        return dictionary[key]
    else:
        # TODO: Throw exception instead?
        print 'ERROR: MediaWiki Key %s not found' % key 

def refresh_messages():
    host = wikipedia.family.hostname(wikipedia.mylang)
    # broken redirect maintenance page's URL
    url = wikipedia.family.allmessages_address(wikipedia.mylang)
    print 'Retrieving MediaWiki messages...' 
    allmessages, charset = wikipedia.getUrl(host,url)

    #f=open('/home/daniel/allmessages.html', 'r')
    #allmessages =  f.read()
    
    # First group is MediaWiki key string. Second group is the current value string.
    itemR = re.compile("<tr bgcolor=\"#F0F0FF\">\n"
                     + "<td>\n"
                     + "<p><a href=\"\/wiki/MediaWiki:.+?\" title=\"MediaWiki:.+?\">(.+?)<\/a><br \/>\n"
                     + "<a href=.+? class=\"new\" title=.+?>.+?<\/a><\/p>\n"
                     + "</td>\n"
                     + "<td>\n"
                     + "<p>.+?</p>\n"
                     + "</td>\n"
                     + "<td>\n"
                     + "<p>(.+?)</p>\n"
                     + "<\/td>\n"
                     + "<\/tr>", re.DOTALL)
    items = itemR.findall(allmessages)
    # we will save the found key:value pairs here
    dictionary = {}
    for item in items:
        # Key strings only contain ASCII characters, so we can use them as dictionary keys
        dictionary[item[0]] = unicode(item[1], wikipedia.code2encoding(wikipedia.mylang))
        # Save the dictionary to disk
        # TODO: Put them into another directory
        f = open('mediawiki-messages-%s.dat' % wikipedia.mylang, 'w')
        pickle.dump(dictionary, f)
        f.close()
    
if __name__ == "__main__":
    # TODO: lang param
    
    refresh_messages()

