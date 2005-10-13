import family, config
    
# The wikimedia family that is known as wikitravel

# Translation used on all wikitravels for the 'article' text.
# A language not mentioned here is not known by the robot

__version__ = '$Id$'

class Family(family.Family):
    name = 'wikitravel'
    
    def __init__(self):
        family.Family.__init__(self)
        self.langs = {
            'de':'de',
            'en':'en',
            'fr':'fr',
            'ro':'ro',
            'sv':'sv',
        }
        self.namespaces[4] = {
            '_default': 'Wikitravel',
        }
        self.namespaces[5] = {
            '_default': 'Wikitravel talk',
            'de': 'Wikitravel Diskussion',
        }

    # A few selected big languages for things that we do not want to loop over
    # all languages. This is only needed by the titletranslate.py module, so
    # if you carefully avoid the options, you could get away without these
    # for another wikimedia family.

    self.languages_by_size = ['en','fr','ro']

    def hostname(self,code):
        return 'wikitravel.org'

    def path(self, code):
        return '/wiki/%s/index.php' % code

    def version(self, code):
        return "1.3.10"
