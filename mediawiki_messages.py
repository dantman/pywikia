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
    if not os.path.exists('mediawiki_messages/mediawiki-messages-%s.dat' % wikipedia.mylang):
        refresh_messages()
    # TODO: It's quite inefficient to reload the file every time this function
    # is used. Maybe we can save its content the first time the function is
    # called.
    f = open('mediawiki_messages/mediawiki-messages-%s.dat' % wikipedia.mylang, 'r')
    dictionary = pickle.load(f)
    f.close()
    key = key[0].lower() + key[1:]
    if dictionary.has_key(key):
        return dictionary[key]
    else:
        # TODO: Throw exception instead?
        print 'ERROR: MediaWiki Key %s not found' % key 

def makepath(path):
    """ creates missing directories for the given path and
        returns a normalized absolute version of the path.

    - if the given path already exists in the filesystem
      the filesystem is not modified.

    - otherwise makepath creates directories along the given path
      using the dirname() of the path. You may append
      a '/' to the path if you want it to be a directory path.

    from holger@trillke.net 2002/03/18
    """
    from os import makedirs
    from os.path import normpath,dirname,exists,abspath

    dpath = normpath(dirname(path))
    if not exists(dpath): makedirs(dpath)
    return normpath(abspath(path))
    
def refresh_messages():
    host = wikipedia.family.hostname(wikipedia.mylang)
    # broken redirect maintenance page's URL
    url = wikipedia.family.allmessages_address(wikipedia.mylang)
    print 'Retrieving MediaWiki messages...' 
    allmessages, charset = wikipedia.getUrl(host,url)

    #f=open('/home/daniel/allmessages.html', 'r')
    #allmessages =  f.read()
    
    print 'Parsing MediaWiki messages...'
    # First group is MediaWiki key string. Second group is the current value string.
    itemR = re.compile("<tr bgcolor=\"#F0F0FF\">\n"
                     + "<td>\n"
                     + "<p><a href=\"\/wiki/MediaWiki:.+?\" title=\"MediaWiki:.+?\">(.+?)<\/a><br \/>\n"
                     + "<a href=.+? title=.+?>.+?<\/a><\/p>\n"
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
        # Create directory for these files, if it doesn't exist already
        makepath('mediawiki_messages')
        # The file is stored in the mediawiki_messages subdir. Create if necessary. 
        f = open(makepath('mediawiki_messages/mediawiki-messages-%s.dat' % wikipedia.mylang), 'w')
        pickle.dump(dictionary, f)
        f.close()
    
if __name__ == "__main__":
    # TODO: lang param
    
    refresh_messages()

