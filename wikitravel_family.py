# The wikimedia family that is known as wikitravel

# Translation used on all wikitravels for the 'article' text.
# A language not mentioned here is not known by the robot

langs = {
    'en':'en/article',
    'fr':'fr/article',
    'ro':'ro/articol'
    }

# Translation used on all wikitravels for the Special: namespace.
# Only necessary when it is not 'Special'.
special = {
    'en': 'Special',
    'fr': 'Sp%C3%A9cial',
    'ro': 'Special'
    }
# And the image namespace.

image = {
    'en': 'Image',
    'fr': 'Image',
    'ro': 'Imagine'
    }

redirect = {}

# Defaults for Special: and Image: namespace names

for lang in langs:
    if not lang in special:
        special[lang] = 'Special'
    if not lang in image:
        image[lang] = 'Image'

obsolete = []

# A few selected big languages for things that we do not want to loop over
# all languages. This is only needed by the titletranslate.py module, so
# if you carefully avoid the options, you could get away without these
# for another wikimedia family.

biglangs = ['en','fr','ro']

#
# Some functionality that is simple for the wikipedia family, but more
# difficult for e.g. wikitravel
#

def hostname(code):
    return 'wikitravel.org'

def version(code):
    return "1.2"

def put_address(code, name):
    return '/%s/wiki/wiki.phtml?title=%s&action=submit'%(code,name)

def get_address(code, name):
    return '/%s/wiki/wiki.phtml?title=%s&redirect=no'%(code,name)

def references_address(code, name):
    return "/%s/wiki/wiki.phtml?title=%s:Whatlinkshere&target=%s"%(code,special[code], name)

def upload_address(code):
    return '/%s/%s:Upload'%(langs[code],special[code])

def login_address(code):
    return '/%s/wiki/wiki.phtml?title=%s:Userlogin&amp;action=submit'%(code,special[code])

def move_address(code):
    return '/%s/wiki/wiki.phtml?title=%s:Movepage&action=submit'%(code,special[code])

def export_address(code):
    return '/%s/%s:Export'%(langs[code],special[code])

def allpagesname(code, start):
    # This is very ugly: to get all pages, the wikipedia code
    # 'fakes' getting a page with the returned name.
    # This will need to be fixed someday.
    if version(code)=="1.2":
        return '%s:Allpages&printable=yes&from=%s'%(special[code], start)
    else:
        return '%s:Allpages&from=%s'%(special[code], start)

# Two functions to figure out the encoding of different languages
# This may be a lot simpler for other families!

            
def code2encoding(code):
    """Return the encoding for a specific language wikipedia"""
    if code == 'ascii':
        return code # Special case where we do not want special characters.
    return 'utf-8'

def code2encodings(code):
    """Return a list of historical encodings for a specific language
       wikipedia"""
    return code2encoding(code),
