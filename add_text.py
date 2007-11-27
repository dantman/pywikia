#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
This is a Bot written by Filnik to add a text in a given category.

--- GenFactory Generator is used ---
-start              Define from which page should the Bot start
-ref                Use the ref as generator
-cat                Use a category as generator
-filelinks          Use all the links to an image as generator
-unusedfiles
-unwatched
-withoutinterwiki
-interwiki
-file
-uncatfiles
-uncatcat
-uncat
-subcat
-transcludes        Use all the page that transclude a certain page as generator
-weblink            Use the pages with a certain web link as generator
-links              Use the links from a certain page as generator
-regex              Only work on pages whose titles match the given regex

--- Other parameters ---
-page               Use a page as generator
-text               Define which text add
-summary            Define the summary to use
-except             Use a regex to understand if the template is already in the page
-excepturl          Use the html page as text where you want to see if there's the text, not the wiki-page.
-newimages          Add text in the new images
-untagged           Add text in the images that doesn't have any license template
-always             If used, the bot won't asked if it should add the text specified
"""

#
# (C) Filnik, 2007
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id: AddText.py,v 1.0 2007/11/27 17:08:30 filnik Exp$'
#

import re, pagegenerators, urllib2, urllib
import wikipedia, catlib

class NoEnoughData(wikipedia.Error):
    """ Error class for when the user doesn't specified all the data needed """

class NothingFound(wikipedia.Error):
	""" An exception indicating that a regex has return [] instead of results."""

def pageText(url):
	try:
                request = urllib2.Request(url)
                user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.12) Gecko/20050915 Firefox/1.0.7'
                request.add_header("User-Agent", user_agent)
                response = urllib2.urlopen(request)
                text = response.read()
                response.close()
                # When you load to many users, urllib2 can give this error.
	except urllib2.HTTPError:
		wikipedia.output(u"Server error. Pausing for 10 seconds... " + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime()) )
		time.sleep(10)
                request = urllib2.Request(url)
                user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.12) Gecko/20050915 Firefox/1.0.7'
                request.add_header("User-Agent", user_agent)
                response = urllib2.urlopen(request)
                text = response.read()
                response.close()
	return text

def untaggedGenerator(untaggedProject, limit = 500):
        lang = untaggedProject.split('.', 1)[0]
        project = '.' + untaggedProject.split('.', 1)[1]
        if lang == 'commons':
                link = 'http://tools.wikimedia.de/~daniel/WikiSense/UntaggedImages.php?wikifam=commons.wikimedia.org&since=-100d&until=&img_user_text=&order=img_timestamp&max=100&order=img_timestamp&format=html'
        else:
                link = 'http://tools.wikimedia.de/~daniel/WikiSense/UntaggedImages.php?wikilang=' + lang + '&wikifam=' + project + '&order=img_timestamp&max=' + str(limit) + '&ofs=0&max=' + str(limit)         
        text = pageText(link)
        #print text
        regexp = r"""<td valign='top' title='Name'><a href='http://.*?\..*?\.org/w/index\.php\?title=(.*?)'>.*?</a></td>"""
        results = re.findall(regexp, text)
        if results == []:
                print link
                raise NothingFound('Nothing found! Try to use the tool by yourself to be sure that it works!')
        else:
                for result in results:
                        yield wikipedia.Page(self.site, result)

def newImages(limit):
        # Search regular expression to find links like this (and the class attribute is optional too)
        # class="new" title="Immagine:Soldatino2.jpg">Immagine:Soldatino2.jpg</a>" ‎ <span class="comment">
        url = "/w/index.php?title=Special:Log&type=upload&user=&page=&pattern=&limit=%d&offset=0" % int(limit)
        site = wikipedia.getSite()
        textrun = site.getUrl(url)
	image_namespace = site.image_namespace() + ":"
        regexp = r'(class=\"new\" |)title=\"' + image_namespace + '(.*?)\.(\w\w\w|jpeg)\">.*?</a>\".*?<span class=\"comment\">'    
        pos = 0
        done = list()
        ext_list = list()
        r = re.compile(regexp, re.UNICODE)
        while 1:
                m = r.search(textrun, pos)
                if m == None:
                        wikipedia.output(u"\t\t>> All images checked. <<")
                        break
                pos = m.end()
                new = m.group(1)
                im = m.group(2)
                ext = m.group(3)
                # This prevent pages with strange characters. They will be loaded without problem.
                image = im + "." + ext
                if new != '':
                        wikipedia.output(u"Skipping %s because it has been deleted." % image)
                        done.append(image)
                if image not in done:
                        done.append(image)
                        yield wikipedia.Page(site, 'Image:%s' % image)				

def main():
    starsList = ['link[ _]fa', 'link[ _]adq', 'enllaç[ _]ad',
                 'link[ _]ua', 'legătură[ _]af', 'destacado',
                 'ua', 'liên k[ _]t[ _]chọn[ _]lọc']
    summary = None
    addText = None
    regexSkip = None
    generator = None
    always = False
    exceptUrl = False
    genFactory = pagegenerators.GeneratorFactory()
    errorCount = 0
    
    for arg in wikipedia.handleArgs():
        if arg.startswith('-text'):
            if len(arg) == 5:
                addText = wikipedia.input(u'What text do you want to add?')
            else:
                addText = arg[6:]
        elif arg.startswith('-summary'):
            if len(arg) == 8:
                summary = wikipedia.input(u'What summary do you want to use?')
            else:
                summary = arg[9:]
        elif arg.startswith('-page'):
            if len(arg) == 5:
                generator = list(wikipedia.input(u'What page do you want to use?'))
            else:
                generator = listr(arg[6:])
        elif arg.startswith('-excepturl'):
            exceptUrl = True
            if len(arg) == 10:
                regexSkip = wikipedia.input(u'What text should I skip?')
            else:
                regexSkip = arg[11:]
        elif arg.startswith('-except'):
            if len(arg) == 7:
                regexSkip = wikipedia.input(u'What text should I skip?')
            else:
                regexSkip = arg[8:]
        elif arg.startswith('-untagged'):
            if len(arg) == 9:
                untaggedProject = wikipedia.input(u'What project do you want to use?')
            else:
                untaggedProject = arg[10:]
            generator = untaggedGenerator(untaggedProject)
        elif arg.startswith('-newimages'):
            if len(arg) == 10:
                limit = wikipedia.input(u'How many images do you want to check?')
            else:
                limit = arg[11:]
            generator = newImages(limit)      
        elif arg == '-always':
            always = True
        else:
            generator = genFactory.handleArg(arg)
                
    site = wikipedia.getSite()
    pathWiki = site.family.nicepath(site.lang)
    if not generator:
        raise NoEnoughData('You have to specify the generator you want to use for the script!')
    if not addText:
        raise NoEnoughData('You have to specify what text you want to add!')
    if not summary:
        summary = 'Bot: Adding %s' % addText
    for page in generator:
        wikipedia.output(u'Loading %s...' % page.title())
        try:
            text = page.get()
        except wikipedia.NoPage:
            wikipedia.output(u"%s doesn't exist, skip!" % page.title())
            continue
        except wikipedia.IsRedirectPage:
            wikipedia.output(u"%s is a redirect, skip!" % page.title())
            continue
        if regexSkip and exceptUrl:          
            url = '%s%s' % (pathWiki, page.urlname())
            result = re.findall(regexSkip, site.getUrl(url))
        elif regexSkip:
            result = re.findall(regexSkip, text)
        else:
            result = []
        if result != []:
            wikipedia.output(u'Exception! regex (or word) use with -except, is in the page. Skip!')
            continue
        newtext = text
        categoryNamespace = site.namespace(14)
        regexpCat = re.compile(r'\[\[((?:category|%s):.*?)\]\]' % categoryNamespace.lower(), re.I)
        categorieInside = regexpCat.findall(text)
        newtext = wikipedia.removeCategoryLinks(newtext, site)
        interwikiInside = page.interwiki()
        interwikiList = list()
        for paginetta in interwikiInside:
            nome = str(paginetta).split('[[')[1].split(']]')[0]
            interwikiList.append(nome)
            lang = nome.split(':')[0]
        newtext = wikipedia.removeLanguageLinks(newtext, site)
        interwikiList.sort()
        newtext += "\n%s" % addText
        for paginetta in categorieInside:
            try:
                newtext += '\n[[%s]]' % paginetta.decode('utf-8')
            except UnicodeEncodeError:
                try:
                    newtext += '\n[[%s]]' % paginetta.decode('Latin-1')
                except UnicodeEncodeError:
                    newtext += '\n[[%s]]' % paginetta
        newtext += '\n'
        starsListInPage = list()
        for star in starsList:
            regex = re.compile('(\{\{(?:template:|)%s\|.*?\}\}\n)' % star, re.I)
            risultato = regex.findall(newtext)
            if risultato != []:
                newtext = regex.sub('', newtext)
                for element in risultato:
                    newtext += '\n%s' % element
        for paginetta in interwikiList:
            try:
                newtext += '\n[[%s]]' % paginetta.decode('utf-8')
            except UnicodeEncodeError:
                try:
                    newtext += '\n[[%s]]' % paginetta.decode('Latin-1')
                except UnicodeEncodeError:
                    newtext += '\n[[%s]]' % paginetta
        wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" % page.title())
        wikipedia.showDiff(text, newtext)
        while 1:
            if not always:
                choice = wikipedia.inputChoice(u'Do you want to accept these changes?', ['Yes', 'No', 'All'], ['y', 'N', 'a'], 'N')
            if choice.lower() in ['a', 'all']:
                always = True
            if choice.lower() in ['n', 'no']:
                break
            if choice.lower() in ['y', 'yes'] or always:
                try:
                    page.put(newtext, summary)
                except wikipedia.EditConflict:
                    wikipedia.output(u'Edit conflict! skip!')
                    break
                except wikipedia.ServerError:
                    errorCount += 1
                    if errorCount < 5:
                        wikipedia.output(u'Server Error! Wait..')
                        time.sleep(3)
                        continue
                    else:
                        raise wikipedia.ServerError(u'Fifth Server Error!')
                except wikipedia.SpamfilterError, e:
                    wikipedia.output(u'Cannot change %s because of blacklist entry %s' % (page.title(), e.url))
                    break
                except wikipedia.PageNotSaved, error:
                    wikipedia.output(u'Error putting page: %s' % (error.args,))
                    break
                except wikipedia.LockedPage:
                    wikipedia.output(u'Skipping %s (locked page)' % (page.title(),))
                    break
                else:
                    # Break only if the errors are one after the other...
                    errorCount = 0
                    break
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
