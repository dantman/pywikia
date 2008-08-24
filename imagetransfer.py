# -*- coding: utf-8 -*-
"""
Script to copy images to Wikimedia Commons, or to another wiki.

Syntax:

    python imagetransfer.py pagename [-interwiki] [-targetLang:xx] -targetFamily:yy]

Arguments:

  -interwiki   Look for images in pages found through interwiki links.

  -tolang:xx   Copy the image to the wiki in language xx

  -tofamily:yy Copy the image to a wiki in the family yy

  -file:zz     Upload many files from textfile: [[Image:xx]]
                                                [[Image:yy]]

If pagename is an image description page, offers to copy the image to the
target site. If it is a normal page, it will offer to copy any of the images
used on that page, or if the -interwiki argument is used, any of the images
used on a page reachable via interwiki links.
"""
#
# (C) Andre Engels, 2004
#
# Distributed under the terms of the MIT license.
#
__version__='$Id$'

import re, sys, md5, urllib
import wikipedia, upload, config, pagegenerators

copy_message = {
    'ar':u"هذه الصورة تم نقلها من %s. الوصف الأصلي كان:\r\n\r\n%s",
    'en':u"This image was copied from %s. The original description was:\r\n\r\n%s",
    'de':u"Dieses Bild wurde von %s kopiert. Die dortige Beschreibung lautete:\r\n\r\n%s",
    'fr':u"Cette image est copiée de %s. La description originale était:\r\n\r\n%s",
    'he':u"תמונה זו הועתקה מהאתר %s. תיאור הקובץ המקורי היה:\r\n\r\n%s",
    'hu':u"Kép másolása innen: %s. Az eredeti leírás:\r\n\r\n%s",
    'ia':u"Iste imagine esseva copiate de %s. Le description original esseva:\r\n\r\n%s",
    'it':u"Questa immagine è stata copiata da %s. La descrizione originale era:\r\n\r\n%s",
    'kk':u"Бұл сурет %s дегеннен көшірілді. Түпнұсқа сипатттамасы былай болды:\r\n\r\n%s",
    'lt':u"Šis paveikslėlis buvo įkeltas iš %s. Originalus aprašymas buvo:\r\n\r\n%s",
    'nl':u"Afbeelding gekopieerd vanaf %s. De beschrijving daar was:\r\n\r\n%s",
    'pl':u"Ten obraz został skopiowany z %s. Oryginalny opis to:\r\n\r\n%s",
    'pt':u"Esta imagem foi copiada de %s. A descrição original foi:\r\n\r\n%s",
    'sr':u"Ова слика је копирана са %s. Оригинални опис је:\r\n\r\n%s",
    'zh':u"本圖像從 %s 複製，原始說明資料：\r\n\r\n%s",
}

nowCommonsTemplate = {
    'ar': u'{{subst:الآن_كومنز|Image:%s}}',
    'de': u'{{NowCommons|%s}}',
    'fr': u'{{Désormais sur Commons|%s}}',
    'en': u'{{subst:ncd|Image:%s}}',
    'he': u'{{גם בוויקישיתוף|%s}}',
    'hu': u'{{azonnali-commons|Kép:%s}}',
    'ia': u'{{OraInCommons|Imagine:%s}}',
    'it': u'{{NowCommons unlink|%s}}',
    'ja': u'{{NowCommons|Image:%s}}',
    'kk': u'{{NowCommons|Image:%s}}',
    'lt': u'{{NowCommons|Image:%s}}',
    'nl': u'{{NuCommons|Image:%s}}',
    'pl': u'{{NowCommons|%s}}',
    'pt': u'{{NowCommons|%s}}',
    'sr': u'{{NowCommons|%s}}',
    'zh': u'{{NowCommons|Image:%s}}',
}

#nowCommonsThis = {
    #'en': u'{{NowCommonsThis|%s}}',
    #'it': u'{{NowCommons omonima|%s}}',
    #'kk': u'{{NowCommonsThis|%s}}',
    #'pt': u'{{NowCommonsThis|%s}}',
#}

nowCommonsMessage = {
    'ar': u'الملف الآن متوفر في ويكيميديا كومنز.',
    'de': u'Datei ist jetzt auf Wikimedia Commons verfügbar.',
    'en': u'File is now available on Wikimedia Commons.',
    'eo': u'Dosiero nun estas havebla en la Wikimedia-Komunejo.',
    'he': u'הקובץ זמין כעת בוויקישיתוף.',
    'hu': u'A fájl most már elérhető a Wikimedia Commonson',
    'ia': u'Le file es ora disponibile in Wikimedia Commons.',
    'ja': u'ファイルはウィキメディア・コモンズにあります',
    'it': u'L\'immagine è adesso disponibile su Wikimedia Commons.',
    'kk': u'Файлды енді Wikimedia Ортаққорынан қатынауға болады.',
    'lt': u'Failas įkeltas į Wikimedia Commons projektą.',
    'nl': u'Dit bestand staat nu op [[w:nl:Wikimedia Commons|Wikimedia Commons]].',
    'pl': u'Plik jest teraz dostępny na Wikimedia Commons.',
    'pt': u'Arquivo está agora na Wikimedia Commons.',
    'sr': u'Слика је сада доступна и на Викимедија Остави.',
    'zh': u'檔案已存在於維基共享資源。',
}

#nowCommonsThisMessage = {
    #'en': u'File is now available on Commons with the same name.',
    #'he': u'הקובץ זמין כעת בוויקישיתוף בשם זהה.',
    #'it': u'L\'immagine è adesso disponibile su Wikimedia Commons con lo stesso nome.',
    #'kk': u'Файлды дәл сол атауымен енді Ортаққордан қатынауға болады.',
    #'pt': u'Esta imagem está agora no Commons com o mesmo nome.',
#}

# Translations for license templates.
# Must only be given when they are in fact different.
licenseTemplates = {
    ('wikipedia:de', 'commons:commons'): {
        u'Bild-GFDL':                u'GFDL',
        u'Bild-GFDL-OpenGeoDB':      u'GFDL-OpenGeoDB',
        u'Bild-Innweb-Lizenz':       u'Map-Austria-GNU',
        u'Bild-PD':                  u'PD',
        u'Bild-PD-alt':              u'PD-old',
        u'Bild-PD-Kunst':            u'PD-Art',
        u'Bild-PD-US':               u'PD-USGov',
    },
    ('wikipedia:fr', 'commons:commons'): {
        u'Domaine public':           u'PD'
    },
    ('wikipedia:he', 'commons:commons'): {
        u'שימוש חופשי':              u'PD-self',
        u'שימוש חופשי מוגן':         u'Copyrighted free use',
        u'שימוש חופשי מוגן בתנאי':   u'Copyrighted free use provided that',
        u'תמונה ישנה':              u'PD-Israel',
        u'ייחוס':                   u'Attribution',
        u'לוגו ויקימדיה':           u'Copyright by Wikimedia',
    },
    ('wikipedia:hu', 'commons:commons'): {
        u'Közkincs':                 u'PD',
        u'Közkincs-régi':            u'PD-old',
    },
    ('wikipedia:pt', 'commons:commons'): {
        u'Domínio público':          u'PD',
    },
}

class ImageTransferBot:
    def __init__(self, generator, targetSite = None, interwiki = False):
        self.generator = generator
        self.interwiki = interwiki
        self.targetSite = targetSite

    def transferImage(self, sourceImagePage, debug=False):
        """Gets a wikilink to an image, downloads it and its description,
           and uploads it to another wikipedia.
           Returns the filename which was used to upload the image
           This function is used by imagetransfer.py and by copy_table.py
        """
        sourceSite = sourceImagePage.site()
        if debug: print "--------------------------------------------------"
        if debug: print "Found image: %s"% imageTitle
        url = sourceImagePage.fileUrl().encode('utf-8')
        wikipedia.output(u"URL should be: %s" % url)
        # localize the text that should be printed on the image description page
        try:
            description = sourceImagePage.get()
            # try to translate license templates
            if licenseTemplates.has_key((sourceSite.sitename(), self.targetSite.sitename())):
                for old, new in licenseTemplates[(sourceSite.sitename(), self.targetSite.sitename())].iteritems():
                    new = '{{%s}}' % new
                    old = re.compile('{{%s}}' % old)
                    description = wikipedia.replaceExcept(description, old, new, ['comment', 'math', 'nowiki', 'pre'])

            description = wikipedia.translate(self.targetSite, copy_message) % (sourceSite, description)
            description += '\n\n' + sourceImagePage.getFileVersionHistoryTable()
            # add interwiki link
            if sourceSite.family == self.targetSite.family:
                description += "\r\n\r\n" + sourceImagePage.aslink(forceInterwiki = True)
        except wikipedia.NoPage:
            description=''
            print "Image does not exist or description page is empty."
        except wikipedia.IsRedirectPage:
            description=''
            print "Image description page is redirect."
        else:
            bot = upload.UploadRobot(url = url, description = description, targetSite = self.targetSite, urlEncoding = sourceSite.encoding())
            # try to upload
            targetFilename = bot.run()
            if targetFilename and self.targetSite.family.name == 'commons' and self.targetSite.lang == 'commons':
                # upload to Commons was successful
                reason = wikipedia.translate(sourceSite, nowCommonsMessage)
                # try to delete the original image if we have a sysop account
                if config.sysopnames.has_key(sourceSite.family.name) and config.sysopnames[sourceSite.family.name].has_key(sourceSite.lang):
                    if sourceImagePage.delete(reason):
                        return
                if nowCommonsTemplate.has_key(sourceSite.lang) and config.usernames.has_key(sourceSite.family.name) and config.usernames[sourceSite.family.name].has_key(sourceSite.lang):
                    # add the nowCommons template.
                    wikipedia.output(u'Adding nowCommons template to %s' % sourceImagePage.title())
                    sourceImagePage.put(sourceImagePage.get() + '\n\n' + nowCommonsTemplate[sourceSite.lang] % targetFilename, comment = nowCommonsMessage[sourceSite.lang])

    def showImageList(self, imagelist):
        for i in range(len(imagelist)):
            image = imagelist[i]
            #sourceSite = sourceImagePage.site()
            print "-"*60
            wikipedia.output(u"%s. Found image: %s"% (i, image.aslink()))
            try:
                # Show the image description page's contents
                wikipedia.output(image.get(throttle=False))
                # look if page already exists with this name.
                # TODO: consider removing this: a different image of the same
                # name may exist on the target wiki, and the bot user may want
                # to upload anyway, using another name.
                try:
                    # Maybe the image is on the target site already
                    targetTitle = '%s:%s' % (self.targetSite.image_namespace(), image.title().split(':', 1)[1])
                    targetImage = wikipedia.Page(self.targetSite, targetTitle)
                    targetImage.get(throttle=False)
                    wikipedia.output(u"Image with this name is already on %s." % self.targetSite)
                    print "-"*60
                    wikipedia.output(targetImage.get(throttle=False))
                    sys.exit()
                except wikipedia.NoPage:
                    # That's the normal case
                    pass
                except wikipedia.IsRedirectPage:
                    wikipedia.output(u"Description page on target wiki is redirect?!")

            except wikipedia.NoPage:
                break

        print "="*60

    def run(self):
        for page in self.generator:
            if self.interwiki:
                imagelist = []
                for linkedPage in page.interwiki():
                    imagelist += linkedPage.imagelinks(followRedirects = True)
            elif page.isImage():
                imagePage = wikipedia.ImagePage(page.site(), page.title())
                imagelist = [imagePage]
            else:
                imagelist = page.imagelinks(followRedirects = True)

            while len(imagelist)>0:
                self.showImageList(imagelist)
                if len(imagelist) == 1:
                    # no need to query the user, only one possibility
                    todo = 0
                else:
                    wikipedia.output(u"Give the number of the image to transfer.")
                    todo = wikipedia.input(u"To end uploading, press enter:")
                    if not todo:
                        break
                    todo = int(todo)
                if todo in range(len(imagelist)):
                    if imagelist[todo].fileIsOnCommons():
                        wikipedia.output(u'The image is already on Wikimedia Commons.')
                    else:
                        self.transferImage(imagelist[todo], debug = False)
                    # remove the selected image from the list
                    imagelist = imagelist[:todo] + imagelist[todo + 1:]
                else:
                    wikipedia.output(u'No such image number.')

def main():
    # if -file is not used, this temporary array is used to read the page title.
    pageTitle = []
    page = None
    gen = None
    interwiki = False
    targetLang = None
    targetFamily = None

    for arg in wikipedia.handleArgs():
        if arg == '-interwiki':
            interwiki = True
        elif arg.startswith('-tolang:'):
            targetLang = arg[8:]
        elif arg.startswith('-tofamily:'):
            targetFamily = arg[10:]
        elif arg.startswith('-file'):
            if len(arg) == 5:
                filename = wikipedia.input(u'Please enter the list\'s filename: ')
            else:
                filename = arg[6:]
            gen = pagegenerators.TextfilePageGenerator(filename)
        else:
            pageTitle.append(arg)

    if not gen:
        # if the page title is given as a command line argument,
        # connect the title's parts with spaces
        if pageTitle != []:
            pageTitle = ' '.join(pageTitle)
            page = wikipedia.Page(wikipedia.getSite(), pageTitle)
        # if no page title was given as an argument, and none was
        # read from a file, query the user
        if not page:
            pageTitle = wikipedia.input(u'Which page to check:')
            page = wikipedia.Page(wikipedia.getSite(), pageTitle)
            # generator which will yield only a single Page
        gen = iter([page])

    if not targetLang and not targetFamily:
        targetSite = wikipedia.getSite('commons', 'commons')
    else:
        if not targetLang:
            targetLang = wikipedia.getSite().language
        if not targetFamily:
            targetFamily = wikipedia.getSite().family
        targetSite = wikipedia.Site(targetLang, targetFamily)
    bot = ImageTransferBot(gen, interwiki = interwiki, targetSite = targetSite)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
