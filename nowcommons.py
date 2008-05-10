#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Script to delete files that are also present on Wikimedia Commons on a local
wiki. Do not run this script on Wikimedia Commons itself. It works based on
a given array of templates defined below.

Files are downloaded and compared. If the files match, it can be deleted on
the source wiki. If multiple versions of the file exist, the script will not
delete. If the MD5 comparison is not equal, the script will not delete.

A sysop account on the local wiki is required if you want all features of
this script to work properly.

This script understands various command-line arguments:
    -autonomous:    run automatically, do not ask any questions. All files
                    that qualify for deletion are deleted. Reduced screen
                    output.

    -replace:       replace links if the files are equal and the file names
                    differ

    -replacealways: replace links if the files are equal and the file names
                    differ without asking for confirmation

    -replaceloose:  Do loose replacements.  This will replace all occurences
                    of the name of the image (and not just explicit image
                    syntax).  This should work to catch all instances of the
                    file, including where it is used as a template parameter
                    or in galleries.  However, it can also make more
                    mistakes.

    -replaceonly:   Use this if you do not have a local sysop account, but do
                    wish to replace links from the NowCommons template.

Known issues. Please fix these if you are capable and motivated:
- if a file marked nowcommons is not present on Wikimedia Commons, the bot
  will exit.
"""
#
# (C) Wikipedian, 2006-2007
# (C) Siebrand Mazeland, 2007
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import sys, re
import wikipedia, pagegenerators
import image
# only for nowCommonsMessage
from imagetransfer import nowCommonsMessage

autonomous = False
replace = False
replacealways = False
replaceloose = False
replaceonly = False

for arg in wikipedia.handleArgs():
    if arg == '-autonomous':
        autonomous = True
    if arg == '-replace':
        replace = True
    if arg == '-replacealways':
        replace = True
        replacealways = True
    if arg == '-replaceloose':
        replaceloose = True
    if arg == '-replaceonly':
        replaceonly = True

nowCommons = {
    '_default': [
        u'NowCommons'
    ],
	'ar': [
        u'الآن كومنز',
        u'الآن كومونز',
    ],
    'de': [
        u'NowCommons',
        u'NC',
        u'NCT',
        u'Nowcommons',
    ],
    'en': [
        u'NowCommons',
        u'Ncd',
    ],
    'eo': [
        u'Nun en komunejo',
        u'NowCommons',
    ],
    'fr': [
        u'Désormais sur Commons'
    ],
    'he': [
        u'גם בוויקישיתוף'
    ],
    'ja':[
        u'NowCommons',
    ],
    'ia': [
        u'OraInCommons'
    ],
    'nl': [
        u'NuCommons',
        u'Nucommons',
        u'NowCommons',
        u'Nowcommons',
        u'NCT',
        u'Nct',
    ],
    'ro': [
        u'NowCommons'
    ],
    'zh':[
        u'NowCommons',
        u'Nowcommons',
        u'NCT',
    ],
}

namespaceInTemplate = [
    'en',
    'ia',
    'ja',
    'lt',
    'ro',
    'zh',
]


#nowCommonsMessage = imagetransfer.nowCommonsMessage

class NowCommonsDeleteBot:
    def __init__(self):
        self.site = wikipedia.getSite()
        if repr(self.site) == 'commons:commons':
            sys.exit('Do not run this bot on Commons!')
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
            # Show the title of the page we're working on.
            # Highlight the title in purple.
            wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" % page.title())
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
                    wikipedia.output(u"This image has a version history. Please delete it manually after making sure that the old versions are not worth keeping.""")
                    continue
                if localImagePage.titleWithoutNamespace() != commonsImagePage.titleWithoutNamespace():
                    usingPages = list(localImagePage.usingPages())
                    if usingPages and usingPages != [localImagePage]:
                        wikipedia.output(u'\"\03{lightred}%s\03{default}\" is still used in %i pages.' % (localImagePage.titleWithoutNamespace(), len(usingPages)))
                        if replace == True:
                                wikipedia.output(u'Replacing \"\03{lightred}%s\03{default}\" by \"\03{lightgreen}%s\03{default}\".' % (localImagePage.titleWithoutNamespace(), commonsImagePage.titleWithoutNamespace()))
                                oImageRobot = image.ImageRobot(pagegenerators.FileLinksGenerator(localImagePage), localImagePage.titleWithoutNamespace(), commonsImagePage.titleWithoutNamespace(), '', replacealways, replaceloose)
                                oImageRobot.run()
                        else:
                            wikipedia.output(u'Please change them manually.')
                        continue
                    else:
                        wikipedia.output(u'No page is using \"\03{lightgreen}%s\03{default}\" anymore.' % localImagePage.titleWithoutNamespace())
                commonsText = commonsImagePage.get()
                if replaceonly == False:
                    if md5 == commonsImagePage.getFileMd5Sum():
                        wikipedia.output(u'The image is identical to the one on Commons.')
                        if autonomous == False:
                            wikipedia.output(u'\n\n>>>> Description on \03{lightpurple}%s\03{default} <<<<\n' % page.title())
                            wikipedia.output(localImagePage.get())
                            wikipedia.output(u'\n\n>>>> Description on \03{lightpurple}%s\03{default} <<<<\n' % commonsImagePage.title())
                            wikipedia.output(commonsText)
                            choice = wikipedia.inputChoice(u'Does the description on Commons contain all required source and license information?', ['yes', 'no'], ['y', 'N'], 'N')
                            if choice == 'y':
                                localImagePage.delete(comment + ' [[:commons:Image:%s]]' % filenameOnCommons, prompt = False)
                        else:
                            localImagePage.delete(comment + ' [[:commons:Image:%s]]' % filenameOnCommons, prompt = False)
                    else:
                        wikipedia.output(u'The image is not identical to the one on Commons.')
            except (wikipedia.NoPage, wikipedia.IsRedirectPage), e:
                wikipedia.output(u'%s' % e)
                continue

def main():
    bot = NowCommonsDeleteBot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
