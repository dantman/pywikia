#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Goes through the disambiguation pages, checks their links, and asks for
each link that goes to a redirect page whether it should be replaced.
"""
#
# (C) André Engels, 2006
#
# Distributed under the terms of the MIT license.
#
__version__='$Id$'
#
import wikipedia
import pagegenerators
import sys, re
import catlib

def firstcap(string):
    return string[0].upper()+string[1:]

def treat(text, linkedPage, targetPage):
    """
    Based on the method of the same name in solve_disambiguation.py.
    """
    # make a backup of the original text so we can show the changes later
    linkR = re.compile(r'\[\[(?P<title>[^\]\|#]*)(?P<section>#[^\]\|]*)?(\|(?P<label>[^\]]*))?\]\](?P<linktrail>' + linktrail + ')')
    curpos = 0
    # This loop will run until we have finished the current page
    while True:
        m = linkR.search(text, pos = curpos)
        if not m:
            break
        # Make sure that next time around we will not find this same hit.
        curpos = m.start() + 1
        # ignore interwiki links and links to sections of the same page
        if m.group('title') == '' or mysite.isInterwikiLink(m.group('title')):
            continue
        else:
            actualLinkPage = wikipedia.Page(page.site(), m.group('title'))
            # Check whether the link found is to page.
            if actualLinkPage != linkedPage:
                continue

        # how many bytes should be displayed around the current link
        context = 30
        # This loop will run while the user doesn't choose an option
        # that will actually change the page
        colors = [None for c in text[max(0, m.start() - context) : m.start()]] + [12 for c in text[m.start() : m.end()]] + [None for c in text[m.end() : m.end() + context]]
        wikipedia.output(text[max(0, m.start() - context) : m.end() + context], colors = colors)
        while True:
            colors = [None for c in u"Option (n=do not change, y=change link to "] + [14 for c in targetPage.title()] + [None for c in u", r=change and replace text, u=unlink)"]
            choice = wikipedia.input(u"Option (n=do not change, y=change link to %s, r=change and replace text, u=unlink)"%targetPage.title(),colors=colors)
            try:
                choice = choice[0]
            except:
                continue
            if choice in 'nNyYrRuU':
                break
        if choice in "nN":
            continue

        # The link looks like this:
        # [[page_title|link_text]]trailing_chars
        page_title = m.group('title')
        link_text = m.group('label')

        if not link_text:
            # or like this: [[page_title]]trailing_chars
            link_text = page_title
        if m.group('section') == None:
            section = ''
        else:
            section = m.group('section')
        trailing_chars = m.group('linktrail')
        if trailing_chars:
            link_text += trailing_chars

        if choice in "uU":
            # unlink - we remove the section if there's any
            text = text[:m.start()] + link_text + text[m.end():]
            continue
        replaceit = choice in "rR"

        if link_text[0].isupper():
            new_page_title = targetPage.title()
        else:
            new_page_title = targetPage.title()[0].lower() + targetPage.title()[1:]
        if replaceit and trailing_chars:
            newlink = "[[%s%s]]%s" % (new_page_title, section, trailing_chars)
        elif replaceit or (new_page_title == link_text and not section):
            newlink = "[[%s]]" % new_page_title
        # check if we can create a link with trailing characters instead of a pipelink
        elif len(new_page_title) <= len(link_text) and firstcap(link_text[:len(new_page_title)]) == firstcap(new_page_title) and re.sub(re.compile(linktrail), '', link_text[len(new_page_title):]) == '' and not section:
            newlink = "[[%s]]%s" % (link_text[:len(new_page_title)], link_text[len(new_page_title):])
        else:
            newlink = "[[%s%s|%s]]" % (new_page_title, section, link_text)
        text = text[:m.start()] + newlink + text[m.end():]
        continue
    return text

def workon(page):
    try:
        text = page.get()
    except wikipedia.IsRedirectPage:
        return
    # Show the title of the page where the link was found.
    # Highlight the title in purple.
    colors = [None] * 6 + [13] * len(page.title()) + [None] * 4
    wikipedia.output(u"\n\n>>> %s <<<" % page.title(), colors = colors)
    links = page.linkedPages()
    wikipedia.getall(mysite,links)
    for page2 in links:
        try:
            target = wikipedia.Page(mysite,page2.getRedirectTarget())
        except wikipedia.IsNotRedirectPage:
            continue
        except wikipedia.NoPage:
            continue
        text = treat(text, page2, target)
    if text != page.get():
        comment = wikipedia.translate(mysite, msg)
        page.put(text, comment)

try:
    msg = {
        'en': u'Changing redirects on a disambiguation page',
        'nl': u'Verandering van redirects op een doorverwijspagina',
        'pl': u'Zmiana przekierowań na stronie ujednoznaczającej',
        'pt': u'Arrumando redirects na página de desambiguação',
        }
    start = []
    test = False
    for arg in wikipedia.handleArgs():
        if arg.startswith("-test"):
            test = True
        else:
            start.append(arg)
    if start:
        start = " ".join(start)
    else:
        start = "!"
    mysite = wikipedia.getSite()
    linktrail = mysite.linktrail()
    try:
        basicgenerator = pagegenerators.CategorizedPageGenerator(mysite.disambcategory(),start=start)
    except wikipedia.NoPage:
        print "The bot does not know the disambiguation category for your wiki."
        raise
    generator = pagegenerators.PreloadingGenerator(basicgenerator)
    for page in generator:
        workon(page)

finally:
    wikipedia.stopme()

