# -*- coding: utf-8 -*-
"""
Allows access to the MediaWiki messages, that's the label texts of the MediaWiki
software in the current language. These can be used in other bots.

The function refresh_messages() downloads all the current messages and saves
them to disk. It is run automatically when a bot first tries to access one of
the messages. It can be updated manually by running this script, e.g. when
somebody changed the current message at the wiki. The texts will also be
reloaded automatically once a month.

Syntax: python mediawiki_messages [-all] [-debug]

Command line options:
    -refresh - Reloads messages for the home wiki or for the one defined via
               the -lang and -family parameters.

    -all     - Reloads messages for all wikis where messages are already present

    If another parameter is given, it will be interpreted as a MediaWiki key.
    The script will then output the respective value, without refreshing..
    
"""

# (C) Daniel Herding, 2004
#
# Distributed under the terms of the MIT license.

import wikipedia
import re, sys, pickle
import os.path
import time
import codecs

__version__='$Id$'

loaded = {}

def get(key, site = None, allowreload = True):
    site = site or wikipedia.getSite()
    if loaded.has_key(site):
        # Use cached copy if it exists.
        dictionary = loaded[site]
    else:
        fn = 'mediawiki-messages/mediawiki-messages-%s-%s.dat' % (site.family.name, site.lang)
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
    elif allowreload:
        refresh_messages(site = site)
        return get(key, site = site, allowreload = False)
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
    
def refresh_messages(site = None):
    site = site or wikipedia.getSite()
    # get 'all messages' special page's path
    path = site.allmessages_address()
    print 'Retrieving MediaWiki messages for %s' % repr(site)
    wikipedia.put_throttle() # It actually is a get, but a heavy one.
    allmessages = site.getUrl(path)

    print 'Parsing MediaWiki messages'
    # First group is MediaWiki key string. Second group is the current value string.
    if site.version() >= "1.5":
        # In MediaWiki 1.5, there are some single quotes around attributes.
        # Since about MediaWiki 1.8, there are only double quotes.
        itemR = re.compile("<tr class=['\"]def['\"] id=['\"].*?['\"]>\n"               # first possibility: original MediaWiki message used
                         + "\s*<td>\n"
                         + '\s*<a id=".+?" name=".+?"></a>'            # anchor
                         + '\s*<a href=".+?" title=".+?"><span id=[\'"].*?[\'"]>(?P<key>.+?)</span><\/a><br \/>'   # message link
                         + '\s*<a href=".+?" title=".+?">.+?<\/a>\n'   # talk link
                         + "\s*</td><td>"
                         + "\s*(?P<current>.+?)\n"                     # current message
                         + "\s*</td>"
                         + "\s*</tr>"
                         + "|"
                         + "<tr class=['\"]orig['\"] id=['\"].*?['\"]>\n"              # second possibility: custom message used
                         + "\s*<td rowspan=['\"]2['\"]>"
                         + '\s*<a id=".+?" name=".+?"></a>'            # anchor
                         + '\s*<a href=".+?" title=".+?"><span id=[\'"].*?[\'"]>(?P<key2>.+?)</span><\/a><br \/>'  # message link
                         + '\s*<a href=".+?" title=".+?">.+?<\/a>\n'   # talk link
                         + "\s*</td><td>"
                         + "\s*.+?\n"                                  # original message
                         + "\s*</td>"
                         + "\s*</tr><tr class=['\"]new['\"] id=['\"].*?['\"]>"
                         + "\s*<td>\n"
                         + "\s*(?P<current2>.+?)\n"                    # current message
                         + "\s*</td>"
                         + "\s*</tr>", re.DOTALL)
    else:
        itemR = re.compile("<tr bgcolor=\"#[0-9a-f]{6}\"><td>\n"
                         #+ "\s*(?:<script[^<>]+>[^<>]+<[^<>]+script>)?[^+<a href=.+?>(?P<key>.+?)<\/a><br \/>\n"
                         + "\s*<a href=.+?>(?P<key>.+?)<\/a><br \/>\n"
                         + "\s*<a href=.+?>.+?<\/a>\n"
                         + "\s*</td><td>\n"
                         + "\s*.+?\n"
                         + "\s*</td><td>\n"
                         + "\s*(?P<current>.+?)\n"
                         + "\s*<\/td><\/tr>", re.DOTALL)
    # we will save the found key:value pairs here
    dictionary = {}
    for match in itemR.finditer(allmessages):
        # Key strings only contain ASCII characters, so we can use them as dictionary keys
        key = match.group('key') or match.group('key2')
        current = match.group('current') or match.group('current2')
        dictionary[key] = current
    # Save the dictionary to disk
    # The file is stored in the mediawiki_messages subdir. Create if necessary. 
    if dictionary == {}:
        wikipedia.debugDump( 'MediaWiki_Msg', site, u'Error URL: '+unicode(path), allmessages )
        sys.exit()
    else:
        f = open(makepath('mediawiki-messages/mediawiki-messages-%s-%s.dat' % (site.family.name, site.lang)), 'w')
        pickle.dump(dictionary, f)
        f.close()
    #print dictionary['addgroup']
    #print dictionary['sitestatstext']

def refresh_all_messages():
    import dircache, time
    filenames = dircache.listdir('mediawiki-messages')
    message_filenameR = re.compile('mediawiki-messages-([a-z\-:]+).dat')
    for filename in filenames:
        match = message_filenameR.match(filename)
        if match:
            family, lang = match.group(1).split('-')
            site = wikipedia.getSite(code = lang, fam = family)
            refresh_messages(site)
def main():
    debug = False
    refresh_all = False
    refresh = False
    key = None
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'mediawiki_messages')
        if arg:
            if arg == '-all':
                refresh_all = True
            elif arg == '-refresh':
                refresh = True
            else:
                key = arg
    if key:
        wikipedia.output(get(key))
    elif refresh_all:
        refresh_all_messages()
    elif refresh:
        refresh_messages(wikipedia.getSite())
    else:
        wikipedia.showHelp('mediawiki_messages')

if __name__ == "__main__":
    try:
        main()
    except:
        wikipedia.stopme()
        raise
    else:
        wikipedia.stopme()

