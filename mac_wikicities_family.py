import family, config
    
# A language not mentioned here is not known by the robot

class Family(family.Family):
    name = 'mac_wikicities'
    
    langs = {
        'de':'de.mac.wikicities.com',
        'en':'en.mac.wikicities.com',
        'es':'es.mac.wikicities.com',
        'fr':'fr.mac.wikicities.com',
        'it':'it.mac.wikicities.com',
        'zh':'zh.mac.wikicities.com',
        }

    # A few selected big languages for things that we do not want to loop over
    # all languages. This is only needed by the titletranslate.py module, so
    # if you carefully avoid the options, you could get away without these
    # for another wikimedia family.

    biglangs = ['en','de']

    def version(self, code):
        return "1.4"
    
    def path(self, code):
        return '/index.php'
