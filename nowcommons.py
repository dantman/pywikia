# -*- coding: utf-8  -*-
import sys, re
import wikipedia, pagegenerators
# only for nowCommonsMessage
from imagetransfer import nowCommonsMessage

nowCommons = {
    '_default': u'NowCommons',
    'fr':       u'Désormais sur Commons',
    'ia':       u'OraInCommons',
    'nl':       u'NuCommons',
}

nowCommonsRedirects = {
    'de': [
        u'NC',
        u'NCT',        
    ],
}

namespaceInTemplate = [
    'en',
    'ia',
    'lt',
]



#nowCommonsMessage = imagetransfer.nowCommonsMessage

class NowCommonsDeleteBot:
    def __init__(self):
        self.site = wikipedia.getSite()
        if repr(self.site) == 'commons:commons':
            sys.exit('Don\'t run this bot on Commons!')
        if nowCommons.has_key(self.site.lang):
            self.nc = nowCommons[self.site.lang]
        else:
            self.nc = nowCommons['_default']
        self.nowCommonsTemplate = wikipedia.Page(self.site, 'Template:' + self.nc)
        if nowCommonsRedirects.has_key(self.site.lang):
            self.nc = ('(%s|%s)' % (self.nc, '|'.join(nowCommonsRedirects[self.site.lang])))
        if self.site.lang in namespaceInTemplate:
            self.nowCommonsR = re.compile(u'{{%s(\|%s:(?P<filename>.+?))?}}' % (self.nc, self.site.namespace(6)))
        else:
            self.nowCommonsR = re.compile(u'{{%s(\|(?P<filename>.+?))?}}' % self.nc)
        
    def getPageGenerator(self):
        gen = pagegenerators.ReferringPageGenerator(self.nowCommonsTemplate, followRedirects = True, onlyTemplateInclusion = True)
        gen = pagegenerators.NamespaceFilterPageGenerator(gen, [6])
        return gen
    
    def run(self):
        commons = wikipedia.Site('commons', 'commons')
        comment = wikipedia.translate(self.site, nowCommonsMessage)
        for page in self.getPageGenerator():
            wikipedia.output(u'\n\n>> %s <<\n' % page.title())
            try:
                localImagePage = wikipedia.ImagePage(self.site, page.title())
                if localImagePage.fileIsOnCommons():
                    wikipedia.output(u'File is already on Commons.')
                    continue
                md5 = localImagePage.getFileMd5Sum()
                
                localText = localImagePage.get()
                match = self.nowCommonsR.search(localText)
                if not match:
                    wikipedia.output(u'NowCommons template not found.')
                    continue                    
                filename = match.group('filename') or localImagePage.titleWithoutNamespace()
                commonsImagePage = wikipedia.ImagePage(commons, 'Image:%s' % filename)
                if len(localImagePage.getFileVersionHistory()) > 1:
                    wikipedia.output(u'This image has a version history. Please manually delete it after making sure that the old versions aren\'t worth keeping.')
                    continue
                commonsText = commonsImagePage.get()
                if md5 == commonsImagePage.getFileMd5Sum():
                    wikipedia.output(u'The image is identical to the one on Commons.')
                    wikipedia.output(u'\n\n>>>>>>> Description on %s <<<<<<\n\n' % repr(self.site))
                    wikipedia.output(localText)
                    wikipedia.output(u'\n\n>>>>>> Description on Commons <<<<<<\n\n')
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
