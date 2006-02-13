# -*- coding: utf-8  -*-
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
    def __init__(self, site, text, debug = False):
        self.site = site
        self.text = text
        self.debug = debug

    def change(self):
        oldText = self.text
        self.standardizeInterwiki()
        self.standardizeCategories()
        self.cleanUpLinks()
        self.cleanUpSectionHeaders()
        self.translateNamespaces()
        self.removeDeprecatedTemplates()
        self.resolveHtmlEntities()
        self.validXhtml()
        if self.debug:
            wikipedia.showDiff(oldText, self.text)
        return self.text

    def standardizeInterwiki(self):
        interwikiLinks = wikipedia.getLanguageLinks(self.text, insite = self.site, getPageObjects = True)
        self.text = wikipedia.replaceLanguageLinks(self.text, interwikiLinks, site = self.site)

    def standardizeCategories(self):
        categories = wikipedia.getCategoryLinks(self.text, site = self.site)
        self.text = wikipedia.replaceCategoryLinks(self.text, categories, site = self.site)

    def translateNamespaces(self):
        family = self.site.family
        for nsNumber in family.namespaces:
            thisNs = family.namespace(self.site.lang, nsNumber)
            defaultNs = family.namespace('_default', nsNumber)
            if thisNs != defaultNs:
                self.text = wikipedia.replaceExceptNowikiAndComments(self.text, r'\[\[\s*' + defaultNs + '\s*:(?P<nameAndLabel>.*?)\]\]', r'[[' + thisNs + ':\g<nameAndLabel>]]')

    def cleanUpLinks(self):
        trailR = re.compile(self.site.linktrail())
        # The regular expression which finds links. Results consist of four groups:
        # group title is the target page title, that is, everything before | or ].
        # group section is the page section. It'll include the # to make life easier for us.
        # group label is the alternative link title, that's everything between | and ].
        # group linktrail is the link trail, that's letters after ]] which are part of the word.
        # note that the definition of 'letter' varies from language to language.
        self.linkR = re.compile(r'\[\[(?P<titleWithSection>[^\]\|]+)(\|(?P<label>[^\]\|]*))?\]\](?P<linktrail>' + self.site.linktrail() + ')')
        curpos = 0
        # This loop will run until we have finished the current page
        while True:
            m = self.linkR.search(self.text, pos = curpos)
            if not m:
                break
            # Make sure that next time around we will not find this same hit.
            curpos = m.start() + 1
            titleWithSection = m.group('titleWithSection')
            if not wikipedia.isInterwikiLink(titleWithSection):
                # The link looks like this:
                # [[page_title|link_text]]trailing_chars
                # We only work on namespace 0 because pipes and linktrails work
                # differently for images and categories.
                page = wikipedia.Page(self.site, titleWithSection)
                if page.namespace() == 0:
                    # Replace underlines by spaces, also multiple underlines
                    titleWithSection = re.sub('_+', ' ', titleWithSection)
                    # Remove double spaces
                    titleWithSection = re.sub('  +', ' ', titleWithSection)
                    # Convert URL-encoded characters to unicode
                    titleWithSection = wikipedia.url2unicode(titleWithSection, site = self.site)
                    label = m.group('label') or titleWithSection
                    trailingChars = m.group('linktrail')
                    if trailingChars:
                        label += trailingChars
                    if titleWithSection == label:
                        newLink = "[[%s]]" % titleWithSection
                    # Check if we can create a link with trailing characters instead of a pipelink
                    elif len(titleWithSection) <= len(label) and label[:len(titleWithSection)] == titleWithSection and re.sub(trailR, '', label[len(titleWithSection):]) == '':
                        newLink = "[[%s]]%s" % (label[:len(titleWithSection)], label[len(titleWithSection):])
                    else:
                        if not self.site.nocapitalize:
                            if len(titleWithSection) == 1:
                                titleWithSection = titleWithSection[0].upper()
                            else:
                                titleWithSection = titleWithSection[0].upper() + titleWithSection[1:]
                        newLink = "[[%s|%s]]" % (titleWithSection, label)
                    self.text = self.text[:m.start()] + newLink + self.text[m.end():]

    def resolveHtmlEntities(self):
        ignore = [
             38,     # Ampersand (&amp;)
             60,     # Less than (&lt;)
             62,     # Less than (&lt;)
            160,     # Non-breaking space (&nbsp;) - not supported by Firefox textareas
        ]
        self.text = wikipedia.html2unicode(self.text, ignore = ignore)

    def validXhtml(self):
        self.text = wikipedia.replaceExceptNowikiAndComments(self.text, r'<br>', r'<br />')

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
            ccToolkit = CosmeticChangesToolkit(page.site(), page.get(), debug = True)
            changedText = ccToolkit.change()
            if changedText != page.get():
                page.put(changedText)


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

