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
    'he': u'רובוט: שינויים קוסמטיים',
    'lt': u'robotas: smulkūs taisymai',
    'pl': u'Robot dokonuje poprawek kosmetycznych',
    'pt': u'Bot: Mudanças triviais',
    }

# Summary message  that will be appended to the normal message when
# cosmetic changes are made on the fly
msg_append = {
    'de': u'; kosmetische Änderungen',
    'en': u'; cosmetic changes',
    'he': u'; שינויים קוסמטיים',
    'lt': u'; smulkūs taisymai',
    'pl': u'; zmiany kosmetyczne',
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
        text = self.removeUselessSpaces(text)
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
        # The PyWikipediaBot is no longer allowed to touch categories on the German Wikipedia. See de.wikipedia.org/wiki/Wikipedia_Diskussion:Personendaten#Position
        if self.site != wikipedia.Site('de', 'wikipedia'):
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
            label = m.group('label')
            trailingChars = m.group('linktrail')

            if not self.site.isInterwikiLink(titleWithSection):
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
                    # Remove unnecessary leading spaces from title,
                    # but remember if we did this because we eventually want
                    # to re-add it outside of the link later.
                    titleLength = len(titleWithSection)
                    titleWithSection = titleWithSection.lstrip()
                    hadLeadingSpaces = (len(titleWithSection) != titleLength)
                    hadTrailingSpaces = False
                    # Remove unnecessary trailing spaces from title,
                    # but remember if we did this because it may affect
                    # the linktrail and because we eventually want to
                    # re-add it outside of the link later.
                    if not trailingChars:
                        titleLength = len(titleWithSection)
                        titleWithSection = titleWithSection.rstrip()
                        hadTrailingSpaces = (len(titleWithSection) != titleLength)

                    # Convert URL-encoded characters to unicode
                    titleWithSection = wikipedia.url2unicode(titleWithSection, site = self.site)

                    if titleWithSection == '':
                        # just skip empty links.
                        continue

                    # Remove unnecessary initial and final spaces from label.
                    # Please note that some editors prefer spaces around pipes. (See [[en:Wikipedia:Semi-bots]]). We remove them anyway.
                    if label:
                        # Remove unnecessary leading spaces from label,
                        # but remember if we did this because we want
                        # to re-add it outside of the link later.
                        labelLength = len(label)
                        label = label.lstrip()
                        hadLeadingSpaces = (len(label) != labelLength)
                        # Remove unnecessary trailing spaces from label,
                        # but remember if we did this because it affects
                        # the linktrail.
                        if not trailingChars:
                            labelLength = len(label)
                            label = label.rstrip()
                            hadTrailingSpaces = (len(label) != labelLength)
                    else:
                        label = titleWithSection
                    if trailingChars:
                        label += trailingChars

                    if titleWithSection == label or titleWithSection[0].lower() + titleWithSection[1:] == label:
                        newLink = "[[%s]]" % label
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
                    # re-add spaces that were pulled out of the link.
                    # Examples: 
                    #   text[[ title ]]text        -> text [[title]] text
                    #   text[[ title | name ]]text -> text [[title|name]] text
                    #   text[[ title |name]]text   -> text[[title|name]]text
                    #   text[[title| name]]text    -> text [[title|name]]text
                    if hadLeadingSpaces:
                        newLink = ' ' + newLink
                    if hadTrailingSpaces:
                        newLink = newLink + ' '
                    text = text[:m.start()] + newLink + text[m.end():]
        return text

    def resolveHtmlEntities(self, text):
        ignore = [
             38,     # Ampersand (&amp;)
             60,     # Less than (&lt;)
             62,     # Great than (&gt;)
            124,     # Vertical bar (??) - used intentionally in navigation bar templates on de:
            160,     # Non-breaking space (&nbsp;) - not supported by Firefox textareas
        ]
        text = wikipedia.html2unicode(text, ignore = ignore)
        return text

    def validXhtml(self, text):
        text = wikipedia.replaceExceptNowikiAndComments(text, r'<br>', r'<br />')
        return text

    def removeUselessSpaces(self, text):
        result = []
        multipleSpacesR = re.compile('  +')
        spaceAtLineEndR = re.compile(' $')

        exceptions = ['comment', 'math', 'nowiki', 'pre', 'table', 'template']
        text = wikipedia.replaceExcept(text, multipleSpacesR, ' ', exceptions)
        text = wikipedia.replaceExcept(text, spaceAtLineEndR, '', exceptions)

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

    def treat(self, page):
        try:
            # Show the title of the page where the link was found.
            # Highlight the title in purple.
            colors = [None] * 5 + [13] * len(page.title()) + [None] * 4
            wikipedia.output(u'\n>>> %s <<<' % page.title(), colors = colors)
            ccToolkit = CosmeticChangesToolkit(page.site(), debug = True)
            changedText = ccToolkit.change(page.get())
            if changedText != page.get():
                if not self.acceptall:
                    choice = wikipedia.inputChoice(u'Do you want to accept these changes?',  ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
                    if choice in ['a', 'A']:
                        self.acceptall = True
                if self.acceptall or choice in ['y', 'Y']:
                    page.put(changedText)
            else:
                wikipedia.output('No changes were necessary in %s' % page.title())
        except wikipedia.NoPage:
            wikipedia.output("Page %s does not exist?!" % page.aslink())
        except wikipedia.IsRedirectPage:
            wikipedia.output("Page %s is a redirect; skipping." % page.aslink())
        except wikipedia.LockedPage:
            wikipedia.output("Page %s is locked?!" % page.aslink())

    def run(self):
        for page in self.generator:
            self.treat(page)

def main():
    #page generator
    gen = None
    pageTitle = []
    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()

    for arg in wikipedia.handleArgs():
        generator = genFactory.handleArg(arg)
        if generator:
            gen = generator
        else:
            pageTitle.append(arg)

    if pageTitle:
        page = wikipedia.Page(wikipedia.getSite(), ' '.join(pageTitle))
        gen = iter([page])
    if not gen:
        wikipedia.showHelp()
    else:
        preloadingGen = pagegenerators.PreloadingGenerator(gen)
        bot = CosmeticChangesBot(preloadingGen)
        bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()

