#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
This module allow you to use the API in a simple and easy way.


-- Example --

    params = {
        'action'    :'query',
        'prop'      :'revisions',
        'titles'    :'Test',
        'rvlimit'   :'2',
        'rvprop'    :'user|timestamp|content',
        }

    print query.GetData(params, encodeTitle = False)

"""
#
# (C) Yuri Astrakhan, 2006
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import wikipedia, urllib, time
try:
    #For Python 2.6 newer
    import json
    if not hasattr(json, 'loads'):
        # 'json' can also be the name in for 
        # http://pypi.python.org/pypi/python-json
        raise ImportError
except ImportError:
    import simplejson as json
    

def GetData(params, site = None, useAPI = True, retryCount = 5, encodeTitle = True, sysop = False, back_response = False):
    """Get data from the query api, and convert it into a data object
    """
    if not site:
        site = wikipedia.getSite()

    if wikipedia.verbose:
        wikipedia.output("====API PARAMS====")
    for k,v in params.iteritems():
        if not IsString(v):
            params[k] = unicode(v)
        if wikipedia.verbose:
            if type(v) != int:
                if v.count('|') == 0 and len(v) > 40:
                    wikipedia.output("[%s]: %s (total %d char)" % (k,v[0:30], lev(v)) )
                elif v.count('|') > 8:
                    wikipedia.output("[%s]: %s (and more %d values)" % (k,v[0:v.index('|')], len(v.split('|')) ) )
                else:
                    wikipedia.output("[%s]: %s" % (k,v) )
            elif k == u'format':
                continue
            else:
                wikipedia.output("[%s]: %s" % (k,v) )
    if wikipedia.verbose:
        wikipedia.output("==================")
    

    if 'format' not in params:
        params['format'] = 'json'

    if not useAPI:
        params['noprofile'] = ''

    for k,v in params.iteritems():
        if type(v) == type(u''):
            params[k] = ToUtf8(v)

    # Titles param might be long, case convert it to post request
    data = None
    titlecount = 0
    for pLongKey in ['titles', 'pageids', 'ucusers', 'ususers']: #
        if pLongKey in params:
            titlecount = params[pLongKey].count('|') + 1
            if encodeTitle:
                data = {pLongKey : params[pLongKey]}
                del params[pLongKey]

    postAC = [
        'edit', 'login', 'purge', 'rollback', 'delete', 'undelete', 'protect',
        'block', 'unblock', 'move', 'emailuser','import', 'userrights', 'upload',
    ]
    if useAPI:
        if params['action'] in postAC:
            path = site.api_address()
            cont = ''
        else:
            path = site.api_address() + urllib.urlencode(params.items())

    else:
        path = site.query_address() + urllib.urlencode(params.items())

    if wikipedia.verbose:
        if titlecount > 1:
            wikipedia.output(u"Requesting %d %s from %s" % (titlecount, data.keys()[0], site))
        else:
            wikipedia.output(u"Requesting API query from %s" % site)

    lastError = None
    retry_idle_time = 1

    while retryCount >= 0:
        try:
            jsontext = "Nothing received"
            if params['action'] == 'upload' and ('file' in params or cont):
                import upload
                if not cont:
                    cont = params['file']
                    del params['file']
                
                res, jsontext = upload.post_multipart(site, path, params.items(),
                  (('file', params['filename'].encode(site.encoding()), cont),),
                  site.cookies(sysop=sysop)
                  )
            elif site.hostname() in wikipedia.config.authenticate.keys():
                params["Content-type"] = "application/x-www-form-urlencoded"
                params["User-agent"] = useragent
                res = urllib2.urlopen(urllib2.Request(site.protocol() + '://' + site.hostname() + address, site.urlEncode(params)))
                jsontext = res.read()
            elif params['action'] in postAC:
                res, jsontext = site.postForm(path, params, sysop, site.cookies(sysop = sysop) )
            else:
                if back_response:
                    res, jsontext = site.getUrl( path, retry=True, data=data, sysop=sysop, back_response=True)
                else:
                    jsontext = site.getUrl( path, retry=True, sysop=sysop, data=data)

            # This will also work, but all unicode strings will need to be converted from \u notation
            # decodedObj = eval( jsontext )
            if back_response:
                return res, json.loads( jsontext )
            else:
                return json.loads( jsontext )

        except ValueError, error:
            if 'Wikimedia Error' in jsontext: #wikimedia server error
                raise wikipedia.ServerError
            
            retryCount -= 1
            wikipedia.output(u"Error downloading data: %s" % error)
            wikipedia.output(u"Request %s:%s" % (site.lang, path))
            lastError = error
            if retryCount >= 0:
                wikipedia.output(u"Retrying in %i minutes..." % retry_idle_time)
                time.sleep(retry_idle_time*60)
                # Next time wait longer, but not longer than half an hour
                retry_idle_time *= 2
                if retry_idle_time > 30:
                    retry_idle_time = 30
            else:
                wikipedia.debugDump('ApiGetDataParse', site, str(error) + '\n%s\n%s' % (site.hostname(), path), jsontext)



    raise lastError

def GetInterwikies(site, titles, extraParams = None ):
    """ Usage example: data = GetInterwikies('ru','user:yurik')
    titles may be either ane title (as a string), or a list of strings
    extraParams if given must be a dict() as taken by GetData()
    """

    params = {
        'action': 'query',
        'prop': 'langlinks',
        'titles': ListToParam(titles),
        'redirects': 1,
    }
    params = CombineParams( params, extraParams )
    return GetData(params, site)

def GetLinks(site, titles, extraParams = None ):
    """ Get list of templates for the given titles
    """
    params = {
        'action': 'query',
        'prop': 'links',
        'titles': ListToParam(titles),
        'redirects': 1,
    }
    params = CombineParams( params, extraParams )
    return GetData(params, site)

def GetDisambigTemplates(site):
    """This method will return a set of disambiguation templates.
    Template:Disambig is always assumed to be default, and will be
    appended (in localized format) regardless of its existence.
    The rest will be aquired from the Wikipedia:Disambiguation Templates page.
    Only links to templates will be used from that page.
    """

    disambigs = set()
    disambigName = wikipedia.translate(site, site.family.disambiguationTemplates())
    disListName = u"Wikipedia:Disambiguation Templates"
    disListId = 0

    templateNames = GetLinks(site, [disListName, disambigName])
    for id, page in templateNames['pages'].iteritems():
        if page['title'] in disambigName:
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
        if type(l) == str and '|' in l:
            raise wikipedia.Error("item '%s' contains '|' symbol" % l )
        encList += ToUtf8(l) + '|'
    return encList[:-1]

def ToUtf8(s):
    if type(s) != unicode:
        try:
            s = unicode(s)
        except UnicodeDecodeError:
            s = s.decode(wikipedia.config.console_encoding)
    return s.encode('utf-8')

def IsString(s):
    return type( s ) in [type( '' ), type( u'' )]
