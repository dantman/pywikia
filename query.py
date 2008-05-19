#!/usr/bin/python
# -*- coding: utf-8  -*-
"""

This module allow you to use the API in a simple and easy way. Here there's an example:

-- Example --
--- Code ---
try:
    params = {
        'action'    :'query',
        'prop'      :'revisions',
        'titles'    :'Test',
        'rvlimit'   :'2',
        'rvprop'    :'user|timestamp|content',
        }
    
    print query.GetData('en', params,
                        useAPI = True, encodeTitle = False)
    
finally:
    wikipedia.stopme()
--- Output ---
(It's a whole line, but I've put some brakets to make it clearer)
{u'query-continue': {u'revisions': {u'rvstartid': 212496859}}, u'query': {u'pages': {u'11089416': {u'ns': 0, u'pageid': 11089416,
u'revisions': [{u'timestamp': u'2008-05-16T02:24:54Z', u'anon': u'', u'*': u"TEXT HERE", u'user': u'69.221.252.225'},
{u'timestamp': u'2008-05-16T02:23:49Z', u'anon': u'', u'*': u"TEXT TWO HERE", u'user': u'69.221.252.225'}], u'title': u'Test'}}}}

-- To Do --
Put a better documentation
    
"""
#
# (C) Yurik, 2007
# (C) Filnik, 2008
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import wikipedia, simplejson, urllib, time

def GetData(lang, params, verbose = False, useAPI = False, retryCount = 5, encodeTitle = True):
    """Get data from the query api, and convert it into a data object
    """
    site = wikipedia.getSite(lang)
    
    for k,v in params.iteritems():
        if not IsString(v):
            params[k] = unicode(v)

    params['format'] = 'json'

    if not useAPI:
        params['noprofile'] = ''
    
    for k,v in params.iteritems():
        if type(v) == type(u''):
            params[k] = ToUtf8(v)

    # Titles param might be long, case convert it to post request
    data = None
    titlecount = 0
    if 'titles' in params:
        titlecount = params['titles'].count('|')
        if encodeTitle:
            data = urllib.urlencode({'titles' : params['titles']})
            del params['titles']
    
    if useAPI:
        path = site.api_address() + urllib.urlencode(params.items())
    else:
        path = site.query_address() + urllib.urlencode(params.items())
    
    if verbose:
        if titlecount > 0:
            wikipedia.output(u"Requesting %d titles from %s:%s" % (titlecount, lang, path))
        else:
            wikipedia.output(u"Request %s:%s" % (lang, path))
    
    lastError = None
    retry_idle_time = 5
    while retryCount >= 0:
        try:
            jsontext = "Nothing received"
            jsontext = site.getUrl( path, retry=True, data=data )

            # This will also work, but all unicode strings will need to be converted from \u notation
            # decodedObj = eval( jsontext )
            return simplejson.loads( jsontext )
            
        except ValueError, error:
            retryCount -= 1
            wikipedia.output(u"Error downloading data: %s" % error)
            wikipedia.output(u"Request %s:%s" % (lang, path))
            wikipedia.debugDump('ApiGetDataParse', site, str(error) + '\n%s' % path, jsontext)
            lastError = error
            if retryCount >= 0:
                wikipedia.output(u"Retrying in %i seconds..." % retry_idle_time)
                time.sleep(retry_idle_time)
                # Next time wait longer, but not longer than half an hour
                retry_idle_time *= 2
                if retry_idle_time > 300:
                    retry_idle_time = 300

    
    raise lastError

def GetInterwikies( lang, titles, extraParams = None ):
    """ Usage example: data = GetInterwikies('ru','user:yurik')
    titles may be either ane title (as a string), or a list of strings
    extraParams if given must be a dict() as taken by GetData()
    """
    
    params = {'titles':ListToParam(titles), 'what' : 'redirects|langlinks'}
    params = CombineParams( params, extraParams )
    return GetData( lang, params )

def GetLinks( lang, titles, extraParams = None ):
    """ Get list of templates for the given titles
    """
    params = {'titles':ListToParam(titles), 'what': 'redirects|links'}
    params = CombineParams( params, extraParams )
    return GetData( lang, params )

def GetDisambigTemplates(lang):
    """This method will return a set of disambiguation templates.
    Template:Disambig is always assumed to be default, and will be
    appended (in localized format) regardless of its existence.
    The rest will be aquired from the Wikipedia:Disambiguation Templates page.
    Only links to templates will be used from that page.
    """
    
    disambigs = set()
    disambigName = u"template:disambig"
    disListName = u"Wikipedia:Disambiguation Templates"
    disListId = 0
    
    templateNames = GetLinks(lang, [disListName, disambigName])
    for id, page in templateNames['pages'].iteritems():
        if page['title'] == disambigName:
            if 'normalizedTitle' in page:
                disambigs.add(page['normalizedTitle'])
            elif 'redirect' in page:
                disambigs.add(page['title'])
        elif page['title'] == disListName:
            if 'normalizedTitle' in page:
                if 'refid' in page:
                    disListId = page['refid']
            else:
                disListId = id
    
    # Disambig page was found
    if disListId > 0:
        page = templateNames['pages'][disListId]
        if 'links' in page:
            for l in page['links']:
                if l['ns'] == 10:
                    disambigs.add(l['*'])
    
    return disambigs
#
#
# Helper utilities
#
#

def CleanParams( params ):
    """Params may be either a tuple, a list of tuples or a dictionary.
    This method will convert it into a dictionary
    """
    if params is None:
        return dict()
    pt = type( params )
    if pt == type( {} ):
        return params
    elif pt == type( () ):
        if len( params ) != 2: raise "Tuple size must be 2"
        return {params[0]:params[1]}
    elif pt == type( [] ):
        for p in params:
            if p != type( () ) or len( p ) != 2: raise "Every list element must be a 2 item tuple"
        return dict( params )
    else:
        raise "Unknown param type %s" % pt
    
def CombineParams( params1, params2 ):
    """Merge two dictionaries. If they have the same keys, their values will
    be appended one after another separated by the '|' symbol.
    """

    params1 = CleanParams( params1 )
    if params2 is None:
        return params1
    params2 = CleanParams( params2 )
    
    for k, v2 in params2.iteritems():
        if k in params1:
            v1 = params1[k]
            if len( v1 ) == 0:
                params1[k] = v2
            elif len( v2 ) > 0:
                if type('') != type(v1) or type('') != type(v2):
                    raise "Both merged values must be of type 'str'"
                params1[k] = v1 + '|' + v2
            # else ignore
        else:
            params1[k] = v2
    return params1

def ConvToList( item ):
    """Ensure the output is a list
    """
    if item is None:
        return []
    elif IsString(item):
        return [item]
    else:
        return item

def ListToParam( list ):
    """Convert a list of unicode strings into a UTF8 string separated by the '|' symbols
    """
    list = ConvToList( list )
    if len(list) == 0:
        return ''
    
    encList = ''
    # items may not have one symbol - '|'
    for l in list:
        if '|' in l: raise "item '%s' contains '|' symbol" % l
        encList += ToUtf8(l) + '|'
    return encList[:-1]

def ToUtf8(s):
    if type(s) != type(u''):
        wikipedia.output("item %s is not unicode" % unicode(s))
        raise
    return s.encode('utf-8')

def IsString(s):
    return type( s ) in [type( '' ), type( u'' )]
