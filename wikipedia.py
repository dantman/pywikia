# Library to get and put pages on Wikipedia
import urllib,re

# known wikipedia languages
langs = {'en':'www.wikipedia.org',
         'pl':'pl.wikipedia.org',
         'da':'da.wikipedia.org',
         'sv':'sv.wikipedia.org',
         'zh':'zh.wikipedia.org',
         'eo':'eo.wikipedia.org',
         'nl':'nl.wikipedia.org',
         'de':'de.wikipedia.org',
         'fr':'fr.wikipedia.org',
         'es':'es.wikipedia.org',
         'it':'it.wikipedia.com',
         'no':'no.wikipedia.com',
         'pt':'pt.wikipedia.com',
         'af':'af.wikipedia.com',
         'fy':'fy.wikipedia.com',
         'la':'la.wikipedia.com',
         'ca':'ca.wikipedia.com',
         'fi':'fi.wikipedia.com',
         'ia':'ia.wikipedia.com',
         'et':'et.wikipedia.com',
         'cs':'cs.wikipedia.org',
         }

action = 'Rob Hooft - Wikipedia python library'

debug = 0

# Keep the modification time of all downloaded pages for an eventual put.
edittime = {}

# Local exceptions

class Error(Exception):
    """Wikipedia error"""

class NoPage(Error):
    """Wikipedia page does not exist"""

# Library functions
def unescape(s):
    if '&' not in s:
        return s
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&apos;", "'")
    s = s.replace("&quot;", '"')
    s = s.replace("&amp;", "&") # Must be last
    return s

def setAction(s):
    """Set a summary to use for changed page submissions"""
    global action
    action = s

def urlencode(query):
    l=[]
    for k, v in query:
        k = urllib.quote(str(k))
        v = urllib.quote(str(v))
        l.append(k + '=' + v)
    return '&'.join(l)

def putPage(code, name, text):
    """Upload 'text' on page 'name' to the 'code' language wikipedia."""
    import httplib
    host = langs[code]
    if host[-4:] == '.com':
        raise Error("Cannot put pages on a .com wikipedia")
    address = '/w/wiki.phtml?title=%s&action=submit'%(name)
    data = urlencode((
        ('wpSummary', action),
        ('wpMinoredit', '1'),
        ('wpSave', '1'),
        ('wpEdittime', edittime[code,name]),
        ('wpTextbox1', text)))
    if debug:
        print text
        print address
        print data
        #return None, None, None
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    conn = httplib.HTTPConnection(host)
    conn.request("POST", address, data, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return response.status, response.reason, data

def getPage(code, name):
    """Get the contents of page 'name' from the 'code' language wikipedia"""
    host = langs[code]
    name = re.sub(' ', '_', name)
    name = urllib.quote(name)
    if host[-4:] == '.org': # New software
        url = 'http://'+host+'/w/wiki.phtml?title='+name+'&action=edit'
    elif host[-4:]=='.com': # Old software
        url = 'http://'+host+'/wiki.cgi?action=edit&id='+name
    if debug:
        print url
    f = urllib.urlopen(url)
    text = f.read()
    f.close()
    m = re.search('value="(\d+)" name=\'wpEdittime\'',text)
    if m:
        edittime[code,name]=m.group(1)
    else:
        m = re.search('value="(\d+)" name="wpEdittime"',text)
        if m:
            edittime[code,name]=m.group(1)
    i1 = re.search('<textarea[^>]*>',text).end()
    i2 = re.search('</textarea>',text).start()
    if i2-i1 < 2:
        raise NoPage()
    elif text[i1:i2] == 'Describe the new page here.\n':
        raise NoPage()
    else:
        return unescape(text[i1:i2])

def languages(first):
    """Return a list of language codes for known wikipedia servers"""
    result=[]
    for key in first:
        if key in langs.iterkeys():
            result.append(key)
    for key in langs.iterkeys():
        if key not in result:
            result.append(key)
    return result

# Part of library dealing with interwiki links

def getLanguageLinks(text):
    """Returns a dictionary of other language links mentioned in the text
       in the form {code:pagename}"""
    result = {}
    for code in langs:
        m=re.search(r'\[\['+code+':([^\]]*)\]\]', text)
        if m:
            result[code] = m.group(1)
    return result

def removeLanguageLinks(text):
    for code in langs:
        text=re.sub(r'\[\['+code+':([^\]]*)\]\]', '', text)
    m=re.search(r'\[\[([a-z][a-z]):([^\]]*)\]\]', text)
    if m:
        print "WARNING: Link to unknown language %s name %s"%(m.group(1), m.group(2))
    return text
    
def interwikiFormat(links):
    s=''
    ar=links.keys()
    ar.sort()
    for code in ar:
        s = s + '[[%s:%s]]'%(code, links[code])
    return s
    
