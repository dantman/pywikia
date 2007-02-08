# -*- coding: utf-8  -*-
import sys, re
import wikipedia, pagegenerators
# only for nowCommonsMessage
from imagetransfer import nowCommonsMessage

nowCommons = {
    '_default': [
        u'NowCommons'
    ],
    'de': [
        u'NowCommons',
        u'NC',
        u'NCT',
        u'Nowcommons',
    ],
    'fr': [
        u'Désormais sur Commons'
    ],
    'he': [
        u'תמונת ויקישיתוף'
    ],
    'ia': [
        u'OraInCommons'
    ],
    'nl': [
        u'NuCommons',
        u'Nucommons',
    ],
}

namespaceInTemplate = [
    'en',
    'he',
    'ia',
    'lt',
    'nl',
]



#nowCommonsMessage = imagetransfer.nowCommonsMessage

class NowCommonsDeleteBot:
    def __init__(self):
        self.site = wikipedia.getSite()
        if repr(self.site) == 'commons:commons':
            sys.exit('Don\'t run this bot on Commons!')
        ncList = self.ncTemplates()
        self.nowCommonsTemplate = wikipedia.Page(self.site, 'Template:' + ncList[0])

    def ncTemplates(self):
        if nowCommons.has_key(self.site.lang):
            return nowCommons[self.site.lang]
        else:
            return nowCommons['_default']

    def getPageGenerator(self):
        gen = pagegenerators.ReferringPageGenerator(self.nowCommonsTemplate, followRedirects = True, onlyTemplateInclusion = True)
        gen = pagegenerators.NamespaceFilterPageGenerator(gen, [6])
        return gen

    def findFilenameOnCommons(self, localImagePage):
        filenameOnCommons = None
        for templateName, params in localImagePage.templatesWithParams():
            if templateName in self.ncTemplates():
                if params == []:
                    filenameOnCommons = localImagePage.titleWithoutNamespace()
                elif self.site.lang in namespaceInTemplate:
                    filenameOnCommons = params[0][params[0].index(':') + 1:]
                else:
                    filenameOnCommons = params[0]
                return filenameOnCommons

    def run(self):
        commons = wikipedia.Site('commons', 'commons')
        comment = wikipedia.translate(self.site, nowCommonsMessage)
        for page in self.getPageGenerator():
            # Show the title of the image page.
            # Highlight the title in purple.
            colors = [None] * 5 + [13] * len(page.title()) + [None] * 4
            wikipedia.output(u'\n\n>> %s <<\n' % page.title(), colors = colors)
            try:
                localImagePage = wikipedia.ImagePage(self.site, page.title())
                if localImagePage.fileIsOnCommons():
                    wikipedia.output(u'File is already on Commons.')
                    continue
                md5 = localImagePage.getFileMd5Sum()

                filenameOnCommons = self.findFilenameOnCommons(localImagePage)
                if not filenameOnCommons:
                    wikipedia.output(u'NowCommons template not found.')
                    continue
                commonsImagePage = wikipedia.ImagePage(commons, 'Image:%s' % filenameOnCommons)
                if len(localImagePage.getFileVersionHistory()) > 1:
                    wikipedia.output(u'This image has a version history. Please manually delete it after making sure that the old versions aren\'t worth keeping.')
                    continue
                if localImagePage.titleWithoutNamespace() != commonsImagePage.titleWithoutNamespace():
                    usingPages = localImagePage.usingPages()
                    if usingPages and usingPages != [localImagePage]:
                        wikipedia.output('%s is still used in %i pages. Please change them manually.' % (localImagePage.title(), len(localImagePage.usingPages())))
                        continue
                    else:
                        wikipedia.output('No page is using %s anymore.' % localImagePage.title())
                commonsText = commonsImagePage.get()
                if md5 == commonsImagePage.getFileMd5Sum():
                    wikipedia.output(u'The image is identical to the one on Commons.')
                    wikipedia.output(u'\n>>>>>>> Description on %s <<<<<<\n' % localImagePage.aslink())
                    wikipedia.output(localImagePage.get())
                    wikipedia.output(u'\n>>>>>> Description on %s <<<<<<\n' % commonsImagePage.aslink())
                    wikipedia.output(commonsText)
                    choice = wikipedia.inputChoice(u'Does the description on Commons contain all required source and license information?', ['yes', 'no'], ['y', 'N'], 'N')
                    if choice == 'y':
                        localImagePage.delete(comment, prompt = False)
                else:
                    wikipedia.output(u'The image is not identical to the one on Commons!')
            except (wikipedia.NoPage, wikipedia.IsRedirectPage), e:
                wikipedia.output(u'%s' % e)
                continue

def main():
    for arg in wikipedia.handleArgs():
        pass

    bot = NowCommonsDeleteBot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
