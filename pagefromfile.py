#!/usr/bin/python
#coding: utf-8
"""
This bot takes its input from a file that contains a number of
pages to be put on the wiki. The pages should all have the same
begin and end text (which may not overlap).

By default the text should have the intended title of the page
as the first text in bold (that is, between ''' and '''),
you can modify this behavior with command line options.

The default is not to include the begin and
end text in the page, if you want to include that text, use
the -include option.

Specific arguments:
-start:xxx      Specify the text that marks the beginning of a page
-end:xxx        Specify the text that marks the end of a page
-file:xxx       Give the filename we are getting our material from
-include        The beginning and end markers should be included
                in the page.
-titlestart:xxx Use xxx in place of ''' for identifying the
                beginning of page title
-titleend:xxx   Use xxx in place of ''' for identifying the
                end of page title
-summary:xxx    Use xxx as the summary for the upload
-minor          set minor edit flag on page edits
-debug          Do not really upload pages, just check and report
                messages

If the page to be uploaded already exists:
-safe           do nothing (default)
-appendtop      add the text to the top of it
-appendbottom   add the text to the bottom of it
-force          overwrite the existing page
-notitle        do not include the title line in the page
"""
#
# (C) Andre Engels, 2004
#
# Distributed under the terms of the MIT license.
#

__version__='$Id$'

import re, codecs
import wikipedia, config

class PageFromFileRobot:
    """
    Responsible for writing pages to the wiki, with the titles and contents
    given by a PageFromFileReader.
    """

    msg = {
	    'ar': u'استيراد تلقائي للمقالات',
        'de': u'Automatischer Import von Artikeln',
        'en': u'Automated import of articles',
        'fr': u'Import automatique',
        'he': u'ייבוא ערכים אוטומטי',
        'ia': u'Importation automatic de articulos',
        'id': u'Impor artikel automatis',
        'it': u'Caricamento automatico',
        'ja': u'ロボットによる: 記事の作成',
        'ksh': u'Automatesch aanjelaat',
        'nl': u'Geautomatiseerde import',
        'no': u'bot: Automatisk import',
        'pl': u'Automatyczny import artykułów',
        'pt': u'Importação automática de artigos',
        'zh': u'機器人: 自動匯入頁面',
    }

    # The following messages are added to topic when the page already exists
    msg_top = {
	    'ar': u'كتابة على الأعلى',
        'de': u'ergänze am Anfang',
        'en': u'append on top',
        'he': u'הוספה בראש הדף',
        'fr': u'rajouté en haut',
        'id': u'ditambahkan di atas',
        'it': u'aggiungo in cima',
        'ja': u'ロボットによる: 冒頭への追加',
        'ksh': u'Automatesch füürjesaz',
        'nl': u'bovenaan toegevoegd',
        'no': u'legger til øverst',
        'pl': u'dodaj na górze',
        'pt': u'adicionado no topo',
        'zh': u'機器人: 增加至最上層',
    }

    msg_bottom = {
	    'ar': u'كتابة على الأسفل',
        'de': u'ergänze am Ende',
        'en': u'append on bottom',
        'he': u'הוספה בתחתית הדף',
        'fr': u'rajouté en bas',
        'id': u'ditambahkan di bawah',
        'it': u'aggiungo in fondo',
        'ja': u'ロボットによる: 末尾への追加',
        'ksh': u'Automatesch aanjehange',
        'nl': u'onderaan toegevoegd',
        'no': u'legger til nederst',
        'pl': u'dodaj na dole',
        'pt': u'adicionando no fim',
        'zh': u'機器人: 增加至最底層',
    }

    msg_force = {
	    'ar': u'تمت الكتابة على النص الموجود',
        'de': u'bestehender Text überschrieben',
        'en': u'existing text overwritten',
        'he': u'הטקסט הישן נמחק',
        'fr': u'texte existant écrasé',
        'id': u'menimpa teks yang ada',
        'it': u'sovrascritto il testo esistente',
        'ja': u'ロボットによる: ページの置換',
        'ksh': u'Automatesch ußjetuusch',
        'nl': u'bestaande tekst overschreven',
        'no': u'erstatter eksisterende tekst',
        'pl': u'aktualny tekst nadpisany',
        'pt': u'sobrescrever texto'
        'zh': u'機器人: 覆寫已存在的文字',
    }

    def __init__(self, reader, force, append, summary, minor, autosummary, debug):
        self.reader = reader
        self.force = force
        self.append = append
        self.summary = summary
        self.minor = minor
        self.autosummary = autosummary
        self.debug = debug

    def run(self):
        for title, contents in self.reader.run():
            self.put(title, contents)

    def put(self, title, contents):
        mysite = wikipedia.getSite()

        page = wikipedia.Page(mysite, title)
        # Show the title of the page we're working on.
        # Highlight the title in purple.
        wikipedia.output(u">>> \03{lightpurple}%s\03{default} <<<" % page.title())

        if self.summary:
            comment = self.summary
        else:
            comment = wikipedia.translate(mysite, self.msg)

        comment_top = comment + " - " + wikipedia.translate(mysite, self.msg_top)
        comment_bottom = comment + " - " + wikipedia.translate(mysite, self.msg_bottom)
        comment_force = comment + " *** " + wikipedia.translate(mysite, self.msg_force) + " ***"

        #Remove trailing newlines (cause troubles when creating redirects)
        contents = re.sub('^[\r\n]*','',contents)

        if page.exists():
            if self.append == "Top":
                wikipedia.output(u"Page %s already exists, appending on top!" % title)
                contents = contents + page.get()
                comment = comment_top
            elif self.append == "Bottom":
                wikipedia.output(u"Page %s already exists, appending on bottom!" % title)
                contents = page.get() + contents
                comment = comment_bottom
            elif self.force:
                wikipedia.output(u"Page %s already exists, ***overwriting!" % title)
                comment = comment_force
            else:
                wikipedia.output(u"Page %s already exists, not adding!" % title)
                return
        else:
           if self.autosummary:
                comment = ''
                wikipedia.setAction('')

        if self.debug:
            wikipedia.output("*** Debug mode ***\n" + \
                "\03{lightpurple}title\03{default}: " + title + "\n" + \
                "\03{lightpurple}contents\03{default}:\n" + contents + "\n" \
                "\03{lightpurple}comment\03{default}: " + comment + "\n")
            return

        try:
            page.put(contents, comment = comment, minorEdit = self.minor)
        except wikipedia.LockedPage:
            wikipedia.output(u"Page %s is locked; skipping." % title)
        except wikipedia.EditConflict:
            wikipedia.output(u'Skipping %s because of edit conflict' % title)
        except wikipedia.SpamfilterError, error:
            wikipedia.output(u'Cannot change %s because of spam blacklist entry %s' % (title, error.url))

class PageFromFileReader:
    """
    Responsible for reading the file.

    The run() method yields a (title, contents) tuple for each found page.
    """
    def __init__(self, filename, pageStartMarker, pageEndMarker, titleStartMarker, titleEndMarker, include, notitle):
        self.filename = filename
        self.pageStartMarker = pageStartMarker
        self.pageEndMarker = pageEndMarker
        self.titleStartMarker = titleStartMarker
        self.titleEndMarker = titleEndMarker
        self.include = include
        self.notitle = notitle

    def run(self):
        f = codecs.open(self.filename, 'r', encoding = config.textfile_encoding)
        text = f.read()
        position = 0
        while True:
            length, title, contents = self.findpage(text[position:])
            if length == 0:
                break
            else:
                position += length
                yield title, contents

    def findpage(self, text):
        pageR = re.compile(self.pageStartMarker + "(.*?)" + self.pageEndMarker, re.DOTALL)
        titleR = re.compile(self.titleStartMarker + "(.*?)" + self.titleEndMarker)

        try:
            location = pageR.search(text)
            if self.include:
                contents = location.group()
            else:
                contents = location.group(1)
        except AttributeError:
            wikipedia.output(u'\nStart or end marker not found.')
            return 0, None, None
        try:
            title = titleR.search(contents).group(1)
            if self.notitle:
                #Remove title (to allow creation of redirects)
                contents = titleR.sub('', contents, count = 1)
        except AttributeError:
            wikipedia.output(u'\nNo title found - skipping a page.')
            return 0, None, None
        else:
            return location.end(), title, contents

def main():
    # Adapt these to the file you are using. 'pageStartMarker' and 'pageEndMarker' are
    # the beginning and end of each entry. Take text that should be included
    # and does not occur elsewhere in the text.

    # TODO: make config variables for these.
    filename = "dict.txt"
    pageStartMarker = "{{-start-}}"
    pageEndMarker = "{{-stop-}}"
    titleStartMarker = u"'''"
    titleEndMarker = u"'''"

    include = False
    force = False
    append = None
    notitle = False
    summary = None
    minor = False
    autosummary = False
    debug = False

    for arg in wikipedia.handleArgs():
        if arg.startswith("-start:"):
            pageStartMarker = arg[7:]
        elif arg.startswith("-end:"):
            pageEndMarker = arg[5:]
        elif arg.startswith("-file:"):
            filename = arg[6:]
        elif arg == "-include":
            include = True
        elif arg == "-appendtop":
            append = "Top"
        elif arg == "-appendbottom":
            append = "Bottom"
        elif arg == "-force":
            force=True
        elif arg == "-debug":
            debug = True
        elif arg == "-safe":
            force = False
            append = None
        elif arg == '-notitle':
            notitle = True
        elif arg == '-minor':
            minor = True
        elif arg.startswith("-titlestart:"):
            titleStartMarker = arg[12:]
        elif arg.startswith("-titleend:"):
            titleEndMarker = arg[10:]
        elif arg.startswith("-summary:"):
            summary = arg[9:]
        elif arg == '-autosummary':
            autosummary = True
        else:
            wikipedia.output(u"Disregarding unknown argument %s." % arg)

    reader = PageFromFileReader(filename, pageStartMarker, pageEndMarker, titleStartMarker, titleEndMarker, include, notitle)

    bot = PageFromFileRobot(reader, force, append, summary, minor, autosummary, debug)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    except:
        wikipedia.stopme()
        raise
    else:
        wikipedia.stopme()
