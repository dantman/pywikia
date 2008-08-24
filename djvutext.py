#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
This bot uploads text from djvu files onto pages in the "Page"
namespace.  It is intended to be used for Wikisource.

The following parameters are supported:

    -debug         If given, doesn't do any real changes, but only shows
                   what would have been changed.
    -ask           Ask for confirmation before creating each page.
    -index:...     Name of the index page
    -djvu:...      Filename of the djvu file
    -pages:<start>-<end> Page range to upload; <end> is optional

All other parameters will be regarded as part of the title of a single page,
and the bot will only work on that single page.
"""
__version__ = '$Id$'
import wikipedia
import os
import config, codecs

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
}

class DjVuTextBot:
    # Edit summary message that should be used.
    # NOTE: Put a good description here, and add translations, if possible!
    msg = {
        'en': u'Robot: creating page with text extracted from DjVu',
		'ar': u'روبوت: إنشاء صفحة بنص مستخرج من DjVu',
	    'fr': u'Bot: creating page with texte extracted from DjVu',
        'pt': u'Bot: criando página com texto extraído do DjVu',
    }
    # On English Wikisource, {{blank page}} is used to track blank pages.
    # It may be omitted by adding an empty string like has been done for 'fr'.
    blank = {
        'en': u'{{blank page}}',
	    'fr': u'',
        'pt': u'',
    }

    def __init__(self, djvu, index, pages):
        """
        Constructor. Parameters:
	   djvu : filename
	   index : page name
	   pages : page range
        """
        self.djvu = djvu
        self.index = index
	self.pages = pages
	self.debug = False
	self.ask = False

    def NoOfImages(self):
	cmd = "djvused -e 'n' \"%s\"" % (self.djvu)
        count = os.popen( cmd ).readline().rstrip()
	#count = count[:-1]
	print "page count = %s" % count
	count = int(count)
	print "page count = %d" % count
	return int(count)

    def PagesGenerator(self):
        start = 1
	end = self.NoOfImages()

	if self.pages:
	    pos = self.pages.find('-')
	    if pos != -1:
	        start = self.pages[:pos]
		if pos < len(self.pages)-1:
		    end = self.pages[pos+1:]
		    end = int(end)
	    else:
	        start = self.pages
		end = int(start)
	i = int(start)
	print "processing pages %d-%d" % (i, end)
	while i <= end:
	   yield i
	   i=i+1

    def run(self):
        # Set the edit summary message
        wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), self.msg))

        linkingPage = wikipedia.Page(wikipedia.getSite(), self.index)
        self.prefix = linkingPage.titleWithoutNamespace()
	if self.prefix[0:6] == 'Liber:':
	    self.prefix = self.prefix[6:]
	    wikipedia.output("Using prefix %s" % self.prefix)
        gen = self.PagesGenerator()

	site = wikipedia.getSite()
        self.username = config.usernames[site.family.name][site.lang]

        for pageno in gen:
	    print "Processing page %d" % pageno
            self.treat(pageno)

    def treat(self, pageno):
        """
        Loads the given page, does some changes, and saves it.
        """
	site = wikipedia.getSite()
	page_namespace = site.family.namespaces[104][site.lang]
	page = wikipedia.Page(site, '%s:%s/%d' % (page_namespace, self.prefix, pageno) )
	exists = page.exists()

        ################################################################
        # NOTE: Here you can modify the text in whatever way you want. #
        ################################################################

        print "fetching page %d" % (pageno)
	cmd = "djvutxt -page=%d \"%s\" \"%s.out\"" % (pageno, self.djvu, self.djvu)
        os.system ( cmd )

        f = codecs.open("%s.out" % self.djvu, 'r', config.textfile_encoding, 'replace')

	djvutxt = f.read()

	f.close()

        if not djvutxt:
	    djvutxt = wikipedia.translate(wikipedia.getSite(), self.blank)
	text = '<noinclude>{{PageQuality|1|%s}}<div class="pagetext">%s</noinclude>%s<noinclude><references/></div></noinclude>' % (self.username,"\n\n\n",djvutxt)

        # convert to wikisyntax
        #   this adds a second line feed, which makes a new paragraph
	text = text.replace('', "\n")

        # only save if something was changed
        if (not exists and text) or text != page.get():
            # Show the title of the page we're working on.
            # Highlight the title in purple.
            wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" % page.title())
            # show what was changed
	    if exists:
                wikipedia.showDiff(page.get(), text)
            else:
	        wikipedia.output(text)
            if not self.debug:
	        choice = 'y'
		if self.ask:
                    choice = wikipedia.inputChoice(u'Do you want to accept these changes?', ['Yes', 'No'], ['y', 'N'], 'N')
                if choice == 'y':
                    try:
                        # Save the page
                        page.put_async(text)
                    except wikipedia.LockedPage:
                        wikipedia.output(u"Page %s is locked; skipping." % page.aslink())
                    except wikipedia.EditConflict:
                        wikipedia.output(u'Skipping %s because of edit conflict' % (page.title()))
                    except wikipedia.SpamfilterError, error:
                        wikipedia.output(u'Cannot change %s because of spam blacklist entry %s' % (page.title(), error.url))


def main():
    index = None
    djvu = None
    pages = None
    # what would have been changed.
    debug = False
    ask = False

    # Parse command line arguments
    for arg in wikipedia.handleArgs():
        if arg.startswith("-debug"):
            debug = True
        elif arg.startswith("-ask"):
	    ask = True
        elif arg.startswith("-djvu:"):
	    djvu = arg[6:]
	elif arg.startswith("-index:"):
	    index = arg[7:]
        elif arg.startswith("-pages:"):
	    pages = arg[7:]
        else:
            print "Unknown argument %s" % arg

    if djvu and index:
	index_page = wikipedia.Page(wikipedia.getSite(), index)
	if not index_page.exists():
	     wikipedia.output("%s does not exist" % index)
	     raise Exception

        wikipedia.output("uploading text from %s to %s" % (djvu, index) )

        bot = DjVuTextBot(djvu, index, pages)
	bot.ask = ask
        bot.run()
    else:
        wikipedia.showHelp()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
