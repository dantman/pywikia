# -*- coding: utf-8  -*-
"""
This module can do slight modifications to a wiki page source code such that
the code looks cleaner. The changes are not supposed to change the look of the
rendered wiki page.

The following parameters are supported:

&params;

-summary:XYZ      Set the summary message text for the edit to XYZ, bypassing
                  the predefined message texts with original and replacements
                  inserted.

All other parameters will be regarded as part of the title of a single page,
and the bot will only work on that single page.

&warning;

For regular use, it is recommended to put this line into your user-config.py:

    cosmetic_changes = True

There is another config variable: You can set

    cosmetic_changes_mylang_only = False

if you're running a bot on multiple sites and want to do cosmetic changes on
all of them, but be careful if you do.
"""
__version__ = '$Id$'
import wikipedia, pagegenerators, isbn
import sys
import re

warning = """ATTENTION: You can run this script as a stand-alone for testing purposes.
However, the changes are that are made are only minor, and other users
might get angry if you fill the version histories and watchlists with such
irrelevant changes."""

docuReplacements = {
    '&params;': pagegenerators.parameterHelp,
    '&warning;': warning,
}

# Summary message when using this module as a stand-alone script
msg_standalone = {
    'als': u'Bötli: chleineri Änderige',
    'ar': u'روبوت: تغييرات تجميلية',
    'be-x-old': u'Робат: касмэтычныя зьмены',
    'bg': u'Робот козметични промени',
    'ca': u'Robot: Canvis cosmètics',
    'da': u'Bot: Kosmetiske ændringer',
    'de': u'Bot: Kosmetische Änderungen',
    'el': u'Ρομπότ: διακοσμητικές αλλαγές',
    'en': u'Robot: Cosmetic changes',
    'es': u'Robot: Cambios triviales',
    'et': u'robot: kosmeetilised muudatused',
    'fa': u'ربات: ویرایش جزئی',
    'fi': u'Botti kosmeettisia muutoksia',
    'fr': u'Robot : Changement de type cosmétique',
    'fy': u'bot tekstwiziging',
    'gl': u'bot Cambios estética',
    'he': u'בוט: שינויים קוסמטיים',
    'hi': u'Bot: अंगराग परिवर्तन',
    'hr': u'robot kozmetičke promjene',
    'hu': u'Bot: kozmetikai változtatások',
    'ia': u'Robot: Cambios cosmetic',
    'id': u'bot kosmetik perubahan',
    'it': u'Bot: Modifiche estetiche',
    'ja': u'ロボットによる: 細部の編集',
    'ko': u'로봇: 예쁘게 바꿈',
    'la': u'automaton: mutationes minores',
    'lt': u'robotas: smulkūs taisymai',
    'lv': u'robots kosmētiskās izmaiņas',
    'mk': u'Бот: козметички промени',
    'ms': u'Bot: perubahan kosmetik',
    'mt': u'Bot: kosmetiċi bidliet',
    'nl': u'Bot: cosmetische wijzigingen',
    'no': u'Bot: Kosmetiske endringer',
    'pdc': u'Waddefresser: gleene Enneringe',
    'pl': u'Robot dokonuje poprawek kosmetycznych',
    'pt': u'Bot: Mudanças triviais',
    'ro': u'robot modificări cosmetice',
    'ru': u'робот косметические изменения',
    'sk': u'robot kozmetické zmeny',
    'sl': u'robot kozmetične spremembe',
    'sr': u'Бот козметичке промене',
    'sv': u'Bot: Kosmetiska ändringar',
    'th': u'บอต ปรับแต่งให้อ่านง่าย',
    'tl': u'robot Kosmetiko pagbabago',
    'tr': u'Bot Kozmetik değişiklikler',
    'uk': u'робот косметичні зміни',
    'vec': u'Bot: Modifiche estetiche',
    'vi': u'robot: Sửa cách trình bày',
    'war': u'Robot: Kosmetiko nga mga pagbag-o',
    'zh': u'機器人: 細部更改',
}

# Summary message  that will be appended to the normal message when
# cosmetic changes are made on the fly
msg_append = {
    'als': u'; chleineri Änderige',
    'ar': u'; تغييرات تجميلية',
    'be-x-old': u'; касмэтычныя зьмены',
    'bg': u'; козметични промени',
    'ca': u'; canvis cosmètics',
    'da': u'; kosmetiske ændringer',
    'de': u'; kosmetische Änderungen',
    'el': u'; διακοσμητικές αλλαγές',
    'en': u'; cosmetic changes',
    'es': u'; cambios triviales',
    'et': u'; kosmeetilised muudatused',
    'fa': u'; ویرایش جزئی',
    'fi': u'; kosmeettisia muutoksia',
    'fr': u'; changement de type cosmétique',
    'fy': u'; tekstwiziging',
    'gl': u'; cambios estética',
    'he': u'; שינויים קוסמטיים',
    'hi': u'; अंगराग परिवर्तन',
    'hr': u'; kozmetičke promjene',
    'hu': u'; kozmetikai változtatások',
    'ia': u'; cambios cosmetic',
    'id': u'; kosmetik perubahan',
    'it': u'; modifiche estetiche',
    'ja': u'; 細部の編集',
    'ko': u'; 예쁘게 바꿈',
    'la': u'; mutationes minores',
    'lt': u'; smulkūs taisymai',
    'lv': u'; kosmētiskās izmaiņas',
    'mt': u'; kosmetiċi bidliet',
    'mk': u'; козметички промени',
    'ms': u'; perubahan kosmetik',
    'nl': u'; cosmetische veranderingen',
    'no': u'; kosmetiske endringer',
    'pdc': u', gleene Enneringe',
    'pl': u'; zmiany kosmetyczne',
    'pt': u'; mudanças triviais',
    'ro': u'; modificări cosmetice',
    'ru': u'; косметические изменения',
    'sk': u'; kozmetické zmeny',
    'sl': u'; kozmetične spremembe',
    'sr': u'; козметичке промене',
    'sv': u'; kosmetiska ändringar',
    'th': u'; ปรับแต่งให้อ่านง่าย',
    'tl': u'; Kosmetiko pagbabago',
    'tr': u'; Kozmetik değişiklikler',
    'uk': u'; косметичні зміни',
    'vec': u'; modifiche estetiche',
    'vi': u'; sửa cách trình bày',
    'war': u'; kosmetiko nga mga pagbag-o',
    'zh': u'; 細部更改',
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
        text = self.fixSelfInterwiki(text)
        text = self.standardizeInterwiki(text)
        text = self.standardizeCategories(text)
        text = self.cleanUpLinks(text)
        text = self.cleanUpSectionHeaders(text)
        # Disabled because of a bug, and because its usefulness is disputed
        # text = self.putSpacesInLists(text)
        text = self.translateAndCapitalizeNamespaces(text)
        text = self.removeDeprecatedTemplates(text)
        text = self.resolveHtmlEntities(text)
        text = self.validXhtml(text)
        text = self.removeUselessSpaces(text)
        text = self.removeNonBreakingSpaceBeforePercent(text)
        try:
            text = isbn.hyphenateIsbnNumbers(text)
        except isbn.InvalidIsbnException, error:
            pass
        if self.debug:
            wikipedia.showDiff(oldText, text)
        return text

    def fixSelfInterwiki(self, text):
        """
        Interwiki links to the site itself are displayed like local links.
        Remove their language code prefix.
        """
        interwikiR = re.compile(r'\[\[%s\s?:([^\[\]\n]*)\]\]' % self.site.lang)
        text = interwikiR.sub(r'[[\1]]', text)
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
        Makes sure that categories are put to the correct position, but
        does not sort them.
        """
        # The PyWikipediaBot is no longer allowed to touch categories on the German Wikipedia. See http://de.wikipedia.org/wiki/Hilfe_Diskussion:Personendaten/Archiv/bis_2006#Position_der_Personendaten_am_.22Artikelende.22
        if self.site != wikipedia.getSite('de', 'wikipedia'):
            categories = wikipedia.getCategoryLinks(text, site = self.site)
            text = wikipedia.replaceCategoryLinks(text, categories, site = self.site)
        return text

    def translateAndCapitalizeNamespaces(self, text):
        """
        Makes sure that localized namespace names are used.
        """
        family = self.site.family
        # wiki links aren't parsed here.
        exceptions = ['nowiki', 'comment', 'math', 'pre']

        for nsNumber in family.namespaces:
            if not family.isDefinedNSLanguage(nsNumber, self.site.lang):
                # Skip undefined namespaces
                continue
            namespaces = list(family.namespace(self.site.lang, nsNumber, all = True))
            thisNs = namespaces.pop(0)

            # skip main (article) namespace
            if thisNs and namespaces:
                text = wikipedia.replaceExcept(text, r'\[\[\s*(' + '|'.join(namespaces) + ') *:(?P<nameAndLabel>.*?)\]\]', r'[[' + thisNs + ':\g<nameAndLabel>]]', exceptions)
        return text

    def cleanUpLinks(self, text):
        # helper function which works on one link and either returns it
        # unmodified, or returns a replacement.
        def handleOneLink(match):
            titleWithSection = match.group('titleWithSection')
            label = match.group('label')
            trailingChars = match.group('linktrail')

            if not self.site.isInterwikiLink(titleWithSection):
                # The link looks like this:
                # [[page_title|link_text]]trailing_chars
                # We only work on namespace 0 because pipes and linktrails work
                # differently for images and categories.
                try:
                    page = wikipedia.Page(self.site, titleWithSection)
                except wikipedia.InvalidTitle:
                    return match.group()
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
                        return match.group()

                    # Remove unnecessary initial and final spaces from label.
                    # Please note that some editors prefer spaces around pipes. (See [[en:Wikipedia:Semi-bots]]). We remove them anyway.
                    if label is not None:
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
                    return newLink
            # don't change anything
            return match.group()

        trailR = re.compile(self.site.linktrail())
        # The regular expression which finds links. Results consist of four groups:
        # group title is the target page title, that is, everything before | or ].
        # group section is the page section. It'll include the # to make life easier for us.
        # group label is the alternative link title, that's everything between | and ].
        # group linktrail is the link trail, that's letters after ]] which are part of the word.
        # note that the definition of 'letter' varies from language to language.
        linkR = re.compile(r'\[\[(?P<titleWithSection>[^\]\|]+)(\|(?P<label>[^\]\|]*))?\]\](?P<linktrail>' + self.site.linktrail() + ')')

        text = wikipedia.replaceExcept(text, linkR, handleOneLink, ['comment', 'math', 'nowiki', 'pre', 'startspace'])
        return text

    def resolveHtmlEntities(self, text):
        ignore = [
             38,     # Ampersand (&amp;)
             39,     # ignore ' see http://eo.wikipedia.org/w/index.php?title=Liberec&diff=next&oldid=2320801
             60,     # Less than (&lt;)
             62,     # Great than (&gt;)
             91,     # Opening bracket - sometimes used intentionally inside links
             93,     # Closing bracket - sometimes used intentionally inside links
            124,     # Vertical bar (??) - used intentionally in navigation bar templates on de:
            160,     # Non-breaking space (&nbsp;) - not supported by Firefox textareas
        ]
        text = wikipedia.html2unicode(text, ignore = ignore)
        return text

    def validXhtml(self, text):
        text = wikipedia.replaceExcept(text, r'<br>', r'<br />', ['comment', 'math', 'nowiki', 'pre'])
        return text

    def removeUselessSpaces(self, text):
        result = []
        multipleSpacesR = re.compile('  +')
        spaceAtLineEndR = re.compile(' $')

        exceptions = ['comment', 'math', 'nowiki', 'pre', 'startspace', 'table', 'template']
        text = wikipedia.replaceExcept(text, multipleSpacesR, ' ', exceptions)
        text = wikipedia.replaceExcept(text, spaceAtLineEndR, '', exceptions)

        return text

    def removeNonBreakingSpaceBeforePercent(self, text):
        '''
        Newer MediaWiki versions automatically place a non-breaking space in
        front of a percent sign, so it is no longer required to place it
        manually.
        '''
        text = wikipedia.replaceExcept(text, r'(\d)&nbsp;%', r'\1 %', ['timeline'])
        return text

    def cleanUpSectionHeaders(self, text):
        """
        For better readability of section header source code, puts a space
        between the equal signs and the title.
        Example: ==Section title== becomes == Section title ==

        NOTE: This space is recommended in the syntax help on the English and
        German Wikipedia. It might be that it is not wanted on other wikis.
        If there are any complaints, please file a bug report.
        """
        for level in range(1, 7):
            equals = '=' * level
            text = wikipedia.replaceExcept(text, r'\n' + equals + ' *(?P<title>[^=]+?) *' + equals + ' *\r\n', '\n' + equals + ' \g<title> ' + equals + '\r\n', ['comment', 'math', 'nowiki', 'pre'])
        return text

    def putSpacesInLists(self, text):
        """
        For better readability of bullet list and enumeration wiki source code,
        puts a space between the * or # and the text.

        NOTE: This space is recommended in the syntax help on the English, German,
        and French Wikipedia. It might be that it is not wanted on other wikis.
        If there are any complaints, please file a bug report.
        """
        # FIXME: This breaks redirects.
        text = wikipedia.replaceExcept(text, r'(?m)^(?P<bullet>(\*+|#+):*)(?P<char>[^\s\*#:].+?)', '\g<bullet> \g<char>', ['comment', 'math', 'nowiki', 'pre'])
        return text

    def removeDeprecatedTemplates(self, text):
        if deprecatedTemplates.has_key(self.site.family.name) and deprecatedTemplates[self.site.family.name].has_key(self.site.lang):
            for template in deprecatedTemplates[self.site.family.name][self.site.lang]:
                if not self.site.nocapitalize:
                    template = '[' + template[0].upper() + template[0].lower() + ']' + template[1:]
                text = wikipedia.replaceExcept(text, r'\{\{([mM][sS][gG]:)?' + template + '(?P<parameters>\|[^}]+|)}}', '', ['comment', 'math', 'nowiki', 'pre'])
        return text

class CosmeticChangesBot:
    def __init__(self, generator, acceptall = False):
        self.generator = generator
        self.acceptall = acceptall
        # Load default summary message.
        wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg_standalone))

    def treat(self, page):
        try:
            # Show the title of the page we're working on.
            # Highlight the title in purple.
            wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" % page.title())
            ccToolkit = CosmeticChangesToolkit(page.site(), debug = True)
            changedText = ccToolkit.change(page.get())
            if changedText != page.get():
                if not self.acceptall:
                    choice = wikipedia.inputChoice(u'Do you want to accept these changes?',  ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
                    if choice == 'a':
                        self.acceptall = True
                if self.acceptall or choice == 'y':
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
        if not genFactory.handleArg(arg):
            pageTitle.append(arg)

    # Disabled this check. Although the point is still valid, there
    # is now a warning and a prompt (see below).
    #if wikipedia.getSite() == wikipedia.getSite('nl','wikipedia'):
        #print "Deze bot is op WikipediaNL niet gewenst."
        #print "Het toevoegen van cosmetic changes bij andere wijzigingen is toegestaan,"
        #print "maar cosmetic_changes als stand-alone bot niet."
        #print "Zoek alstublieft een nuttig gebruik voor uw bot."
        #sys.exit()

    if pageTitle:
        page = wikipedia.Page(wikipedia.getSite(), ' '.join(pageTitle))
        gen = iter([page])
    if not gen:
        gen = genFactory.getCombinedGenerator()
    if not gen:
        wikipedia.showHelp()
    elif wikipedia.inputChoice(warning + '\nDo you really want to continue?', ['yes', 'no'], ['y', 'N'], 'N') == 'y':
        preloadingGen = pagegenerators.PreloadingGenerator(gen)
        bot = CosmeticChangesBot(preloadingGen)
        bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
