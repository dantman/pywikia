import family, config
    
# The wikimedia family that is known as wikitravel

# Translation used on all wikitravels for the 'article' text.
# A language not mentioned here is not known by the robot

class Family(family.Family):
    name = 'wikitravel'
    
    langs = {
        'de':'de/artikel',
        'en':'en/article',
        'fr':'fr/article',
        'ro':'ro/articol',
        'sv':'sv/artikel',
        }

    # A few selected big languages for things that we do not want to loop over
    # all languages. This is only needed by the titletranslate.py module, so
    # if you carefully avoid the options, you could get away without these
    # for another wikimedia family.

    biglangs = ['en','fr','ro']

    def hostname(self,code):
        return 'wikitravel.org'

    def version(self,code):
        return "1.2"

    def put_address(self, code, name):
        return '/%s/wiki/wiki.phtml?title=%s&action=submit'%(code,name)

    def get_address(self, code, name):
        return '/%s/wiki/wiki.phtml?title=%s&redirect=no'%(code,name)

    def references_address(self, code, name):
        return "/%s/wiki/wiki.phtml?title=%s:Whatlinkshere&target=%s"%(code,special[code], name)

    def upload_address(self, code):
        return '/%s/%s:Upload'%(langs[code],special[code])

    def login_address(self, code):
        return '/%s/wiki/wiki.phtml?title=%s:Userlogin&amp;action=submit'%(code,special[code])

    def move_address(self, code):
        return '/%s/wiki/wiki.phtml?title=%s:Movepage&action=submit'%(code,special[code])

    def version_history_address(self, code, name):
        return '/w/wiki.phtml?title=%s&action=history&limit=%d' % (name, config.special_page_limit)

    def export_address(self, code):
        return '/%s/%s:Export'%(langs[code],special[code])

    def version(self, code):
        return "1.3"
