import family, config
    
# The wikimedia family that is known as wikitravel

# Translation used on all wikitravels for the 'article' text.
# A language not mentioned here is not known by the robot

class Family(family.Family):
    name = 'memoryalpha'
    
    langs = {
        'de':'de',
        'en':'en',
        'nl':'nl',
        }

    # A few selected big languages for things that we do not want to loop over
    # all languages. This is only needed by the titletranslate.py module, so
    # if you carefully avoid the options, you could get away without these
    # for another wikimedia family.

    biglangs = ['en','fr','ro']

    def hostname(self,code):
        return 'www.memory-alpha.org'

    def path(self, code):
        return '/%s/index.php' % code

    def version(self, code):
        return "1.4"
