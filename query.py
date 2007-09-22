""" Please describe your module here ;) """

__version__ = '$Id$'
import wikipedia
import simplejson
import urllib

def GetData( lang, params, verbose = False ):
    """Get data from the query api, and convert it into a data object
    """
    site = wikipedia.getSite( lang )
    
    for k,v in params.iteritems():
        if not IsString(v):
            params[k] = unicode(v)

    params['format'] = 'json'
    params['noprofile'] = ''
    
    for k,v in params.iteritems():
        if type(v) == type(u''):
            params[k] = ToUtf8(v)

    # Titles param might be long, case convert it to post request
    if 'titles' in params:
        data = urllib.urlencode( {'titles' : params['titles']} )
        titlecount = params['titles'].count('|')
        del params['titles']
    else:
        data = None
        titlecount = 0
    
    path = u"/w/query.php?" + urllib.urlencode( params.items() )
    
    if verbose:
        wikipedia.output( u"Requesting %d titles from %s:%s" % (titlecount, lang, path) )
    
    url = site.family.querypath(lang)
    
    jsontext = site.getUrl( path, retry=True, data=data )


    # This will also work, but all unicode strings will need to be converted from \u notation
    # return eval( jsontext )

    return simplejson.loads( jsontext )

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