# -*- coding: utf-8 -*-
"""
Allows access to the MediaWiki messages, that's the label texts of the MediaWiki
software in the current language. These can be used in other bots.

The function refresh_messages() downloads all the current messages and saves
them to disk. It is run automatically when a bot first tries to access one of
the messages. It can be updated manually by running this script, e.g. when
somebody changed the current message at the wiki.

Syntax: python mediawiki_messages [-lang:xx]

Command line options:

-lang:XX download labels in language XX instead of the one given in
         username.dat

"""

# (C) Daniel Herding, 2004
#
# Distributed under the terms of the PSF license.

import wikipedia
import re, sys, pickle, codecs
import os.path
import time

def get(key):
    try:
        # find out how old our saved dump is (in seconds)
        file_age = time.time() - os.path.getmtime('mediawiki-messages/mediawiki-messages-%s.dat' % wikipedia.mylang)
        # if it's older than 7 days, reload it
        if file_age > 7 * 24 * 60 * 60:
            print 'Current MediaWiki message dump is outdated, reloading'
            refresh_messages()
    except OSError:
        # no saved dumped exists yet
        refresh_messages()
    # TODO: It's quite inefficient to reload the file every time this function
    # is used. Maybe we can save its content the first time the function is
    # called.
    f = open('mediawiki-messages/mediawiki-messages-%s.dat' % wikipedia.mylang, 'r')
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
    print 'Retrieving MediaWiki messages' 
    allmessages, charset = wikipedia.getUrl(host,url)

    #f=open('/home/daniel/allmessages.html', 'r')
    #allmessages =  f.read()
    
    print 'Parsing MediaWiki messages'
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
        dictionary[item[0]] = unicode(item[1], wikipedia.myencoding())
        # Save the dictionary to disk
        # The file is stored in the mediawiki_messages subdir. Create if necessary. 
        f = open(makepath('mediawiki-messages/mediawiki-messages-%s.dat' % wikipedia.mylang), 'w')
        pickle.dump(dictionary, f)
        f.close()
    
if __name__ == "__main__":
    for arg in sys.argv[1:]:
        if wikipedia.argHandler(arg):
            pass
        elif arg == '-debug':
            get('about')
    refresh_messages()

