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

    -hash:          Use the hash to identify the images that are the same. It
                    doesn't work always, so the bot opens two tabs to let to
                    the user to check if the images are equal or not.

-- Example --
python nowcommons.py -replaceonly -hash -replace -replaceloose -replacealways

-- Known issues --
Please fix these if you are capable and motivated:
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

import sys, re, webbrowser
import wikipedia, pagegenerators
import welcome # for urlname
import image
# only for nowCommonsMessage
from imagetransfer import nowCommonsMessage

autonomous = False
replace = False
replacealways = False
replaceloose = False
replaceonly = False
use_hash = False

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
    if arg == '-hash':
        use_hash = True

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
    'hu': [
        u'Azonnali-commons',
        u'NowCommons',
        u'Nowcommons',
        u'NC'
    ],
    'ja':[
        u'NowCommons',
    ],
    'ia': [
        u'OraInCommons'
    ],
    'it': [
        u'NowCommons',
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
    'it',
    'ja',
    'lt',
    'ro',
    'zh',
]

# Stemma and stub are images not to be deleted (and are a lot) on it.wikipedia
# if your project has images like that, put the word often used here to skip them
word_to_skip = {
    'en': [],
    'it': ['stemma', 'stub', 'hill40 '],
    }

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

    def useHashGenerator(self):
        # http://toolserver.org/~multichill/nowcommons.php?language=it&page=2&filter=
        lang = self.site.lang
        num_page = 0
        word_to_skip_translated = wikipedia.translate(self.site, word_to_skip)
        images_processed = list()
        while 1:
            url = 'http://toolserver.org/~multichill/nowcommons.php?language=%s&page=%s&filter=' % (lang, num_page)
            HTML_text = self.site.getUrl(url, no_hostname = True)
            reg = r'<[Aa] href="(?P<urllocal>.*?)">(?P<imagelocal>.*?)</[Aa]> +?</td><td>\n\s*?'
            reg += r'<[Aa] href="(?P<urlcommons>http://commons.wikimedia.org/.*?)">Image:(?P<imagecommons>.*?)</[Aa]> +?</td><td>'
            regex = re.compile(reg, re.UNICODE)
            found_something = False
            change_page = True
            for x in regex.finditer(HTML_text):
                found_something = True
                image_local = x.group('imagelocal')
                image_commons = x.group('imagecommons')
                if image_local in images_processed:
                    continue
                change_page = False
                images_processed.append(image_local)
                # Skip images that have something in the title (useful for it.wiki)
                image_to_skip = False
                for word in word_to_skip_translated:
                    if word.lower() in image_local.lower():
                        image_to_skip = True
                if image_to_skip:
                    continue
                url_local = x.group('urllocal')
                url_commons = x.group('urlcommons')
                wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" % image_local)
                wikipedia.output(u'Local: %s\nCommons: %s\n' % (url_local, url_commons))
                result1 = webbrowser.open(url_local, 0, 1)
                result2 = webbrowser.open(url_commons, 0, 1)
                if image_local.split('Image:')[1] == image_commons:
                    choice = wikipedia.inputChoice(u'The local and the commons images have the same name, continue?', ['Yes', 'No'], ['y', 'N'], 'N')
                else:
                    choice = wikipedia.inputChoice(u'Are the two images equal?', ['Yes', 'No'], ['y', 'N'], 'N')
                if choice.lower() in ['y', 'yes']:
                    yield [image_local, image_commons]
                else:
                    continue
            # The page is dinamically updated, so we may don't need to change it
            if change_page:
                num_page += 1
            # If no image found means that there aren't anymore, break.
            if not found_something:
                break

    def getPageGenerator(self):
        if use_hash:
            gen = self.useHashGenerator()
        else:
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
                    for par in params:
                        if ':' in par:
                            filenameOnCommons = par[par.index(':') + 1:]
                else:
                    filenameOnCommons = params[0]
                return filenameOnCommons

    def run(self):
        commons = wikipedia.getSite('commons', 'commons')
        comment = wikipedia.translate(self.site, nowCommonsMessage)

        for page in self.getPageGenerator():
            if use_hash:
                # Page -> Has the namespace | commons image -> Not
                images_list = page # 0 -> local image, 1 -> commons image
                page = wikipedia.Page(self.site, images_list[0])
            else:
                # If use_hash is true, we have already print this before, no need
                # Show the title of the page we're working on.
                # Highlight the title in purple.
                wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" % page.title())
            try:
                localImagePage = wikipedia.ImagePage(self.site, page.title())
                if localImagePage.fileIsOnCommons():
                    wikipedia.output(u'File is already on Commons.')
                    continue
                md5 = localImagePage.getFileMd5Sum()
                if use_hash:
                    filenameOnCommons = images_list[1]
                else:
                    filenameOnCommons = self.findFilenameOnCommons(localImagePage)
                if not filenameOnCommons and not use_hash:
                    wikipedia.output(u'NowCommons template not found.')
                    continue
                commonsImagePage = wikipedia.ImagePage(commons, 'Image:%s' % filenameOnCommons)
                if localImagePage.titleWithoutNamespace() == commonsImagePage.titleWithoutNamespace() and use_hash:
                    wikipedia.output(u'The local and the commons images have the same name')
                if len(localImagePage.getFileVersionHistory()) > 1 and not use_hash:
                    wikipedia.output(u"This image has a version history. Please delete it manually after making sure that the old versions are not worth keeping.""")
                    continue
                if localImagePage.titleWithoutNamespace() != commonsImagePage.titleWithoutNamespace():
                    usingPages = list(localImagePage.usingPages())
                    if usingPages and usingPages != [localImagePage]:
                        wikipedia.output(u'\"\03{lightred}%s\03{default}\" is still used in %i pages.' % (localImagePage.titleWithoutNamespace(), len(usingPages)))
                        if replace == True:
                                wikipedia.output(u'Replacing \"\03{lightred}%s\03{default}\" by \"\03{lightgreen}%s\03{default}\".' % (localImagePage.titleWithoutNamespace(), commonsImagePage.titleWithoutNamespace()))
                                oImageRobot = image.ImageRobot(pagegenerators.FileLinksGenerator(localImagePage),
                                                localImagePage.titleWithoutNamespace(), commonsImagePage.titleWithoutNamespace(),
                                                '', replacealways, replaceloose)
                                oImageRobot.run()
                                # If the image is used with the urlname the previous function won't work
                                if len(list(wikipedia.ImagePage(self.site, page.title()).usingPages())) > 0 and replaceloose:
                                    oImageRobot = image.ImageRobot(pagegenerators.FileLinksGenerator(localImagePage),
                                                    welcome.urlname(localImagePage.titleWithoutNamespace(), self.site), commonsImagePage.titleWithoutNamespace(),
                                                    '', replacealways, replaceloose)
                                    oImageRobot.run()
                                # refresh because we want the updated list
                                usingPages = len(list(wikipedia.ImagePage(self.site, page.title()).usingPages()))
                                if usingPages > 0 and use_hash:
                                    # just an enter
                                    wikipedia.input(u'There are still %s pages with this image, confirm the manual removal from them please.' % usingPages)

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
                            if choice.lower() in ['y', 'yes']:
                                localImagePage.delete(comment + ' [[:commons:Image:%s]]' % filenameOnCommons, prompt = False)
                        else:
                            localImagePage.delete(comment + ' [[:commons:Image:%s]]' % filenameOnCommons, prompt = False)
                    else:
                        wikipedia.output(u'The image is not identical to the one on Commons.')
            except (wikipedia.NoPage, wikipedia.IsRedirectPage), e:
                wikipedia.output(u'%s' % e[0])
                continue

def main():
    bot = NowCommonsDeleteBot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
