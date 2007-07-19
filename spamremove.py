# -*- coding: utf-8 -*-
#!/usr/bin/python

import wikipedia, editarticle
"""
Script to remove links that are being or have been spammed.
Usage:

spamremove.py spammedsite.com

It will use Special:Linksearch to find the pages on the wiki that link to
that site, then for each page make a proposed change consisting of removing
all the lines where that url occurs. You can choose to:
* accept the changes as proposed
* edit the page yourself to remove the offending link
* not change the page in question

Command line options:
* -automatic: Do not ask, but remove the lines automatically. Be very careful
              in using this option!

"""

def main():
    automatic = False
    msg = {
        'de': u'Entferne in Spam-Whitelist eingetragenen Weblink auf %s',
        'en': u'Removing links to spammed site %s',
        'nl': u'Links naar gespamde site %s verwijderd',
    }
    spamSite = ''
    for arg in wikipedia.handleArgs():
        if arg.startswith("-automatic"):
            automatic = True
        else:
            spamSite = arg
    if not automatic:
        wikipedia.put_throttle.setDelay(1)
    if not spamSite:
        wikipedia.output(u"No spam site specified.")
        sys.exit()
    mysite = wikipedia.getSite()
    pages = list(set(mysite.linksearch(spamSite)))
    wikipedia.getall(mysite, pages)
    for p in pages:
        if not spamSite in p.get():
            continue
        wikipedia.output(u'')
        # Show the title of the page where the link was found.
        # Highlight the title in purple.
        colors = [None] * 6 + [13] * len(p.title()) + [None] * 4
        wikipedia.output(u"\n\n>>> %s <<<" % p.title(), colors = colors)
        lines = p.get().split('\n')
        newpage = []
        lastok = ""
        for line in lines:
            if spamSite in line:
                if lastok:
                    wikipedia.output(lastok)
                wikipedia.output(line, colors = [12] * len(line))
                lastok = None
            else:
                newpage.append(line)
                if line.strip():
                    if lastok is None:
                        wikipedia.output(line)
                    lastok = line
        if automatic:
            answer = "Y"
        else:
            answer = "blablabla"
        while not answer in "yYnNeE":
            answer = wikipedia.input("Delete the red lines ([Y]es, [N]o, [E]dit)?")[0]
        if answer in "nN":
            continue
        elif answer in "eE":
            editor = editarticle.TextEditor()
            newtext = editor.edit(p.get(), highlight = spamSite)
        else:
            newtext = "\n".join(newpage)
        if newtext != p.get():
            p.put(newtext, wikipedia.translate(mysite, msg) % spamSite)

try:
    main()
finally:
   wikipedia.stopme()
