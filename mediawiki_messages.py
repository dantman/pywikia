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
import re, sys, pickle
import os.path
import time

loaded = {}

def get(key, site = None):
    if site is None:
        site = wikipedia.getSite()
    if loaded.has_key(site):
        # Use cached copy if it exists.
        dictionary = loaded[site]
    else:
        fn = 'mediawiki-messages/mediawiki-messages-%s.dat' % repr(site)
        try:
            # find out how old our saved dump is (in seconds)
            file_age = time.time() - os.path.getmtime(fn)
            # if it's older than 1 month, reload it
            if file_age > 30 * 24 * 60 * 60:
                print 'Current MediaWiki message dump is one month old, reloading'
                refresh_messages(site)
        except OSError:
            # no saved dumped exists yet
            refresh_messages(site)
        f = open(fn, 'r')
        dictionary = pickle.load(f)
        f.close()
        loaded[site] = dictionary
    key = key[0].lower() + key[1:]
    if dictionary.has_key(key):
        return dictionary[key]
    else:
        raise KeyError('MediaWiki Key %s not found' % key)

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
    
def refresh_messages(site):
    host = site.hostname()
    # get 'all messages' special page's URL
    url = site.allmessages_address()
    print 'Retrieving MediaWiki messages for %s' % repr(site)
    wikipedia.put_throttle() # It actually is a get, but a heavy one.
    allmessages, charset = wikipedia.getUrl(host,url)

    print 'Parsing MediaWiki messages'
    # First group is MediaWiki key string. Second group is the current value string.
    itemR = re.compile("<tr bgcolor=\"#f0f0ff\"><td>\n"
                     + "\s*<a href=.+?>(.+?)<\/a><br \/>\n"
                     + "\s*<a href=.+?>.+?<\/a>\n"
                     + "\s*</td><td>\n"
                     + "\s*(.+?)\n"
                     + "\s*</td><td>\n"
                     + "\s*.+?\n"
                     + "\s*<\/td><\/tr>", re.DOTALL)
    items = itemR.findall(allmessages)
    # we will save the found key:value pairs here
    dictionary = {}
    for item in items:
        # Key strings only contain ASCII characters, so we can use them as dictionary keys
        dictionary[item[0]] = unicode(item[1], wikipedia.myencoding())
    # Save the dictionary to disk
    # The file is stored in the mediawiki_messages subdir. Create if necessary. 
    if dictionary == {}:
        print 'Error extracting MediaWiki messages for %s.' % repr(site)
        sys.exit()
    else:
        f = open(makepath('mediawiki-messages/mediawiki-messages-%s.dat' % repr(site)), 'w')
        pickle.dump(dictionary, f)
        f.close()

def refresh_all_messages():
    import dircache, time
    filenames = dircache.listdir('mediawiki-messages')
    message_filenameR = re.compile('mediawiki-messages-([a-z\-:]+).dat')
    for filename in filenames:
        match = message_filenameR.match(filename)
        if match:
            if not ':' in match.group(1):
                family, lang = 'wikipedia', match.group(1)
            else:
                family, lang = match.group(1).split(':')
            site = wikipedia.getSite(code = lang, fam = family)
            refresh_messages(site)
def main():
    debug = False
    refresh_all = False
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg)
        if arg:
            if arg == '-debug':
                debug = True
            elif arg == '-all':
                refresh_all = True
                
    if refresh_all:
        refresh_all_messages()
    else:
        refresh_messages(wikipedia.getSite())
    if debug:
        print "DBG> successfulupload contains %s" % get('successfulupload')

if __name__ == "__main__":
    try:
        main()
    except:
        wikipedia.stopme()
        raise
    else:
        wikipedia.stopme()

