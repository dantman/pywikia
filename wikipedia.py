# -*- coding: utf-8  -*-
"""
Library to get and put pages on a MediaWiki.

Contents of the library (objects and functions to be used outside, situation
late August 2004)

Classes:
Page: A MediaWiki page
    __init__: Page(xx,Title) - the page with title Title on language xx:
    title: The name of the page, in a form suitable for an interwiki link
    urlname: The name of the page, in a form suitable for a URL
    titleWithoutNamespace: The name of the page, with the namespace part removed
    section: The section of the page (the part of the name after '#')
    sectionFreeTitle: The name without the section part
    aslink: The name of the page in the form [[Title]] or [[lang:Title]]
    site: The wiki where this page is in
    encoding: The encoding the page is in

    get (*): The text of the page
    exists (*): True if the page actually exists, false otherwise
    isRedirectPage (*): True if the page is a redirect, false otherwise
    isEmpty (*): True if the page has 4 characters or less content, not
        counting interwiki and category links
    interwiki (*): The interwiki links from the page (list of Pages)
    categories (*): The categories the page is in (list of Pages)
    linkedPages (*): The normal pages linked from the page (list of Pages)
    imagelinks (*): The pictures on the page (list of Pages)
    templates (*): All templates referenced on the page (list of strings)
    getRedirectTarget (*): The page the page redirects to
    isCategory: True if the page is a category, false otherwise
    isImage: True if the page is an image, false otherwise
    isDisambig (*): True if the page is a disambiguation page
    getReferences: List of pages linking to the page
    namespace: The namespace in which the page is
    permalink (*): The url of the permalink of the current version

    put(newtext): Saves the page
    delete: Deletes the page (requires being logged in)

    (*): This loads the page if it has not been loaded before; permalink might
         even reload it if it has been loaded before

Site: a MediaWiki site
    forceLogin(): Does not continue until the user has logged in to the site
    getUrl(): Retrieve an URL from the site

    Special pages:
        Dynamic pages: 
            allpages(): Special:Allpages
            newpages(): Special:Newpages
            longpages(): Special:Longpages
            shortpages(): Special:Shortpages
            categories(): Special:Categories

        Cached pages:
            deadendpages(): Special:Deadendpages
            ancientpages(): Special:Ancientpages
            lonelypages(): Special:Lonelypages
            uncategorizedcategories(): Special:Uncategorizedcategories
            uncategorizedpages(): Special:Uncategorizedpages
            unusedcategories(): Special:Unusuedcategories
    
Other functions:
getall(): Load pages via Special:Export
setAction(text): Use 'text' instead of "Wikipedia python library" in
    editsummaries
argHandler(text): Checks whether text is an argument defined on wikipedia.py
    (these are -family, -lang, -log and others)
translate(xx, dict): dict is a dictionary, giving text depending on language,
    xx is a language. Returns the text in the most applicable language for
    the xx: wiki

output(text): Prints the text 'text' in the encoding of the user's console.
input(text): Asks input from the user, printing the text 'text' first.
showDiff(oldtext, newtext): Prints the differences between oldtext and newtext
    on the screen

getLanguageLinks(text,xx): get all interlanguage links in wikicode text 'text'
    in the form xx:pagename
removeLanguageLinks(text): gives the wiki-code 'text' without any interlanguage
    links.
replaceLanguageLinks(oldtext, new): in the wiki-code 'oldtext' remove the
    language links and replace them by the language links in new, a dictionary
    with the languages as keys and either Pages or titles as values
getCategoryLinks(text,xx): get all category links in text 'text' (links in the
    form xx:pagename)
removeCategoryLinks(text,xx): remove all category links in 'text'
replaceCategoryLinks(oldtext,new): replace the category links in oldtext by
    those in new (new a list of category Pages)
stopme(): Put this on a bot when it is not or not communicating with the Wiki
    any longer. It will remove the bot from the list of running processes,
    and thus not slow down other bot threads anymore.

"""
from __future__ import generators
#
# (C) Rob W.W. Hooft, Andre Engels, 2003-2005
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#
import os, sys
import httplib, socket, urllib
import traceback
import time
import math
import re, codecs, difflib, locale
import xml.sax, xml.sax.handler
import htmlentitydefs
import warnings

import config, mediawiki_messages, login
import xmlreader

# we'll set the locale to system default. This will ensure correct string
# handling for non-latin characters on Python 2.3.x. For Python 2.4.x it's no
# longer needed.
locale.setlocale(locale.LC_ALL, '')

try:
    set # introduced in Python2.4: faster and future
except NameError:
    from sets import Set as set

# Local exceptions

class Error(Exception):
    """Wikipedia error"""

class NoUsername(Error):
    """Username is not in user-config.py"""

class NoPage(Error):
    """Wikipedia page does not exist"""

class IsRedirectPage(Error):
    """Wikipedia page is a redirect page"""

class IsNotRedirectPage(Error):
    """Wikipedia page is not a redirect page"""

class LockedPage(Error):
    """Wikipedia page is locked"""

class NoSuchEntity(ValueError):
    """No entity exist for this character"""

class SectionError(ValueError):
    """The section specified by # does not exist"""

class PageNotSaved(Error):
    """ Saving the page has failed """

class EditConflict(PageNotSaved):
    """There has been an edit conflict while uploading the page"""

# UserBlocked exceptions should in general not be catched. If the bot has been
# blocked, the bot operator has possibly done a mistake and should take care of
# the issue before continuing.
class UserBlocked(Error):
    """Your username or IP has been blocked"""

class PageInList(LookupError):
    """Trying to add page to list that is already included"""

class PageNotFound(Exception):
    """Page not found in list"""

SaxError = xml.sax._exceptions.SAXParseException

# The most important thing in this whole module: The Page class
class Page(object):
    """A page on the wiki."""
    def __init__(self, site, title = None, insite = None, tosite = None):
        """
        Constructor. Normally called with two arguments:
        Parameters:
         1) The wikimedia site on which the page resides
         2) The title of the page as a unicode string
             
        The argument insite can be specified to help decode
        the name; it is the wikimedia site where this link was found.
        """
        self._site = site
        if tosite:
            self._tosite = tosite
        else:
            self._tosite = getSite() # Default to home wiki
        # Clean up the name, it can come from anywhere.
        # Replace underlines by spaces
        title = underline2space(title)
        # Convert HTML entities to unicode
        title = html2unicode(title)
        # Convert URL-encoded characters to unicode
        title = url2unicode(title, site = site)
        # Remove double spaces
        while '  ' in title:
            title = title.replace('  ', ' ')
        # Remove leading colon
        if title.startswith(':'):
             title = title[1:]
        # Capitalize first letter
        try:
            if not site.nocapitalize:
                title = title[0].upper() + title[1:]
        except IndexError: # title is empty
            pass
        # split up into namespace and rest
        title = title.split(':', 1)
        # if the page is not in namespace 0:
        if len(title) > 1:
            # translate a default namespace name into the local namespace name
            for ns in site.family.namespaces.keys():
                if title[0] == site.family.namespace('_default', ns):
                    title[0] = site.namespace(ns)
            # Capitalize the first non-namespace part
            for ns in site.family.namespaces.keys():
                if title[0] == site.namespace(ns):
                    # Remove leading and trailing whitespace from namespace and from rest
                    for i in range(len(title)):
                        title[i] = title[i].strip()
                    if not site.nocapitalize:
                        try:
                            title[1] = title[1][0].upper()+title[1][1:]
                        except IndexError: # title[1] is empty
                            print "WARNING: Strange title %s"%'%3A'.join(title)
        # In case the part before the colon was not a namespace, we need to
        # remove leading and trailing whitespace now.
        title = ':'.join(title).strip()
        self._title = title
        self.editRestriction = None
        self._permalink = None

    def site(self):
        """The site of the page this Page refers to,
           without :"""
        return self._site

    def encoding(self):
        """
        Returns the character encoding used on this page's wiki.
        """
        return self._site.encoding()
    
    def urlname(self):
        """The name of the page this Page refers to, in a form suitable
           for the URL of the page."""
        encodedTitle = self.title().encode(self.site().encoding())
        return urllib.quote(encodedTitle)

    def title(self):
        """The name of this Page, as a Unicode string"""
        return self._title

    def titleWithoutNamespace(self):
        """The name of the page without the namespace part.
        Returns the sectionFreeTitle if the page is from the main namespace.
        Note that this is a raw way of doing things - it simply looks for
        a : in the name."""
        t=self.sectionFreeTitle()
        p=t.split(':', 1)
        if len(p) == 1:
            # page is in the main namespace
            return p[0]
        else:
            return p[1]

    def section(self):
        """The name of the section this Page refers to. Sections are
           denominated by a # in the title(). If no section is referenced,
           None is returned."""
        ln = self.title()
        ln = re.sub('&#', '&hash;', ln)
        if not '#' in ln:
            return None
        else:
            hn = ln[ln.find('#') + 1:]
            hn = re.sub('&hash;', '&#', hn)
            return hn

    def sectionFreeTitle(self):
        sectionName = self.section()
        title = self.title()
        if sectionName:
            return title[:-len(sectionName)-1]
        else:
            return title
            
    def __str__(self):
        """A console representation of the pagelink"""
        return self.aslink().encode(config.console_encoding, 'replace')

    def __repr__(self):
        """A more complete string representation"""
        return "%s{%s}" % (self.__class__.__name__, str(self))

    def aslink(self, forceInterwiki = False):
        """
        A string representation in the form of a link. The link will
        be an interwiki link if needed.

        If you set forceInterwiki to True, the link will have the format
        of an interwiki link even if it points to the home wiki.

        Note that the family is never included.
        """
        if forceInterwiki or self.site() != getSite():
            return '[[%s:%s]]' % (self.site().lang, self.title())
        else:
            return '[[%s]]' % self.title()

    def get(self, force = False, get_redirect=False, throttle = True, sysop = False):
        """The wiki-text of the page. This will retrieve the page if it has not
           been retrieved yet. This can raise the following exceptions that
           should be caught by the calling code:

            NoPage: The page does not exist

            IsRedirectPage: The page is a redirect. The argument of the
                            exception is the title of the page it redirects to.

            SectionError: The subject does not exist on a page with a # link
        """
        # \ufffd represents a badly encoded character, the other characters are
        # disallowed by MediaWiki.
        for illegalChar in ['#', '<', '>', '[', ']', '|', '{', '}', '\n', u'\ufffd']:
            if illegalChar in self.sectionFreeTitle():
                output(u'Illegal character in %s!' % self.aslink())
                raise NoPage('Illegal character in %s!' % self.aslink())
        if self.namespace() == -1:
                raise NoPage('%s is in the Special namespace!' % self.aslink())
        if force:
            # When forcing, we retry the page no matter what. Old exceptions
            # and contents do not apply any more.
            for attr in ['_redirarg','_getexception','_contents']:
                if hasattr(self, attr):
                    delattr(self, attr)
        else:
            # Make sure we re-raise an exception we got on an earlier attempt
            if hasattr(self, '_redirarg') and not get_redirect:
                raise IsRedirectPage, self._redirarg
            elif hasattr(self, '_getexception'):
                if self._getexception == IsRedirectPage and get_redirect:
                    pass
                else:
                    raise self._getexception
        # Make sure we did try to get the contents once
        if not hasattr(self, '_contents'):
            try:
                self._contents, self._isWatched, self.editRestriction = self.getEditPage(get_redirect = get_redirect, throttle = throttle, sysop = sysop)
                hn = self.section()
                if hn:
                    hn = underline2space(hn)
                    m = re.search("=+ *%s *=+" % hn, self._contents)
                    if not m:
                        output(u"WARNING: Section does not exist: %s" % self.title())
            # Store any exceptions for later reference
            except NoPage:
                self._getexception = NoPage
                raise
            except IsRedirectPage, arg:
                self._getexception = IsRedirectPage
                self._redirarg = arg
                if not get_redirect:
                    raise
            except SectionError:
                self._getexception = SectionError
                raise
        return self._contents

    def getEditPage(self, get_redirect=False, throttle = True, sysop = False):
        """
        Get the contents of the Page via the edit page.
        Do not use this directly, use get() instead.
       
        Arguments:
            get_redirect  - Get the contents, even if it is a redirect page
     
        This routine returns a unicode string containing the wiki text.
        """
        isWatched = False
        editRestriction = None
        output(u'Getting page %s' % self.aslink())
        path = self.site().edit_address(self.urlname())
        # Make sure Brion doesn't get angry by waiting if the last time a page
        # was retrieved was not long enough ago.
        if throttle:
            get_throttle()
        # Try to retrieve the page until it was successfully loaded (just in case
        # the server is down or overloaded)
        # wait for retry_idle_time minutes (growing!) between retries.
        retry_idle_time = 1
        while True:
            starttime = time.time()
            try:
                text = self.site().getUrl(path, sysop = sysop)
            except AttributeError:
                # We assume that the server is down. Wait some time, then try again.
                print "WARNING: Could not load %s%s. Maybe the server is down. Retrying in %i minutes..." % (self.site().hostname(), path, retry_idle_time)
                time.sleep(retry_idle_time * 60)
                # Next time wait longer, but not longer than half an hour
                retry_idle_time *= 2
                if retry_idle_time > 30:
                    retry_idle_time = 30
                continue
            # Extract the actual text from the textedit field
            try:
                i1 = re.search('<textarea[^>]*>', text).end()
                i2 = re.search('</textarea>', text).start()
            except AttributeError:
                # find out if the username or IP has been blocked
                if text.find(mediawiki_messages.get('blockedtitle', self.site())) != -1:
                    raise UserBlocked(self.site(), self.title())
                else:
                    # We assume that the server is down. Wait some time, then try again.
                    print "WARNING: No text area found on %s%s. Maybe the server is down. Retrying in %i minutes..." % (self.site().hostname(), path, retry_idle_time)
                    time.sleep(retry_idle_time * 60)
                    # Next time wait longer, but not longer than half an hour
                    retry_idle_time *= 2
                    if retry_idle_time > 30:
                        retry_idle_time = 30
                    continue
            # We now know that there is a textarea.
            # Look for the edit token
            Rwatch = re.compile(r"\<input type='hidden' value=\"(.*?)\" name=\"wpEditToken\"")
            tokenloc = Rwatch.search(text)
            if tokenloc:
                self.site().putToken(tokenloc.group(1), sysop = sysop)
            elif not self.site().getToken(getalways = False):
                self.site().putToken('', sysop = sysop)
    
            # Find out if page actually exists. Only existing pages have a 
            # version history tab. 
            RversionTab = re.compile(r'<li id="ca-history"><a href=".*title=.*&amp;action=history">.*</a></li>')
            matchVersionTab = RversionTab.search(text)
            if not matchVersionTab:
                raise NoPage(self.site(), self.title())                
            # Look if the page is on our watchlist
            R = re.compile(r"\<input tabindex='[\d]+' type='checkbox' name='wpWatchthis' checked='checked'")
            matchWatching = R.search(text)
            if matchWatching:
                isWatched = True
            # Get timestamps
            m = re.search('value="(\d+)" name=["\']wpEdittime["\']', text)
            if m:
                self._editTime = m.group(1)
            else:
                self._editTime = "0"
            m = re.search('value="(\d+)" name=["\']wpStarttime["\']', text)
            if m:
                self._startTime = m.group(1)
            else:
                self._startTime = "0"
            # Now process the contents of the textarea
            m = self.site().redirectRegex().match(text[i1:i2])
            if self._editTime == "0":
                output(u"DBG> page may be locked?!")
                editRestriction = 'sysop'
            if m:
                if get_redirect:
                    self._redirarg = m.group(1)
                else:
                    output(u"DBG> %s is redirect to %s" % (self.title(), m.group(1)))
                    raise IsRedirectPage(m.group(1))
            x = text[i1:i2]
            x = unescape(x)
            while x and x[-1] in '\n ':
                x = x[:-1]
    
            return x, isWatched, editRestriction

    def permalink(self):
        """
        Get the permalink page for this page
        """
        if not self._permalink:
            # When we get the page with getall, the permalink is received automatically
            getall(self.site(),[self,],force=True)
        return "http://%s%s&oldid=%s"%(self.site().hostname(), self.site().get_address(self.title()), self._permalink)

    def exists(self):
        """
        True iff the page exists, even if it's a redirect.
        
        If the title includes a section, False if this section isn't found.
        """
        try:
            self.get()
        except NoPage:
            return False
        except IsRedirectPage:
            return True
        except SectionError:
            return False
        return True

    def isRedirectPage(self):
        """True if the page is a redirect page, False if not or not existing"""
        try:
            self.get()
        except NoPage:
            return False
        except IsRedirectPage:
            return True
        return False
    
    def isEmpty(self):
        """
        True if the page has less than 4 characters, except for
        language links and category links, False otherwise.
        Can raise the same exceptions as get()
        """
        txt = self.get()
        txt = removeLanguageLinks(txt)
        txt = removeCategoryLinks(txt, site = self.site())
        if len(txt) < 4:
            return True
        else:
            return False

    def namespace(self):
        """Gives the number of the namespace of the page. Does not work for
           all namespaces in all languages, only when defined in family.py.
           If not defined, it will return 0 (the main namespace)"""
        t=self.sectionFreeTitle()
        p=t.split(':')
        if p[1:]==[]:
            return 0
        for namespaceNumber in self.site().family.namespaces.iterkeys():
            if p[0]==self.site().namespace(namespaceNumber):
                return namespaceNumber
        return 0

    def isCategory(self):
        """
        True if the page is a Category, false otherwise.
        """
        return self.namespace() == 14

    def isImage(self):
        """
        True if the page is an image description page, false otherwise.
        """
        return self.namespace() == 6

    def isDisambig(self):
        if not hasattr(self, '_isDisambig'):
            defdis = self.site().family.disambig( "_default" )
            locdis = self.site().family.disambig( self._site.lang )

            for tn in self.templates():
                tn = tn[0].upper() + tn[1:]
                tn = tn.replace('_', ' ')
                if tn in defdis or tn in locdis:
                    _isDisambig = True
                    break
            else:
                _isDisambig = False
        return _isDisambig

    def getReferences(self, follow_redirects=True):
        """
        Return a list of pages that link to the page.
        If follow_redirects is True, also returns pages
          that link to a redirect pointing to the page.
        """
        site = self.site()
        path = site.references_address(self.urlname())
        
        output(u'Getting references to %s' % self.aslink())
        delay = 1
        refTitles = set()  # use a set to avoid duplications
        redirTitles = set()

        # NOTE: this code relies on the way MediaWiki 1.6 formats the
        #       "Whatlinkshere" special page; if future versions change the
        #       format, they may break this code.
        startmarker = u"<!-- start content -->"
        endmarker = u"<!-- end content -->"
        listitempattern = re.compile(
            r"<li><a href=.*>(.*)</a>(?: \(.*\) )?</li>")
        redirectpattern = re.compile(
            r"<li><a href=.*>(.*)</a> \(.*\) <ul>")
        nextpattern = re.compile(
            r'\(<a href="([^"]*)" title="Special:Whatlinkshere/[^"]*">next [0-9]+</a>\)')
        more = True

        while more:
            while True:
                print path
                txt = site.getUrl(path)
                # trim irrelevant portions of page
                try:
                    start = txt.index(startmarker) + len(startmarker)
                    end = txt.index(endmarker)
                except ValueError:
                    output(
                u"Invalid page received from server.... Retrying in %i minutes."
                           % delay)
                    time.sleep(delay * 60.)
                    delay *= 2
                    if delay > 30:
                        delay = 30
                    continue
                txt = txt[start:end]
                break
            nexturl = nextpattern.search(txt)
            if nexturl:
                path = nexturl.group(1).replace("&amp;", "&")
            else:
                more = False
            try:
                start = txt.index(u"<ul>")
                end = txt.rindex(u"</ul>")
            except ValueError:
                # No incoming links found on page
                continue
            txt = txt[start:end+5]

            txtlines = txt.split(u"\n")
            redirect = 0
            ignore_redirect = False
            for num, line in enumerate(txtlines):
                if line == u"</ul>":
                    # end of list of references to redirect page
                    if ignore_redirect:
                        ignore_redirect = False
                    elif redirect:
                        redirect -= 1
                    continue
                if line == u"</li>":
                    continue
                if ignore_redirect:
                    continue
                lmatch = None
                rmatch = redirectpattern.search(line)
                if rmatch:
                    # make sure this is really a redirect to this page
                    # (MediaWiki will mark as a redirect any link that follows
                    # a #REDIRECT marker, not just the first one).
                    linkpage = Page(site, rmatch.group(1))
                    if linkpage.getRedirectTarget() != self.sectionFreeTitle():
                        ignore_redirect = True
                        lmatch = rmatch
                    else:
                        if redirect:
                            output(u"WARNING: [[%s]] is a double-redirect."
                                   % rmatch.group(1))
                        if follow_redirects or not redirect:
                            refTitles.add(rmatch.group(1))
                            redirTitles.add(rmatch.group(1))
                        redirect += 1
                # the same line may match both redirectpattern and
                # listitempattern, because there is no newline after
                # a redirect link
                if not lmatch:
                    lmatch = listitempattern.search(line)
                if lmatch:
                    if follow_redirects or not redirect:
                        refTitles.add(lmatch.group(1))
                        continue
                if rmatch is None and lmatch is None:
                    output(u"DBG> Unparsed line:")
                    output(u"(%i) %s" % (num, line))
        refTitles = list(refTitles)
        refTitles.sort()
        refPages = []
        # create list of Page objects
        for refTitle in refTitles:
            page = Page(site, refTitle)
            refPages.append(page)
        return refPages

    def put(self, newtext, comment=None, watchArticle = None, minorEdit = True):
        """Replace the new page with the contents of the first argument.
           The second argument is a string that is to be used as the
           summary for the modification

           If watchArticle is None, leaves the watchlist status unchanged.
        """
        if self.editRestriction:
            try:
                self.site().forceLogin(sysop = True)
                output(u'Page is locked, using sysop account.')
            except NoUsername:
                raise LockedPage()
        else:
            self.site().forceLogin()
        if watchArticle == None:
            # if the page was loaded via get(), we know its status
            if hasattr(self, '_isWatched'):
                watchArticle = self._isWatched
            else:
                import watchlist
                watchArticle = watchlist.isWatched(self.title(), site = self.site())
        newPage = not self.exists()
        sysop = (self.editRestriction is not None)
        return self.putPage(newtext, comment, watchArticle, minorEdit, newPage, self.site().getToken(sysop = sysop), sysop = sysop)

    def putPage(self, text, comment = None, watchArticle = False, minorEdit = True, newPage = False, token = None, gettoken = False, sysop = False):
        """
        Upload 'text' as new contents for this Page by filling out the edit
        page.
        
        Don't use this directly, use put() instead.
        """
        safetuple = () # safetuple keeps the old value, but only if we did not get a token yet could
        # TODO: get rid of safetuple
        if self.site().version() >= "1.4":
            if gettoken or not token:
                token = self.site().getToken(getagain = gettoken, sysop = sysop)
            else:
                safetuple = (text, comment, watchArticle, minorEdit, newPage, sysop)
        # Check whether we are not too quickly after the previous putPage, and
        # wait a bit until the interval is acceptable
        put_throttle()
        # Which web-site host are we submitting to?
        host = self.site().hostname()
        # Get the address of the page on that host.
        address = self.site().put_address(self.urlname())
        # If no comment is given for the change, use the default
        if comment is None:
            comment=action
        # Use the proper encoding for the comment
        comment = comment.encode(self.site().encoding())
        # Encode the text into the right encoding for the wiki
        text = text.encode(self.site().encoding())
        predata = [
            ('wpSave', '1'),
            ('wpSummary', comment),
            ('wpTextbox1', text)]
        # Except if the page is new, we need to supply the time of the
        # previous version to the wiki to prevent edit collisions
        if newPage:
            predata.append(('wpEdittime', ''))
        else:
            predata.append(('wpEdittime', self._editTime))
        predata.append(('wpStarttime', self._startTime))            
        # Pass the minorEdit and watchArticle arguments to the Wiki.
        if minorEdit:
            predata.append(('wpMinoredit', '1'))
        if watchArticle:
            predata.append(('wpWatchthis', '1'))
        # Give the token, but only if one is supplied.
        if token:
            predata.append(('wpEditToken', token))
        # Encode all of this into a HTTP request
        data = urlencode(tuple(predata))
        
        if newPage:
            output('Creating page %s' % self.aslink())
        else:
            output('Changing page %s' % self.aslink())
        # Submit the prepared information
        conn = httplib.HTTPConnection(host)
    
        conn.putrequest("POST", address)
        conn.putheader('Content-Length', str(len(data)))
        conn.putheader("Content-type", "application/x-www-form-urlencoded")
        conn.putheader("User-agent", "PythonWikipediaBot/1.0")
        if self.site().cookies():
            conn.putheader('Cookie', self.site().cookies(sysop = sysop))
        conn.endheaders()
        conn.send(data)
    
        # Prepare the return values
        try:
            response = conn.getresponse()
        except httplib.BadStatusLine, line:
            raise PageNotSaved('Bad status line: %s' % line)
        data = response.read().decode(self.site().encoding())
        conn.close()
        if data != u'':
            # Saving unsuccessful. Possible reasons: edit conflict or invalid edit token.
            # A second text area means that an edit conflict has occured.
            if 'id=\'wpTextbox2\' name="wpTextbox2"' in data:
                raise EditConflict(u'An edit conflict has occured.')
            elif '<label for=\'wpRecreate\'' in data:
                # Make sure your system clock is correct if this error occurs
                # without any reason!
                raise EditConflict(u'Someone deleted the page.')
            elif safetuple and "<" in data:
                # We might have been using an outdated token
                print "Changing page has failed. Retrying."
                return self.putPage(safetuple[0], comment=safetuple[1],
                        watchArticle=safetuple[2], minorEdit=safetuple[3], newPage=safetuple[4],
                        token=None, gettoken=True, sysop=safetuple[5])
            else:
                output(data)
        return response.status, response.reason, data

    def canBeEdited(self):
        """
        Returns True iff:
            * the page is unprotected, and we have an account for this site, or
            * the page is protected, and we have a sysop account for this site.
        """
        if self.editRestriction:
            userdict = config.sysopnames
        else:
            userdict = config.usernames
        try:
            userdict[self.site().family.name][self.site().lang]
            return True
        except:
            # We don't have a user account for that wiki, or the
            # page is locked and we don't have a sysop account.
            return False
        
    def interwiki(self):
        """A list of interwiki links in the page. This will retrieve
           the page text to do its work, so it can raise the same exceptions
           that are raised by the get() method.

           The return value is a list of Page objects for each of the
           interwiki links in the page text.
        """
        result = []
        ll = getLanguageLinks(self.get(), insite = self.site(), pageLink = self.aslink())
        for newsite,newname in ll.iteritems():
            for pagenametext in self.site().family.pagenamecodes(self.site().language()):
                newname = newname.replace("{{"+pagenametext+"}}",self.title())
            try:
                result.append(self.__class__(newsite, newname, insite = self.site()))
            except UnicodeError:
                output(u"ERROR: link from %s to [[%s:%s]] is invalid encoding?!" % (self.aslink(), newsite, newname))
            except NoSuchEntity:
                output(u"ERROR: link from %s to [[%s:%s]] contains invalid character?!" % (self.aslink(), newsite, newname))
            except ValueError:
                output(u"ERROR: link from %s to [[%s:%s]] contains invalid unicode reference?!" % (self.aslink(), newsite, newname))
        return result

    def categories(self, withSortKeys = False):
        """
        A list of categories that the article is in. This will retrieve
        the page text to do its work, so it can raise the same exceptions
        that are raised by the get() method.
        
        The return value is a list of Category objects, one for each of the
        category links in the page text.

        If withSortKeys is False, sort keys will be omitted. If it's true, the
        | and the sort key following it will be included in the category title.
        This means that the Category can't be retrieved, but as long as we
        just use title() and such, that won't matter.
        """
        import catlib
        categoryTitles = getCategoryLinks(self.get(), self.site(), withSortKeys = withSortKeys)
        return [catlib.Category(self.site(), ':'.join(title.split(':')[1:])) for title in categoryTitles]

    def __cmp__(self, other):
        """Pseudo method to be able to use equality and inequality tests on
           Page objects"""
        if not isinstance(other, Page):
            # especially, return -1 if other is None
            return -1
        if not self.site() == other.site():
            return cmp(self.site(), other.site())
        owntitle = self.title()
        othertitle = other.title()
        # In Esperanto X-Convention, Bordeauxx is the same as BordeauxX, and
        # CxefpagXo is the same as Ĉefpaĝo.
        #if self.site().lang == 'eo':
        #    owntitle = doubleXForEsperanto(resolveEsperantoXConvention(owntitle))
        #    othertitle = doubleXForEsperanto(resolveEsperantoXConvention(othertitle))
        return cmp(owntitle, othertitle)

    def __hash__(self):
        """Pseudo method that makes it possible to store Page objects as
           keys in hash-tables. This relies on the fact that the string
           representation of an instance can not change after the construction.
        """
        return hash(str(self))

    def linkedPages(self):
        """Gives the normal (not-interwiki, non-category) pages the page
           links to, as a list of Page objects
        """
        result = []
        try:
            thistxt = removeLanguageLinks(self.get())
        except NoPage:
            return []
        except IsRedirectPage:
            raise
        thistxt = removeCategoryLinks(thistxt, self.site())

        Rlink = re.compile(r'\[\[(?P<title>[^\]\|]*)(\|[^\]]*)?\]\]')
        for match in Rlink.finditer(thistxt):
            title = match.group('title')
            if self.site().lang == 'eo':
                title = resolveEsperantoXConvention(title)
            page = Page(self.site(), title)
            result.append(page)
        return result

    def imagelinks(self, followRedirects = False):
        """
        Gives the images the page shows, as a list of Page objects.
        This includes images in galleries.
        """
        results = []
        # Find normal images
        for page in self.linkedPages():
            if page.isImage():
                results.append(page)
        # Find images in galleries
        galleryR = re.compile('<gallery>.*?</gallery>', re.DOTALL)
        galleryEntryR = re.compile('(?P<title>(%s|%s):.+?)(\|.+)?\n' % (self.site().image_namespace(), self.site().family.image_namespace(code = '_default')))
        for gallery in galleryR.findall(self.get()):
            for match in galleryEntryR.finditer(gallery):
                page = Page(self.site(), match.group('title'))
                results.append(page)
        return results

    def templates(self):
        """
        Gives a list of template names used on a page, as a list of strings. Template parameters are ignored.
        """
        try:
            thistxt = self.get()
        except IsRedirectPage:
            return []
                
        result = []
        Rtemplate = re.compile(r'{{(msg:)?(?P<name>[^\|]+?)(\|(?P<pamars>.+?))?}}', re.DOTALL)
        for m in Rtemplate.finditer(thistxt):
            # we ignore parameters.
            result.append(m.group('name'))
        return result

    def getRedirectTarget(self):
        """
        If the page is a redirect page, gives the title of the page it
        redirects to. Otherwise it will raise an IsNotRedirectPage exception.
        
        This function can raise a NoPage exception.
        """
        try:
            self.get()
        except NoPage:
            raise NoPage(self)
        except IsRedirectPage, arg:
            if '|' in arg:
                warnings.warn("%s has a | character, this makes no sense", Warning)
            return arg[0]
        else:
            raise IsNotRedirectPage(self)

    def getVersionHistory(self, forceReload = False, reverseOrder = False, getAll = False):
        """
        Loads the version history page and returns a list of tuples, where each
        tuple represents one edit and is built of edit date/time, user name, and edit
        summary.  Defaults to getting the first 500 edits.
        """
        site = self.site()

        # regular expression matching one edit in the version history.
        # results will have 3 groups: edit date/time, user name, and edit
        # summary.
        if self.site().version() < "1.4":
            editR = re.compile('<li>.*?<a href=".*?" title=".*?">([^<]*)</a> <span class=\'user\'><a href=".*?" title=".*?">([^<]*?)</a></span>.*?(?:<span class=\'comment\'>(.*?)</span>)?</li>')
        else:
            editR = re.compile('<li>.*?<a href=".*?" title=".*?">([^<]*)</a> <span class=\'history-user\'><a href=".*?" title=".*?">([^<]*?)</a></span>.*?(?:<span class=\'comment\'>(.*?)</span>)?</li>')

        startFromPage = None
        thisHistoryDone = False
        skip = False # Used in determining whether we need to skip the first page

        RLinkToNextPage = re.compile('&amp;offset=(.*?)&amp;')

        # Are we getting by Earliest first?
        if reverseOrder:
            # Check if _versionhistoryearliest exists
            if not hasattr(self, '_versionhistoryearliest') or forceReload:
                self._versionhistoryearliest = []
            elif getAll and len(self._versionhistoryearliest) == 500:
                # Cause a reload, or at least make the loop run
                thisHistoryDone = False
                skip = True
            else:
                thisHistoryDone = True
        elif not hasattr(self, '_versionhistory') or forceReload:
            self._versionhistory = []
        elif getAll and len(self._versionhistory) == 500:
            # Cause a reload, or at least make the loop run
            thisHistoryDone = False
            skip = True
        else:
            thisHistoryDone = True

        while not thisHistoryDone:
            path = site.family.version_history_address(self.site().language(), self.urlname())

            if reverseOrder:
                if len(self._versionhistoryearliest) >= 500:
                    path += '&dir=prev'
                else:
                    path += '&go=first'

            if startFromPage:
                path += '&offset=' + startFromPage

            # this loop will run until the page could be retrieved
            # Try to retrieve the page until it was successfully loaded (just in case
            # the server is down or overloaded)
            # wait for retry_idle_time minutes (growing!) between retries.
            retry_idle_time = 1

            # The principle being applied here is the same idea from the catlib
            while True:
                try:
                    if startFromPage:
                        output(u'Continuing to get version history of %s' % self.title())
                    else:
                        output(u'Getting version history of %s' % self.title())

                    txt = site.getUrl(path)
                except:
                    # We assume that the server is down. Wait some time, then try again.
                    raise
                    print "WARNING: There was a problem retrieving %s. Maybe the server is down. Retrying in %d minutes..." % (self.title(), retry_idle_time)
                    time.sleep(retry_idle_time * 60)
                    # Next time wait longer, but not longer than half an hour
                    if retry_idle_time < 32:
                        retry_idle_time *= 2
                        continue
                break

            # save a copy of the text
            self_txt = txt

            if reverseOrder:
                # If we are getting all of the page history...
                if getAll:
                    if len(self._versionhistoryearliest) == 0:
                        matchObj = RLinkToNextPage.search(self_txt)
                        if matchObj:
                            startFromPage = matchObj.group(1)
                        else:
                            thisHistoryDone = True

                        edits = editR.findall(self_txt)
                        edits.reverse()
                        for edit in edits:
                            self._versionhistoryearliest.append(edit)
                        if len(edits) < 500:
                            thisHistoryDone = True
                    else:
                        if not skip:
                            edits = editR.findall(self_txt)
                            edits.reverse()
                            for edit in edits:
                                self._versionhistoryearliest.append(edit)
                            if len(edits) < 500:
                                thisHistoryDone = True

                            matchObj = RLinkToNextPage.search(self_txt)
                            if matchObj:
                                startFromPage = matchObj.group(1)
                            else:
                                thisHistoryDone = True

                        else:
                            # Skip the first page only,
                            skip = False

                            matchObj = RLinkToNextPage.search(self_txt)
                            if matchObj:
                                startFromPage = matchObj.group(1)
                            else:
                                thisHistoryDone = True
                else:
                    # If we are not getting all, we stop on the first page.
                    for edit in editR.findall(self_txt):
                        self._versionhistoryearliest.append(edit)
                    self._versionhistoryearliest.reverse()

                    thisHistoryDone = True
            else:
                # If we are getting all of the page history...
                if getAll:
                    if len(self._versionhistory) == 0:
                        matchObj = RLinkToNextPage.search(self_txt)
                        if matchObj:
                            startFromPage = matchObj.group(1)
                        else:
                            thisHistoryDone = True

                        edits = editR.findall(self_txt)
                        for edit in edits:
                            self._versionhistory.append(edit)
                        if len(edits) < 500:
                            thisHistoryDone = True
                    else:
                        if not skip:
                            edits = editR.findall(self_txt)
                            for edit in edits:
                                self._versionhistory.append(edit)
                            if len(edits) < 500:
                                thisHistoryDone = True

                            matchObj = RLinkToNextPage.findall(self_txt)
                            if len(matchObj) >= 2:
                                startFromPage = matchObj[1]
                            else:
                                thisHistoryDone = True
                        else:
                            # Skip the first page only,
                            skip = False

                            matchObj = RLinkToNextPage.search(self_txt)
                            if matchObj:
                                startFromPage = matchObj.group(1)
                            else:
                                thisHistoryDone = True
                else:
                    # If we are not getting all, we stop on the first page.
                    for edit in editR.findall(self_txt):
                        self._versionhistory.append(edit)

                    thisHistoryDone = True

        if reverseOrder:
            # Return only 500 edits, even if the version history is extensive
            if len(self._versionhistoryearliest) > 500 and not getAll:
                return self._versionhistoryearliest[0:500]
            return self._versionhistoryearliest

        # Return only 500 edits, even if the version history is extensive
        if len(self._versionhistory) > 500 and not getAll:
            return self._versionhistory[0:500]
        return self._versionhistory
            
    def getVersionHistoryTable(self, forceReload = False, reverseOrder = False, getAll = False):
        """
        Returns the version history as a wiki table.
        """
        result = '{| border="1"\n'
        result += '! date/time || username || edit summary\n'
        for time, username, summary in self.getVersionHistory(forceReload = forceReload, reverseOrder = reverseOrder, getAll = getAll):
            result += '|----\n'
            result += '| %s || %s || <nowiki>%s</nowiki>\n' % (time, username, summary)
        result += '|}\n'
        return result

    def contributingUsers(self):
        """
        Returns a set of all user names (including anonymous IPs) of those who
        edited the page.
        """
        edits = self.getVersionHistory()
        users = set()
        for edit in edits:
            users.add(edit[1])
        return users
                          
    def delete(self, reason = None, prompt = True):
        """Deletes the page from the wiki. Requires administrator status. If
           reason is None, asks for a reason. If prompt is True, asks the user
           if he wants to delete the page.
        """
        if reason == None:
            reason = input(u'Please enter a reason for the deletion:')
        reason = reason.encode(self.site().encoding())
        answer = 'y'
        if prompt:
            answer = inputChoice(u'Do you want to delete %s?' % self.title(), ['Yes', 'No'], ['y', 'N'], 'N')
        if answer in ['y', 'Y']:
            host = self.site().hostname()
            address = self.site().delete_address(self.urlname())

            self.site().forceLogin(sysop = True)

            token = self.site().getToken(self, sysop = True)
            predata = [
                ('wpReason', reason),
                ('wpConfirmB', '1')]
            if token:
                predata.append(('wpEditToken', token))
            data = urlencode(tuple(predata))
            conn = httplib.HTTPConnection(host)
            conn.putrequest("POST", address)
            conn.putheader('Content-Length', str(len(data)))
            conn.putheader("Content-type", "application/x-www-form-urlencoded")
            conn.putheader("User-agent", "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.7.5) Gecko/20041107 Firefox/1.0")
            if self.site().cookies(sysop = True):
                conn.putheader('Cookie', self.site().cookies(sysop = True))
            conn.endheaders()
            conn.send(data)
        
            response = conn.getresponse()
            data = response.read()
            conn.close()
        
            if data != '':
                data = data.decode(myencoding())
                if mediawiki_messages.get('actioncomplete') in data:
                    output(u'Deletion successful.')
                    return True
                else:
                    output(u'Deletion failed:.')
                    try:
                        ibegin = data.index('<!-- start content -->') + 22
                        iend = data.index('<!-- end content -->')
                    except ValueError:
                        # if begin/end markers weren't found, show entire HTML file
                        output(data)
                    else:
                        # otherwise, remove the irrelevant sections
                        data = data[ibegin:iend]
                    output(data)
                    return False

class XmlPage(Page):
    '''A subclass of Page that wraps an XMLEntry object (from xmlreader.py).

    Sample usage:
    >>> source = xmlreader.XmlDump(some_file_name)
    >>> for entry in source.parse():
    ...     page = XmlPage(getSite(), entry)
    ...     # do something with page...
    '''

    def __init__(self, site, xmlentry):
        if not isinstance(xmlentry, xmlreader.XmlEntry):
            raise TypeError("Invalid argument to XmlPage constructor.")
        Page.__init__(self, site, xmlentry.title)
        self.editRestriction = xmlentry.editRestriction
        self.moveRestriction = xmlentry.moveRestriction
        self._contents = xmlentry.text
        self._xml = xmlentry    # save XML source in case we need it later
        m = self.site().redirectRegex().match(self._contents)
        if m:
            self._redirarg = m.group(1)
            self._getexception = IsRedirectPage


class GetAll(object):
    def __init__(self, site, pages, throttle, force):
        """First argument is Site object.
        Second argument is list (should have .append and be iterable)"""
        self.site = site
        self.pages = []
        self.throttle = throttle
        for pl in pages:
            if ((not hasattr(pl,'_contents') and not hasattr(pl,'_getexception')) or force):
                self.pages.append(pl)
            else:
                output(u"BUGWARNING: %s already done!" % pl.aslink())

    def run(self):
        dt=15
        while True:
            try:
                data = self.getData()
            except (socket.error, httplib.BadStatusLine):
                # Print the traceback of the caught exception
                print ''.join(traceback.format_exception(*sys.exc_info()))
                output(u'DBG> got network error in GetAll.run. Sleeping for %d seconds'%dt)
                time.sleep(dt)
                if dt <= 60:
                    dt += 15
                elif dt < 360:
                    dt += 60
            else:
                break
        if not data:
            return
        handler = xmlreader.MediaWikiXmlHandler()
        handler.setCallback(self.oneDone)
        handler.setHeaderCallback(self.headerDone)
        try:
            xml.sax.parseString(data, handler)
        except xml.sax._exceptions.SAXParseException:
            f=open('sax_parse_bug.dat','w')
            f.write(data)
            f.close()
            print >>sys.stderr, "Dumped invalid XML to sax_parse_bug.dat"
            raise
        except PageNotFound:
            return
        # All of the ones that have not been found apparently do not exist
        for pl in self.pages:
            if not hasattr(pl,'_contents') and not hasattr(pl,'_getexception'):
                pl._getexception = NoPage

    def oneDone(self, entry):
        title = entry.title
        timestamp = entry.timestamp
        text = entry.text
        editRestriction = entry.editRestriction
        moveRestriction = entry.moveRestriction
        # Edit-pages on eo: use X-convention, XML export does not.
        # Internally we keep titles without X convention, but text with X
        # convention.
        if self.site.lang == 'eo':
            #title = doubleXForEsperanto(title)
            text = doubleXForEsperanto(text)
        pl = Page(self.site, title)
        for pl2 in self.pages:
            if Page(self.site, pl2.sectionFreeTitle()) == pl:
                if not hasattr(pl2,'_contents') and not hasattr(pl2,'_getexception'):
                    break
        else:
            print "BUG: page not found in list"
            print 'Title:', repr(title)
            print 'Page:', repr(pl)
            print 'Expected one of:', repr(self.pages)

            raise PageNotFound

        pl2.editRestriction = entry.editRestriction
        pl2.moveRestriction = entry.moveRestriction
        pl2._permalink = entry.revisionid
        m = self.site.redirectRegex().match(text)
        if m:
            pl._editTime = timestamp
            redirectto=m.group(1)
            pl2._getexception = IsRedirectPage
            pl2._redirarg = redirectto
        # There's no possibility to read the wpStarttime argument from the XML.
        # This argument makes sure an edit conflict is raised if the page is
        # deleted between retrieval and saving of the page. It contains the
        # UTC timestamp (server time) of the moment we first retrieved the edit
        # page. As we can't use server time, we simply use client time. Please
        # make sure your system clock is correct. If it's too slow, the bot might
        # recreate pages someone deleted. If it's too fast, the bot will raise
        # EditConflict exceptions although there's no conflict.
        pl2._startTime = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
        section = pl2.section()
        if section:
            m = re.search("== *%s *==" % section, text)
            if not m:
                output(u"WARNING: Section not found: %s" % pl2.title())
            else:
                # Store the content
                pl2._contents = text
                # Store the time stamp
                pl2._editTime = timestamp
        else:
            # Store the content
            pl2._contents = text
            # Store the time stamp
            pl2._editTime = timestamp

    def headerDone(self, header):
        # Verify our family data
        lang = self.site.lang
        ids = header.namespaces.keys()
        ids.sort()
        for id in ids:
            nshdr = header.namespaces[id]
            if self.site.family.namespaces.has_key(id):
                ns = self.site.namespace(id)
                if ns == None:
                    ns = u''
                if ns != nshdr:
                    dflt = self.site.family.namespaces[id]['_default']
                    if dflt == ns:
                        flag = u"is set to default ('%s'), but should be '%s'" % (ns, nshdr)
                    elif dflt == nshdr:
                        flag = u"is '%s', but should be removed (default value '%s')" % (ns, nshdr)
                    else:
                        flag = u"is '%s', but should be '%s'" % (ns, nshdr)
                        
                    output(u"WARNING: Outdated family file %s: namespace['%s'][%i] %s" % (self.site.family.name, lang, id, flag))
                    self.site.family.namespaces[id][lang] = nshdr
            else:
                output(u"WARNING: Missing namespace in family file %s: namespace['%s'][%i] (it is set to '%s')" % (self.site.family.name, lang, id, nshdr))
    
    def getData(self):
        if self.pages == []:
            return
        address = self.site.export_address()
        pagenames = [page.sectionFreeTitle() for page in self.pages]
        # We need to use X convention for requested page titles.
        if self.site.lang == 'eo':
            pagenames = [doubleXForEsperanto(pagetitle) for pagetitle in pagenames]
        pagenames = u'\r\n'.join(pagenames)
        if type(pagenames) != type(u''):
            print 'Warning: xmlreader.WikipediaXMLHandler.getData() got non-unicode page names. Please report this.'
            print pagenames
        # convert Unicode string to the encoding used on that wiki
        pagenames = pagenames.encode(self.site.encoding())
        data = urlencode((
                    ('action', 'submit'),
                    ('pages', pagenames),
                    ('curonly', 'True'),
                    ))
        #print repr(data)
        # Slow ourselves down
        get_throttle(requestsize = len(self.pages))
        # Now make the actual request to the server
        now = time.time()
        conn = httplib.HTTPConnection(self.site.hostname())
        conn.putrequest("POST", address)
        conn.putheader('Content-Length', str(len(data)))
        conn.putheader("Content-type", "application/x-www-form-urlencoded")
        conn.putheader("User-agent", "PythonWikipediaBot/1.0")
        if self.site.cookies():
            conn.putheader('Cookie', self.site.cookies())
        conn.endheaders()
        conn.send(data)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        get_throttle.setDelay(time.time() - now)
        return data
    
def getall(site, pages, throttle = True, force = False):
    output(u'Getting %d pages from %s...' % (len(pages), site))
    return GetAll(site, pages, throttle, force).run()
    
# Library functions


def unescape(s):
    """Replace escaped HTML-special characters by their originals"""
    if '&' not in s:
        return s
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&apos;", "'")
    s = s.replace("&quot;", '"')
    s = s.replace("&amp;", "&") # Must be last
    return s

def setAction(s):
    """Set a summary to use for changed page submissions"""
    global action
    action = s

# Default action
setAction('Wikipedia python library')

def urlencode(query):
    """This can encode a query so that it can be sent as a query using
       a http POST request"""
    l=[]
    for k, v in query:
        k = urllib.quote(k)
        v = urllib.quote(v)
        l.append(k + '=' + v)
    return '&'.join(l)

Rmorespaces = re.compile('  +')

def space2underline(name):
    name = Rmorespaces.sub(' ', name)
    return name.replace(' ', '_')

Rmoreunderlines = re.compile('__+')

def underline2space(name):
    name = Rmoreunderlines.sub('_', name)
    return name.replace('_', ' ')

# Mechanics to slow down page download rate.

class Throttle(object):
    def __init__(self, mindelay = config.minthrottle, maxdelay = config.maxthrottle, multiplydelay = True):
        """Make sure there are at least 'delay' seconds between page-gets
           after 'ignore' initial page-gets"""
        self.mindelay = mindelay
        self.maxdelay = maxdelay
        self.pid = False # If self.pid remains False, we're not checking for multiple processes
        self.now = 0
        self.next_multiplicity = 1.0
        self.checkdelay = 240 # Check the file with processes again after this many seconds
        self.dropdelay = 360 # Drop processes from the list that have not made a check in this many seconds
        self.releasepid = 100000 # Free the process id
        self.lastwait = 0.0
        self.delay = 0
        if multiplydelay:
            self.checkMultiplicity()
        self.setDelay(mindelay)

    def checkMultiplicity(self):
        processes = {}
        my_pid = 1
        count = 1
        try:
            f = open('throttle.log','r')
        except IOError:
            if not self.pid:
                pass
            else:
                raise
        else:
            now = time.time()
            for line in f.readlines():
                line = line.split(' ')
                pid = int(line[0])
                ptime = int(line[1].split('.')[0])
                if now - ptime <= self.releasepid:
                    if now - ptime <= self.dropdelay and pid != self.pid:
                        count += 1
                    processes[pid] = ptime
                    if pid >= my_pid:
                        my_pid = pid+1
        if not self.pid:
            self.pid = my_pid
        self.checktime = time.time()
        processes[self.pid] = self.checktime
        f = open('throttle.log','w')
        for p in processes.keys():
            f.write(str(p)+' '+str(processes[p])+'\n')
        f.close()
        self.process_multiplicity = count
        print("Checked for running processes. %s processes currently running, "%count +
              "including the current process.")

    def setDelay(self, delay = config.minthrottle, absolute = False):
        if absolute:
            self.maxdelay = delay
            self.mindelay = delay
        self.delay = delay
        # Don't count the time we already waited as part of our waiting time :-0
        self.now = time.time()

    def getDelay(self):
        thisdelay = self.delay
        if self.pid: # If self.pid, we're checking for multiple processes
            if time.time() > self.checktime + self.checkdelay:
                self.checkMultiplicity()
            if thisdelay < (self.mindelay * self.next_multiplicity):
                thisdelay = self.mindelay * self.next_multiplicity
            elif thisdelay > self.maxdelay:
                thisdelay = self.maxdelay
            thisdelay *= self.process_multiplicity
        return thisdelay

    def waittime(self):
        """Calculate the time in seconds we will have to wait if a query
           would be made right now"""
        # Take the previous requestsize in account calculating the desired
        # delay this time
        thisdelay = self.getDelay()
        now = time.time()
        ago = now - self.now
        if ago < thisdelay:
            delta = thisdelay - ago
            return delta
        else:
            return 0.0

    def drop(self):
        """Remove me from the list of running bots processes."""
        self.checktime = 0
        processes = {}
        try:
            f = open('throttle.log','r')
        except IOError:
            return
        else:
            now = time.time()
            for line in f.readlines():
                line = line.split(' ')
                pid = int(line[0])
                ptime = int(line[1].split('.')[0])
                if now - ptime <= self.releasepid and pid != self.pid:
                    processes[pid] = ptime
        f = open('throttle.log','w')
        for p in processes.keys():
            f.write(str(p)+' '+str(processes[p])+'\n')
        f.close()
    
    def __call__(self, requestsize = 1):
        """This is called from getEditPage without arguments. It will make sure
           that if there are no 'ignores' left, there are at least delay seconds
           since the last time it was called before it returns."""
        waittime = self.waittime()
        # Calculate the multiplicity of the next delay based on how
        # big the request is that is being posted now.
        # We want to add "one delay" for each factor of two in the
        # size of the request. Getting 64 pages at once allows 6 times
        # the delay time for the server.
        self.next_multiplicity = math.log(1+requestsize)/math.log(2.0)
        # Announce the delay if it exceeds a preset limit
        if waittime > config.noisysleep:
            print "Sleeping for %.1f seconds" % waittime
        time.sleep(waittime)
        self.now = time.time()

get_throttle = Throttle(config.minthrottle,config.maxthrottle)
put_throttle = Throttle(config.put_throttle,config.put_throttle,False)


class MyURLopener(urllib.FancyURLopener):
    version="PythonWikipediaBot/1.0"

def replaceExceptNowikiAndComments(text, old, new):
    """
    Replaces old by new in text, skipping occurences of old within nowiki tags
    and HTML comments.
    
    Parameters:
        text - a string
        old  - a compiled regular expression
        new  - a string
    """
    
    nowikiOrHtmlCommentR = re.compile(r'<nowiki>.*?</nowiki>|<!--.*?-->', re.IGNORECASE | re.DOTALL)
    # How much of the text we have looked at so far
    index = 0
    while True:
        match = old.search(text, index)
        if not match:
            break
        nowikiOrHtmlCommentMatch = nowikiOrHtmlCommentR.search(text, index)
        if nowikiOrHtmlCommentMatch and nowikiOrHtmlCommentMatch.start() < match.start():
            # an HTML comment or text in nowiki tags stands before the next valid match. Skip.
            index = nowikiOrHtmlCommentMatch.end()
        else:
            # We found a valid match. Replace it.
            text = text[:match.start()] + new + text[match.end():]
            # continue the search on the remaining text
            index = match.start()
    return text

# Part of library dealing with interwiki links

def getLanguageLinks(text, insite = None, getPageObjects = False, pageLink = "[[]]"):
    """Returns a dictionary of other language links mentioned in the text
       in the form {code:pagename}. Do not call this routine directly, use
       Page objects instead"""
    if insite == None:
        insite = getSite()
    result = {}
    # Ignore interwiki links within nowiki tags and HTML comments
    nowikiOrHtmlCommentR = re.compile(r'<nowiki>.*?</nowiki>|<!--.*?-->', re.IGNORECASE | re.DOTALL)
    match = nowikiOrHtmlCommentR.search(text)
    while match:
        text = text[:match.start()] + text[match.end():]    
        match = nowikiOrHtmlCommentR.search(text)
        
    # This regular expression will find every link that is possibly an
    # interwiki link.
    # NOTE: This assumes that language codes only consist of non-capital
    # ASCII letters and hyphens.
    interwikiR = re.compile(r'\[\[([a-z\-]+)\s?:([^\[\]\n]*)\]\]')
    for lang, pagetitle in interwikiR.findall(text):
        # Check if it really is in fact an interwiki link to a known
        # language, or if it's e.g. a category tag or an internal link
        if lang in insite.family.obsolete:
            lang=insite.family.obsolete[lang]
        if lang in insite.family.langs:
            if '|' in pagetitle:
                # ignore text after the pipe
                pagetitle = pagetitle[:pagetitle.index('|')]
            if insite.lang == 'eo':
                pagetitle = resolveEsperantoXConvention(pagetitle)
            if not pagetitle:
                output(u"ERROR: %s - ignoring impossible link to %s:%s" % (pageLink, lang, pagetitle))
            else:
                if getPageObjects:
                    # if getPageObjects is true, we want the actual page objects rather than the titles
                    result[insite.getSite(code=lang)] = Page(insite.getSite(code=lang),pagetitle)
                else:
                    result[insite.getSite(code=lang)] = pagetitle
    return result

def removeLanguageLinks(text, site = None):
    """Given the wiki-text of a page, return that page with all interwiki
       links removed. If a link to an unknown language is encountered,
       a warning is printed."""
    if site == None:
        site = getSite()
    # This regular expression will find every interwiki link, plus trailing
    # whitespace.
    languageR = '|'.join(site.family.langs)
    interwikiR = re.compile(r'\[\[(%s)\s?:[^\]]*\]\][\s]*' % languageR)
    text = replaceExceptNowikiAndComments(text, interwikiR, '')
    return normalWhitespace(text)

def replaceLanguageLinks(oldtext, new, site = None):
    """Replace the interwiki language links given in the wikitext given
       in oldtext by the new links given in new.

       'new' should be a dictionary with the language names as keys, and
       either Page objects or the link-names of the pages as values.
    """
    if site == None:
        site = getSite()
    s = interwikiFormat(new, insite = site)
    s2 = removeLanguageLinks(oldtext, site = site)
    if s:
        if site.language() in site.family.interwiki_attop:
            newtext = s + site.family.interwiki_text_separator + s2
        elif site.language() in site.family.categories_last:
            cats = getCategoryLinks(s2, site = site)
            s3 = []
            for catname in cats:
                s3.append(Page(site, catname))
            s2 = removeCategoryLinks(s2, site) + site.family.interwiki_text_separator + s
            newtext = replaceCategoryLinks(s2, s3, site=site)
        else:
            newtext = s2 + site.family.interwiki_text_separator + s
    else:
        newtext = s2
    return newtext
    
def interwikiFormat(links, insite = None):
    """Create a suitable string encoding all interwiki links for a wikipedia
       page.

       'links' should be a dictionary with the language names as keys, and
       Page objects as values.

       The string is formatted for inclusion in insite (defaulting to your own).
    """
    if insite is None:
        insite = getSite()
    if not links:
        return ''
    # Security check: site may not refer to itself.
    for pl in links.values():
        if pl.site() == insite:
            raise ValueError("Trying to add interwiki link to self")
    s = []
    ar = links.keys()
    ar.sort()
    putfirst = insite.interwiki_putfirst()
    if putfirst:
        #In this case I might have to change the order
        ar2 = []
        for code in putfirst:
            # The code may not exist in this family?
            if code in getSite().family.langs:
                site = insite.getSite(code = code)
                if site in ar:
                    del ar[ar.index(site)]
                    ar2 = ar2 + [site]
        ar = ar2 + ar
    if insite.interwiki_putfirst_doubled(ar):
        ar = insite.interwiki_putfirst_doubled(ar) + ar
    for site in ar:
        try:
            link = links[site].aslink(forceInterwiki = True)
            # if linking from Esperanto, we must e.g. write Bordeauxx instead
            # of Bordeaux
            if insite.lang == 'eo':
                link = doubleXForEsperanto(link)
            s.append(link)
        except AttributeError:
            s.append(site.linkto(links[site],othersite=insite))
    if insite.lang in insite.family.interwiki_on_one_line:
        sep = ' '
    else:
        sep = '\r\n'
    s=sep.join(s) + '\r\n'
    return s 

def normalWhitespace(text):
    # Remove white space at the beginning
    while 1:
        if text and text.startswith('\r\n'):
            text=text[2:]
        elif text and text.startswith(' '):
            # This assumes that the first line NEVER starts with a space!
            text=text[1:]
        else:
            break
    # Remove white space at the end
    while 1:
        if text and text[-1:] in '\r\n \t':
            text=text[:-1]
        else:
            break
    # Add final newline back in
    text += '\n'
    return text

# Categories

def getCategoryLinks(text, site, withSortKeys = False):
    """Returns a list of category links.
       in the form {code:pagename}. Do not call this routine directly, use
       Page objects instead"""
    result = []
    # Ignore interwiki links within nowiki tags and HTML comments
    nowikiOrHtmlCommentR = re.compile(r'<nowiki>.*?</nowiki>|<!--.*?-->', re.IGNORECASE | re.DOTALL)
    match = nowikiOrHtmlCommentR.search(text)
    while match:
        text = text[:match.start()] + text[match.end():]    
        match = nowikiOrHtmlCommentR.search(text)
    namespaces = site.category_namespaces()
    for prefix in namespaces:
        if withSortKeys:
            R = re.compile(r'\[\[(%s:[^\]]+)\]' % prefix)
        else:
            R = re.compile(r'\[\[(%s:[^\]\|]+)(?:\||\])'  % prefix)
        for title in R.findall(text):
            result.append(title)
    return result

def removeCategoryLinks(text, site):
    """Given the wiki-text of a page, return that page with all category
       links removed. """
    # This regular expression will find every link that is possibly an
    # interwiki link, plus trailing whitespace. The language code is grouped.
    # NOTE: This assumes that language codes only consist of non-capital
    # ASCII letters and hyphens.
    catNamespace = '|'.join(site.category_namespaces())
    categoryR = re.compile(r'\[\[(%s):.*?\]\][\s]*' % catNamespace)
    text = replaceExceptNowikiAndComments(text, categoryR, '') 
    return normalWhitespace(text)

def replaceCategoryLinks(oldtext, new, site = None):
    """Replace the category links given in the wikitext given
       in oldtext by the new links given in new.

       'new' should be a list of category pagelink objects.
    """
    if site is None:
        site = getSite()
    # first remove interwiki links and add them later, so that
    # interwiki tags appear below category tags if both are set
    # to appear at the bottom of the article
    if not site.lang in site.family.categories_last:
        interwiki_links = getLanguageLinks(oldtext, insite = site, getPageObjects = True)
        oldtext = removeLanguageLinks(oldtext, site = site)
    s = categoryFormat(new, insite = site)
    s2 = removeCategoryLinks(oldtext, site = site)
    if s:
        if site.language() in site.family.category_attop:
            newtext = s + site.family.category_text_separator + s2
        else:
            newtext = s2 + site.family.category_text_separator + s
    else:
        newtext = s2
    # now re-add interwiki links
    if not site.lang in site.family.categories_last:
        newtext = replaceLanguageLinks(newtext, interwiki_links)
    return newtext
    
def categoryFormat(links, insite = None):
    """Create a suitable string encoding all category links for a wikipedia
       page.

       'links' should be a list of category pagelink objects.

       The string is formatted for inclusion in insite.
    """
    if not links:
        return ''
    if insite is None:
        insite = getSite()
    s = []
    for pl in links:
        s.append(pl.aslink())
    if insite.category_on_one_line():
        sep = ' '
    else:
        sep = '\r\n'
    s.sort()
    s=sep.join(s) + '\r\n'
    return s 

# end of category specific code

def myencoding():
    """The character encoding used by the home wiki"""
    return getSite().encoding()

def url2link(percentname, insite, site):
    """Convert a url-name of a page into a proper name for an interwiki link
       the argument 'insite' specifies the target wiki
       """
    percentname = underline2space(percentname)
    x = url2unicode(percentname, site = site)
    return unicode2html(x, insite.encoding())

def resolveEsperantoXConvention(text):
    """
    Resolves the x convention used to encode Esperanto special characters,
    e.g. Cxefpagxo and CXefpagXo will both be converted to Ĉefpaĝo.
    Note that to encode non-Esperanto words like Bordeaux, one uses a
    double x, i.e. Bordeauxx or BordeauxX.
    """
    chars = {
        u'cx': u'ĉ',
        u'Cx': u'Ĉ',
        u'gx': u'ĝ',
        u'Gx': u'Ĝ',
        u'hx': u'ĥ',
        u'Hx': u'Ĥ',
        u'jx': u'ĵ',
        u'Jx': u'Ĵ',
        u'sx': u'ŝ',
        u'Sx': u'Ŝ',
        u'ux': u'ŭ',
        u'Ux': u'Ŭ',
        u'xx': u'x',
        u'Xx': u'X',
        u'cX': u'ĉ',
        u'CX': u'Ĉ',
        u'gX': u'ĝ',
        u'GX': u'Ĝ',
        u'hX': u'ĥ',
        u'HX': u'Ĥ',
        u'jX': u'ĵ',
        u'JX': u'Ĵ',
        u'sX': u'ŝ',
        u'SX': u'Ŝ',
        u'uX': u'ŭ',
        u'UX': u'Ŭ',
        u'xX': u'x',
        u'XX': u'X'
    }
    # Run backwards through the text. Post fun stuff like
    # cx, cxx, cxxx, cxxxx, cxxxxx to an eo: wiki and you will know why.
    i = len(text) - 1
    while i > 0:
        if text[i-1 : i+1] in chars.keys():
            # We found two characters that should be replaced either by an x
            # or by an Esperanto special character.
            text = text[:i-1] + chars[text[i-1 : i+1]] + text[i+1:]
            i -= 2
        else:
            i -= 1
    return text

def doubleXForEsperanto(text):
    # Double X-es where necessary so that we can submit a changed
    # page later.
    for c in 'CGHJSU':
        for c2 in c,c.lower():
            text = text.replace(c2 + 'x', c2 + 'xx')
            text = text.replace(c2 + 'X', c2 + 'Xx')
    return text

def isInterwikiLink(s, site = None):
    """Try to check whether s is in the form "xx:link" where xx: is a
       known language. In such a case we are dealing with an interwiki link."""
    if not ':' in s:
        return False
    if site is None:
        site = getSite()
    l,k=s.split(':',1)
    if l in site.family.langs:
        return True
    return False
    
######## Unicode library functions ########

def UnicodeToAsciiHtml(s):
    html = []
    for c in s:
        cord = ord(c)
        #print cord,
        if cord < 128:
            html.append(c)
        else:
            html.append('&#%d;'%cord)
    return ''.join(html)

def url2unicode(title, site):
    try:
        t = title.encode(site.encoding())
        t = urllib.unquote(t)
        return unicode(t, site.encoding())
    except UnicodeError:
        # try to handle all encodings (will probably retry utf-8)
        for enc in site.encodings():
            try:
                t = title.encode(enc)
                t = urllib.unquote(t)
                return unicode(t, enc)
            except UnicodeError:
                pass
        # Couldn't convert, raise the original exception
        raise

def unicode2html(x, encoding):
    """
    We have a unicode string. We can attempt to encode it into the desired
    format, and if that doesn't work, we encode the unicode into html #
    entities. If it does work, we return it unchanged.
    """
    try:
        x.encode(encoding)
    except UnicodeError:
        x = UnicodeToAsciiHtml(x)
    return x
    
def removeEntity(name):
    Rentity = re.compile(r'&([A-Za-z]+);')
    result = u''
    i = 0
    while i < len(name):
        m = Rentity.match(name[i:])
        if m:
            if htmlentitydefs.name2codepoint.has_key(m.group(1)):
                x = htmlentitydefs.name2codepoint[m.group(1)]
                result = result + unichr(x)
                i += m.end()
            else:
                result += name[i]
                i += 1
        else:
            result += name[i]
            i += 1
    return result

def html2unicode(name):
    name = removeEntity(name)

    Runi = re.compile('&#(\d+);')
    Runi2 = re.compile('&#x([0-9a-fA-F]+);')
    result = u''
    i=0
    while i < len(name):
        m = Runi.match(name[i:])
        m2 = Runi2.match(name[i:])
        if m:
            result += unichr(int(m.group(1)))
            i += m.end()
        elif m2:
            result += unichr(int(m2.group(1),16))
            i += m2.end()
        else:
            try:
                result += name[i]
                i += 1
            except UnicodeDecodeError:
                print repr(name)
                raise
    return result

def Family(fam = None, fatal = True):
    """
    Import the named family.
    """
    if fam == None:
        fam = config.family
    try:
        # search for family module in the 'families' subdirectory
        sys.path.append('families')
        exec "import %s_family as myfamily" % fam
    except ImportError:
        if fatal:
            print "Error importing the %s family. This probably means the family"%fam
            print "does not exist. Also check your configuration file"
            sys.exit(1)
        else:
            raise ValueError("Family does not exist")
    return myfamily.Family()

class Site(object):
    def __init__(self, code, fam=None, user=None):
        """Constructor takes three arguments:

        code    language code for Site
        fam     Wikimedia family (optional: defaults to configured)
        user    User to use (optional: defaults to configured)"""

        self.lang = code.lower()
        if isinstance(fam, basestring) or fam is None:
            self.family = Family(fam)
        else:
            self.family = fam
        if self.lang not in self.family.langs:
            raise KeyError("Language %s does not exist in family %s"%(self.lang,self.family.name))

        self.nocapitalize = self.lang in self.family.nocapitalize
        self.user = user
        self._token = None
        self._sysoptoken = None
        self.loginStatusKnown = False
        self.loggedInAs = None
        
    def forceLogin(self, sysop = False):
        if not self.loggedin(sysop = sysop):
            loginMan = login.LoginManager(site = self, sysop = sysop)
            if loginMan.login(retry = True):
                self.loginStatusKnown = True
                self.loggedInAs = loginMan.username
    
    def loggedin(self, sysop = False):
        """
        Checks if we're logged in by loading a page and looking for the login
        link. We assume that we're not being logged out during a bot run, so
        loading the test page is only required once.
        """
        self._loadCookies()
        if not self.loginStatusKnown:
            output(u'Getting a page to check if we\'re logged in on %s' % self)
            path = self.get_address('Non-existing_page')
            text = self.getUrl(path, sysop = sysop)
            # Search for the "my talk" link at the top
            mytalkR = re.compile('<a href=".+?">(?P<username>.+?)</a></li>\s*<li id="pt-mytalk">')
            m = mytalkR.search(text)
            if m:
                self.loginStatusKnown = True
                self.loggedInAs = m.group('username')
                # While we're at it, check if we have got unread messages
                if '<div class="usermessage">' in text:
                    output(u'NOTE: You have unread messages on %s' % self)
        return (self.loggedInAs is not None)
    
    def cookies(self, sysop = False):
        # TODO: cookie caching is disabled
        #if not hasattr(self,'_cookies'):
        self._loadCookies(sysop = sysop)
        return self._cookies

    def _loadCookies(self, sysop = False):
        """Retrieve session cookies for login"""
        try:
            if sysop:
                username = config.sysopnames[self.family.name][self.lang]
            else:
                username = config.usernames[self.family.name][self.lang]
        except KeyError:
            self._cookies = None
            self.loginStatusKnown = True
        else:
            fn = 'login-data/%s-%s-%s-login.data' % (self.family.name, self.lang, username)
            #if not os.path.exists(fn):
            #    fn = 'login-data/%s-login.data' % self.lang
            if not os.path.exists(fn):
                #print "Not logged in"
                self._cookies = None
                self.loginStatusKnown = True
            else:
                f = open(fn)
                self._cookies = '; '.join([x.strip() for x in f.readlines()])
                f.close()

    def getUrl(self, path, sysop = False):
        """
        Low-level routine to get a URL from the wiki.
           
        Parameters:
            path  - The absolute path.
            sysop - If True, the sysop account's cookie will be used.
    
           Returns the HTML text of the page converted to unicode.
        """
        uo = MyURLopener()
        if self.cookies(sysop = sysop):
            uo.addheader('Cookie', self.cookies(sysop = sysop))
        f = uo.open('http://%s%s' % (self.hostname(), path))
        text = f.read()
        # Find charset in the content-type meta tag
        contentType = f.info()['Content-Type']
        R = re.compile('charset=([^\'\"]+)')
        m = R.search(contentType)
        if m:
            charset = m.group(1)
        else:
            print "WARNING: No character set found"
            # UTF-8 as default
            charset = 'utf-8'
        # Check if this is the charset we expected
        self.checkCharset(charset)
        # Convert HTML to Unicode
        try:
            text = unicode(text, charset, errors = 'strict')
        except UnicodeDecodeError, e:
            print e
            output(u'ERROR: Invalid characters found on http://%s%s, replaced by \\ufffd.' % (self.hostname(), path)) 
            # We use error='replace' in case of bad encoding.
            text = unicode(text, charset, errors = 'replace')
        return text
        
    
    def newpages(self, number = 10, repeat = False):
        """Generator which yields new articles subsequently.
           It starts with the article created 'number' articles
           ago (first argument). When these are all yielded
           it fetches NewPages again. If there is no new page,
           it blocks until there is one, sleeping between subsequent
           fetches of NewPages.
    
           The objects yielded are dictionairies. The keys are
           date (datetime object), title (pagelink), length (int)
           user_login (only if user is logged in, string), comment
           (string) and user_anon (if user is not logged in, string).
    
           The throttling is important here, so always enabled.
        """
        throttle = True
        seen = set()
        while True:
            path = self.newpages_address()
            get_throttle()
            html = self.getUrl(path)
    
            entryR = re.compile('<li>(?P<date>.+?) <a href=".+?" title="(?P<title>.+?)">.+?</a> \((?P<length>\d+)(.+?)\) \. \. (?P<loggedin><a href=".+?" title=".+?">)?(?P<username>.+?)(</a>)?( <em>\((?P<comment>.+?)\)</em>)?</li>')
            for m in entryR.finditer(html):
                date = m.group('date')
                title = m.group('title')
                title = title.replace('&quot;', '"')
                length = int(m.group('length'))
                loggedIn = (m.group('loggedin') is not None)
                username = m.group('username')
                comment = m.group('comment')
    
                if title not in seen:
                    seen.add(title)
                    page = Page(self, title)
                    yield page, date, length, loggedIn, username, comment
            if not repeat:
                break

    def longpages(self, number = 10, repeat = False):
        throttle = True
        seen = set()
        while True:
            path = self.longpages_address()
            get_throttle()
            html = self.getUrl(path)
            entryR = re.compile('<li><a href=".+?" title="(?P<title>.+?)">.+?</a> \((?P<length>\d+)(.+?)\)</li>')
            for m in entryR.finditer(html):
                title = m.group('title')
                length = int(m.group('length'))
                   
                if title not in seen:
                    seen.add(title)
                    page = Page(self, title)
                    yield page, length
            if not repeat:
                break
            
    def shortpages(self, number = 10, repeat = False):
        throttle = True
        seen = set()
        while True:
            path = self.shortpages_address()
            get_throttle()
            html = self.getUrl(path)
            entryR = re.compile('<li><a href=".+?" title="(?P<title>.+?)">.+?</a> \((?P<length>\d+)(.+?)\)</li>')
            for m in entryR.finditer(html):
                title = m.group('title')
                length = int(m.group('length'))
                   
                if title not in seen:
                    seen.add(title)
                    page = Page(self, title)
                    yield page, length
            if not repeat:
                break

    def categories(self, number = 10, repeat = False):
        throttle = True
        seen = set()
        while True:
            path = self.categories_address()
            get_throttle()
            html = self.getUrl(path)
            entryR = re.compile('<li><a href=".+?" title="(?P<title>.+?)">.+?</a></li>')
            for m in entryR.finditer(html):
                title = m.group('title')
                                   
                if title not in seen:
                    seen.add(title)
                    page = Page(self, title)
                    yield page
            if not repeat:
                break

    def deadendpages(self, number = 10, repeat = False):
        throttle = True
        seen = set()
        while True:
            path = self.deadendpages_address()
            get_throttle()
            html = self.getUrl(path)
            entryR = re.compile('<li><a href=".+?" title="(?P<title>.+?)">.+?</a></li>')
            for m in entryR.finditer(html):
                title = m.group('title')
                                   
                if title not in seen:
                    seen.add(title)
                    page = Page(self, title)
                    yield page
            if not repeat:
                break

    def ancientpages(self, number = 10, repeat = False):
        throttle = True
        seen = set()
        while True:
            path = self.ancientpages_address()
            get_throttle()
            html = self.getUrl(path)
            entryR = re.compile('<li><a href=".+?" title="(?P<title>.+?)">.+?</a> (?P<date>.+?)</li>')
            for m in entryR.finditer(html):
                title = m.group('title')
                date = m.group('date')
                                                  
                if title not in seen:
                    seen.add(title)
                    page = Page(self, title)
                    yield page, date
            if not repeat:
                break
    
    def lonelypages(self, number = 10, repeat = False):
        throttle = True
        seen = set()
        while True:
            path = self.lonelypages_address()
            get_throttle()
            html = self.getUrl(path)
            entryR = re.compile('<li><a href=".+?" title="(?P<title>.+?)">.+?</a></li>')
            for m in entryR.finditer(html):
                title = m.group('title')
                                   
                if title not in seen:
                    seen.add(title)
                    page = Page(self, title)
                    yield page
            if not repeat:
                break

    def uncategorizedcategories(self, number = 10, repeat = False):
        throttle = True
        seen = set()
        while True:
            path = self.uncategorizedcategories_address()
            get_throttle()
            html = self.getUrl(path)
            entryR = re.compile('<li><a href=".+?" title="(?P<title>.+?)">.+?</a></li>')
            for m in entryR.finditer(html):
                title = m.group('title')
                                   
                if title not in seen:
                    seen.add(title)
                    page = Page(self, title)
                    yield page
            if not repeat:
                break

    def uncategorizedpages(self, number = 10, repeat = False):
        throttle = True
        seen = set()
        while True:
            path = self.uncategorizedpages_address()
            get_throttle()
            html = self.getUrl(path)
            entryR = re.compile('<li><a href=".+?" title="(?P<title>.+?)">.+?</a></li>')
            for m in entryR.finditer(html):
                title = m.group('title')
                                   
                if title not in seen:
                    seen.add(title)
                    page = Page(self, title)
                    yield page
            if not repeat:
                break

    def unusedcategories(self, number = 10, repeat = False):
        throttle = True
        seen = set()
        while True:
            path = self.unusedcategories_address()
            get_throttle()
            html = self.getUrl(path)
            entryR = re.compile('<li><a href=".+?" title="(?P<title>.+?)">.+?</a></li>')
            for m in entryR.finditer(html):
                title = m.group('title')
                                   
                if title not in seen:
                    seen.add(title)
                    page = Page(self, title)
                    yield page
            if not repeat:
                break
    
    def allpages(self, start = '!', namespace = 0, throttle = True):
        """Generator which yields all articles in the home language in
           alphanumerical order, starting at a given page. By default,
           it starts at '!', so it should yield all pages.
    
           The objects returned by this generator are all Page()s.
        """
        while True:
            # encode Non-ASCII characters in hexadecimal format (e.g. %F6)
            start = start.encode(self.encoding())
            start = urllib.quote(start)
            # load a list which contains a series of article names (always 480)
            path = self.allpages_address(start, namespace)
            print 'Retrieving Allpages special page for %s from %s, namespace %i' % (repr(self), start, namespace)
            returned_html = self.getUrl(path)
            # Try to find begin and end markers
            try:
                # In 1.4, another table was added above the navigational links
                if self.version() < "1.4":
                    begin_s = '<table'
                    end_s = '</table'
                else:
                    begin_s = '</table><hr /><table'
                    end_s = '</table><div class="printfooter">'
                ibegin = returned_html.index(begin_s)
                iend = returned_html.index(end_s)
            except ValueError:
                raise NoPage('Couldn\'t extract allpages special page. Make sure you\'re using the MonoBook skin.')
            # remove the irrelevant sections
            returned_html = returned_html[ibegin:iend]
            if self.version()=="1.2":
                R = re.compile('/wiki/(.*?)" *class=[\'\"]printable')
            else:
                R = re.compile('title ?="(.*?)"')
            # Count the number of useful links on this page
            n = 0
            for hit in R.findall(returned_html):
                # count how many articles we found on the current page
                n = n + 1
                if self.version()=="1.2":
                    yield Page(self, url2link(hit, site = self, insite = self))
                else:
                    yield Page(self, hit)
                # save the last hit, so that we know where to continue when we
                # finished all articles on the current page. Append a '!' so that
                # we don't yield a page twice.
                start = hit + '!'
            # A small shortcut: if there are less than 100 pages listed on this
            # page, there is certainly no next. Probably 480 would do as well,
            # but better be safe than sorry.
            if n < 100:
                break

    def __repr__(self):
        return self.family.name+":"+self.lang
    
    def linkto(self, title, othersite = None):
        if othersite and othersite.lang != self.lang:
            return '[[%s:%s]]' % (self.lang, title)
        else:
            return '[[%s]]' % title

    def encoding(self):
        return self.family.code2encoding(self.lang)

    def encodings(self):
        return self.family.code2encodings(self.lang)

    def redirect(self, default = False):
        """
        Gives the localized redirect tag for the site. Falls back
        to 'REDIRECT' if the site has no special redirect tag.
        """
        if default:
            return self.family.redirect.get(self.lang, "REDIRECT") 	 
        else: 	 
            return self.family.redirect.get(self.lang, None)

    def redirectRegex(self):
        """
        Regular expression recognizing redirect pages
        """
        redirKeywords = [u'redirect']
        try:
            redirKeywords += self.family.redirect[self.lang]
        except KeyError:
            pass
        txt = '(?:'+'|'.join(redirKeywords)+')'
        return re.compile(r'\#'+txt+'[^[]*\[\[(.*?)(\]|\|)', re.IGNORECASE)

    def category_namespace(self):
        return self.family.category_namespace(self.lang)

    def category_namespaces(self):
        return self.family.category_namespaces(self.lang)

    def image_namespace(self, fallback = '_default'):
        return self.family.image_namespace(self.lang, fallback)

    def template_namespace(self, fallback = '_default'):
        return self.family.template_namespace(self.lang, fallback)

    def export_address(self):
        return self.family.export_address(self.lang)
    
    def hostname(self):
        return self.family.hostname(self.lang)

    def delete_address(self, s):
        return self.family.delete_address(self.lang, s)

    def put_address(self, s):
        return self.family.put_address(self.lang, s)

    def get_address(self, s):
        return self.family.get_address(self.lang, s)

    def edit_address(self, s):
        return self.family.edit_address(self.lang, s)
    
    def purge_address(self, s):
        return self.family.purge_address(self.lang, s)
    
    def checkCharset(self, charset):
        if not hasattr(self,'charset'):
            self.charset = charset
        assert self.charset.lower() == charset.lower(), "charset for %s changed from %s to %s"%(repr(self),self.charset,charset)
        if self.encoding().lower() != charset.lower():
            raise ValueError("code2encodings has wrong charset for %s. It should be %s, but is %s"%(repr(self),charset, self.encoding()))

    def allpages_address(self, s, ns = 0):
        return self.family.allpages_address(self.lang, start = s, namespace = ns)

    def newpages_address(self, n=50):
        return self.family.newpages_address(self.lang, n)

    def longpages_address(self, n=500):
        return self.family.longpages_address(self.lang, n)

    def shortpages_address(self, n=500):
        return self.family.shortpages_address(self.lang, n)

    def categories_address(self, n=500):
        return self.family.categories_address(self.lang, n)

    def deadendpages_address(self, n=500):
        return self.family.deadendpages_address(self.lang, n)

    def ancientpages_address(self, n=500):
        return self.family.ancientpages_address(self.lang, n)

    def lonelypages_address(self, n=500):
        return self.family.lonelypages_address(self.lang, n)

    def uncategorizedcategories_address(self, n=500):
        return self.family.uncategorizedcategories_address(self.lang, n)

    def uncategorizedpages_address(self, n=500):
        return self.family.uncategorizedpages_address(self.lang, n)

    def unusedcategories_address(self, n=500):
        return self.family.unusedcategories_address(self.lang, n)

    def references_address(self, s):
        return self.family.references_address(self.lang, s)

    def __hash__(self):
        return hash(repr(self))

    def version(self):
        return self.family.version(self.lang)

    def __cmp__(self, other):
        """Pseudo method to be able to use equality and inequality tests on
           Site objects"""
        if not isinstance(other,Site):
            return 1
        if self.family==other.family:
            return cmp(self.lang,other.lang)
        return cmp(self.family.name,other.family.name)

    def category_on_one_line(self):
        return self.lang in self.family.category_on_one_line

    def interwiki_putfirst(self):
        return self.family.interwiki_putfirst.get(self.lang,None)

    def interwiki_putfirst_doubled(self,list_of_links):
        if self.family.interwiki_putfirst_doubled.has_key(self.lang):
            if len(list_of_links) >= self.family.interwiki_putfirst_doubled[self.lang][0]:
                list_of_links2 = []
                for lang in list_of_links:
                    list_of_links2.append(lang.language())
                list = []
                for lang in self.family.interwiki_putfirst_doubled[self.lang][1]:
                    try:
                        list.append(list_of_links[list_of_links2.index(lang)])
                    except ValueError:
                        pass
                return list
            else:
                return False
        else:
            return False

    def login_address(self):
        return self.family.login_address(self.lang)

    def watchlist_address(self):
        return self.family.watchlist_address(self.lang)

    def getSite(self, code):
        return getSite(code = code, fam = self.family, user=self.user)

    def namespace(self, num):
        return self.family.namespace(self.lang, num)

    def namespaces(self):
        list=()
        for n in self.family.namespaces:
            ns = self.family.namespace(self.lang, n)
            if ns is not None:
                list += (self.family.namespace(self.lang, n),)
        return list

    def allmessages_address(self):
        return self.family.allmessages_address(self.lang)

    def upload_address(self):
        return self.family.upload_address(self.lang)

    def maintenance_address(self, sub, default_limit = True):
        return self.family.maintenance_address(self.lang, sub, default_limit)

    def double_redirects_address(self, default_limit = True):
        return self.family.double_redirects_address(self.lang, default_limit)

    def broken_redirects_address(self, default_limit = True):
        return self.family.broken_redirects_address(self.lang, default_limit)

    def language(self):
        return self.lang

    def family(self):
        return self.family

    def sitename(self):
        return self.family.name+':'+self.lang

    def languages(self):
        return self.family.langs.keys()

    def getToken(self, getalways = True, getagain = False, sysop = False):
        if getagain or (getalways and ((sysop and not self._sysoptoken) or (not sysop and not self._token))):
            output(u"Getting page to get a token.")
            try:
                Page(self, "%s:Sandbox" % self.family.namespace(self.lang, 4)).get(force = True, sysop = sysop)
            except UserBlocked:
                raise
            except Error:
                pass
        if sysop:
            if not self._sysoptoken:
                return False
            else:
                return self._sysoptoken
        else:
            if not self._token:
                return False
            else:
                return self._token

    def putToken(self,value, sysop = False):
        if sysop:
            self._sysoptoken = value
        else:
            self._token = value
        return
    
_sites = {}

def getSite(code = None, fam = None, user=None):
    if code == None:
        code = default_code
    if fam == None:
        fam = default_family
    key = '%s:%s'%(fam,code)
    if not _sites.has_key(key):
        _sites[key] = Site(code=code, fam=fam, user=user)
    return _sites[key]

def setSite(site):
    default_code = site.language
    default_family = site.family
    
def argHandler(arg, moduleName):
    '''
    Takes a commandline parameter, converts it to unicode, and returns it unless
    it is one of the global parameters as -lang or -log. If it is a global
    parameter, processes it and returns None.

    moduleName should be the name of the module calling this function. This is
    required because the -help option loads the module's docstring and because
    the module name will be used for the filename of the log.
    '''
    global default_code, default_family
    if sys.platform=='win32':
        # stupid Windows gives parameters encoded as windows-1252, but input
        # encoded as cp850
        arg = unicode(arg, 'windows-1252')
    else:
        # Linux uses the same encoding for both
        arg = unicode(arg, config.console_encoding)
    if arg == '-help':
        showHelp(moduleName)
        sys.exit(0)
    elif arg.startswith('-family:'):
        global default_family 
        default_family = arg[8:]
    elif arg.startswith('-lang:'):
        global default_code
        default_code = arg[6:]
    elif arg.startswith('-putthrottle:'):
        put_throttle.setDelay(int(arg[13:]),absolute = True)
    elif arg == '-log':
        activateLog('%s.log' % moduleName)
    elif arg.startswith('-log:'):
        activateLog(arg[5:])
    elif arg == '-nolog':
        global logfile
        logfile = None
    else:
        return arg
    return None

#########################
# Interpret configuration
#########################

# search for user interface module in the 'userinterfaces' subdirectory
sys.path.append('userinterfaces')
exec "import %s_interface as uiModule" % config.userinterface
ui = uiModule.UI()

default_family = config.family
default_code = config.mylang
logfile = None
# Check
try:
    getSite()
except KeyError:
    print(
u"""Please create a file user-config.py, and put in there:\n
One line saying \"mylang='language'\"
One line saying \"usernames['wikipedia']['language']='yy'\"\n
...filling in your username and the language code of the wiki you want to work
on.\n
For other possible configuration variables check config.py.
""")
    sys.exit(1)


# Languages to use for comment text after the actual language but before
# en:. For example, if for language 'xx', you want the preference of
# languages to be:
# xx:, then fr:, then ru:, then en:
# you let altlang return ['fr','ru'].
# This code is used by translate() below.

def altlang(code):
    if code=='aa':
        return ['am']
    if code in ['fa','so']:
        return ['ar']
    if code=='ku':
        return ['ar','tr']
    if code=='sk':
        return ['cs']
    if code=='nds':
        return ['de','nl']
    if code in ['als','lb']:
        return ['de','fr']
    if code in ['an','ast','ay','ca','gn','nah','qu']:
        return ['es']
    if code=='eu':
        return ['es','fr']
    if code=='gl':
        return ['es','pt']
    if code=='lad':
        return ['es','he']
    if code in ['br','ht','ln','lo','vi','wa']:
        return ['fr']
    if code in ['ie','oc']:
        return ['ie','oc','fr']
    if code=='co':
        return ['fr','it']
    if code in ['lmo','nap','sc','scn','vec']:
        return ['it']
    if code=='rm':
        return ['it','de','fr']
    if code=='fy':
        return ['nl']
    if code=='li':
        return ['nl','de']
    if code=='csb':
        return ['pl']
    if code in ['mo','roa-rup']:
        return ['ro']
    if code in ['av','be','cv','hy','lt','lv','tt','udm','uk']:
        return ['ru']
    if code=='got':
        return ['ru','uk']
    if code in ['kk','ky','tk','ug','uz']:
        return ['tr','ru']
    if code in ['bo','ja','ko','minnan','za','zh','zh-cn','zh-tw']:
        return ['zh','zh-tw','zh-cn']
    if code=='da':
        return ['nb','no']
    if code in ['is','no','nb','nn']:
        return ['no','nb','nn','da','sv']
    if code=='sv':
        return ['da','no','nb']
    if code=='se':
        return ['no','nb','sv','nn','fi','da']
    if code in ['bug','id','jv','ms','su']:
        return ['id','ms','jv']
    if code in ['bs','hr','mk','sh','sr']:
        return ['sh','hr','sr','bs']
    if code=='ia':
        return ['la','es','fr','it']
    if code=='sa':
        return ['hi']
    if code=='yi':
        return ['he']
    if code in ['ceb','war']:
        return ['tl']
    if code=='bi':
        return ['tpi']
    if code=='tpi':
        return ['bi']
    return []


def translate(code, dict):
    """
    Given a language code and a dictionary, returns the dictionary's value for
    key 'code' if this key exists; otherwise tries to return a value for an
    alternative language that is most applicable to use on the Wikipedia in
    language 'code'.
    The language itself is always checked first, then languages that
    have been defined to be alternatives, and finally English. If none of
    the options gives result, we just take the first language in the
    list.
    """
    # If a site is given instead of a code, use its language
    if hasattr(code,'lang'):
        code = code.lang
        
    if dict.has_key(code):
        return dict[code]
    for alt in altlang(code):
        if dict.has_key(alt):
            return dict[alt]
    if dict.has_key('en'):
        return dict['en']
    return dict.values()[0]

def showDiff(oldtext, newtext):
    """
    Prints a string showing the differences between oldtext and newtext.
    The differences are highlighted (only on Unix systems) to show which
    changes were made.
    """
    # For information on difflib, see http://pydoc.org/2.3/difflib.html
    color = {
        '+': 10, # green
        '-': 12  # red
    }
    diff = u''
    colors = []
    # This will store the last line beginning with + or -.
    lastline = None
    # For testing purposes only: show original, uncolored diff
    #     for line in difflib.ndiff(oldtext.splitlines(), newtext.splitlines()):
    #         print line
    for line in difflib.ndiff(oldtext.splitlines(), newtext.splitlines()):
        if line.startswith('?'):
            # initialize color vector with None, which means default color
            lastcolors = [None for c in lastline]
            # colorize the + or - sign
            lastcolors[0] = color[lastline[0]]
            # colorize changed parts in red or green
            for i in range(min(len(line), len(lastline))):
                if line[i] != ' ':
                    lastcolors[i] = color[lastline[0]]
            diff += lastline + '\n'
            # append one None (default color) for the newline character
            colors += lastcolors + [None]
        elif lastline:
            diff += lastline + '\n'
            # colorize the + or - sign only
            lastcolors = [None for c in lastline]
            lastcolors[0] = color[lastline[0]]
            colors += lastcolors + [None]
        lastline = None
        if line[0] in ('+', '-'):
            lastline = line
    # there might be one + or - line left that wasn't followed by a ? line.
    if lastline:
        diff += lastline + '\n'
        # colorize the + or - sign only
        lastcolors = [None for c in lastline]
        lastcolors[0] = color[lastline[0]]
        colors += lastcolors + [None]

    output(diff, colors = colors)

def activateLog(logname):
    global logfile
    try:
        logfile = codecs.open('logs/%s' % logname, 'a', 'utf-8')
    except IOError:
        logfile = codecs.open('logs/%s' % logname, 'w', 'utf-8')

def output(text, decoder = None, colors = [], newline = True):
    """
    Works like print, but uses the encoding used by the user's console
    (console_encoding in the configuration file) instead of ASCII.
    If decoder is None, text should be a unicode string. Otherwise it
    should be encoded in the given encoding.

    colors is a list of integers, one for each character of text. If a
    list entry is None, the default color will be used for the
    character at that position.

    If newline is True, a linebreak will be added after printing the text.
    """
    if decoder:
        text = unicode(text, decoder)
    elif type(text) != type(u''):
        print "DBG> BUG: Non-unicode passed to wikipedia.output without decoder!"
        print traceback.print_stack()
        print "DBG> Attempting to recover, but please report this problem"
        try:
            text = unicode(text, 'utf-8')
        except UnicodeDecodeError:
            text = unicode(text, 'iso8859-1')
    if logfile:
        # save the text in a logfile (will be written in utf-8)
        logfile.write(text + '\n')
        logfile.flush()
    ui.output(text, colors = colors, newline = newline)

def input(question):
    return ui.input(question)

def inputChoice(question, answers, hotkeys, default = None):
    return ui.inputChoice(question, answers, hotkeys, default)

def showHelp(moduleName):
    globalHelp =u'''
Global arguments available for all bots:

-lang:xx          Set the language of the wiki you want to work on, overriding
                  the configuration in user-config.py. xx should be the
                  language code.

-family:xyz       Set the family of the wiki you want to work on, e.g.
                  wikipedia, wiktionary, wikitravel, ...
                  This will override the configuration in user-config.py.

-log              Enable the logfile. Logs will be stored in the logs
                  subdirectory.

-log:xyz          Enable the logfile, using xyz as the filename.

-nolog            Disable the logfile (if it's enabled by default).

-putthrottle:nn   Set the minimum time (in seconds) the bot will wait between
                  saving pages.
'''
    output(globalHelp)
    try:
        exec('import %s as module' % moduleName)
        output(module.__doc__, 'utf-8')
    except:
        output(u'Sorry, no help available for %s' % moduleName)

def stopme():
    """This should be run when a bot does not interact with the Wiki, or
       when it has stopped doing so. After a bot has run stopme() it will
       not slow down other bots any more.
    """
    get_throttle.drop()
