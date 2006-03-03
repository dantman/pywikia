# -*- coding: utf-8  -*-
"""
This module can do slight modifications to a wiki page source code such that
the code looks cleaner. The changes are not supposed to change the look of the
rendered wiki page.

WARNING: This module needs more testing!
"""

import wikipedia, pagegenerators
import sys
import re

# Summary message when using this module as a stand-alone script
msg_standalone = {
    'de': u'Bot: Kosmetische Änderungen',
    'en': u'Robot: Cosmetic changes',
    'pt': u'Bot: Mudanças triviais',
    }

# Summary message  that will be appended to the normal message when
# cosmetic changes are made on the fly
msg_append = {
    'de': u'; kosmetische Änderungen',
    'en': u'; cosmetic changes',
    'pt': u'; mudanças triviais',
    }

deprecatedTemplates = {
    'wikipedia': {
        'de': [
            u'Stub',
        ]
    }
}

class CosmeticChangesToolkit:
    def __init__(self, site, debug = False):
        self.site = site
        self.debug = debug

    def change(self, text):
        """
        Given a wiki source code text, returns the cleaned up version.
        """
        oldText = text
        text = self.standardizeInterwiki(text)
        text = self.standardizeCategories(text)
        text = self.cleanUpLinks(text)
        text = self.cleanUpSectionHeaders(text)
        text = self.translateAndCapitalizeNamespaces(text)
        text = self.removeDeprecatedTemplates(text)
        text = self.resolveHtmlEntities(text)
        text = self.validXhtml(text)
        if self.debug:
            wikipedia.showDiff(oldText, text)
        return text

    def standardizeInterwiki(self, text):
        """
        Makes sure that interwiki links are put to the correct position and
        into the right order.
        """
        interwikiLinks = wikipedia.getLanguageLinks(text, insite = self.site)
        text = wikipedia.replaceLanguageLinks(text, interwikiLinks, site = self.site)
        return text

    def standardizeCategories(self, text):
        """
        Makes sure that interwiki links are put to the correct position, but
        does not sort them.
        """
        categories = wikipedia.getCategoryLinks(text, site = self.site)
        text = wikipedia.replaceCategoryLinks(text, categories, site = self.site)
        return text

    def translateAndCapitalizeNamespaces(self, text):
        """
        Makes sure that localized namespace names are used.
        """
        family = self.site.family
        for nsNumber in family.namespaces:
            thisNs = family.namespace(self.site.lang, nsNumber)
            defaultNs = family.namespace('_default', nsNumber)
            if thisNs != defaultNs:
                text = wikipedia.replaceExceptNowikiAndComments(text, r'\[\[\s*' + defaultNs + '\s*:(?P<nameAndLabel>.*?)\]\]', r'[[' + thisNs + ':\g<nameAndLabel>]]')
        if self.site.nocapitalize: 
            for nsNumber in family.namespaces:
                thisNs = family.namespace(self.site.lang, nsNumber)
                lowerNs = thisNs[0].lower() + thisNs[1:] # this assumes that all NS names have length at least 2
                text = wikipedia.replaceExceptNowikiAndComments(text, r'\[\[\s*' + lowerNs + '\s*:(?P<nameAndLabel>.*?)\]\]', r'[[' + thisNs + ':\g<nameAndLabel>]]')
        return text

    def cleanUpLinks(self, text):
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
            m = self.linkR.search(text, pos = curpos)
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
                        # Try to capitalize the first letter of the title.
                        # Maybe this feature is not useful for languages that
                        # don't capitalize nouns...
                        #if not self.site.nocapitalize:
                        if self.site.sitename() == 'wikipedia:de':
                            titleWithSection = titleWithSection[0].upper() + titleWithSection[1:]
                        newLink = "[[%s|%s]]" % (titleWithSection, label)
                    text = text[:m.start()] + newLink + text[m.end():]
        return text

    def resolveHtmlEntities(self, text):
        ignore = [
             38,     # Ampersand (&amp;)
             60,     # Less than (&lt;)
             62,     # Less than (&lt;)
            160,     # Non-breaking space (&nbsp;) - not supported by Firefox textareas
        ]
        text = wikipedia.html2unicode(text, ignore = ignore)
        return text

    def validXhtml(self, text):
        text = wikipedia.replaceExceptNowikiAndComments(text, r'<br>', r'<br />')
        return text

    def cleanUpSectionHeaders(self, text):
        for level in range(1, 7):
            equals = '=' * level
            text = wikipedia.replaceExceptNowikiAndComments(text, r'\n' + equals + ' *(?P<title>[^=]+?) *' + equals + ' *\r\n', r'\n' + equals + ' \g<title> ' + equals + '\r\n')
        return text

    def removeDeprecatedTemplates(self, text):
        if deprecatedTemplates.has_key(self.site.family.name) and deprecatedTemplates[self.site.family.name].has_key(self.site.lang):
            for template in deprecatedTemplates[self.site.family.name][self.site.lang]:
                if not self.site.nocapitalize:
                    template = '[' + template[0].upper() + template[0].lower() + ']' + template[1:]
                text = wikipedia.replaceExceptNowikiAndComments(text, r'\{\{([mM][sS][gG]:)?' + template + '(?P<parameters>\|[^}]+|)}}', '')
        return text

class CosmeticChangesBot:
    def __init__(self, generator, acceptall = False):
        self.generator = generator
        self.acceptall = acceptall
        # Load default summary message.
        wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg_standalone))
    
    def run(self):
        for page in self.generator:
            ccToolkit = CosmeticChangesToolkit(page.site(), debug = True)
            changedText = ccToolkit.change(page.get())
            if changedText != page.get():
                if not self.acceptall:
                    choice = wikipedia.inputChoice(u'Do you want to accept these changes?',  ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
                    if choice in ['a', 'A']:
                        self.acceptall = True
                if self.acceptall or choice in ['y', 'Y']:
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

