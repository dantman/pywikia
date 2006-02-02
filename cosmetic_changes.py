# WARNING: needs more testing!

import wikipedia, pagegenerators
import sys
import re

deprecatedTemplates = {
    'wikipedia': {
        'de': [
            u'Stub',
        ]
    }
}

class CosmeticChangesToolkit:
    def __init__(self, site, text):
        self.site = site
        self.text = text
    
    def change(self):
        self.standardizeInterwiki()
        self.standardizeCategories()
        self.cleanUpSectionHeaders()
        self.translateNamespaces()
        self.removeDeprecatedTemplates()
        return self.text

    def standardizeInterwiki(self):
        interwikiLinks = wikipedia.getLanguageLinks(self.text, insite = self.site, getPageObjects = True)
        self.text = wikipedia.replaceLanguageLinks(self.text, interwikiLinks, site = self.site)

    def standardizeCategories(self):
        categories = wikipedia.getCategoryLinks(self.text, site = self.site, withSortKeys = True)
        self.text = wikipedia.replaceCategoryLinks(self.text, categories, site = self.site)

    def translateNamespaces(self):
        family = self.site.family
        for nsNumber in family.namespaces:
            thisNs = family.namespace(self.site.lang, nsNumber)
            defaultNs = family.namespace('_default', nsNumber)
            if thisNs != defaultNs:
                self.text = wikipedia.replaceExceptNowikiAndComments(self.text, r'\[\[\s*' + defaultNs + '\s*:(?P<nameAndLabel>.*?)\]\]', r'[[' + thisNs + ':\g<nameAndLabel>]]')

    def removeWhitespaceFromLinks(self):
        pass # TODO

    def cleanUpSectionHeaders(self):
        for level in range(1, 7):
            equals = '=' * level
            self.text = wikipedia.replaceExceptNowikiAndComments(self.text, r'\n' + equals + ' *(?P<title>[^=]+?) *' + equals + ' *\r\n', r'\n' + equals + ' \g<title> ' + equals + '\r\n')

    def removeDeprecatedTemplates(self):
        if deprecatedTemplates.has_key(self.site.family.name) and deprecatedTemplates[self.site.family.name].has_key(self.site.lang):
            for template in deprecatedTemplates[self.site.family.name][self.site.lang]:
                if not self.site.nocapitalize:
                    template = '[' + template[0].upper() + template[0].lower() + ']' + template[1:]
                self.text = wikipedia.replaceExceptNowikiAndComments(self.text, r'\{\{([mM][sS][gG]:)?' + template + '(?P<parameters>\|[^}]+|)}}', '')

class CosmeticChangesBot:
    def __init__(self, generator):
        self.generator = generator
    
    def run(self):
        for page in self.generator:
            ccToolkit = CosmeticChangesToolkit(page.site(), page.get())
            
            page.put(ccToolkit.change())


def main():
    #page generator
    gen = None
    pageTitle = []
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'cosmetic_changes')
        if arg:
            if arg.startswith('-start:'):
                gen = pagegenerators.AllpagesPageGenerator(arg[7:])
            elif arg.startswith('-ref:'):
                referredPage = wikipedia.Page(wikipedia.getSite(), arg[5:])
                gen = pagegenerators.ReferringPageGenerator(referredPage)
            elif arg.startswith('-links:'):
                linkingPage = wikipedia.Page(wikipedia.getSite(), arg[7:])
                gen = pagegenerators.LinkedPageGenerator(linkingPage)
            elif arg.startswith('-file:'):
                gen = pagegenerators.TextfilePageGenerator(arg[6:])
            elif arg.startswith('-cat:'):
                cat = catlib.Category(wikipedia.getSite(), arg[5:])
                gen = pagegenerators.CategorizedPageGenerator(cat)
            else:
                pageTitle.append(arg)

    if pageTitle:
        page = wikipedia.Page(wikipedia.getSite(), ' '.join(pageTitle))
        gen = iter([page])
    if not gen:
        wikipedia.showHelp('cosmetic_changes')
    else:
        preloadingGen = pagegenerators.PreloadingGenerator(gen)
        bot = CosmeticChangesBot(preloadingGen)
        bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()

