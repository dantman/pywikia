""" Module to determine the pywikipedia version (tag, revision and date) """
#
# (C) Merlijn 'valhallasw' van Deen
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'

import os
import time
import sys
import wikipediatools

cache = None

class ParseError(Exception):
    """ Parsing went wrong """

def getversion():
    return '%(tag)s (r%(rev)s, %(date)s)' % getversiondict()
    
def getversiondict():
    global cache
    if cache:
      return cache
    try:
        (tag, rev, date) = getversion_svn()
    except Exception, e:
        try:
            (tag, rev, date) = getversion_nightly()
        except Exception, e:
            import wikipedia
            version = wikipedia.__version__
            if len(version) == 4:
                # the value is most likely '$Id' + '$', it means that
                # wikipedia.py got imported without using svn at all
                cache = dict(tag='', rev='-1 (unknown)', date='0 (unknown)')
                return cache

            d = version.split(' ')
            tag = ''
            date = time.strptime('T'.join(d[3:5]), '%Y-%m-%dT%H:%M:%SZ')
            rev = d[2] + ' (wikipedia.py)'
    datestring = time.strftime('%b %d %Y, %H:%M:%S', date)
    cache = {'tag': tag, 'rev': rev, 'date': datestring}
    return cache

def getversion_svn():
    entries = open(os.path.join(wikipediatools.get_base_dir(), '.svn/entries'))
    for i in range(4):
        entries.readline()
    tag = entries.readline().strip()
    t = tag.split('://')
    t[1] = t[1].replace('svn.wikimedia.org/svnroot/pywikipedia/', '')
    tag = '[%s] %s' % (t[0], t[1])
    for i in range(4):
        entries.readline()
    date = time.strptime(entries.readline()[:19],'%Y-%m-%dT%H:%M:%S')
    rev = entries.readline()[:-1]
    if not date or not tag or not rev:
        raise ParseError
    return (tag, rev, date)    

def getversion_nightly():
    data = open(os.path.join(wikipediatools.get_base_dir(), 'version'))
    tag = data.readline().strip()
    date = time.strptime(data.readline()[:19],'%Y-%m-%dT%H:%M:%S')
    rev = data.readline().strip()
    if not date or not tag or not rev:
        raise ParseError
    return (tag, rev, date)
    
if __name__ == '__main__':
    print 'Pywikipedia %s' % getversion()
    print 'Python %s' % sys.version
