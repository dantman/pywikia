#!/usr/bin/python
# coding: utf-8

"""
Include commons template in home wiki.

This bot functions mainly in the en.wikipedia, because it
compares the names of articles and category in English
language (standard language in Commons). If the name of
an article in Commons will not be in English but with
redirect, this also functions.

Run:
Syntax: python commons_link.py action [-option]

where action can be one of these:
 * pages      : Run over articles, include {{commons}}
 * categories : Run over categories, include {{commonscat}}

and option can be one of these:
 * -cat     : Work on all pages which are in a specific category.
 * -ref     : Work on all pages that link to a certain page.
 * -link    : Work on all pages that are linked from a certain page.
 * -start   : Work on all pages on the home wiki, starting at the named page.
 * -page    : Work on one page.

"""
#
# (C) Leonardo Gregianin, 2006
#
# Distributed under the terms of the MIT license.
#

__version__='$Id$'

import wikipedia, pagegenerators, catlib
import re

comment1 = {
    'ar':u'روبوت: تضمين قالب كومنز',
    'cs':u'Robot přidal šablonu commons',
    'en':u'Robot: Include commons template',
    'he':u'בוט: מוסיף תבנית Commons',
    'ja':u'ロボットによる: テンプレcommons追加',
    'nl':u'Bot: sjabloon commons toegevoegd',
    'zh':u'機器人: 增加commons模板',
    }
comment2 = {
    'ar':u'روبوت: تضمين قالب تصنيف كومنز',
    'cs':u'Robot přidal šablonu commonscat',
    'en':u'Robot: Include commonscat template',
    'he':u'בוט: מוסיף תבנית Commonscat',
    'ja':u'ロボットによる: テンプレcommonscat追加',
    'nl':u'Bot: sjabloon commonscat toegevoegd',
    'zh':u'機器人: 增加commonscat模板',
    }

class CommonsLinkBot:
    def __init__(self, generator, acceptall = False):
        self.generator = generator
        self.acceptall = acceptall

    def pages(self):
        for page in self.generator:
            try:
                wikipedia.output(u'\n>>>> %s <<<<' % page.title())
                commons = wikipedia.getSite('commons', 'commons')
                commonspage = wikipedia.Page(commons, page.title())
                try:
                    getcommons = commonspage.get(get_redirect=True)
                    if page.title() == commonspage.title():
                        oldText = page.get()
                        text = oldText

                        # for commons template
                        findTemplate=re.compile(ur'\{\{[Cc]ommonscat')
                        s = findTemplate.search(text)
                        findTemplate2=re.compile(ur'\{\{[Ss]isterlinks')
                        s2 = findTemplate2.search(text)
                        if s or s2:
                            wikipedia.output(u'** Already done.')
                        else:
                            text = wikipedia.replaceCategoryLinks(text+u'{{commons|%s}}'%commonspage.title(), page.categories())
                            if oldText != text:
                                wikipedia.showDiff(oldText, text)
                                if not self.acceptall:
                                    choice = wikipedia.inputChoice(u'Do you want to accept these changes?', ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
                                    if choice == 'a':
                                        self.acceptall = True
                                if self.acceptall or choice == 'y':
                                    try:
                                        msg = wikipedia.translate(wikipedia.getSite(), comment1)
                                        page.put(text, msg)
                                    except wikipedia.EditConflict:
                                        wikipedia.output(u'Skipping %s because of edit conflict' % (page.title()))

                except wikipedia.NoPage:
                    wikipedia.output(u'Page does not exist in Commons!')

            except wikipedia.NoPage:
                wikipedia.output(u'Page %s does not exist?!' % page.title())
            except wikipedia.IsRedirectPage:
                wikipedia.output(u'Page %s is a redirect; skipping.' % page.title())
            except wikipedia.LockedPage:
                wikipedia.output(u'Page %s is locked?!' % page.title())

    def categories(self):
        for page in self.generator:
            try:
                wikipedia.output(u'\n>>>> %s <<<<' % page.title())
                getCommons = wikipedia.getSite('commons', 'commons')
                commonsCategory = catlib.Category(getCommons,'Category:%s'%page.title())
                try:
                    getcommonscat = commonsCategory.get(get_redirect=True)
                    commonsCategoryTitle = commonsCategory.title()
                    categoryname = commonsCategoryTitle.split('Category:',1)[1]
                    if page.title() == categoryname:
                        oldText = page.get()
                        text = oldText

                        # for commonscat template
                        findTemplate=re.compile(ur'\{\{[Cc]ommons')
                        s = findTemplate.search(text)
                        findTemplate2=re.compile(ur'\{\{[Ss]isterlinks')
                        s2 = findTemplate2.search(text)
                        if s or s2:
                            wikipedia.output(u'** Already done.')
                        else:
                            text = wikipedia.replaceCategoryLinks(text+u'{{commonscat|%s}}'%categoryname, page.categories())
                            if oldText != text:
                                wikipedia.showDiff(oldText, text)
                                if not self.acceptall:
                                    choice = wikipedia.inputChoice(u'Do you want to accept these changes?', ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
                                    if choice == 'a':
                                        self.acceptall = True
                                if self.acceptall or choice == 'y':
                                    try:
                                        msg = wikipedia.translate(wikipedia.getSite(), comment2)
                                        page.put(text, msg)
                                    except wikipedia.EditConflict:
                                        wikipedia.output(u'Skipping %s because of edit conflict' % (page.title()))

                except wikipedia.NoPage:
                    wikipedia.output(u'Category does not exist in Commons!')

            except wikipedia.NoPage:
                wikipedia.output(u'Page %s does not exist?!' % page.title())
            except wikipedia.IsRedirectPage:
                wikipedia.output(u'Page %s is a redirect; skipping.' % page.title())
            except wikipedia.LockedPage:
                wikipedia.output(u'Page %s is locked?!' % page.title())

if __name__ == "__main__":
    singlepage = []
    gen = None
    start = None
    try:
        action = None
        for arg in wikipedia.handleArgs():
            if arg == ('pages'):
                action = 'pages'
            elif arg == ('categories'):
                action = 'categories'
            elif arg.startswith('-start:'):
                start = wikipedia.Page(wikipedia.getSite(),arg[7:])
                gen = pagegenerators.AllpagesPageGenerator(start.titleWithoutNamespace(),namespace=start.namespace(),includeredirects = False)
            elif arg.startswith('-cat:'):
                cat = catlib.Category(wikipedia.getSite(),'Category:%s'%arg[5:])
                gen = pagegenerators.CategorizedPageGenerator(cat)
            elif arg.startswith('-ref:'):
                ref = wikipedia.Page(wikipedia.getSite(), arg[5:])
                gen = pagegenerators.ReferringPageGenerator(ref)
            elif arg.startswith('-link:'):
                link = wikipedia.Page(wikipedia.getSite(), arg[6:])
                gen = pagegenerators.LinkedPageGenerator(link)
            elif arg.startswith('-page:'):
                singlepage = wikipedia.Page(wikipedia.getSite(), arg[6:])
                gen = iter([singlepage])
            #else:
                #bug

        if action == 'pages':
            preloadingGen = pagegenerators.PreloadingGenerator(gen)
            bot = CommonsLinkBot(preloadingGen, acceptall=False)
            bot.pages()
        elif action == 'categories':
            preloadingGen = pagegenerators.PreloadingGenerator(gen)
            bot = CommonsLinkBot(preloadingGen, acceptall=False)
            bot.categories()
        else:
            wikipedia.showHelp(u'commons_link')

    finally:
        wikipedia.stopme()
