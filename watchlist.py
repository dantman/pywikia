# -*- coding: utf-8 -*-
"""
Allows access to the bot account's watchlist.

The function refresh() downloads the current watchlist and saves
it to disk. It is run automatically when a bot first tries to save a page
retrieved via XML Export. The watchlist can be updated manually by running
this script. The list will also be reloaded automatically once a month.

Syntax: python watchlist [-all]

Command line options:
    -all  -  Reloads watchlists for all wikis where a watchlist is already
             present
"""

# (C) Daniel Herding, 2005
#
# Distributed under the terms of the PSF license.

import wikipedia
import re, sys, pickle
import os.path
import time

cache = {}

def get(site = None):
    if site is None:
        site = wikipedia.getSite()
    if cache.has_key(site):
        # Use cached copy if it exists.
        dictionary = cache[site]
    else:
        fn = 'watchlists/watchlist-%s-%s.dat' % (site.family.name, site.lang)
        try:
            # find out how old our saved dump is (in seconds)
            file_age = time.time() - os.path.getmtime(fn)
            # if it's older than 1 month, reload it
            if file_age > 30 * 24 * 60 * 60:
                print 'Copy of watchlist is one month old, reloading'
                refresh(site)
        except OSError:
            # no saved watchlist exists yet, retrieve one
            refresh(site)
        f = open(fn, 'r')
        watchlist = pickle.load(f)
        f.close()
        # create cached copy
        cache[site] = watchlist
    return watchlist

def isWatched(pageName, site=None):
    watchlist = get(site)
    return pageName in watchlist

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
    
def refresh(site):
    host = site.hostname()
    # get watchlist special page's URL
    url = site.watchlist_address()
    print 'Retrieving watchlist for %s' % repr(site)
    #wikipedia.put_throttle() # It actually is a get, but a heavy one.
    watchlistHTML, charset = wikipedia.getUrl(host, url, site)

    print 'Parsing watchlist'
    watchlist = []
    itemR = re.compile(r'<input type=\'checkbox\' name=\'id\[\]\' value=\"(.+?)\"')
    for m in itemR.finditer(watchlistHTML):
        watchlist.append(m.group(1))
    # Save the dictionary to disk
    # The file is stored in the watchlists subdir. Create if necessary.
    if watchlist == []:
        print 'Error extracting watchlist for %s. Maybe you\'re not logged in, or the server is down.' % repr(site)
        sys.exit()
    else:
        f = open(makepath('watchlists/watchlist-%s-%s.dat' % (site.family.name, site.lang)), 'w')
        pickle.dump(watchlist, f)
        f.close()

def refresh_all():
    import dircache, time
    filenames = dircache.listdir('watchlists')
    watchlist_filenameR = re.compile('watchlist-([a-z\-:]+).dat')
    for filename in filenames:
        match = watchlist_filenameR.match(filename)
        if match:
            family, lang = match.group(1).split('-')
            site = wikipedia.getSite(code = lang, fam = family)
            refresh(site)
def main():
    debug = False
    refresh_all = False
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg)
        if arg:
            if arg == '-all':
                refresh_all = True

    if refresh_all:
        refresh_all()
    else:
        refresh(wikipedia.getSite())

if __name__ == "__main__":
    try:
        main()
    except:
        wikipedia.stopme()
        raise
    else:
        wikipedia.stopme()

