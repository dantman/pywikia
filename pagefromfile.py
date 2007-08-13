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

import wikipedia, config
import re, sys, codecs

class PageFromFileRobot:
    """
    Responsible for writing pages to the wiki, with the titles and contents
    given by a PageFromFileReader.
    """

    msg = {
        'de': u'Automatischer Import von Artikeln',
        'en': u'Automated import of articles',
        'fr': u'Import automatique',
        'he': u'ייבוא ערכים אוטומטי',
        'ia': u'Importation automatic de articulos',
        'id': u'Impor artikel automatis',
        'it': u'Caricamento automatico',
        'ksh': u'Automatesch aanjelaat',
        'nl': u'Geautomatiseerde import',
        'no': u'bot: Automatisk import',
        'pl': u'Automatyczny import artykułów',
        'pt': u'Importação automática de artigos'
    }

    # The following messages are added to topic when the page already exists
    msg_top = {
        'de': u'ergänze am Anfang',
        'en': u'append on top',
        'he': u'הצמד בהתחלה',
        'fr': u'attaché en haut',
        'id': u'ditambahkan di atas',
        'it': u'aggiungo in cima',
        'ksh': u'Automatesch füürjesaz',
        'nl': u'bovenaan toegevoegd',
        'no': u'legger til øverst',
        'pl': u'dodaj na górze',
        'pt': u'adicionado no topo'
    }

    msg_bottom = {
        'de': u'ergänze am Ende',
        'en': u'append on bottom',
        'he': u'הצמד בסוף',
        'fr': u'attaché en bas',
        'id': u'ditambahkan di bawah',
        'it': u'aggiungo in fondo',
        'ksh': u'Automatesch aanjehange',
        'nl': u'onderaan toegevoegd',
        'no': u'legger til nederst',
        'pl': u'dodaj na dole',
        'pt': u'adicionando no fim'
    }

    msg_force = {
        'en': u'bestehender Text überschrieben',
        'en': u'existing text overwritten',
        'he': u'הטקסט הקיים נדרס',
        'fr': u'texte existant écrasé',
        'id': u'menimpa teks yang ada',
        'it': u'sovrascritto il testo esistente',
        'ksh': u'Automatesch ußjetuusch',
        'nl': u'bestaande tekst overschreven',
        'no': u'erstatter eksisterende tekst',
        'pl': u'aktualny tekst nadpisany',
        'pt': u'sobrescrever texto'
    }

    def __init__(self, reader, force, append, minor, debug):
        self.reader = reader
        self.force = force
        self.append = append
        self.minor = minor
        self.debug = debug

    def run(self):
        for title, contents in self.reader.run():
            self.create(title, contents)

    def create(self, title, contents):
        mysite = wikipedia.getSite()

        page = wikipedia.Page(mysite, title)
        # Show the title of the page we're working on.
        # Highlight the title in purple.
        wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" % page.title())
        commenttext = wikipedia.translate(mysite, self.msg)

        #Remove trailing newlines (cause troubles when creating redirects)
        contents = re.sub('^[\r\n]*','',contents)
        if page.exists():
            if self.append == "Top":
                old_text = page.get()
                contents = contents + old_text
                commenttext_top = commenttext + " - " + wikipedia.translate(mysite, self.msg_top)
                wikipedia.output(u"Page %s already exists, appending on top!" % title)
                if not self.debug:
                    page.put(contents, comment = commenttext_top, minorEdit = self.minor)
            elif self.append == "Bottom":
                old_text = page.get()
                contents = old_text + contents
                commenttext_bottom = commenttext + " - " + wikipedia.translate(mysite, self.msg_bottom)
                wikipedia.output(u"Page %s already exists, appending on bottom!"%title)
                if not self.debug:
                    page.put(contents, comment = commenttext_bottom, minorEdit = self.minor)
            elif self.force:
                commenttext_force = commenttext + " *** " + wikipedia.translate(mysite, self.msg_force) + " ***"
                wikipedia.output(u"Page %s already exists, ***overwriting!" % title)
                if not self.debug:
                    page.put(contents, comment = commenttext_force, minorEdit = self.minor)
            else:
                wikipedia.output(u"Page %s already exists, not adding!" % title)
        else:
            if not self.debug:
                page.put(contents, comment = commenttext, minorEdit = self.minor)

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
            if self.notitle:
                #Remove title (to allow creation of redirects)
                contents = titleR.sub('', contents, count = 1)
        except AttributeError:
            wikipedia.output(u'\nStart or end marker not found.')
            return 0, None, None
        try:
            title = titleR.search(contents).group(1)
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
    minor = False
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
            wikipedia.output(u"Debug mode enabled.")
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
            commenttext = arg[9:]
        else:
            wikipedia.output(u"Disregarding unknown argument %s." % arg)

    reader = PageFromFileReader(filename, pageStartMarker, pageEndMarker, titleStartMarker, titleEndMarker, include, notitle)

    bot = PageFromFileRobot(reader, force, append, minor, debug)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    except:
        wikipedia.stopme()
        raise
    else:
        wikipedia.stopme()
