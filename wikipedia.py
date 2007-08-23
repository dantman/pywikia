## -*- coding: utf-8  -*-
"""
Library to get and put pages on a MediaWiki.

Contents of the library (objects and functions to be used outside, situation
late August 2004)

Classes:
Page: A MediaWiki page
    __init__              : Page(Site, Title) - the page with title Title on wikimedia site Site
    title                 : The name of the page, in a form suitable for an interwiki link
    urlname               : The name of the page, in a form suitable for a URL
    titleWithoutNamespace : The name of the page, with the namespace part removed
    section               : The section of the page (the part of the name after '#')
    sectionFreeTitle      : The name without the section part
    aslink                : The name of the page in the form [[Title]] or [[lang:Title]]
    site                  : The wiki this page is in
    encoding              : The encoding of the page
    isAutoTitle           : If the title is a well known, auto-translatable title
    autoFormat            : Returns (dictName, value), where value can be a year, date, etc.,
                            and dictName is 'YearBC', 'December', etc.
    isCategory            : True if the page is a category, false otherwise
    isImage               : True if the page is an image, false otherwise

    get (*)               : The text of the page
    exists (*)            : True if the page actually exists, false otherwise
    isRedirectPage (*)    : True if the page is a redirect, false otherwise
    isEmpty (*)           : True if the page has 4 characters or less content, not
                            counting interwiki and category links
    botMayEdit (*)        : True if bot is allowed to edit page
    interwiki (*)         : The interwiki links from the page (list of Pages)
    categories (*)        : The categories the page is in (list of Pages)
    linkedPages (*)       : The normal pages linked from the page (list of Pages)
    imagelinks (*)        : The pictures on the page (list of ImagePages)
    templates (*)         : All templates referenced on the page (list of strings)
    getRedirectTarget (*) : The page the page redirects to
    isDisambig (*)        : True if the page is a disambiguation page
    getReferences         : List of pages linking to the page
    namespace             : The namespace in which the page is
    permalink (*)         : The url of the permalink of the current version
    move                  : Move the page to another title
    put(newtext)          : Saves the page
    put_async(newtext)    : Queues the page to be saved asynchronously
    delete                : Deletes the page (requires being logged in)

    (*) : This loads the page if it has not been loaded before; permalink might
          even reload it if it has been loaded before

Site: a MediaWiki site
    messages              : There are new messages on the site
    forceLogin()          : Does not continue until the user has logged in to
                            the site
    getUrl()              : Retrieve an URL from the site
    mediawiki_message(key): Retrieve the text of the MediaWiki message with
                            the key "key"
    has_mediawiki_message(key) : True if this site defines a MediaWiki message
                                 with the key "key"
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
handleArgs(): Checks whether text is an argument defined on wikipedia.py
    (these are -family, -lang, -log and others)
translate(xx, dict): dict is a dictionary, giving text depending on language,
    xx is a language. Returns the text in the most applicable language for
    the xx: wiki
setUserAgent(text): Sets the string being passed to the HTTP server as
    the User-agent: header. Defaults to 'Pywikipediabot/1.0'.

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
# (C) Pywikipedia bot team, 2003-2006
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'

import os, sys
import httplib, socket, urllib
import traceback
import time, threading, Queue
import math
import re, md5, codecs, difflib, locale
import xml.sax, xml.sax.handler
import htmlentitydefs
import warnings
import unicodedata

import config, login
import xmlreader
from BeautifulSoup import *
import simplejson

# we'll set the locale to system default. This will ensure correct string
# handling for non-latin characters on Python 2.3.x. For Python 2.4.x it's no
# longer needed.
locale.setlocale(locale.LC_ALL, '')

try:
    set # introduced in Python2.4: faster and future
except NameError:
    from sets import Set as set


# Check Unicode support (is this a wide or narrow python build?)
# See http://www.python.org/doc/peps/pep-0261/
try:
    unichr(66365)  # a character in th: alphabet, uses 32 bit encoding
    WIDEBUILD = True
except ValueError:
    WIDEBUILD = False


# Local exceptions

class Error(Exception):
    """Wikipedia error"""

class NoUsername(Error):
    """Username is not in user-config.py"""

class NoPage(Error):
    """Page does not exist"""

class IsRedirectPage(Error):
    """Page is a redirect page"""

class IsNotRedirectPage(Error):
    """Page is not a redirect page"""

class LockedPage(Error):
    """Page is locked"""

class LockedNoPage(NoPage, LockedPage):
    """Page does not exist, and creating it is not possible because of a lock."""

class NoSuchEntity(ValueError):
    """No entity exist for this character"""

class SectionError(Error):
    """The section specified by # does not exist"""

class PageNotSaved(Error):
    """Saving the page has failed"""

class EditConflict(PageNotSaved):
    """There has been an edit conflict while uploading the page"""

class SpamfilterError(PageNotSaved):
    """Saving the page has failed because the MediaWiki spam filter detected a blacklisted URL."""
    def __init__(self, arg):
        self.url = arg
        self.args = arg,

class ServerError(Error):
    """Got unexpected server response"""
    
class BadTitle(Error):
    """Server responded with BadTitle."""

# UserBlocked exceptions should in general not be catched. If the bot has been
# blocked, the bot operator has possibly done a mistake and should take care of
# the issue before continuing.
class UserBlocked(Error):
    """Your username or IP has been blocked"""

class PageNotFound(Exception):
    """Page not found in list"""

SaxError = xml.sax._exceptions.SAXParseException

# Pre-compile re expressions
reNamespace = re.compile("^(.+?) *: *(.*)$")

# The most important thing in this whole module: The Page class
class Page(object):
    """A page on the wiki."""
    def __init__(self, site, title, insite = None, defaultNamespace = 0):
        """
        Constructor. Normally called with two arguments:
        Parameters:
         1) The wikimedia site on which the page resides
         2) The title of the page as a unicode string

        The argument insite can be specified to help decode
        the name; it is the wikimedia site where this link was found.
        """
        try:
            # if _editrestriction is True, it means that the page has been found
            # to have an edit restriction, but we do not know yet whether the
            # restriction affects us or not
            self._editrestriction = False
            
            if site == None:
                site = getSite()
            elif type(site) in [type(''), type(u'')]:
                site = getSite(site)
            
            self._site = site

            if not insite:
                insite = site

            # Convert HTML entities to unicode
            t = html2unicode(title)
            
            # Convert URL-encoded characters to unicode
            # Sometimes users copy the link to a site from one to another. Try both the source site and the destination site to decode.
            t = url2unicode(t, site = insite, site2 = site)
            
            #Normalize unicode string to a NFC (composed) format to allow proper string comparisons
            # According to http://svn.wikimedia.org/viewvc/mediawiki/branches/REL1_6/phase3/includes/normal/UtfNormal.php?view=markup
            # the mediawiki code normalizes everything to NFC, not NFKC (which might result in information loss).
            t = unicodedata.normalize('NFC', t)
            
            # Clean up the name, it can come from anywhere.
            # Replace underscores by spaces, also multiple spaces and underscores with a single space
            # Strip spaces at both ends
            t = re.sub('[ _]+', ' ', t).strip()
            # leading colon implies main namespace instead of the default
            if t.startswith(':'):
                t = t[1:]
                self._namespace = 0
            else:
                self._namespace = defaultNamespace

            #
            # This code was adapted from Title.php : secureAndSplit()
            #
            # Namespace or interwiki prefix
            while True:
                m = reNamespace.match(t)
                if not m:
                    break
                p = m.group(1)
                lowerNs = p.lower()
                ns = self.site().getNamespaceIndex(lowerNs)
                if ns:
                    t = m.group(2)
                    self._namespace = ns
                    break
                else:
                    if lowerNs in self.site().family.langs.keys():
                        # Interwiki link
                        t = m.group(2)

                        # Redundant interwiki prefix to the local wiki
                        if lowerNs == self.site().lang:
                            if t == '':
                                raise Error("Can't have an empty self-link")
                        else:
                            self._site = getSite(lowerNs, self.site().family.name)

                        # If there's an initial colon after the interwiki, that also
                        # resets the default namespace
                        if t != '' and t[0] == ':':
                            self._namespace = 0
                            t = t[1:]
                    elif lowerNs in self.site().family.known_families:
                        if self.site().family.known_families[lowerNs] == self.site().family.name:
                            t = m.group(2)
                        else:
                            # This page is from a different family
                            output(u"Target link '%s' has different family '%s'" % (title, lowerNs))
                            otherlang = self.site().lang
                            if lowerNs in ['commons']:
                                otherlang = lowerNs
                            familyName = self.site().family.known_families[lowerNs]
                            try:
                                self._site = getSite(otherlang, familyName)
                            except ValueError:
                                raise NoPage('%s is not a local page on %s, and the %s family is not supported by PyWikipediaBot!' % (title, self.site(), familyName))
                            t = m.group(2)
                    else:
                        # If there's no recognized interwiki or namespace,
                        # then let the colon expression be part of the title.
                        break
                continue

            sectionStart = t.find(u'#')
            if sectionStart >= 0:
                self._section = t[sectionStart+1:].strip()
                self._section = sectionencode(self._section, self.site().encoding())
                if self._section == u'': self._section = None          
                t = t[:sectionStart].strip()
            else:
                self._section = None

            if len(t) > 0:
                if not self.site().nocapitalize:
                    t = t[0].upper() + t[1:]
    #        else:
    #            output( u"DBG>>> Strange title: %s:%s" % (site.lang, title) )

            if self._namespace != 0:
                t = self.site().namespace(self._namespace) + u':' + t
                
            if self._section:
                t += u'#' + self._section
                
            self._title = t
            self.editRestriction = None
            self._permalink = None
            self._userName = None
            self._ipedit = None
            self._editTime = None
            self._deletedRevs = None
        except:
            print >>sys.stderr, "Exception in Page constructor"
            print >>sys.stderr, (
                "site=%s, title=%s, insite=%s, defaultNamespace=%i"
                % (site, title, insite, defaultNamespace)
            )
            raise

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
        title = self.title(underscore = True)
        encodedTitle = title.encode(self.site().encoding())
        return urllib.quote(encodedTitle)

    def title(self, underscore = False, savetitle = False):
        """The name of this Page, as a Unicode string"""
        title = self._title
        if savetitle: # Ensure there's no wiki syntax in the title
            if title.find("''") > -1:
                try:
                    title = urllib.quote(title).replace('%20',' ')
                except KeyError:
                    # We can't encode everything; to be on the safe side, we encode nothing
                    pass
        if underscore:
            title = title.replace(' ', '_')
        return title

    def titleWithoutNamespace(self, underscore = False):
        """
        Returns the name of the page without the namespace and without section.
        """
        if self.namespace() == 0:
            return self.title(underscore = underscore)
        else:
            return self.sectionFreeTitle(underscore = underscore).split(':', 1)[1]

    def section(self, underscore = False):
        """The name of the section this Page refers to. Sections are
           denominated by a # in the title(). If no section is referenced,
           None is returned."""
        return self._section
        # ln = self.title(underscore = underscore)
        # ln = re.sub('&#', '&hash;', ln)
        # if not '#' in ln:
            # return None
        # else:
            # hn = ln[ln.find('#') + 1:]
            # hn = re.sub('&hash;', '&#', hn)
            # return hn

    def sectionFreeTitle(self, underscore = False):
        sectionName = self.section(underscore = underscore)
        title = self.title(underscore = underscore)
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

    def aslink(self, forceInterwiki = False, textlink=False):
        """
        A string representation in the form of a link. The link will
        be an interwiki link if needed.

        If you set forceInterwiki to True, the link will have the format
        of an interwiki link even if it points to the home wiki.

        If you set textlink to True, the link will always appear in text
        form (that is, links to the Category: and Image: namespaces will
        be preceded by a : character).

        Note that the family is never included.
        """
        if forceInterwiki or self.site() != getSite():
            if self.site().family != getSite().family:
                return '[[%s:%s:%s]]' % (self.site().family.name, self.site().lang, self.title(savetitle=True))
            else:
                return '[[%s:%s]]' % (self.site().lang, self.title(savetitle=True))
        elif textlink and self.namespace() in (6, 14): # Image: or Category:
                return '[[:%s]]' % self.title()
        else:
            return '[[%s]]' % self.title()

    def isAutoTitle(self):
        """If the title is a well known, auto-translatable title
        """
        return self.autoFormat()[0] is not None

    def autoFormat(self):
        """Returns (dictName, value), where value can be a year, date, etc.,
           and dictName is 'YearBC', 'Year_December', or another dictionary name.
           Please note that two entries may have exactly the same autoFormat,
           but be in two different namespaces, as some sites have categories with the same names.
           Regular titles return (None,None)."""
        if not hasattr(self, '_autoFormat'):
            import date
            _autoFormat = date.getAutoFormat(self.site().language(), self.titleWithoutNamespace())
        return _autoFormat


    def get(self, force = False, get_redirect=False, throttle = True, sysop = False, nofollow_redirects=False, change_edit_time = True):
        """The wiki-text of the page. This will retrieve the page if it has not
           been retrieved yet. This can raise the following exceptions that
           should be caught by the calling code:

            NoPage: The page does not exist

            IsRedirectPage: The page is a redirect. The argument of the
                            exception is the title of the page it redirects to.

            SectionError: The subject does not exist on a page with a # link

            Set get_redirect to True to follow redirects rather than raise an exception.
            Set force to True to ignore all exceptions (including redirects).
            Set nofollow_redirects to True to not follow redirects but obey all other exceptions.
            Set change_version_date to False if you have already loaded the page before and
                do not check this version for changes before saving
        """
        # NOTE: The following few NoPage exceptions could already be thrown at
        # the Page() constructor. They are raised here instead for convenience,
        # because all scripts are prepared for NoPage exceptions raised by
        # get(), but not for such raised by the constructor.
        # \ufffd represents a badly encoded character, the other characters are
        # disallowed by MediaWiki.
        for illegalChar in ['#', '<', '>', '[', ']', '|', '{', '}', '\n', u'\ufffd']:
            if illegalChar in self.sectionFreeTitle():
                if verbose:
                    output(u'Illegal character in %s!' % self.aslink())
                raise NoPage('Illegal character in %s!' % self.aslink())
        if self.namespace() == -1:
            raise NoPage('%s is in the Special namespace!' % self.aslink())
        if self.site().isInterwikiLink(self.title()):
            raise NoPage('%s is not a local page on %s!' % (self.aslink(), self.site()))
        if force:
            # When forcing, we retry the page no matter what. Old exceptions
            # and contents do not apply any more.
            for attr in ['_redirarg','_getexception','_contents']:
                if hasattr(self, attr):
                    delattr(self,attr)
        else:
            # Make sure we re-raise an exception we got on an earlier attempt
            if hasattr(self, '_redirarg') and not get_redirect and not nofollow_redirects:
                raise IsRedirectPage, self._redirarg
            elif hasattr(self, '_getexception'):
                if self._getexception == IsRedirectPage and get_redirect:
                    pass
                elif self._getexception == IsRedirectPage and nofollow_redirects:
                    pass
                else:
                    raise self._getexception
        # Make sure we did try to get the contents once
        if not hasattr(self, '_contents'):
            try:
                self._contents, self._isWatched, self.editRestriction = self.getEditPage(get_redirect = get_redirect, throttle = throttle, sysop = sysop, nofollow_redirects=nofollow_redirects)
                hn = self.section()
                if hn:
                    m = re.search("=+ *%s *=+" % hn, self._contents)
                    if verbose and not m:
                        output(u"WARNING: Section does not exist: %s" % self.aslink(forceInterwiki = True))
                if self.site().lang == 'eo':
                    self._contents = resolveEsperantoXConvention(self._contents)
            # Store any exceptions for later reference
            except NoPage:
                self._getexception = NoPage
                raise
            except IsRedirectPage, arg:
                self._getexception = IsRedirectPage
                self._redirarg = arg
                if not get_redirect and not nofollow_redirects:
                    raise
            except SectionError:
                self._getexception = SectionError
                raise
        return self._contents

    def getEditPage(self, get_redirect=False, throttle = True, sysop = False, oldid = None, nofollow_redirects = False, change_edit_time = True):
        """
        Get the contents of the Page via the edit page.
        Do not use this directly, use get() instead.

        Arguments:
            get_redirect  - Get the contents, even if it is a redirect page

        This routine returns a unicode string containing the wiki text.
        """
        isWatched = False
        editRestriction = None
        if verbose:
            output(u'Getting page %s' % self.aslink())
        path = self.site().edit_address(self.urlname())
        if oldid:
            path = path + "&oldid="+oldid
        # Make sure Brion doesn't get angry by waiting if the last time a page
        # was retrieved was not long enough ago.
        if throttle:
            get_throttle()
        textareaFound = False
        retry_idle_time = 1
        while not textareaFound:
            text = self.site().getUrl(path, sysop = sysop)

            # Because language lists are filled in a lazy way in the family
            # files of Wikimedia projects (using Family.knownlanguages), you
            # may encounter pages from non-existing wikis such as
            # http://eo.wikisource.org/
            if text.find("<title>Wiki does not exist</title>") != -1:
                raise NoPage(u'Wiki %s does not exist yet' % self.site())

            #Check for new messages
            if '<div class="usermessage">' in text:
                self.site().messages=True
            else:
                self.site().messages=False
            # Extract the actual text from the textarea
            try:
                i1 = re.search('<textarea[^>]*>', text).end()
                i2 = re.search('</textarea>', text).start()
                textareaFound = True
            except AttributeError:
                # find out if the username or IP has been blocked
                if text.find(self.site().mediawiki_message('blockedtitle')) != -1:
                    raise UserBlocked(self.site(), self.aslink(forceInterwiki = True))
                # If there is no text area and the heading is 'View Source',
                # it is a non-existent page with a title protected via
                # cascading protection.
                # See http://en.wikipedia.org/wiki/Wikipedia:Protected_titles
                # and http://de.wikipedia.org/wiki/Wikipedia:Gesperrte_Lemmata
                elif text.find(self.site().mediawiki_message('viewsource')) != -1:
                    raise LockedNoPage(u'%s does not exist, and it is blocked via cascade protection.' % self.aslink())
                # search for 'Login required to edit' message
                elif text.find(self.site().mediawiki_message('whitelistedittitle')) != -1:
                    raise LockedNoPage(u'Page editing is forbidden for anonymous users.')
                # on wikipedia:en, anonymous users can't create new articles.
                # older MediaWiki versions don't have the 'nocreatetitle' message.
                elif self.site().has_mediawiki_message('nocreatetitle') and text.find(self.site().mediawiki_message('nocreatetitle')) != -1:
                    raise LockedNoPage(u'%s does not exist, and page creation is forbidden for anonymous users.' % self.aslink())
                elif text.find('var wgPageName = "Special:Badtitle";'):
                    raise BadTitle('BadTitle: %s' % self)
                else:
                    output( unicode(text) )
                    # We assume that the server is down. Wait some time, then try again.
                    output( u"WARNING: No text area found on %s%s. Maybe the server is down. Retrying in %i minutes..." % (self.site().hostname(), path, retry_idle_time) )
                    time.sleep(retry_idle_time * 60)
                    # Next time wait longer, but not longer than half an hour
                    retry_idle_time *= 2
                    if retry_idle_time > 30:
                        retry_idle_time = 30
        # We now know that there is a textarea.
        # Look for the edit token
        Rwatch = re.compile(r"\<input type='hidden' value=\"(.*?)\" name=\"wpEditToken\"")
        tokenloc = Rwatch.search(text)
        if tokenloc:
            self.site().putToken(tokenloc.group(1), sysop = sysop)
        elif not self.site().getToken(getalways = False):
            self.site().putToken('', sysop = sysop)
        if change_edit_time:
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
        # Find out if page actually exists. Only existing pages have a
        # version history tab.
        if self.site().family.RversionTab(self.site().language()):
            # In case a family does not have version history tabs, or in
            # another form
            RversionTab = re.compile(self.site().family.RversionTab(self.site().language()))
        else:
            RversionTab = re.compile(r'<li id="ca-history"><a href=".*?title=.*?&amp;action=history".*?>.*?</a></li>')
        matchVersionTab = RversionTab.search(text)
        if not matchVersionTab:
            raise NoPage(self.site(), self.aslink(forceInterwiki = True))
        # Look if the page is on our watchlist
        R = re.compile(r"\<input tabindex='[\d]+' type='checkbox' name='wpWatchthis' checked='checked'")
        matchWatching = R.search(text)
        if matchWatching:
            isWatched = True
        # Now process the contents of the textarea
        m = self.site().redirectRegex().match(text[i1:i2])
        if self._editTime == "0":
            if verbose:
                output(u"DBG> page may be locked?!")
            editRestriction = 'sysop'
        if m:
            if self.section():
                redirtarget = "%s#%s"%(m.group(1),self.section())
            else:
                redirtarget = m.group(1)
            if get_redirect:
                self._redirarg = redirtarget
            elif not nofollow_redirects:
                raise IsRedirectPage(redirtarget)
        if self.section():
            # TODO: What the hell is this? Docu please.
            m = re.search("\.3D\_*(\.27\.27+)?(\.5B\.5B)?\_*%s\_*(\.5B\.5B)?(\.27\.27+)?\_*\.3D" % re.escape(self.section()), sectionencode(text,self.site().encoding()))
            if not m:
                try:
                    self._getexception
                except AttributeError:
                    raise SectionError # Page has no section by this name
        x = text[i1:i2]
        x = unescape(x)
        while x and x[-1] in '\n ':
            x = x[:-1]

        return x, isWatched, editRestriction

    def permalink(self):
        """
        Get the permalink page for this page
        """
        return "%s://%s%s&oldid=%i"%(self.site().protocol, self.site().hostname(), self.site().get_address(self.title()), self.latestRevision())
    
    def latestRevision(self):
        """
        Get the latest revision for this page
        """
        if not self._permalink:
            # When we get the page with getall, the permalink is received automatically
            getall(self.site(),[self,],force=True)
        return int(self._permalink)

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
        except SectionError:
            return False
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

    def isTalkPage(self):
        ns = self.namespace()
        return ns >= 0 and ns % 2 == 1

    def botMayEdit(self):
        """
        True if page doesn't contain {{bots}} or {{nobots}} or
        contains them and active bot is allowed or not allowed
        to edit said page

        Note that the framework does not enforce this restriction; if it
        is desired to implement authorization-checking for a particular
        bot, the bot must call this method before editing.
        """
        import re;
        p = re.compile(r"\{\{(?P<type>bots|nobots)\|?(?P<data>.*?)\}\}")
        try:
            txt = self.get(force=True);
        except (NoPage, IsRedirectPage):
            return True

        m = p.search(txt);
        
        if m == None:
            return True

        if m.group('data') == '':
            if m.group('type') == 'bots':
                return True
            return False

        p = re.compile(r"(?P<type>allow|deny)=(?P<bots>.*)")
        n = p.search(m.group('data'))
        listed_bots = n.group('bots').split(',')
        restriction_type = n.group('type')

        if self.editRestriction:
            userdict = config.sysopnames
        else:
            userdict = config.usernames

        try:
            this_bot = userdict[self.site().family.name][self.site().lang]
            if restriction_type == 'allow':
                if this_bot in listed_bots:
                    return True
                elif 'all' in listed_bots:
                    return True
                elif 'none' in listed_bots:
                    return False
                else:
                    return False
            elif restriction_type == 'deny':
                if this_bot in listed_bots:
                    return False
                elif 'all' in listed_bots:
                    return False
                elif 'none' in listed_bots:
                    return True
                else:
                    return True

        except :
            # We don't have a user account for that wiki, or the
            # page is locked and we don't have a sysop account.
            return False

    def userName(self):
        return self._userName
        
    def isIpEdit(self):
        return self._ipedit

    def editTime(self):
        return self._editTime

    def namespace(self):
        """Gives the number of the namespace of the page. Does not work for
           all namespaces in all languages, only when defined in family.py.
           If not defined, it will return 0 (the main namespace)"""
        return self._namespace
        # t=self.sectionFreeTitle()
        # p=t.split(':')
        # if p[1:]==[]:
            # return 0
        # for namespaceNumber in self.site().family.namespaces.iterkeys():
            # if p[0]==self.site().namespace(namespaceNumber):
                # return namespaceNumber
        # return 0

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
            locdis = self.site().family.disambig( self._site.lang )

            for tn in self.templates():
                try:
                    tn = tn[0].upper() + tn[1:]
                except IndexError:
                    # len(tn) < 2
                    tn = tn.upper()
                tn = tn.replace('_', ' ')
                if tn in locdis:
                    _isDisambig = True
                    break
            else:
                _isDisambig = False
        return _isDisambig

    def getReferences(self,
            follow_redirects=True, withTemplateInclusion=True,
            onlyTemplateInclusion=False, redirectsOnly=False):
        """
        Yield all pages that link to the page. If you need a full list of
        referring pages, use this:

            pages = [page for page in s.getReferences()]

        Parameters:
        * follow_redirects      - if True, also returns pages that link to a
                                  redirect pointing to the page.
        * withTemplateInclusion - if True, also returns pages where self is
                                  used as a template.
        * onlyTemplateInclusion - if True, only returns pages where self is
                                  used as a template.
        * redirectsOnly         - if True, only returns redirects to self.
        """
        # Temporary bug-fix while researching more robust solution:
        if config.special_page_limit > 999:
            config.special_page_limit = 999
        site = self.site()
        path = self.site().references_address(self.urlname())
        content = SoupStrainer("div", id=self.site().family.content_id)
        try:
            next_msg = self.site().mediawiki_message('whatlinkshere-next')
        except KeyError:
            next_msg = "next %i" % config.special_page_limit
        plural = (config.special_page_limit == 1) and "\\1" or "\\2"
        next_msg = re.sub(r"{{PLURAL:\$1\|(.*?)\|(.*?)}}", plural, next_msg)
        nextpattern = re.compile("^%s$" % next_msg.replace("$1", "[0-9]+"))
        delay = 1
        self._isredirectmessage = self.site().mediawiki_message("Isredirect")
        if self.site().has_mediawiki_message("Istemplate"):
            self._istemplatemessage = self.site().mediawiki_message("Istemplate")
        # to avoid duplicates:
        refPages = set()
        while path:
            output(u'Getting references to %s' % self.aslink())
            get_throttle()
            txt = self.site().getUrl(path)
            body = BeautifulSoup(txt,
                                 convertEntities=BeautifulSoup.HTML_ENTITIES,
                                 parseOnlyThese=content)
            next_text = body.find(text=nextpattern)
            if next_text is not None:
                path = next_text.parent['href'].replace("&amp;", "&")
            else:
                path = ""
            reflist = body.find("ul")
            if reflist is None:
                return
            for page in self._parse_reflist(reflist,
                                follow_redirects, withTemplateInclusion,
                                onlyTemplateInclusion, redirectsOnly):
                if page not in refPages:
                    yield page
                    refPages.add(page)

    def _parse_reflist(self, reflist,
            follow_redirects=True, withTemplateInclusion=True,
            onlyTemplateInclusion=False, redirectsOnly=False):
        """
        For internal use only

        Parse a "Special:Whatlinkshere" list of references and yield Page
        objects that meet the criteria
        (used by getReferences)
        """
        for link in reflist("li", recursive=False):
            title = link.a.string
            if title is None:
                output("DBG> invalid <li> item in Whatlinkshere: %s" % link)
            p = Page(self.site(), title)
            isredirect, istemplate = False, False
            textafter = link.a.findNextSibling(text=True)
            if textafter is not None:
                if self._isredirectmessage in textafter:
                    # make sure this is really a redirect to this page
                    # (MediaWiki will mark as a redirect any link that follows
                    # a #REDIRECT marker, not just the first one).
                    if Page(self.site(), p.getRedirectTarget()
                            ).sectionFreeTitle() == self.sectionFreeTitle():
                        isredirect = True
                if self.site().has_mediawiki_message("Istemplate") \
                        and self._istemplatemessage in textafter:
                    istemplate = True

            if (withTemplateInclusion or onlyTemplateInclusion or not istemplate
                    ) and (not redirectsOnly or isredirect
                    ) and (not onlyTemplateInclusion or istemplate
                    ):
                yield p

            if isredirect and follow_redirects:
                sublist = link.find("ul")
                if sublist is not None:
                    for p in self._parse_reflist(sublist,
                                follow_redirects, withTemplateInclusion,
                                onlyTemplateInclusion, redirectsOnly):
                        yield p


    def getFileLinks(self):
        """
        Yield all pages that link to the page. If you need a full list of
        referring pages, use this:

            pages = [page for page in s.getReferences()]

        """
        site = self.site()
        #path = site.references_address(self.urlname())
        path = site.get_address(self.urlname())

        delay = 1

        # NOTE: this code relies on the way MediaWiki 1.6 formats the
        #       "Whatlinkshere" special page; if future versions change the
        #       format, they may break this code.
        if self.site().versionnumber() >= 5:
            startmarker = u"<!-- start content -->"
            endmarker = u"<!-- end content -->"
        else:
            startmarker = u"<body "
            endmarker = "printfooter"
        listitempattern = re.compile(r"<li><a href=.*>(?P<title>.*)</a></li>")
        # to tell the previous and next link apart, we rely on the closing ) at the end of the "previous" label.
        more = True

        while more:
            more = False #Kill after one loop because MediaWiki will only display up to the first 500 File links.
            fileLinks = set()  # use a set to avoid duplications
            output(u'Getting references to %s' % self.aslink())
            while True:
                txt = site.getUrl(path)
                # trim irrelevant portions of page
                try:
                    start = txt.index(startmarker) + len(startmarker)
                    end = txt.index(endmarker)
                except ValueError:
                    output(u"Invalid page received from server.... Retrying in %i minutes." % delay)
                    time.sleep(delay * 60.)
                    delay *= 2
                    if delay > 30:
                        delay = 30
                    continue
                txt = txt[start:end]
                break
            try:
                start = txt.index(u"<ul>")
                end = txt.rindex(u"</ul>")
            except ValueError:
                # No incoming links found on page
                continue
            txt = txt[start:end+5]

            txtlines = txt.split(u"\n")
            for num, line in enumerate(txtlines):
                if line == u"</ul>":
                    # end of list of references to redirect page
                    continue
                if line == u"</li>":
                    continue
                lmatch = listitempattern.search(line)
                if lmatch:
                    fileLinks.add(lmatch.group("title"))
                    if lmatch is None:
                        output(u"DBG> Unparsed line:")
                        output(u"(%i) %s" % (num, line))
            fileLinks = list(fileLinks)
            fileLinks.sort()
            for fileLink in fileLinks:
                # create Page objects
                yield Page(site, fileLink)

    def put_async(self, newtext,
                  comment=None, watchArticle=None, minorEdit=True, force=False):
        """Asynchronous version of put (takes the same arguments), which
           places pages on a queue to be saved by a daemon thread.
        """
        page_put_queue.put((self, newtext, comment, watchArticle, minorEdit, force))

    def put(self, newtext, comment=None, watchArticle = None, minorEdit = True, force=False):
        """Replace the new page with the contents of the first argument.
           The second argument is a string that is to be used as the
           summary for the modification

           If watchArticle is None, leaves the watchlist status unchanged.
        """
        # Fetch a page to get an edit token. If we already have
        # fetched a page, this will do nothing, because get() is cached.
        # Disabled in r4027
        #try:
        #    self.site().sandboxpage.get(force = True, get_redirect = True)
        #except NoPage:
        #    pass

        # Determine if we are allowed to edit
        if not force:
            if not self.botMayEdit():
                raise LockedPage(u'Not allowed to edit %s because of a restricting template' % self.aslink())

        # If there is an unchecked edit restriction, we need to load the page
        if self._editrestriction:
            output(u'Page %s is semi-protected. Getting edit page to find out if we are allowed to edit.' % self.aslink())
            self.get(force = True, change_edit_time = False)
            self._editrestriction = False
        # If no comment is given for the change, use the default
        comment = comment or action
        if self.editRestriction:
            try:
                self.site().forceLogin(sysop = True)
                output(u'Page is locked, using sysop account.')
            except NoUsername:
                raise LockedPage()
        else:
            self.site().forceLogin()
        if config.cosmetic_changes and not self.isTalkPage():
            old = newtext
            if not config.cosmetic_changes_mylang_only or (self.site().family.name == config.family and self.site().lang == config.mylang):
                import cosmetic_changes
                ccToolkit = cosmetic_changes.CosmeticChangesToolkit(self.site())
                newtext = ccToolkit.change(newtext)
                if comment and old.strip() != newtext.strip():
                    comment += translate(self.site(), cosmetic_changes.msg_append)

        if watchArticle == None:
            # if the page was loaded via get(), we know its status
            if hasattr(self, '_isWatched'):
                watchArticle = self._isWatched
            else:
                import watchlist
                watchArticle = watchlist.isWatched(self.title(), site = self.site())
        newPage = not self.exists()
        sysop = not not self.editRestriction
        # If we are a sysop, we need to re-obtain the tokens.
        if sysop:
            if hasattr(self, '_contents'): del self._contents
            try:
                self.get(force = True, get_redirect = True,
                    change_edit_time = True, sysop = True)
            except NoPage:
                pass


        # if posting to an Esperanto wiki, we must e.g. write Bordeauxx instead
        # of Bordeaux
        if self.site().lang == 'eo':
            newtext = doubleXForEsperanto(newtext)
        return self.putPage(newtext, comment, watchArticle, minorEdit, newPage, self.site().getToken(sysop = sysop), sysop = sysop)

    def putPage(self, text, comment=None, watchArticle=False, minorEdit=True,
                newPage=False, token=None, gettoken=False, sysop=False):
        """
        Upload 'text' as new contents for this Page by filling out the edit
        page.

        Don't use this directly, use put() instead.
        """

        newTokenRetrieved = False
        if self.site().versionnumber() >= 4:
            if gettoken or not token:
                token = self.site().getToken(getagain = gettoken, sysop = sysop)
                newTokenRetrieved = True

        # Check whether we are not too quickly after the previous putPage, and
        # wait a bit until the interval is acceptable
        put_throttle()
        # Which web-site host are we submitting to?
        host = self.site().hostname()
        # Get the address of the page on that host.
        address = self.site().put_address(self.urlname())
        # Use the proper encoding for the comment
        encodedComment = comment.encode(self.site().encoding())
        # Encode the text into the right encoding for the wiki
        encodedText = text.encode(self.site().encoding())
        predata = {
            'wpSave': '1',
            'wpSummary': encodedComment,
            'wpTextbox1': encodedText,
        }
        # Add server lag parameter (see config.py for details)
        if config.maxlag:
            predata['maxlag'] = str(config.maxlag)
        # Except if the page is new, we need to supply the time of the
        # previous version to the wiki to prevent edit collisions
        if newPage:
            predata['wpEdittime'] = ''
            predata['wpStarttime'] = ''
        else:
            predata['wpEdittime'] = self._editTime
            predata['wpStarttime'] = self._startTime
        # Pass the minorEdit and watchArticle arguments to the Wiki.
        if minorEdit:
            predata['wpMinoredit'] = '1'
        if watchArticle:
            predata['wpWatchthis'] = '1'
        # Give the token, but only if one is supplied.
        if token:
            predata['wpEditToken'] = token

        # Sorry, single-site exception...
        if self.site().fam().name == 'loveto' and self.site().language() == 'recipes':
            predata['masteredit'] = '1'

        if newPage:
            output(u'Creating page %s' % self.aslink(forceInterwiki=True))
        else:
            output(u'Changing page %s' % self.aslink(forceInterwiki=True))
        # Submit the prepared information
        if self.site().hostname() in config.authenticate.keys():
            predata.append(("Content-type","application/x-www-form-urlencoded"))
            predata.append(("User-agent", useragent))
            data = self.site().urlEncode(predata)
            response = urllib2.urlopen(urllib2.Request(self.site().protocol() + '://' + self.site().hostname() + address, data))
            # I'm not sure what to check in this case, so I just assume things went ok.
            # Very naive, I agree.
            data = u''
        else:
            try:
                response, data = self.site().postForm(address, predata, sysop)
            except httplib.BadStatusLine, line:
                raise PageNotSaved('Bad status line: %s' % line.line)
        if data != u'':
            # Saving unsuccessful. Possible reasons:
            # server lag, edit conflict or invalid edit token.
            # A second text area means that an edit conflict has occured.
            if response.status == 503 \
               and 'x-database-lag' in response.msg.keys():
                # server lag; Mediawiki recommends waiting 5 seconds and retrying
                if verbose:
                    output(data, newline=False)
                output(u"Pausing 5 seconds due to excessive database server lag.")
                time.sleep(5)
                return self.putPage(text, comment, watchArticle, minorEdit,
                                    newPage, token, False, sysop)
            if 'id=\'wpTextbox2\' name="wpTextbox2"' in data:
                raise EditConflict(u'An edit conflict has occured.')
            elif self.site().has_mediawiki_message("spamprotectiontitle")\
                    and self.site().mediawiki_message('spamprotectiontitle') in data:
                try:
                    reasonR = re.compile(re.escape(self.site().mediawiki_message('spamprotectionmatch')).replace('\$1', '(?P<url>[^<]*)'))
                    url = reasonR.search(data).group('url')
                except:
                    # Some wikis have modified the spamprotectionmatch
                    # template in a way that the above regex doesn't work,
                    # e.g. on he.wikipedia the template includes a wikilink,
                    # and on fr.wikipedia there is bold text.
                    # This is a workaround for this: it takes the region
                    # which should contain the spamfilter report and the URL.
                    # It then searches for a plaintext URL.
                    relevant = data[data.find('<!-- start content -->')+22:data.find('<!-- end content -->')].strip()
                    # Throw away all the other links etc.
                    relevant = re.sub('<.*?>', '', relevant)
                    # MediaWiki only spam-checks HTTP links, and only the
                    # domain name part of the URL.
                    m = re.search('http://[\w\-\.]+', relevant)
                    if m:
                        url = m.group()
                    else:
                        # Can't extract the exact URL. Let the user search.
                        url = relevant
                raise SpamfilterError(url)
            elif '<label for=\'wpRecreate\'' in data:
                # Make sure your system clock is correct if this error occurs
                # without any reason!
                raise EditConflict(u'Someone deleted the page.')
            elif self.site().has_mediawiki_message("viewsource")\
                    and self.site().mediawiki_message('viewsource') in data:
                # The page is locked. This should have already been detected
                # when getting the page, but there are some reasons why this
                # didn't work, e.g. the page might be locked via a cascade
                # lock.
                # We won't raise a LockedPage exception here because these
                # exceptions are usually already raised when getting pages,
                # not when putting them, and it would be too much work at this
                # moment to rewrite all scripts. Maybe we can later create
                # two different lock exceptions, one for getting and one for
                # putting.
                try:
                    # Page is restricted - try using the sysop account, unless we're using one already
                    if not sysop:
                        self.site().forceLogin(sysop = True)
                        output(u'Page is locked, retrying using sysop account.')
                        return self.putPage(text, comment, watchArticle,
                                            minorEdit, newPage, token=None,
                                            gettoken=True, sysop=True)
                except NoUsername:
                    raise PageNotSaved(u"The page %s is locked. Possible reasons: There is a cascade lock, or you're affected by this MediaWiki bug: http://bugzilla.wikimedia.org/show_bug.cgi?id=9226" % self.aslink())
            elif not newTokenRetrieved and "<textarea" in data:
                # We might have been using an outdated token
                output(u"Changing page has failed. Retrying.")
                return self.putPage(text = text, comment = comment,
                        watchArticle = watchArticle, minorEdit = minorEdit, newPage = newPage,
                        token = None, gettoken = True, sysop = sysop)
            else:
                # Something went wrong, and we don't know what. Show the
                # HTML code that hopefully includes some error message.
                output(data)
        if self.site().hostname() in config.authenticate.keys():
            # No idea how to get the info now.
            return None
        else:
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

    def toggleTalkPage(self):
        """
        If self is a talk page, returns the associated content page; otherwise,
        returns the associated talk page. Returns None if self is a special
        page.
        """
        ns = self.namespace()
        if ns < 0: # Special page
            return None
        if self.isTalkPage():
            if self.namespace() == 1:
                return Page(self.site(), self.titleWithoutNamespace())
            else:
                return Page(self.site(), self.site().namespace(ns - 1) + ':' + self.titleWithoutNamespace())
        else:
            return Page(self.site(), self.site().namespace(ns + 1) + ':' + self.titleWithoutNamespace())

    def interwiki(self):
        """A list of interwiki links in the page. This will retrieve
           the page text to do its work, so it can raise the same exceptions
           that are raised by the get() method.

           The return value is a list of Page objects for each of the
           interwiki links in the page text.
        """
        result = []
        ll = getLanguageLinks(self.get(), insite = self.site(), pageLink = self.aslink())
        for newSite, newPage in ll.iteritems():
            for pagenametext in self.site().family.pagenamecodes(self.site().language()):
                newTitle = newPage.title().replace("{{" + pagenametext + "}}", self.title())
            try:
                result.append(self.__class__(newSite, newTitle, insite = self.site()))
            except UnicodeError:
                output(u"ERROR: link from %s to [[%s:%s]] is invalid encoding?!" % (self.aslink(), newSite, newTitle))
            except NoSuchEntity:
                output(u"ERROR: link from %s to [[%s:%s]] contains invalid character?!" % (self.aslink(), newSite, newTitle))
            except ValueError:
                output(u"ERROR: link from %s to [[%s:%s]] contains invalid unicode reference?!" % (self.aslink(), newSite, newTitle))
        return result

    def categories(self, nofollow_redirects=False):
        """
        A list of categories that the article is in. This will retrieve
        the page text to do its work, so it can raise the same exceptions
        that are raised by the get() method.

        The return value is a list of Category objects, one for each of the
        category links in the page text.
        """
        return getCategoryLinks(self.get(nofollow_redirects=nofollow_redirects), self.site())

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
            thistxt = removeLanguageLinks(self.get(get_redirect=True), self.site())
        except NoPage:
            raise
            #return []
        except IsRedirectPage:
            raise
        except SectionError:
            return []
        thistxt = removeCategoryLinks(thistxt, self.site())

        # remove HTML comments, nowiki sections, and includeonly sections
        # from text before processing
        thistxt = removeDisabledParts(thistxt)

        Rlink = re.compile(r'\[\[(?P<title>[^\]\|]*)(\|[^\]]*)?\]\]')
        for match in Rlink.finditer(thistxt):
            title = match.group('title')
            if title.strip().startswith("#"):
                # this is an internal section link
                continue
            if not self.site().isInterwikiLink(title):
                try:
                    page = Page(self.site(), title)
                except:
                    continue
                if page.sectionFreeTitle():
                    result.append(page)
        return result

    def imagelinks(self, followRedirects = False, loose = False):
        """
        Gives the images the page shows, as a list of ImagePage objects.
        This includes images in galleries.
        If loose is set to true, this will find anything that looks like it could be an image.
        This is useful for finding, say, images that are passed as parameters to templates.
        """
        results = []
        # Find normal images
        for page in self.linkedPages():
            if page.isImage():
                # convert Page object to ImagePage object
                imagePage = ImagePage(page.site(), page.title())
                results.append(imagePage)
        # Find images in galleries
        pageText = self.get(get_redirect=followRedirects)
        galleryR = re.compile('<gallery>.*?</gallery>', re.DOTALL)
        galleryEntryR = re.compile('(?P<title>(%s|%s):.+?)(\|.+)?\n' % (self.site().image_namespace(), self.site().family.image_namespace(code = '_default')))
        for gallery in galleryR.findall(pageText):
            for match in galleryEntryR.finditer(gallery):
                page = ImagePage(self.site(), match.group('title'))
                results.append(page)
        if loose:
            ns = getSite().image_namespace()
            imageR = re.compile('\w\w\w+\.(?:gif|png|jpg|jpeg|svg)', re.IGNORECASE)
            for imageName in imageR.findall(pageText):
                results.append(ImagePage(self.site(), ns + ':' + imageName))
        return set(results)

    def templates(self):
        """
        Gives a list of template names used on a page, as a list of strings.
        Template parameters are ignored.
        """
        return [template for (template, param) in self.templatesWithParams()]

    def templatesWithParams(self):
        """
        Gives a list of tuples. There is one tuple for each use of a template
        in the page, with the template name as the first entry and a list
        of parameters as the second entry.
        """
        try:
            thistxt = self.get()
        except (IsRedirectPage, NoPage):
            return []

        # remove commented-out stuff etc.
        thistxt  = removeDisabledParts(thistxt)

        result = []
        Rtemplate = re.compile(r'{{(msg:)?(?P<name>[^{\|]+?)(\|(?P<params>.+?))?}}', re.DOTALL)
        for m in Rtemplate.finditer(thistxt):
            paramString = m.group('params')
            params = []
            if paramString:
                params = paramString.split('|')
            name = m.group('name')
            if self.site().isInterwikiLink(name):
                continue
            name = Page(self.site(), name).title()
            result.append((name, params))
        return result
        
    def templatePages(self):
        """
        Gives a list of Page objects containing the templates used on the page. Template parameters are ignored.
        """
        return [Page(self.site(), template, self.site(), 10) for template in self.templates()]

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

    def getPreviousVersion(self):
        vh = self.getVersionHistory(revCount=2)
        oldid = vh[1][0]
        return self.getEditPage(oldid=oldid)[0]

    def getVersionHistory(self, forceReload = False, reverseOrder = False, getAll = False, revCount = 500):
        """
        Loads the version history page and returns a list of tuples, where each
        tuple represents one edit and is built of edit date/time, user name, and edit
        summary.  Defaults to getting the first revCount edits.
        """
        site = self.site()

        # regular expression matching one edit in the version history.
        # results will have 4 groups: oldid, edit date/time, user name, and edit
        # summary.
        if self.site().versionnumber() < 4:
            editR = re.compile('<li>.*?<a href=".*?oldid=([0-9]*)" title=".*?">([^<]*)</a> <span class=\'user\'><a href=".*?" title=".*?">([^<]*?)</a></span>.*?(?:<span class=\'comment\'>(.*?)</span>)?</li>')
        else:
            editR = re.compile('<li>.*?<a href=".*?oldid=([0-9]*)" title=".*?">([^<]*)</a> <span class=\'history-user\'><a href=".*?" title=".*?">([^<]*?)</a>.*?</span>.*?(?:<span class=[\'"]comment[\'"]>(.*?)</span>)?</li>')

        startFromPage = None
        thisHistoryDone = False
        skip = False # Used in determining whether we need to skip the first page

        RLinkToNextPage = re.compile('&amp;offset=(.*?)&amp;')

        # Are we getting by Earliest first?
        if reverseOrder:
            # Check if _versionhistoryearliest exists
            if not hasattr(self, '_versionhistoryearliest') or forceReload:
                self._versionhistoryearliest = []
            elif getAll and len(self._versionhistoryearliest) == revCount:
                # Cause a reload, or at least make the loop run
                thisHistoryDone = False
                skip = True
            else:
                thisHistoryDone = True
        elif not hasattr(self, '_versionhistory') or forceReload:
            self._versionhistory = []
        elif getAll and len(self._versionhistory) == revCount:
            # Cause a reload, or at least make the loop run
            thisHistoryDone = False
            skip = True
        else:
            thisHistoryDone = True

        while not thisHistoryDone:
            path = site.family.version_history_address(self.site().language(), self.urlname(), revCount)

            if reverseOrder:
                if len(self._versionhistoryearliest) >= revCount:
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

            if verbose:
                if startFromPage:
                    output(u'Continuing to get version history of %s' % self.aslink(forceInterwiki = True))
                else:
                    output(u'Getting version history of %s' % self.aslink(forceInterwiki = True))

            txt = site.getUrl(path)

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
                        if len(edits) < revCount:
                            thisHistoryDone = True
                    else:
                        if not skip:
                            edits = editR.findall(self_txt)
                            edits.reverse()
                            for edit in edits:
                                self._versionhistoryearliest.append(edit)
                            if len(edits) < revCount:
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
                        if len(edits) < revCount:
                            thisHistoryDone = True
                    else:
                        if not skip:
                            edits = editR.findall(self_txt)
                            for edit in edits:
                                self._versionhistory.append(edit)
                            if len(edits) < revCount:
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
            # Return only revCount edits, even if the version history is extensive
            if len(self._versionhistoryearliest) > revCount and not getAll:
                return self._versionhistoryearliest[0:revCount]
            return self._versionhistoryearliest

        # Return only revCount edits, even if the version history is extensive
        if len(self._versionhistory) > revCount and not getAll:
            return self._versionhistory[0:revCount]
        return self._versionhistory

    def getVersionHistoryTable(self, forceReload = False, reverseOrder = False, getAll = False, revCount = 500):
        """
        Returns the version history as a wiki table.
        """
        result = '{| border="1"\n'
        result += '! oldid || date/time || username || edit summary\n'
        for oldid, time, username, summary in self.getVersionHistory(forceReload = forceReload, reverseOrder = reverseOrder, getAll = getAll, revCount = revCount):
            result += '|----\n'
            result += '| %s || %s || %s || <nowiki>%s</nowiki>\n' % (oldid, time, username, summary)
        result += '|}\n'
        return result

    def fullVersionHistory(self, max = 50, comment = False, since = None):
        """
        Returns all previous versions. Gives a list of tuples consisting of
        edit date/time, user name and content
        """
        RV_LIMIT = 50

        address = self.site().api_address()
        predata = {
            'action': 'query',
            'prop': 'revisions',
            'titles': self.title(),
            'rvprop': 'timestamp|user|comment|content',
            'rvlimit': str(RV_LIMIT),
            'format': 'json'
        }
        if max < RV_LIMIT: predata['rvlimit'] = str(max)
        if since: predata['rvend'] = since

        get_throttle(requestsize = 10)
        now = time.time()

        count = 0
        output = []    

        while count < max and max != -1:
            if self.site().hostname() in config.authenticate.keys():
                predata["Content-type"] = "application/x-www-form-urlencoded"
                predata["User-agent"] = useragent
                data = self.site.urlEncode(predata)
                response = urllib2.urlopen(urllib2.Request(self.site.protocol() + '://' + self.site.hostname() + address, data))
                data = response.read().decode(self.site().encoding())
            else:
                response, data = self.site().postForm(address, predata)
        
            get_throttle.setDelay(time.time() - now)
            data = simplejson.loads(data)
            page = data['query']['pages'].values()[0]        
            if 'missing' in page:
                raise NoPage, 'Page %s not found' % self
            revisions = page.get('revisions', ())
            for revision in revisions:
                if not comment:
                    output.append((revision['timestamp'], 
                      revision['user'], revision.get('*', u'')))
                else:
                    output.append((revision['timestamp'], revision['user'],
                      revision.get('*', u''), revision.get('comment', u'')))
            count += len(revisions)
            if max - count < RV_LIMIT:
                predata['rvlimit'] = str(max - count)
            if 'query-continue' in data:
                predata['rvstartid'] = str(data['query-continue']['revisions']['rvstartid'])
            else:
                break
        return output
    fullRevisionHistory = fullVersionHistory
                       
    def contributingUsers(self):
        """
        Returns a set of all user names (including anonymous IPs) of those who
        edited the page.
        """
        edits = self.getVersionHistory()
        users = set()
        for edit in edits:
            users.add(edit[2])
        return users

    def move(self, newtitle, reason = None, movetalkpage = True, sysop = False, throttle = False):
        if throttle:
            put_throttle()
        if reason == None:
            reason = "Pagemove by bot"
        if self.namespace() // 2 == 1:
            movetalkpage = False
        host = self.site().hostname()
        address = self.site().move_address()
        self.site().forceLogin(sysop = sysop)
        token = self.site().getToken(self, sysop = sysop)
        predata = {
            'wpOldTitle': self.title().encode(self.site().encoding()),
            'wpNewTitle': newtitle.encode(self.site().encoding()),
            'wpReason': reason.encode(self.site().encoding()),
        }
        if movetalkpage:
            predata['wpMovetalk'] = '1'
        else:
            predata['wpMovetalk'] = '0'
        if token:
            predata['wpEditToken'] = token
        if self.site().hostname() in config.authenticate.keys():
            predata['Content-type'] = 'application/x-www-form-urlencoded'
            predata['User-agent'] = useragent
            data = self.site().urlEncode(predata)
            response = urllib2.urlopen(urllib2.Request(self.site().protocol() + '://' + self.site().hostname() + address, data))
            data = ''
        else:
            response, data = self.site().postForm(address, predata, sysop = sysop)
        if data != u'':
            if self.site().mediawiki_message('pagemovedsub') in data:
                output(u'Page %s moved to %s' % (self.title(), newtitle))
                return True
            else:
                output(u'Page move failed.')
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

    def delete(self, reason = None, prompt = True, throttle = False):
        """Deletes the page from the wiki. Requires administrator status. If
           reason is None, asks for a reason. If prompt is True, asks the user
           if he wants to delete the page.
        """
        if throttle:
            put_throttle()
        if reason == None:
            reason = input(u'Please enter a reason for the deletion:')
        reason = reason.encode(self.site().encoding())
        answer = 'y'
        if prompt:
            answer = inputChoice(u'Do you want to delete %s?' % self.aslink(forceInterwiki = True), ['Yes', 'No'], ['y', 'N'], 'N')
        if answer in ['y', 'Y']:
            host = self.site().hostname()
            address = self.site().delete_address(self.urlname())

            try:
                self.site().forceLogin(sysop = True)
            except NoUsername, error:
                # user hasn't entered an admin username.
                output(str(error))
                return
            token = self.site().getToken(self, sysop = True)
            predata = {
                'wpReason': reason,
                'wpConfirm': '1',
                'wpConfirmB': '1'
            }
            if token:
                predata['wpEditToken'] = token
            if self.site().hostname() in config.authenticate.keys():
                predata['Content-type'] = 'application/x-www-form-urlencoded'
                predata['User-agent'] = useragent
                data = self.site().urlEncode(predata)
                response = urllib2.urlopen(urllib2.Request(self.site().protocol() + '://' + self.site().hostname() + address, data))
                data = u''
            else:
                response, data = self.site().postForm(address, predata, sysop = True)
            if data:
                if self.site().mediawiki_message('actioncomplete') in data:
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

    def loadDeletedRevisions(self):
        """Loads up Special/Undelete for the page and stores all revisions'
           timestamps, dates, editors and comments.
           Returns list of timestamps (which are used to refer to revisions later on).
        """
        #TODO: Handle image file revisions too.
        output(u'Loading list of deleted revisions for [[%s]]...' % self.title())

        address = self.site().undelete_view_address(self.urlname())
        self.site().forceLogin(sysop = True)
        text = self.site().getUrl(address, sysop = True)
        #TODO: Handle non-existent pages etc

        rxRevs = re.compile(r'<input name="(?P<ts>(?:ts|fileid)\d+)".*?title=".*?">(?P<date>.*?)</a>.*?title=".*?">(?P<editor>.*?)</a>.*?<span class="comment">\((?P<comment>.*?)\)</span>',re.DOTALL)
        self._deletedRevs = {}
        for rev in rxRevs.finditer(text):
            self._deletedRevs[rev.group('ts')] = [
                    rev.group('date'),
                    rev.group('editor'),
                    rev.group('comment'),
                    None,  #Revision text
                    False, #Restoration marker
                    ]

        self._deletedRevsModified = False
        return self._deletedRevs.keys()

    def getDeletedRevision(self, timestamp, retrieveText=False):
        """Returns a deleted revision [date, editor, comment, text, restoration marker].
           text will be None, unless retrieveText is True (or has been retrieved earlier).
        """
        if self._deletedRevs == None:
            self.loadDeletedRevisions()
        if not self._deletedRevs.has_key(timestamp):
            #TODO: Throw an exception instead?
            return None

        if retrieveText and not self._deletedRevs[timestamp][3] and timestamp[:2]=='ts':
            output(u'Retrieving text of deleted revision...')
            address = self.site().undelete_view_address(self.urlname(),timestamp)
            self.site().forceLogin(sysop = True)
            text = self.site().getUrl(address, sysop = True)
            und = re.search('<textarea readonly="1" cols="80" rows="25">(.*?)</textarea><div><form method="post"',text,re.DOTALL)
            if und:
                self._deletedRevs[timestamp][3] = und.group(1)

        return self._deletedRevs[timestamp]

    def markDeletedRevision(self, timestamp, undelete=True):
        """Marks revision (identified by timestamp) for undeletion (default)
           or to remain as deleted (if undelete=False).
        """
        if self._deletedRevs == None:
            self.loadDeletedRevisions()
        if not self._deletedRevs.has_key(timestamp):
            #TODO: Throw an exception?
            return None
        self._deletedRevs[timestamp][4] = undelete
        self._deletedRevsModified = True

    def undelete(self, comment='', throttle=False):
        """Undeletes page based on the undeletion markers set by previous calls.
           If no calls have been made since loadDeletedRevisions(), everything will be restored.

           Simplest case:
              wikipedia.Page(...).undelete('This will restore all revisions')

           More complex:
              pg = wikipedia.Page(...)
              revs = pg.loadDeletedRevsions()
              for rev in revs:
                  if ... #decide whether to undelete a revision
                      pg.markDeletedRevision(rev) #mark for undeletion
              pg.undelete('This will restore only selected revisions.')
        """
        if throttle:
            put_throttle()
        output(u'Undeleting...')

        address = self.site().undelete_address()
        self.site().forceLogin(sysop = True)
        token = self.site().getToken(self, sysop=True)

        formdata = {
                'target': self.title(),
                'wpComment': comment,
                'wpEditToken': token,
                'restore': self.site().mediawiki_message('undeletebtn')
                }

        if self._deletedRevs != None and self._deletedRevsModified:
            for ts in self._deletedRevs.keys():
                if self._deletedRevs[ts][4]:
                    formdata['ts'+ts] = '1'

        self._deletedRevs = None
        #TODO: Check for errors below (have we succeeded? etc):
        return self.site().postForm(address,formdata,sysop=True)
 
    def protect(self, edit = 'sysop', move = 'sysop', unprotect = False, reason = None, prompt = True, throttle = False):
        """(Un)protects a wiki page. Requires administrator status. If reason is None,
           asks for a reason. If prompt is True, asks the user if he wants to protect the page.
           Valid values for edit and move are:
           * '' (equivalent to 'none')
           * 'autoconfirmed'
           * 'sysop'
        """
        address = self.site().protect_address(self.urlname())
        if unprotect:
            address = self.site().unprotect_address(self.urlname())
        if throttle:
            put_throttle()
        if reason == None:
            reason = input(u'Please enter a reason for the (un)protection:')
        reason = reason.encode(self.site().encoding())
        answer = 'y'
        if prompt:
            answer = inputChoice(u'Do you want to (un)protect %s?' % self.aslink(forceInterwiki = True), ['Yes', 'No'], ['y', 'N'], 'N')
        if answer in ['y', 'Y']:
            host = self.site().hostname()
            
            self.site().forceLogin(sysop = True)

            token = self.site().getToken(self, sysop = True)

            #Translate 'none' to ''
            if edit == 'none': edit = ''
            if move == 'none': move = ''

            predata = {
                'mwProtect-level-edit': edit,
                'mwProtect-level-move': move,
                'mwProtect-reason': reason
            }
            if token:
                predata['wpEditToken'] = token
            if self.site().hostname() in config.authenticate.keys():
                predata["Content-type"] = "application/x-www-form-urlencoded"
                predata["User-agent"] = useragent
                data = self.site().urlEncode(predata)
                response = urllib2.urlopen(urllib2.Request(self.site().protocol() + '://' + self.site().hostname() + address, data))
                data = ''
            else:
                data, response = self.site().postForm(address, predata, sysop = True)

            if not response:
                output(u'(Un)protection successful.')
                return True
            else:
                #Normally, we expect a 302 with no data, so this means an error
                output(u'Protection failed:')
                output(data)
                return False
                
    def removeImage(self, image, put = False, summary = None, safe = True):
        return self.replaceImage(image, None, put, summary, safe)
    
    def replaceImage(self, image, replacement = None, put = False, summary = None, safe = True):
        """Replace all occurences of an image by another image.
        Giving None as argument for replacement will delink 
        instead of replace. 
        
        The argument image must be without namespace and all
        spaces replaced by underscores.
        
        If put is false, the new text will be returned.
        
        If put is true, the edits will be saved to the wiki
        and True will be returned on succes, and otherwise 
        False. Edit errors propagate."""
        
        # Copyright (c) Orgullomoore, Bryan
        
        site = self.site()
        
        text = self.get()
        new_text = text
            
        def create_regex(s):
            s = re.escape(s)
            return ur'(?:[%s%s]%s)' % (s[0].upper(), s[0].lower(), s[1:])
        def create_regex_i(s):
            return ur'(?:%s)' % u''.join([u'[%s%s]' % (c.upper(), c.lower()) for c in s])

        namespaces = ('Image', 'Media') + site.namespace(6, all = True) + site.namespace(-2, all = True)
        # note that the colon is already included here
        r_namespace = ur'\s*(?:%s)\s*\:\s*' % u'|'.join(map(create_regex_i, namespaces))
        r_image = u'(%s)' % create_regex(image).replace(r'\_', '[ _]')
            
        def simple_replacer(match, groupNumber = 1):
            if replacement == None:
                return u''
            else:
                groups = list(match.groups())
                groups[groupNumber] = replacement
                return u''.join(groups)

        # The group params contains parameters such as thumb and 200px, as well
        # as the image caption. The caption can contain wiki links, but each
        # link has to be closed properly.
        r_param = r'(?:\|(?:(?!\[\[).|\[\[.*?\]\])*?)'
        rImage = re.compile(ur'(\[\[)(?P<namespace>%s)%s(?P<params>%s*?)(\]\])' % (r_namespace, r_image, r_param))

        while True:
            m = rImage.search(new_text)
            if not m:
                break
            new_text = new_text[:m.start()] +  simple_replacer(m, 2) + new_text[m.end():]

        # Remove the image from galleries
        r_galleries = ur'(?s)(\<%s\>)(?s)(.*?)(\<\/%s\>)' % (create_regex_i('gallery'), 
            create_regex_i('gallery'))
        r_gallery = ur'(?m)^((?:%s)?)(%s)(\s*(?:\|.*?)?\s*)$' % (r_namespace, r_image)
        def gallery_replacer(match):
            return ur'%s%s%s' % (match.group(1), re.sub(r_gallery, 
                simple_replacer, match.group(2)), match.group(3))
        new_text = re.sub(r_galleries, gallery_replacer, new_text)
            
        if (text == new_text) or (not safe):
            # All previous steps did not work, so the image is
            # likely embedded in a complicated template.
            r_templates = ur'(?s)(\{\{.*?\}\})'
            r_complicated = u'(?s)((?:%s)?)%s' % (r_namespace, r_image)
                
            def template_replacer(match):
                return re.sub(r_complicated, simple_replacer, match.group(1))
            new_text = re.sub(r_templates, template_replacer, new_text)
            
        if put:
            if text != new_text:
                # Save to the wiki
                self.put(new_text, summary)
                return True
            return False
        else:
            return new_text
        
class ImagePage(Page):
    # a Page in the Image namespace
    def __init__(self, site, title = None, insite = None):
        Page.__init__(self, site, title, insite)
        self._imagePageHtml = None

    def getImagePageHtml(self):
        """
        Downloads the image page, and returns the HTML, as a unicode string.

        Caches the HTML code, so that if you run this method twice on the
        same ImagePage object, the page only will be downloaded once.
        """
        if not self._imagePageHtml:
            path = self.site().get_address(self.urlname())
            self._imagePageHtml = self.site().getUrl(path)
        return self._imagePageHtml

    def fileUrl(self):
        # There are three types of image pages:
        # * normal, small images with links like: filename.png (10KB, MIME type: image/png)
        # * normal, large images with links like: Download high resolution version (1024x768, 200 KB)
        # * SVG images with links like: filename.svg (1KB, MIME type: image/svg)
        # This regular expression seems to work with all of them.
        # The part after the | is required for copying .ogg files from en:, as they do not
        # have a "full image link" div. This might change in the future; on commons, there
        # is a full image link for .ogg and .mid files.
        urlR = re.compile(r'<div class="fullImageLink" id="file">.*?<a href="(?P<url>.+?)"|<span class="dangerousLink"><a href="(?P<url2>.+?)"', re.DOTALL)
        m = urlR.search(self.getImagePageHtml())
        try:
            url = m.group('url') or m.group('url2')
        except AttributeError:
            raise NoPage(u'Image file URL for %s not found.' % self.aslink(forceInterwiki = True))
        return url

    def fileIsOnCommons(self):
        return self.fileUrl().startswith(u'http://upload.wikimedia.org/wikipedia/commons/')

    def getFileMd5Sum(self):
        uo = MyURLopener()
        f = uo.open(self.fileUrl())
        md5Checksum = md5.new(f.read()).hexdigest()
        return md5Checksum

    def getFileVersionHistory(self):
        result = []
        history = re.search('(?s)<ul class="special">.+?</ul>', self.getImagePageHtml())

        if history:
            lineR = re.compile('<li> \(.+?\) \(.+?\) <a href=".+?" title=".+?">(?P<datetime>.+?)</a> . . <a href=".+?" title=".+?">(?P<username>.+?)</a> \(.+?\) . . (?P<resolution>\d+.+?\d+) \((?P<size>[\d,\.]+) .+?\)( <span class="comment">(?P<comment>.*?)</span>)?</li>')
            
            for match in lineR.finditer(history.group()):
                datetime = match.group('datetime')
                username = match.group('username')
                resolution = match.group('resolution')
                size = match.group('size')
                comment = match.group('comment') or ''
                result.append((datetime, username, resolution, size, comment))
        return result

    def getFileVersionHistoryTable(self):
        lines = []
        for (datetime, username, resolution, size, comment) in self.getFileVersionHistory():
            lines.append('| %s || %s || %s || %s || <nowiki>%s</nowiki>' % (datetime, username, resolution, size, comment))
        return u'{| border="1"\n! date/time || username || resolution || size || edit summary\n|----\n' + u'\n|----\n'.join(lines) + '\n|}'

    def usingPages(self):
        result = []
        titleList = re.search('(?s)<h2 id="filelinks">.+?</ul>', self.getImagePageHtml()).group()
        lineR = re.compile('<li><a href=".+?" title=".+?">(?P<title>.+?)</a></li>')
        for match in lineR.finditer(titleList):
            result.append(Page(self.site(), match.group('title')))
        return result

class GetAll(object):
    def __init__(self, site, pages, throttle, force):
        """First argument is Site object.
        Second argument is list (should have .append and be iterable)"""
        self.site = site
        self.pages = []
        self.throttle = throttle
        for pl in pages:
            if (not hasattr(pl,'_contents') and not hasattr(pl,'_getexception')) or force:
                self.pages.append(pl)
            elif verbose:
                output(u"BUGWARNING: %s already done!" % pl.aslink())

    def run(self):
        dt=15
        if self.pages != []:
            while True:
                try:
                    data = self.getData()
                except (socket.error, httplib.BadStatusLine, ServerError):
                    # Print the traceback of the caught exception
                    output(u''.join(traceback.format_exception(*sys.exc_info())))
                    output(u'DBG> got network error in GetAll.run. Sleeping for %d seconds...' % dt)
                    time.sleep(dt)
                    if dt <= 60:
                        dt += 15
                    elif dt < 360:
                        dt += 60
                else:
                    # Because language lists are filled in a lazy way in the family
                    # files of Wikimedia projects (using Family.knownlanguages), you
                    # may encounter pages from non-existing wikis such as
                    # http://eo.wikisource.org/
                    if data.find("<title>Wiki does not exist</title>") != -1:
                        return
                    elif data.find("<siteinfo>") == -1: # This probably means we got a 'temporary unaivalable'
                        output(u'Got incorrect export page. Sleeping for %d seconds...' % dt)
                        time.sleep(dt)
                        if dt <= 60:
                            dt += 15
                        elif dt < 360:
                            dt += 60
                    else:
                        break
            R = re.compile(r"\s*<\?xml([^>]*)\?>(.*)",re.DOTALL)
            m = R.match(data)
            if m:
                data = m.group(2)
            handler = xmlreader.MediaWikiXmlHandler()
            handler.setCallback(self.oneDone)
            handler.setHeaderCallback(self.headerDone)
            #f = open("backup.txt", "w")
            #f.write(data)
            #f.close()
            try:
                xml.sax.parseString(data, handler)
            except (xml.sax._exceptions.SAXParseException, ValueError), err:
                debugDump( 'SaxParseBug', self.site, err, data )
                raise
            except PageNotFound:
                return
            # All of the ones that have not been found apparently do not exist
            for pl in self.pages:
                if not hasattr(pl,'_contents') and not hasattr(pl,'_getexception'):
                    pl._getexception = NoPage

    def oneDone(self, entry):
        title = entry.title
        username = entry.username
        ipedit = entry.ipedit
        timestamp = entry.timestamp
        text = entry.text
        editRestriction = entry.editRestriction
        moveRestriction = entry.moveRestriction
        page = Page(self.site, title)
        for page2 in self.pages:
            if page2.sectionFreeTitle() == page.sectionFreeTitle():
                if not hasattr(page2,'_contents') and not hasattr(page2,'_getexception'):
                    break
        else:
            output(u"BUG>> title %s (%s) not found in list" % (title, page.aslink(forceInterwiki=True)))
            output(u'Expected one of: %s' % u','.join([page2.aslink(forceInterwiki=True) for page2 in self.pages]))
            raise PageNotFound

        page2.editRestriction = entry.editRestriction
        page2.moveRestriction = entry.moveRestriction
        if editRestriction == 'autoconfirmed':
            page2._editrestriction = True
        page2._permalink = entry.revisionid
        page2._userName = username
        page2._ipedit = ipedit
        page2._editTime = timestamp
        section = page2.section()
        m = self.site.redirectRegex().match(text)
        if m:
##            output(u"%s is a redirect" % page2.aslink())
            redirectto = m.group(1)
            if section and redirectto.find("#") == -1:
                redirectto = redirectto+"#"+section
            page2._getexception = IsRedirectPage
            page2._redirarg = redirectto
        # There's no possibility to read the wpStarttime argument from the XML.
        # It is this time that the MediaWiki software uses to check for edit
        # conflicts. We take the earliest time later than the last edit, which
        # seems to be the safest possible time.
        page2._startTime = str(int(timestamp)+1)
        if section:
            m = re.search("\.3D\_*(\.27\.27+)?(\.5B\.5B)?\_*%s\_*(\.5B\.5B)?(\.27\.27+)?\_*\.3D" % re.escape(section), sectionencode(text,page2.site().encoding()))                    
            if not m:
                try:
                    page2._getexception
                    output(u"WARNING: Section not found: %s" % page2.aslink(forceInterwiki = True))
                except AttributeError:
                    # There is no exception yet
                    page2._getexception = SectionError
        # Store the content
        page2._contents = text
 
    def headerDone(self, header):
        # Verify our family data
        lang = self.site.lang
        ids = header.namespaces.keys()
        ids.sort()
        for id in ids:
            nshdr = header.namespaces[id]
            if self.site.family.isDefinedNS(id):
                ns = self.site.namespace(id)
                if ns == None:
                    ns = u''
                if ns != nshdr:
                    dflt = self.site.family.namespace('_default', id)
                    if dflt == ns:
                        flag = u"is set to default ('%s'), but should be '%s'" % (ns, nshdr)
                    elif dflt == nshdr:
                        flag = u"is '%s', but should be removed (default value '%s')" % (ns, nshdr)
                    else:
                        flag = u"is '%s', but should be '%s'" % (ns, nshdr)

                    output(u"WARNING: Outdated family file %s: namespace['%s'][%i] %s" % (self.site.family.name, lang, id, flag))
#                    self.site.family.namespaces[id][lang] = nshdr
            else:
                output(u"WARNING: Missing namespace in family file %s: namespace['%s'][%i] (it is set to '%s')" % (self.site.family.name, lang, id, nshdr))

    def getData(self):
        address = self.site.export_address()
        pagenames = [page.sectionFreeTitle() for page in self.pages]
        # We need to use X convention for requested page titles.
        if self.site.lang == 'eo':
            pagenames = [doubleXForEsperanto(pagetitle) for pagetitle in pagenames]
        pagenames = u'\r\n'.join(pagenames)
        if type(pagenames) != type(u''):
            output(u'Warning: xmlreader.WikipediaXMLHandler.getData() got non-unicode page names. Please report this.')
            print pagenames
        # convert Unicode string to the encoding used on that wiki
        pagenames = pagenames.encode(self.site.encoding())
        predata = {
            'action': 'submit',
            'pages': pagenames,
            'curonly': 'True',
        }
        # Slow ourselves down
        get_throttle(requestsize = len(self.pages))
        # Now make the actual request to the server
        now = time.time()
        if self.site.hostname() in config.authenticate.keys():
            predata["Content-type"] = "application/x-www-form-urlencoded"
            predata["User-agent"] = useragent
            data = self.site.urlEncode(predata)
            response = urllib2.urlopen(urllib2.Request(self.site.protocol() + '://' + self.site.hostname() + address, data))
            data = response.read()
        else:
            response, data = self.site.postForm(address, predata)
        # The XML parser doesn't expect a Unicode string, but an encoded one,
        # so we'll encode it back.
        data = data.encode(self.site.encoding())
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

def setUserAgent(s):
    """Set a User-agent: header passed to the HTTP server"""
    global useragent
    useragent = s

# Default User-agent
setUserAgent('PythonWikipediaBot/1.0')

# Mechanics to slow down page download rate.
class Throttle(object):
    def __init__(self, mindelay = config.minthrottle, maxdelay = config.maxthrottle, multiplydelay = True):
        """Make sure there are at least 'delay' seconds between page-gets
           after 'ignore' initial page-gets"""
        self.lock = threading.RLock()
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

    def logfn(self):
        import wikipediatools as _wt
        return _wt.absoluteFilename('throttle.log')
        
    def checkMultiplicity(self):
        self.lock.acquire()
        try:
            processes = {}
            my_pid = 1
            count = 1
            try:
                f = open(self.logfn(), 'r')
            except IOError:
                if not self.pid:
                    pass
                else:
                    raise
            else:
                now = time.time()
                for line in f.readlines():
                    try:
                        line = line.split(' ')
                        pid = int(line[0])
                        ptime = int(line[1].split('.')[0])
                        if now - ptime <= self.releasepid:
                            if now - ptime <= self.dropdelay and pid != self.pid:
                                count += 1
                            processes[pid] = ptime
                            if pid >= my_pid:
                                my_pid = pid+1
                    except (IndexError,ValueError):
                        pass    # Sometimes the file gets corrupted - ignore that line

            if not self.pid:
                self.pid = my_pid
            self.checktime = time.time()
            processes[self.pid] = self.checktime
            f = open(self.logfn(), 'w')
            for p in processes.keys():
                f.write(str(p)+' '+str(processes[p])+'\n')
            f.close()
            self.process_multiplicity = count
            output(u"Checked for running processes. %s processes currently running, including the current process." % count)
        finally:
            self.lock.release()

    def setDelay(self, delay = config.minthrottle, absolute = False):
        self.lock.acquire()
        try:
            if absolute:
                self.maxdelay = delay
                self.mindelay = delay
            self.delay = delay
            # Don't count the time we already waited as part of our waiting time :-0
            self.now = time.time()
        finally:
            self.lock.release()

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
            f = open(self.logfn(), 'r')
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
        f = open(self.logfn(), 'w')
        for p in processes.keys():
            f.write(str(p)+' '+str(processes[p])+'\n')
        f.close()

    def __call__(self, requestsize=1):
        """This is called from getEditPage without arguments. It will make sure
           that if there are no 'ignores' left, there are at least delay seconds
           since the last time it was called before it returns."""
        self.lock.acquire()
        try:
            waittime = self.waittime()
            # Calculate the multiplicity of the next delay based on how
            # big the request is that is being posted now.
            # We want to add "one delay" for each factor of two in the
            # size of the request. Getting 64 pages at once allows 6 times
            # the delay time for the server.
            self.next_multiplicity = math.log(1+requestsize)/math.log(2.0)
            # Announce the delay if it exceeds a preset limit
            if waittime > config.noisysleep:
                output(u"Sleeping for %.1f seconds, %s" % (waittime, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            time.sleep(waittime)
            self.now = time.time()
        finally:
            self.lock.release()

def replaceExcept(text, old, new, exceptions, caseInsensitive = False, allowoverlap = False, marker = ''):
    """
    Replaces old by new in text, skipping occurences of old e.g. within nowiki
    tags or HTML comments.
    If caseInsensitive is true, then use case insensitivity in the regex
    matching. If allowoverlap is true, overlapping occurences are all replaced
    (watch out when using this, it might lead to infinite loops!).

    Parameters:
        text            - a string
        old             - a compiled regular expression
        new             - a string
        exceptList      - a list of strings which signal what to leave out,
                          e.g. ['math', 'table', 'template']
        caseInsensitive - a boolean
        marker          - a string, it will be added to the last replacement,
                          if nothing is changed, it is added at the end
    """
    exceptionRegexes = {
        'comment':     re.compile(r'(?s)<!--.*?-->'),
        'includeonly': re.compile(r'(?is)<includeonly>.*?</includeonly>'),
        'math':        re.compile(r'(?is)<math>.*?</math>'),
        'noinclude':   re.compile(r'(?is)<noinclude>.*?</noinclude>'),
        # wiki tags are ignored inside nowiki tags.
        'nowiki':      re.compile(r'(?is)<nowiki>.*?</nowiki>'),
        # lines that start with a space are shown in a monospace font and
        # have whitespace preserved, with wiki tags being ignored.
        'pre':         re.compile(r'(?is)<pre>.*?</pre>'),
        # lines that start with a space are shown in a monospace font and
        # have whitespace preserved.
        'startspace':  re.compile(r'(?m)^ (.*?)$'),
        # tables often have whitespace that is used to improve wiki
        # source code readability.
        'table':       re.compile(r'(?ims)^{\|.*?^\|}|<table>.*?</table>'),
        # templates with parameters often have whitespace that is used to
        # improve wiki source code readability.
        'template':    re.compile(r'(?s)^{{.*?}}'),
    }

    # if we got a string, compile it as a regular expression
    if type(old) == type('') or type(old) == type(u''):
        if caseInsensitive:
            old = re.compile(old, re.IGNORECASE | re.UNICODE)
        else:
            old = re.compile(old)
    
    #noTouch = '|'.join([exceptions[name] for name in exceptList])
    #noTouchR = re.compile(noTouch)
    # How much of the text we have looked at so far
    dontTouchRegexes = [exceptionRegexes[name] for name in exceptions]
    index = 0
    markerpos = len(text)
    while True:
        match = old.search(text, index)
        if not match:
            # nothing left to replace
            break

        # check which exception will occur next.
        nextExceptionMatch = None
        for dontTouchR in dontTouchRegexes:
            excMatch = dontTouchR.search(text, index)
            if excMatch and (
                    nextExceptionMatch is None or
                    excMatch.start() < nextExceptionMatch.start()):
                nextExceptionMatch = excMatch

        if nextExceptionMatch is not None and nextExceptionMatch.start() <= match.start():
            # an HTML comment or text in nowiki tags stands before the next valid match. Skip.
            index = nextExceptionMatch.end()
        else:
            # We found a valid match. Replace it.

            # We cannot just insert the new string, as it may contain regex
            # group references such as \2 or \g<name>.
            # On the other hand, this approach does not work because it can't
            # handle lookahead or lookbehind (see bug #1731008):
            #replacement = old.sub(new, text[match.start():match.end()])
            #text = text[:match.start()] + replacement + text[match.end():]

            # So we have to process the group references manually.
            replacement = new

            groupR = re.compile(r'\\(?P<number>\d+)|\\g<(?P<name>.+?)>')
            while True:
                groupMatch = groupR.search(replacement)
                if not groupMatch:
                    break
                groupID = groupMatch.group('name') or int(groupMatch.group('number'))
                replacement = replacement[:groupMatch.start()] + match.group(groupID) + replacement[groupMatch.end():]
            text = text[:match.start()] + replacement + text[match.end():]

            # continue the search on the remaining text
            if allowoverlap:
                index = match.start() + 1
            else:
                index = match.start() + len(replacement)
            markerpos = match.start() + len(replacement)
    text = text[:markerpos] + marker + text[markerpos:]
    return text

def removeDisabledParts(text):
    """
    Removes those parts of a wiki text where wiki markup is disabled, i.e.
    * HTML comments
    * nowiki tags
    * includeonly tags
    """
    toRemoveR = re.compile(r'<nowiki>.*?</nowiki>|<!--.*?-->|<includeonly>.*?</includeonly>', re.IGNORECASE | re.DOTALL)
    return toRemoveR.sub('', text)

# Part of library dealing with interwiki links

def getLanguageLinks(text, insite = None, pageLink = "[[]]"):
    """
    Returns a dictionary with language codes as keys and Page objects as values
    for each interwiki link found in the text. Do not call this routine
    directly, use Page objects instead"""
    if insite == None:
        insite = getSite()
    result = {}
    # Ignore interwiki links within nowiki tags, includeonly tags, and HTML comments
    text = removeDisabledParts(text)

    # This regular expression will find every link that is possibly an
    # interwiki link.
    # NOTE: language codes are case-insensitive and only consist of basic latin
    # letters and hyphens.
    interwikiR = re.compile(r'\[\[([a-zA-Z\-]+)\s?:([^\[\]\n]*)\]\]')
    for lang, pagetitle in interwikiR.findall(text):
        lang = lang.lower()
        # Check if it really is in fact an interwiki link to a known
        # language, or if it's e.g. a category tag or an internal link
        if lang in insite.family.obsolete:
            lang = insite.family.obsolete[lang]
        if lang in insite.validLanguageLinks():
            if '|' in pagetitle:
                # ignore text after the pipe
                pagetitle = pagetitle[:pagetitle.index('|')]
            if not pagetitle:
                output(u"ERROR: %s - ignoring impossible link to %s:%s" % (pageLink, lang, pagetitle))
            else:
                # we want the actual page objects rather than the titles
                site = insite.getSite(code = lang)
                result[site] = Page(site, pagetitle, insite = insite)
    return result

def removeLanguageLinks(text, site = None, marker = ''):
    """Given the wiki-text of a page, return that page with all interwiki
       links removed. If a link to an unknown language is encountered,
       a warning is printed. If a marker is defined, the marker is placed
       at the location of the last occurence of an interwiki link (at the end
       if there are no interwikilinks)."""
    if site == None:
        site = getSite()
    if not site.validLanguageLinks():
        return text
    # This regular expression will find every interwiki link, plus trailing
    # whitespace.
    languageR = '|'.join(site.validLanguageLinks())
    interwikiR = re.compile(r'\[\[(%s)\s?:[^\]]*\]\][\s]*' % languageR, re.IGNORECASE)
    text = replaceExcept(text, interwikiR, '', ['nowiki', 'comment', 'math', 'pre'], marker = marker)
    return normalWhitespace(text)

def replaceLanguageLinks(oldtext, new, site = None):
    """Replace the interwiki language links given in the wikitext given
       in oldtext by the new links given in new.

       'new' should be a dictionary with the language names as keys, and
       Page objects as values.
    """
    # Find a marker that is not already in the text.
    marker = '@@'
    while marker in oldtext:
        marker += '@'
    if site == None:
        site = getSite()
    s = interwikiFormat(new, insite = site)
    s2 = removeLanguageLinks(oldtext, site = site, marker = marker)
    if s:
        if site.language() in site.family.interwiki_attop:
            newtext = s + site.family.interwiki_text_separator + s2.replace(marker,'').strip()
        else:
            # calculate what was after the language links on the page
            firstafter = s2.find(marker) + len(marker)
            # Is there any text in the 'after' part that means we should keep it after?
            if "</noinclude>" in s2[firstafter:]:
                newtext = s2[:firstafter] + s + s2[firstafter:]
            elif site.language() in site.family.categories_last:
                cats = getCategoryLinks(s2, site = site)
                s2 = removeCategoryLinks(s2.replace(marker,'').strip(), site) + site.family.interwiki_text_separator + s
                newtext = replaceCategoryLinks(s2, cats, site=site)
            else:
                newtext = s2.replace(marker,'').strip() + site.family.interwiki_text_separator + s
            newtext = newtext.replace(marker,'')
    else:
        newtext = s2.replace(marker,'')
    return newtext

def interwikiFormat(links, insite = None):
    """Create a suitable string encoding all interwiki links for a wikipedia
       page.

       'links' should be a dictionary with the language codes as keys, and
       Page objects as values.

       The string is formatted for inclusion in insite (defaulting to your
       own site).
    """
    if insite is None:
        insite = getSite()
    if not links:
        return ''
    # Security check: site may not refer to itself.
    #
    # Disabled because MediaWiki was changed so that such links appear like
    # normal links, and some people accidentally use them for normal links.
    # While such links are bad style, they are not worth crashing the bot.
    #
    #for pl in links.values():
    #    if pl.site() == insite:
    #        raise ValueError("Trying to add interwiki link to self")
    s = []
    ar = links.keys()
    ar.sort()
    putfirst = insite.interwiki_putfirst()
    if putfirst:
        #In this case I might have to change the order
        ar2 = []
        for code in putfirst:
            # The code may not exist in this family?
            if code in getSite().validLanguageLinks():
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
    return text

# Categories

def getCategoryLinks(text, site):
    import catlib
    """Returns a list of category links.
       in the form {code:pagename}. Do not call this routine directly, use
       Page objects instead"""
    result = []
    # Ignore category links within nowiki tags, includeonly tags, and HTML comments
    text = removeDisabledParts(text)
    catNamespace = '|'.join(site.category_namespaces())
    R = re.compile(r'\[\[\s*(?P<namespace>%s)\s*:\s*(?P<catName>.+?)(?:\|(?P<sortKey>.+?))?\s*\]\]' % catNamespace)
    for match in R.finditer(text):
        cat = catlib.Category(site, '%s:%s' % (match.group('namespace'), match.group('catName')), sortKey = match.group('sortKey'))
        result.append(cat)
    return result

def removeCategoryLinks(text, site, marker = ''):
    """Given the wiki-text of a page, return that page with all category
       links removed. Puts the marker after the last replacement (at the
       end of the text if there is no replacement)"""
    # This regular expression will find every link that is possibly an
    # interwiki link, plus trailing whitespace. The language code is grouped.
    # NOTE: This assumes that language codes only consist of non-capital
    # ASCII letters and hyphens.
    catNamespace = '|'.join(site.category_namespaces())
    categoryR = re.compile(r'\[\[\s*(%s)\s*:.*?\]\][\s]*' % catNamespace)
    text = replaceExcept(text, categoryR, '', ['nowiki', 'comment', 'math', 'pre'], marker = marker)
    return normalWhitespace(text)

def replaceCategoryInPlace(oldtext, oldcat, newcat, site = None):
    """Replaces the category oldcat with the category newcat and then returns
       the modified Wiki source.
    """
    #Note that this doesn't work yet and it has some very strange side-effects.

    if site is None:
        site = getSite()

    catNamespace = '|'.join(site.category_namespaces())
    categoryR = re.compile(r'\[\[\s*(%s)\s*:%s\]\]' % (catNamespace, oldcat.titleWithoutNamespace()))
    text = replaceExcept(oldtext, categoryR, '[[Category:%s]]' % newcat.titleWithoutNamespace(), ['nowiki', 'comment', 'math', 'pre'])
    categoryR = re.compile(r'\[\[\s*(%s)\s*:%s\]\]' % (catNamespace, oldcat.titleWithoutNamespace().replace(' ','_')))
    text = replaceExcept(text, categoryR, '[[Category:%s]]' % newcat.titleWithoutNamespace(), ['nowiki', 'comment', 'math', 'pre'])
    return text

def replaceCategoryLinks(oldtext, new, site = None):
    """Replace the category links given in the wikitext given
       in oldtext by the new links given in new.

       'new' should be a list of Category objects.
    """

    # Find a marker that is not already in the text.
    marker = '@@'
    while marker in oldtext:
        marker += '@'

    if site is None:
        site = getSite()
    if site.sitename() == 'wikipedia:de':
        raise Error('The PyWikipediaBot is no longer allowed to touch categories on the German Wikipedia. See http://de.wikipedia.org/wiki/Hilfe_Diskussion:Personendaten/Archiv2#Position_der_Personendaten_am_.22Artikelende.22')

    s = categoryFormat(new, insite = site)
    s2 = removeCategoryLinks(oldtext, site = site, marker = marker)

    if s:
        if site.language() in site.family.category_attop:
            newtext = s + site.family.category_text_separator + s2
        else:
            # calculate what was after the categories links on the page
            firstafter = s2.find(marker)
            # Is there any text in the 'after' part that means we should keep it after?
            if "</noinclude>" in s2[firstafter:]:
                newtext = s2[:firstafter] + s + s2[firstafter:]
            elif site.language() in site.family.categories_last:
                newtext = s2.replace(marker,'').strip() + site.family.category_text_separator + s
            else:
                interwiki = getLanguageLinks(s2)
                s2 = removeLanguageLinks(s2.replace(marker,'').strip(), site) + site.family.category_text_separator + s
                newtext = replaceLanguageLinks(s2, interwiki, site)
        newtext = newtext.replace(marker,'')
    else:
        s2 = s2.replace(marker,'')
        return s2
    return newtext

def categoryFormat(categories, insite = None):
    """Create a suitable string with all category links for a wiki
       page.

       'categories' should be a list of Category objects.

       The string is formatted for inclusion in insite.
    """
    if not categories:
        return ''
    if insite is None:
        insite = getSite()
    catLinks = [category.aslink() for category in categories]
    if insite.category_on_one_line():
        sep = ' '
    else:
        sep = '\r\n'
    # Some people don't like the categories sorted
    #catLinks.sort()
    return sep.join(catLinks) + '\r\n'

# end of category specific code

def url2link(percentname, insite, site):
    """Convert a url-name of a page into a proper name for an interwiki link
       the argument 'insite' specifies the target wiki
       """
    percentname = percentname.replace('_', ' ')
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
        u'c': u'ĉ',
        u'C': u'Ĉ',
        u'g': u'ĝ',
        u'G': u'Ĝ',
        u'h': u'ĥ',
        u'H': u'Ĥ',
        u'j': u'ĵ',
        u'J': u'Ĵ',
        u's': u'ŝ',
        u'S': u'Ŝ',
        u'u': u'ŭ',
        u'U': u'Ŭ',
    }
    for latin, esperanto in chars.iteritems():
        # A regular expression that matches a letter combination which IS
        # encoded using x-convention.
        xConvR = re.compile(latin + '[xX]+')
        pos = 0
        result = ''
        # Each matching substring will be regarded exactly once.
        while True:
            match = xConvR.search(text[pos:])
            if match:
                old = match.group()
                if len(old) % 2 == 0:
                    # The first two chars represent an Esperanto letter.
                    # Following x's are doubled.
                    new = esperanto + ''.join([old[2 * i] for i in range(1, len(old)/2)])
                else:
                    # The first character stays latin; only the x's are doubled.
                    new = latin + ''.join([old[2 * i + 1] for i in range(0, len(old)/2)])
                result += text[pos : match.start() + pos] + new
                pos += match.start() + len(old)
            else:
                result += text[pos:]
                text = result
                break
    return text

def doubleXForEsperanto(text):
    """
    Doubles X-es where necessary so that we can submit a page to an Esperanto
    wiki. Again, we have to keep stupid stuff like cXxXxxX in mind. Maybe
    someone wants to write about the Sony Cyber-shot DSC-Uxx camera series on
    eo: ;)
    """
    # A regular expression that matches a letter combination which is NOT
    # encoded in x-convention.
    notXConvR = re.compile('[cghjsuCGHJSU][xX]+')
    pos = 0
    result = ''
    while True:
        match = notXConvR.search(text[pos:])
        if match:
            old = match.group()
            # the first letter stays; add an x after each X or x.
            new = old[0] + ''.join([old[i] + 'x' for i in range(1, len(old))])
            result += text[pos : match.start() + pos] + new
            pos += match.start() + len(old)
        else:
            result += text[pos:]
            text = result
            break
    return text

def sectionencode(text, encoding):
    # change the text so that it can be used as a section title in wiki-links
    return urllib.quote(text.replace(" ","_").encode(encoding)).replace("%",".")

######## Unicode library functions ########

def UnicodeToAsciiHtml(s):
    html = []
    for c in s:
        cord = ord(c)
        if cord < 128:
            html.append(c)
        else:
            html.append('&#%d;'%cord)
    return ''.join(html)

def url2unicode(title, site, site2 = None):
    # create a list of all possible encodings for both hint sites
    encList = [site.encoding()] + list(site.encodings())
    if site2 and site2 <> site:
        encList.append(site.encoding())
        encList += list(site2.encodings())
    firstException = None
    # try to handle all encodings (will probably retry utf-8)
    for enc in encList:
        try:
            t = title.encode(enc)
            t = urllib.unquote(t)
            return unicode(t, enc)
        except UnicodeError, ex:
            if not firstException:
                firstException = ex
            pass
    # Couldn't convert, raise the original exception
    raise firstException

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

def html2unicode(text, ignore = []):
    """
    Given a string, replaces all HTML entities by the equivalent unicode
    characters.
    """
    # This regular expression will match any decimal and hexadecimal entity and
    # also entities that might be named entities.
    entityR = re.compile(r'&(#(?P<decimal>\d+)|#x(?P<hex>[0-9a-fA-F]+)|(?P<name>[A-Za-z]+));')
    result = u''
    i = 0
    found = True
    while found:
        text = text[i:]
        match = entityR.search(text)
        if match:
            unicodeCodepoint = None
            if match.group('decimal'):
                unicodeCodepoint = int(match.group('decimal'))
            elif match.group('hex'):
                unicodeCodepoint = int(match.group('hex'), 16)
            elif match.group('name'):
                name = match.group('name')
                if htmlentitydefs.name2codepoint.has_key(name):
                    # We found a known HTML entity.
                    unicodeCodepoint = htmlentitydefs.name2codepoint[name]
            result += text[:match.start()]
            if unicodeCodepoint and unicodeCodepoint not in ignore and (WIDEBUILD or unicodeCodepoint < 65534):
                result += unichr(unicodeCodepoint)
            else:
                # Leave the entity unchanged
                result += text[match.start():match.end()]
            i = match.end()
        else:
            result += text
            found = False
    return result

def Family(fam = None, fatal = True):
    """
    Import the named family.
    If fatal is true, the bot will stop running when the given family is
    unknown. If fatal is false, it will only raise a ValueError exception.
    """
    if fam == None:
        fam = config.family
    try:
        # search for family module in the 'families' subdirectory
        import wikipediatools as _wt
        sys.path.append(_wt.absoluteFilename('families'))
        exec "import %s_family as myfamily" % fam
    except ImportError:
        if fatal:
            output(u"Error importing the %s family. This probably means the family does not exist. Also check your configuration file." % fam)
            import traceback
            traceback.print_stack()
            sys.exit(1)
        else:
            raise ValueError("Family does not exist")
    return myfamily.Family()

class Site(object):
    def __init__(self, code, fam=None, user=None):
        """Constructor takes three arguments:

        code    language code for Site
        fam     Wikimedia family (optional: defaults to configured).
                Can either be a string or a Family object.
        user    User to use (optional: defaults to configured)"""

        self.lang = code.lower()
        if isinstance(fam, basestring) or fam is None:
            self.family = Family(fam, fatal = False)
        else:
            self.family = fam
        if self.lang not in self.languages():
            raise KeyError("Language %s does not exist in family %s"%(self.lang,self.family.name))

        # if we got an outdated language code, use the new one instead.
        if self.lang in self.family.obsolete and self.family.obsolete[self.lang]:
            self.lang = self.family.obsolete[self.lang]

        self.messages=False
        self._mediawiki_messages = {}
        self.nocapitalize = self.lang in self.family.nocapitalize
        self.user = user
        self._token = None
        self._sysoptoken = None
        self.loginStatusKnown = {}
        self._loggedInAs = None
        self.userGroups = []
        # Calculating valid languages took quite long, so we calculate it once
        # in initialization instead of each time it is used.
        self._validlanguages = []
        for language in self.languages():
            if not language[0].upper() + language[1:] in self.namespaces():
                self._validlanguages.append(language)
        self.sandboxpage = Page(self,self.family.sandboxpage(code))

    def urlEncode(self, query):
        """This can encode a query so that it can be sent as a query using
        a http POST request"""
        if not query:
            return None
        l = []
        for key, value in query.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            key = urllib.quote(key)
            value = urllib.quote(value)
            l.append(key + '=' + value)
        return '&'.join(l)

    def postForm(self, address, predata, sysop = False, useCookie=True):
        """
        Posts the given form data to the given address at this site.
        address is the absolute path without hostname.
        predata is a list of key-value tuples.
        Returns a (response, data) tuple where response is the HTTP
        response object and data is a Unicode string containing the
        body of the response.
        """
        data = self.urlEncode(predata)
        return self.postData(address, data, sysop = sysop, useCookie=useCookie)

    def postData(self, address, data, contentType = 'application/x-www-form-urlencoded', sysop = False, useCookie=True):
        """
        Posts the given data to the given address at this site.
        address is the absolute path without hostname.
        data is an ASCII string. (or isn't it?)
        Returns a (response, data) tuple where response is the HTTP
        response object and data is a Unicode string containing the
        body of the response.
        """

        # TODO: add the authenticate stuff here

        # Encode all of this into a HTTP request
        if self.protocol() == 'http':
            conn = httplib.HTTPConnection(self.hostname())
        elif self.protocol() == 'https':
            conn = httplib.HTTPSConnection(self.hostname())
        # otherwise, it will crash, as other protocols are not supported

        conn.putrequest('POST', address)
        conn.putheader('Content-Length', str(len(data)))
        conn.putheader('Content-type', contentType)
        conn.putheader('User-agent', useragent)
        if useCookie and self.cookies(sysop = sysop):
            conn.putheader('Cookie', self.cookies(sysop = sysop))
        conn.endheaders()
        conn.send(data)

        # Prepare the return values
        # Note that this can raise network exceptions which are not
        # caught here.
        response = conn.getresponse()
        data = response.read().decode(self.encoding())
        conn.close()
        return response, data

    def forceLogin(self, sysop = False):
        if not self.loggedInAs(sysop = sysop):
            loginMan = login.LoginManager(site = self, sysop = sysop)
            if loginMan.login(retry = True):
                self.loginStatusKnown = True
                self._loggedInAs = loginMan.username

    def loggedInAs(self, sysop = False):
        """
        Checks if we're logged in by loading a page and looking for the login
        link. We assume that we're not being logged out during a bot run, so
        loading the test page is only required once.

        If logged in, returns the username. Otherwise, returns None
        """
        self._loadCookies(sysop = sysop)
        if not self.loginStatusKnown:
            output(u'Getting a page to check if we\'re logged in on %s' % self)
            path = self.put_address('Non-existing_page')
            text = self.getUrl(path, sysop = sysop)
            # Search for the "my talk" link at the top
            mytalkR = re.compile('<li id="pt-userpage"><a href=".+?">(?P<username>.+?)</a></li>')
            m = mytalkR.search(text)
            if m:
                self.loginStatusKnown = True
                self._loggedInAs = m.group('username')
                # While we're at it, check if we have got unread messages
                if '<div class="usermessage">' in text:
                    output(u'NOTE: You have unread messages on %s' % self)
                    messages=True
                else:
                    messages=False
                # Check whether we found a token
                Rwatch = re.compile(r"\<input type='hidden' value=\"(.*?)\" name=\"wpEditToken\"")
                tokenloc = Rwatch.search(text)
                if tokenloc:
                    self.putToken(tokenloc.group(1), sysop = sysop)
        return self._loggedInAs

    def cookies(self, sysop = False):
        # TODO: cookie caching is disabled
        #if not hasattr(self,'_cookies'):
        self._loadCookies(sysop = sysop)
        return self._cookies

    def _loadCookies(self, sysop = False):
        """Retrieve session cookies for login"""
        try:
            if sysop:
                try:
                    username = config.sysopnames[self.family.name][self.lang]
                except KeyError:
                    raise NoUsername('You tried to perform an action that requires admin privileges, but you haven\'t entered your sysop name in your user-config.py. Please add sysopnames[\'%s\'][\'%s\']=\'name\' to your user-config.py' % (self.family.name, self.lang))
            else:
                username = config.usernames[self.family.name][self.lang]
        except KeyError:
            self._cookies = None
            self.loginStatusKnown = True
        else:
            import wikipediatools as _wt
            tmp = '%s-%s-%s-login.data' % (self.family.name, self.lang, username)
            fn = _wt.absoluteFilename('login-data', tmp)
            if not os.path.exists(fn):
                self._cookies = None
                self.loginStatusKnown = True
            else:
                f = open(fn)
                self._cookies = '; '.join([x.strip() for x in f.readlines()])
                f.close()

    r_userGroups = re.compile(ur'var wgUserGroups \= (.*)\;')
    def getUrl(self, path, retry = True, sysop = False, data = None, compress = True):
        """
        Low-level routine to get a URL from the wiki.

        Parameters:
            path  - The absolute path, without the hostname.
            retry - If True, retries loading the page when a network error
                    occurs.
            sysop - If True, the sysop account's cookie will be used.
            data  - An optional dict providing extra post request parameters

           Returns the HTML text of the page converted to unicode.
        """
        if self.hostname() in config.authenticate.keys():
            uo = authenticateURLopener
        else:
            uo = MyURLopener()
            if self.cookies(sysop = sysop):
                uo.addheader('Cookie', self.cookies(sysop = sysop))
            if compress:
                uo.addheader('Accept-encoding', 'gzip')

        url = '%s://%s%s' % (self.protocol(), self.hostname(), path)
        data = self.urlEncode(data)

        # Try to retrieve the page until it was successfully loaded (just in
        # case the server is down or overloaded).
        # Wait for retry_idle_time minutes (growing!) between retries.
        retry_idle_time = 1
        retrieved = False
        while not retrieved:
            try:
                if self.hostname() in config.authenticate.keys():
                    if compress:
                        request = urllib2.Request(url, data)
                        request.add_header('Accept-encoding', 'gzip')
                        opener = urllib2.build_opener()
                        f = opener.open(request)
                    else:
                        f = urllib2.urlopen(url, data)
                else:
                    f = uo.open(url, data)
                retrieved = True
            except KeyboardInterrupt:
                raise
            except Exception, e:
                if retry:
                    # We assume that the server is down. Wait some time, then try again.
                    output(u"%s" % e)
                    output(u"WARNING: Could not open '%s://%s%s'. Maybe the server or your connection is down. Retrying in %i minutes..." % (self.protocol(), self.hostname(), path, retry_idle_time))
                    time.sleep(retry_idle_time * 60)
                    # Next time wait longer, but not longer than half an hour
                    retry_idle_time *= 2
                    if retry_idle_time > 30:
                        retry_idle_time = 30
                else:
                    raise
        text = f.read()
        if compress and f.headers.get('Content-Encoding') == 'gzip':
            import StringIO, gzip
            compressedstream = StringIO.StringIO(text)
            gzipper = gzip.GzipFile(fileobj=compressedstream)
            text = gzipper.read()
            
        # Find charset in the content-type meta tag
        contentType = f.info()['Content-Type']
        R = re.compile('charset=([^\'\";]+)')
        m = R.search(contentType)
        if m:
            charset = m.group(1)
        else:
            output(u"WARNING: No character set found.")
            # UTF-8 as default
            charset = 'utf-8'
        # Check if this is the charset we expected
        self.checkCharset(charset)
        # Convert HTML to Unicode
        try:
            text = unicode(text, charset, errors = 'strict')
        except UnicodeDecodeError, e:
            print e
            output(u'ERROR: Invalid characters found on %s://%s%s, replaced by \\ufffd.' % (self.protocol(), self.hostname(), path))
            # We use error='replace' in case of bad encoding.
            text = unicode(text, charset, errors = 'replace')

        # Try and see whether we can extract the user groups
        match = self.r_userGroups.search(text)
        if match:
            self.userGroups = []
            if match.group(1) != 'null':
                uG = match.group(1)[1:-1].split(', ')
                for group in uG:
                    if group.strip('"') != '*':
                        self.userGroups.append(group.strip('"'))

        return text

    def mediawiki_message(self, key):
        """Return the MediaWiki message text for key "key" """
        global mwpage, tree
        if key not in self._mediawiki_messages.keys() \
                and not hasattr(self, "_phploaded"):
            retry_idle_time = 1
            while True:
                get_throttle()
                mwpage = self.getUrl("%s?title=%s:%s&action=edit"
                         % (self.path(), urllib.quote(
                                self.namespace(8).replace(' ', '_').encode(
                                    self.encoding())),
                            key))
                tree = BeautifulSoup(mwpage,
                                     convertEntities=BeautifulSoup.HTML_ENTITIES,
                                     parseOnlyThese=SoupStrainer("textarea"))
                if tree.textarea is None:
                    # We assume that the server is down.
                    # Wait some time, then try again.
                    output(
u"""WARNING: No text area found on %s%s?title=MediaWiki:%s&action=edit.
Maybe the server is down. Retrying in %i minutes..."""
                        % (self.hostname(), self.path(), key, retry_idle_time)
                    )
                    time.sleep(retry_idle_time * 60)
                    # Next time wait longer, but not longer than half an hour
                    retry_idle_time *= 2
                    if retry_idle_time > 30:
                        retry_idle_time = 30
                    continue
                break
            value = tree.textarea.string.strip()
            if value:
                self._mediawiki_messages[key] = value
            else:
                self._mediawiki_messages[key] = None
                # Fallback in case MediaWiki: page method doesn't work
                if verbose:
                    output(
                      u"Retrieving mediawiki messages from Special:Allmessages")
                get_throttle()
                phppage = self.getUrl(self.get_address("Special:Allmessages")
                                      + "&ot=php")
                Rphpvals = re.compile(r"(?ms)'([^']*)' =&gt; '(.*?[^\\])',")
                for (phpkey, phpval) in Rphpvals.findall(phppage):
                    self._mediawiki_messages[str(phpkey)] = phpval
                self._phploaded = True

        if self._mediawiki_messages[key] is None:
            raise KeyError("MediaWiki key '%s' does not exist on %s"
                           % (key, self))
        return self._mediawiki_messages[key]

    def has_mediawiki_message(self, key):
        """Return True iff this site defines a MediaWiki message for key "key" """
        try:
            v = self.mediawiki_message(key)
            return True
        except KeyError:
            return False

    # TODO: avoid code duplication for the following methods
    def newpages(self, number = 10, get_redirect = False, repeat = False):
        """Generator which yields new articles subsequently.
           It starts with the article created 'number' articles
           ago (first argument). When these are all yielded
           and repeat is True,
           it fetches NewPages again. If there is no new page,
           it blocks until there is one, sleeping between subsequent
           fetches of NewPages.

           The objects yielded are dictionairies. The keys are
           date (datetime object), title (pagelink), length (int)
           user_login (only if user is logged in, string), comment
           (string) and user_anon (if user is not logged in, string).

        """
        # The throttling is important here, so always enabled.
        if repeat:
            throttle = True
        seen = set()
        while True:
            path = self.newpages_address(n=number)
            get_throttle()
            html = self.getUrl(path)
            
            entryR = re.compile('<li[^>]*>(?P<date>.+?) \S*?<a href=".+?" title="(?P<title>.+?)">.+?</a>.+?[\(\[](?P<length>\d+)[^\)\]]*[\)\]] .?<a href=".+?" title=".+?:(?P<username>.+?)">')
            for m in entryR.finditer(html):
                date = m.group('date')
                title = m.group('title')
                title = title.replace('&quot;', '"')
                length = int(m.group('length'))
                loggedIn = u''
                username = m.group('username')
                comment = u''

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
            path = self.longpages_address(n=number)
            get_throttle()
            html = self.getUrl(path)
            entryR = re.compile(ur'<li>\(<a href=".+?" title=".+?">hist</a>\) ‎<a href=".+?" title="(?P<title>.+?)">.+?</a> ‎\[(?P<length>\d+)(.+?)\]</li>')
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
            path = self.shortpages_address(n = number)
            get_throttle()
            html = self.getUrl(path)
            entryR = re.compile(ur'<li>\(<a href=".+?" title=".+?">hist</a>\) ‎<a href=".+?" title="(?P<title>.+?)">.+?</a> ‎\[(?P<length>\d+)(.+?)\]</li>')
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
            path = self.categories_address(n=number)
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
            path = self.deadendpages_address(n=number)
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
            path = self.ancientpages_address(n=number)
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
            path = self.lonelypages_address(n=number)
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

    def unwatchedpages(self, number = 10, repeat = False):
        throttle = True
        seen = set()
        while True:
            path = self.unwatchedpages_address(n=number)
            get_throttle()
            html = self.getUrl(path, sysop = True)
            print html
            entryR = re.compile('<li><a href=".+?" title="(?P<title>.+?)">.+?</a>.+?</li>')
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
            path = self.uncategorizedcategories_address(n=number)
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
            path = self.uncategorizedpages_address(n=number)
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
            path = self.unusedcategories_address(n=number)
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

    def unusedfiles(self, number = 10, repeat = False):
        throttle = True
        seen = set()
        while True:
            path = self.unusedfiles_address(n=number)
            get_throttle()
            html = self.getUrl(path)
            entryR = re.compile('<li>\(<a href=".+?" title="(?P<title>.+?)">.+?</a>\) ')
            for m in entryR.finditer(html):
                title = m.group('title')

                if title not in seen:
                    seen.add(title)
                    page = ImagePage(self, title)
                    yield page
            if not repeat:
                break

    def withoutinterwiki(self, number = 10, repeat = False):
        throttle = True
        seen = set()
        while True:
            path = self.withoutinterwiki_address(n=number)
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

    def allpages(self, start = '!', namespace = 0, includeredirects = True, throttle = True):
        """Generator which yields all articles in the home language in
           alphanumerical order, starting at a given page. By default,
           it starts at '!', so it should yield all pages.

           If includeredirects is False, redirects will not be found.
           If includeredirects equals the string 'only', only redirects
           will be found. Note that this has not been tested on older
           versions of the MediaWiki code.

           The objects returned by this generator are all Page()s.

           It is advised not to use this directly, but to use the
           AllpagesPageGenerator from pagegenerators.py instead.
        """
        while True:
            # encode Non-ASCII characters in hexadecimal format (e.g. %F6)
            start = start.encode(self.encoding())
            start = urllib.quote(start)
            # load a list which contains a series of article names (always 480)
            path = self.allpages_address(start, namespace)
            output(u'Retrieving Allpages special page for %s from %s, namespace %i' % (repr(self), start, namespace))
            returned_html = self.getUrl(path)
            # Try to find begin and end markers
            try:
                # In 1.4, another table was added above the navigational links
                if self.versionnumber() >= 4:
                    begin_s = '</table><hr /><table'
                    end_s = '</table'
                else:
                    begin_s = '<table'
                    end_s = '</table'
                ibegin = returned_html.index(begin_s)
                iend = returned_html.index(end_s,ibegin + 3)
            except ValueError:
                raise ServerError('Couldn\'t extract allpages special page. Make sure you\'re using the MonoBook skin.')
            # remove the irrelevant sections
            returned_html = returned_html[ibegin:iend]
            if self.versionnumber()==2:
                R = re.compile('/wiki/(.*?)\" *class=[\'\"]printable')
            elif self.versionnumber()<5:
                # Apparently the special code for redirects was added in 1.5
                R = re.compile('title ?=\"(.*?)\"')
            elif not includeredirects:
                R = re.compile('\<td\>\<a href=\"\S*\" +title ?="(.*?)"')
            elif includeredirects == 'only':
                R = re.compile('\<td>\<[^\<\>]*allpagesredirect\"\>\<a href=\"\S*\" +title ?="(.*?)"')
            else:
                R = re.compile('title ?=\"(.*?)\"')
            # Count the number of useful links on this page
            n = 0
            for hit in R.findall(returned_html):
                # count how many articles we found on the current page
                n = n + 1
                if self.versionnumber()==2:
                    yield Page(self, url2link(hit, site = self, insite = self))
                else:
                    yield Page(self, hit)
                # save the last hit, so that we know where to continue when we
                # finished all articles on the current page. Append a '!' so that
                # we don't yield a page twice.
                start = Page(self,hit).titleWithoutNamespace() + '!'
            # A small shortcut: if there are less than 100 pages listed on this
            # page, there is certainly no next. Probably 480 would do as well,
            # but better be safe than sorry.
            if n < 100:
                if (not includeredirects) or includeredirects == 'only':
                    # Maybe there were only so few because the rest is or is not a redirect
                    R = re.compile('title ?=\"(.*?)\"')
                    if len(R.findall(returned_html)) < 100:
                        break
                else:
                    break

    def linksearch(self,siteurl):
        # gives a list of page items, being the pages found on a linksearch
        # for site site.
        if siteurl.startswith('*.'):
            siteurl = siteurl[2:]
        for url in [siteurl,"*."+siteurl]:
            path = self.family.linksearch_address(self.lang,url)
            get_throttle()
            html = self.getUrl(path)
            loc = html.find('<div class="mw-spcontent">')
            if loc > -1:
                html = html[loc:]
            loc = html.find('<div class="printfooter">')
            if loc > -1:
                html = html[:loc]
            R = re.compile('title ?=\"(.*?)\"')
            for title in R.findall(html):
                if not siteurl in title: # the links themselves have similar form
                    yield Page(self,title)

    def __repr__(self):
        return self.family.name+":"+self.lang

    def linkto(self, title, othersite = None):
        if othersite and othersite.lang != self.lang:
            return '[[%s:%s]]' % (self.lang, title)
        else:
            return '[[%s]]' % title

    def isInterwikiLink(self, s):
        """
        Try to check whether s is in the form "foo:bar" or ":foo:bar"
        where foo is a known language code or family. In such a case
        we are dealing with an interwiki link.
        Called recursively if the first part of the link refers to this
        site's own family and/or language.
        """
        s = s.lstrip(":")
        if not ':' in s:
            return False
        first, rest = s.split(':',1)
        # interwiki codes are case-insensitive
        first = first.lower().strip()
        # commons: forwards interlanguage links to wikipedia:, etc.
        if self.family.interwiki_forward:
            interlangTargetFamily = Family(self.family.interwiki_forward)
        else:
            interlangTargetFamily = self.family
        if self.getNamespaceIndex(first):
            return False
        if first in interlangTargetFamily.langs:
            if first == self.lang:
                return self.isInterwikiLink(rest)
            else:
                return True
        if first in self.family.known_families:
            if first == self.family.name:
                return self.isInterwikiLink(rest)
            else:
                return True
        return False

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
        Regular expression recognizing redirect pages, with a
        group on the target title.
        """
        try:
            redirKeywords = [u'redirect'] + self.family.redirect[self.lang]
            redirKeywordsR = r'(?:' + '|'.join(redirKeywords) + ')'
        except KeyError:
            # no localized keyword for redirects
            redirKeywordsR = r'redirect'
        # A redirect starts with hash (#), followed by a keyword, then 
        # arbitrary stuff, then a wikilink. The link target ends before
        # either a | or a ].
        return re.compile(r'#' + redirKeywordsR + '.*?\[\[(.*?)(?:\]|\|)', re.IGNORECASE | re.UNICODE | re.DOTALL)

    # The following methods are for convenience, so that you can access
    # methods of the Family class easier.
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

    def query_address(self):
        return self.family.query_address(self.lang)
    def api_address(self):
        return self.family.api_address(self.lang)
    def apipath(self):
        return self.family.apipath(self.lang)

    def protocol(self):
        return self.family.protocol(self.lang)

    def hostname(self):
        return self.family.hostname(self.lang)

    def path(self):
        return self.family.path(self.lang)

    def dbName(self):
        return self.family.dbName(self.lang)

    def move_address(self):
        return self.family.move_address(self.lang)

    def delete_address(self, s):
        return self.family.delete_address(self.lang, s)

    def undelete_view_address(self, s, ts=''):
        return self.family.undelete_view_address(self.lang, s, ts)

    def undelete_address(self):
        return self.family.undelete_address(self.lang)

    def protect_address(self, s):
        return self.family.protect_address(self.lang, s)

    def unprotect_address(self, s):
        return self.family.unprotect_address(self.lang, s)

    def put_address(self, s):
        return self.family.put_address(self.lang, s)

    def get_address(self, s):
        return self.family.get_address(self.lang, s)

    def nice_get_address(self, s):
        return self.family.nice_get_address(self.lang, s)

    def edit_address(self, s):
        return self.family.edit_address(self.lang, s)

    def purge_address(self, s):
        return self.family.purge_address(self.lang, s)

    def block_address(self):
        return self.family.block_address(self.lang)

    def unblock_address(self):
        return self.family.unblock_address(self.lang)

    def blocksearch_address(self, s):
        return self.family.blocksearch_address(self.lang, s)

    def linksearch_address(self, s, limit=500, offset=0):
        return self.family.linksearch_address(self.lang, s, limit=limit, offset=offset)

    def checkCharset(self, charset):
        if not hasattr(self,'charset'):
            self.charset = charset
        assert self.charset.lower() == charset.lower(), "charset for %s changed from %s to %s" % (repr(self), self.charset, charset)
        if self.encoding().lower() != charset.lower():
            raise ValueError("code2encodings has wrong charset for %s. It should be %s, but is %s" % (repr(self), charset, self.encoding()))

    def allpages_address(self, s, ns = 0):
        return self.family.allpages_address(self.lang, start = s, namespace = ns)

    def newpages_address(self, n=50):
        return self.family.newpages_address(self.lang, n)

    def longpages_address(self, n=500):
        return self.family.longpages_address(self.lang, n)

    def shortpages_address(self, n=500):
        return self.family.shortpages_address(self.lang, n)

    def unusedfiles_address(self, n=500):
        return self.family.unusedfiles_address(self.lang, n)

    def categories_address(self, n=500):
        return self.family.categories_address(self.lang, n)

    def deadendpages_address(self, n=500):
        return self.family.deadendpages_address(self.lang, n)

    def ancientpages_address(self, n=500):
        return self.family.ancientpages_address(self.lang, n)

    def lonelypages_address(self, n=500):
        return self.family.lonelypages_address(self.lang, n)

    def unwatchedpages_address(self, n=500):
        return self.family.unwatchedpages_address(self.lang, n)

    def uncategorizedcategories_address(self, n=500):
        return self.family.uncategorizedcategories_address(self.lang, n)

    def uncategorizedpages_address(self, n=500):
        return self.family.uncategorizedpages_address(self.lang, n)

    def unusedcategories_address(self, n=500):
        return self.family.unusedcategories_address(self.lang, n)

    def withoutinterwiki_address(self, n=500):
        return self.family.withoutinterwiki_address(self.lang, n)

    def references_address(self, s):
        return self.family.references_address(self.lang, s)

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

    def __hash__(self):
        return hash(repr(self))

    def version(self):
        return self.family.version(self.lang)

    def versionnumber(self):
        return self.family.versionnumber(self.lang)

    def live_version(self):
        """Return the 'real' version number found on [[Special:Versions]]
           as a tuple (int, int, str) of the major and minor version numbers
           and any other text contained in the version.
        """
        global htmldata
        if not hasattr(self, "_mw_version"):
            versionpage = self.getUrl(self.get_address("Special:Version"))
            htmldata = BeautifulSoup(versionpage, convertEntities="html")
            versionstring = htmldata.findAll(text="MediaWiki"
                                             )[1].parent.nextSibling
            m = re.match(r"^: ([0-9]+)\.([0-9]+)(.*)$", str(versionstring))
            if m:
                self._mw_version = (int(m.group(1)), int(m.group(2)),
                                        m.group(3))
            else:
                self._mw_version = self.family.version(self.lang).split(".")
        return self._mw_version

    def shared_image_repository(self):
        return self.family.shared_image_repository(self.lang)

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

    def contribs_address(self, target, limit=500, offset=''):
        return self.family.contribs_address(self.lang,target,limit,offset)

    def getSite(self, code):
        return getSite(code = code, fam = self.family, user=self.user)

    def namespace(self, num, all = False):
        return self.family.namespace(self.lang, num, all = all)

    def normalizeNamespace(self, value):
        return self.family.normalizeNamespace(self.lang, value)

    def namespaces(self):
        if _namespaceCache.has_key(self):
            return _namespaceCache[self]
        else:
            nslist = []
            for n in self.family.namespaces:
                try:
                    ns = self.family.namespace(self.lang, n)
                except KeyError:
                    # No default namespace defined
                    continue
                if ns is not None:
                    nslist.append(self.family.namespace(self.lang, n))
            _namespaceCache[self] = nslist
            return nslist

    def getNamespaceIndex(self, namespace):
        return self.family.getNamespaceIndex(self.lang, namespace)

    def linktrail(self):
        return self.family.linktrail(self.lang)

    def language(self):
        return self.lang

    def fam(self):
        return self.family

    def sitename(self):
        return self.family.name+':'+self.lang

    def languages(self):
        return self.family.langs.keys()
    
    def validLanguageLinks(self):
        return self._validlanguages

    def disambcategory(self):
        import catlib
        try:
            return catlib.Category(self,self.namespace(14)+':'+self.family.disambcatname[self.lang])
        except KeyError:
            raise NoPage

    def getToken(self, getalways = True, getagain = False, sysop = False):
        if getagain or (getalways and ((sysop and not self._sysoptoken) or (not sysop and not self._token))):
            output(u"Getting page to get a token.")
            try:
                self.sandboxpage.get(force = True, get_redirect = True, sysop = sysop)
                #Page(self, "Non-existing page").get(force = True, sysop = sysop)
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

# Caches to provide faster access
_sites = {}
_namespaceCache = {}

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

def calledModuleName():
    """
    Gets the name of the module calling this function. This is
    required because the -help option loads the module's docstring
    and because the module name will be used for the filename of the
    log.
    """
    # get commandline arguments
    args = sys.argv
    try:
        # clip off the '.py' filename extension
        return args[0][:args[0].rindex('.')]
    except ValueError:
        return args[0]

def handleArgs():
    '''
    Takes the commandline arguments, converts them to Unicode, processes all
    global parameters such as -lang or -log. Returns a list of all arguments
    that are not global. This makes sure that global arguments are applied
    first, regardless of the order in which the arguments were given.
    '''
    global default_code, default_family, verbose
    # get commandline arguments
    args = sys.argv
    # get the name of the module calling this function. This is
    # required because the -help option loads the module's docstring and because
    # the module name will be used for the filename of the log.
    # TODO: check if the following line is platform-independent
    moduleName = calledModuleName()
    nonGlobalArgs = []
    for arg in args[1:]:
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
            put_throttle.setDelay(int(arg[13:]), absolute = True)
        elif arg.startswith('-pt:'):
            put_throttle.setDelay(int(arg[4:]), absolute = True)
        elif arg == '-log':
            setLogfileStatus(True)
        elif arg.startswith('-log:'):
            setLogfileStatus(True, arg[5:])
        elif arg == '-nolog':
            setLogfileStatus(False)
        elif arg == '-verbose' or arg == "-v":
            import version
            output('Pywikipediabot %s' % (version.getversion()))
            output('Python %s' % (sys.version))
            verbose += 1
        else:
            # the argument is not global. Let the specific bot script care
            # about it.
            nonGlobalArgs.append(arg)
    return nonGlobalArgs

#########################
# Interpret configuration
#########################

# search for user interface module in the 'userinterfaces' subdirectory
import wikipediatools as _wt
sys.path.append(_wt.absoluteFilename('userinterfaces'))
exec "import %s_interface as uiModule" % config.userinterface
ui = uiModule.UI()
verbose = 0

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
    if code in ['bar','hsb','ksh']:
        return ['de']
    if code in ['als','lb']:
        return ['de','fr']
    if code=='io':
        return ['eo']
    if code in ['an','ast','ay','ca','gn','nah','qu']:
        return ['es']
    if code == ['cbk-zam']:
        return ['es','tl']
    if code=='eu':
        return ['es','fr']
    if code in ['glk','mzn']:
        return ['fa','ar']
    if code=='gl':
        return ['es','pt']
    if code=='lad':
        return ['es','he']
    if code in ['br','ht','kab','ln','lo','nrm','wa']:
        return ['fr']
    if code in ['ie','oc']:
        return ['ie','oc','fr']
    if code in ['co','frp']:
        return ['fr','it']
    if code=='yi':
        return ['he','de']
    if code=='sa':
        return ['hi']
    if code in ['eml','lij','lmo','nap','pms','roa-tara','sc','scn','vec']:
        return ['it']
    if code=='rm':
        return ['it','de','fr']
    if code in ['bat-smg','ltg']:
        return ['lt']
    if code=='ia':
        return ['la','es','fr','it']
    if code=='nds':
        return ['nds-nl','de']
    if code=='nds-nl':
        return ['nds','nl']
    if code in ['fy','pap','vls','zea']:
        return ['nl']
    if code=='li':
        return ['nl','de']
    if code=='csb':
        return ['pl']
    if code in ['fab','tet']:
        return ['pt']
    if code in ['mo','roa-rup']:
        return ['ro']
    if code in ['av','bxr','cv','hy','lbe','ru-sib','tg','tt','udm','uk','xal']:
        return ['ru']
    if code in ['be','be-x-old']:
        return ['be','be-x-old','ru']
    if code in ['kk','ky','tk']:
        return ['tr','ru']
    if code == 'zh-classic':
        # the database uses 'zh-classic' instead of 'zh-classical' as the field is varchar(10)
        return ['zh-classical','zh','zh-cn','zh-tw']
    if code in ['diq','ug','uz']:
        return ['tr']
    if code in ['ja','minnan','zh','zh-cn']:
        return ['zh','zh-tw','zh-classical','zh-cn']
    if code in ['bo','cdo','hak','wuu','za','zh-cdo','zh-classical','zh-tw','zh-yue']:
        return ['zh','zh-cn','zh-classical','zh-tw']
    if code=='da':
        return ['nb','no']
    if code in ['is','no','nb','nn']:
        return ['no','nb','nn','da','sv']
    if code=='sv':
        return ['da','no','nb']
    if code=='se':
        return ['no','nb','sv','nn','fi','da']
    if code in ['bug','id','jv','map-bms','ms','su']:
        return ['id','ms','jv']
    if code in ['bs','hr','sh']:
        return ['sh','hr','bs','sr']
    if code in ['mk','sr']:
        return ['sh','sr','hr','bs']
    if code in ['ceb','pag','tl','war']:
        return ['tl','es']
    if code=='bi':
        return ['tpi']
    if code=='tpi':
        return ['bi']
    if code == 'new':
        return ['ne']
    if code == 'nov':
        return ['io','eo']
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
        '+': 'lightgreen',
        '-': 'lightred',
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

    result = u''
    lastcolor = None
    for i in range(len(diff)):
        if colors[i] != lastcolor:
            if lastcolor is None:
                result += '\03{%s}' % colors[i]
            else:
                result += '\03{default}'
        lastcolor = colors[i]
        result += diff[i]
    output(result)

def makepath(path):
    """ creates missing directories for the given path and
        returns a normalized absolute version of the path.

    - if the given path already exists in the filesystem
      the filesystem is not modified.

    - otherwise makepath creates directories along the given path
      using the dirname() of the path. You may append
      a '/' to the path if you want it to be a directory path.

    from holger@trillke.net 2002/03/18
    """
    from os import makedirs
    from os.path import normpath,dirname,exists,abspath

    dpath = normpath(dirname(path))
    if not exists(dpath): makedirs(dpath)
    return normpath(abspath(path))

def setLogfileStatus(enabled, logname = None):
    global logfile
    if enabled:
        if not logname:
            logname = '%s.log' % calledModuleName()
        import wikipediatools as _wt
        logfn = _wt.absoluteFilename('logs', logname)
        try:
            logfile = codecs.open(logfn, 'a', 'utf-8')
        except IOError:
            logfile = codecs.open(logfn, 'w', 'utf-8')
    else:
        # disable the log file
        logfile = None

if '*' in config.log or calledModuleName() in config.log:
    setLogfileStatus(True)

colorTagR = re.compile('\03{.*?}', re.UNICODE)

def log(text):
    """
    Writes the given text to the logfile.
    """
    if logfile:
        # remove all color markup
        # TODO: consider pre-compiling this regex for speed improvements
        plaintext = colorTagR.sub('', text)
        # save the text in a logfile (will be written in utf-8)
        logfile.write(plaintext)
        logfile.flush()



output_lock = threading.Lock()
input_lock = threading.Lock()
output_cache = []
def output(text, decoder = None, newline = True, toStdout = False):
    """
    Works like print, but uses the encoding used by the user's console
    (console_encoding in the configuration file) instead of ASCII.
    If decoder is None, text should be a unicode string. Otherwise it
    should be encoded in the given encoding.

    If newline is True, a linebreak will be added after printing the text.

    If toStdout is True, the text will be sent to standard output,
    so that it can be piped to another process. All other text will
    be sent to stderr. See: http://en.wikipedia.org/wiki/Pipeline_%28Unix%29

    text can contain special sequences to create colored output. These
    consist of the escape character \03 and the color name in curly braces,
    e. g. \03{lightpurple}. \03{default} resets the color.
    """
    output_lock.acquire()
    try:
        if decoder:
            text = unicode(text, decoder)
        elif type(text) != type(u''):
            if verbose:
                print "DBG> BUG: Non-unicode passed to wikipedia.output without decoder!"
                print traceback.print_stack()
                print "DBG> Attempting to recover, but please report this problem"
            try:
                text = unicode(text, 'utf-8')
            except UnicodeDecodeError:
                text = unicode(text, 'iso8859-1')
        if newline:
            text += u'\n'
        log(text)
        if input_lock.locked():
            cache_output(text, toStdout = toStdout)
        else:
            ui.output(text, toStdout = toStdout)
    finally:
        output_lock.release()

def cache_output(*args, **kwargs):
    output_cache.append((args, kwargs))

def flush_output_cache():
    while(output_cache):
        (args, kwargs) = output_cache.pop(0)
        ui.output(*args, **kwargs)
        
def input(question, password = False):
    """
    Asks the user a question, then returns the user's answer.

    Parameters:
    * question - a unicode string that will be shown to the user. Don't add a
                 space after the question mark/colon, this method will do this
                 for you.
    * password - if True, hides the user's input (for password entry).

    Returns a unicode string.
    """
    input_lock.acquire()
    try:
        data = ui.input(question, password)
    finally:    
        flush_output_cache()
        input_lock.release()
 
    return data
    
def inputChoice(question, answers, hotkeys, default = None):
    """
    Asks the user a question and offers several options, then returns the
    user's choice. The user's input will be case-insensitive, so the hotkeys
    should be distinctive case-insensitively.

    Parameters:
    * question - a unicode string that will be shown to the user. Don't add a
                 space after the question mark, this method will do this
                 for you.
    * answers  - a list of strings that represent the options.
    * hotkeys  - a list of one-letter strings, one for each answer.
    * default  - an element of hotkeys, or None. The default choice that will
                 be returned when the user just presses Enter.

    Returns a one-letter string in lowercase.
    """
    input_lock.acquire()
    try:
        data = ui.inputChoice(question, answers, hotkeys, default).lower()
    finally:
        flush_output_cache()
        input_lock.release()

    return data

def showHelp(moduleName = None):
    # the parameter moduleName is deprecated and should be left out.
    moduleName = moduleName or sys.argv[0][:sys.argv[0].rindex('.')]
    try:
        moduleName = moduleName[moduleName.rindex("\\")+1:]
    except ValueError: # There was no \ in the module name, so presumably no problem
        pass
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

-nolog            Disable the logfile (if it is enabled by default).

-putthrottle:nn   Set the minimum time (in seconds) the bot will wait between
-pt:n             saving pages.

-verbose          Have the bot provide additional output that may be useful in
-v                debugging.
'''
    output(globalHelp)
    try:
        exec('import %s as module' % moduleName)
        helpText = module.__doc__.decode('utf-8')
        if hasattr(module, 'docuReplacements'):
            for key, value in module.docuReplacements.iteritems():
                helpText = helpText.replace(key, value.strip('\n\r'))
        output(helpText)
    except:
        raise
        output(u'Sorry, no help available for %s' % moduleName)

page_put_queue = Queue.Queue()
def async_put():
    '''
    Daemon that takes pages from the queue and tries to save them on the wiki.
    '''
    while True:
        page, newtext, comment, watchArticle, minorEdit, force = page_put_queue.get()
        if page is None:
            # needed for compatibility with Python 2.3 and 2.4
            # in 2.5, we could use the Queue's task_done() and join() methods
            return
        try:
            page.put(newtext, comment, watchArticle, minorEdit, force)
        except SpamfilterError, ex:
            output(u"Saving page [[%s]] prevented by spam filter: %s"
                   % (page.title(), ex.url))
        except PageNotSaved, ex:
            output(u"Saving page [[%s]] failed: %s"
                   % (page.title(), ex.message))
        except LockedPage, ex:
            output(u"Page [[%s]] is locked; not saved." % page.title())
        except:
            tb = traceback.format_exception(*sys.exc_info())
            output(u"Saving page [[%s]] failed:\n%s"
                    % (page.title(), "".join(tb)))

_putthread = threading.Thread(target=async_put)
# identification for debugging purposes
_putthread.setName('Put-Thread')
_putthread.setDaemon(True)
_putthread.start()
                 
def stopme():
    """This should be run when a bot does not interact with the Wiki, or
       when it has stopped doing so. After a bot has run stopme() it will
       not slow down other bots any more.
    """
    get_throttle.drop()

def _flush():
    '''Wait for the page-putter to flush its queue;
       called automatically upon exiting from Python.
    '''
    if page_put_queue.qsize() > 0:
        import datetime
        remaining = datetime.timedelta(seconds=(page_put_queue.qsize()+1) * config.put_throttle)
        output('Waiting for %i pages to be put. Estimated time remaining: %s' % (page_put_queue.qsize()+1, remaining))
        
    page_put_queue.put((None, None, None, None, None, None))
    
    while(_putthread.isAlive()):
        try:
            _putthread.join(1)
        except KeyboardInterrupt:
            answer = inputChoice(u'There are %i pages remaining in the queue. Estimated time remaining: %s\nReally exit?'
                             % (page_put_queue.qsize(), datetime.timedelta(seconds=(page_put_queue.qsize()) * config.put_throttle)),
                             ['yes', 'no'], ['y', 'N'], 'N')
            if answer in ['y', 'Y']:
                return
    get_throttle.drop()

import atexit
atexit.register(_flush)

def debugDump(name, site, error, data):
    import time
    name = unicode(name)
    error = unicode(error)
    site = unicode(repr(site).replace(u':',u'_'))
    filename = '%s_%s__%s.dump' % (name, site, time.asctime())
    filename = filename.replace(' ','_').replace(':','-')
    f = file(filename, 'wb') #trying to write it in binary   #f = codecs.open(filename, 'w', 'utf-8')
    f.write(u'Error reported: %s\n\n' % error)
    try:
        f.write(data.encode("utf8"))
    except UnicodeDecodeError:
        f.write(data)
    f.close()
    output( u'ERROR: %s caused error %s. Dump %s created.' % (name,error,filename) )

get_throttle = Throttle(config.minthrottle,config.maxthrottle)
put_throttle = Throttle(config.put_throttle,config.put_throttle,False)


class MyURLopener(urllib.FancyURLopener):
    version="PythonWikipediaBot/1.0"

# Special opener in case we are using a site with authentication
if config.authenticate:
    import urllib2, cookielib
    import wikipediatools as _wt
    COOKIEFILE = _wt.absoluteFilename('login-data', 'cookies.lwp')
    cj = cookielib.LWPCookieJar()
    if os.path.isfile(COOKIEFILE):
        cj.load(COOKIEFILE)
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    for site in config.authenticate.keys():
        passman.add_password(None, site, config.authenticate[site][0], config.authenticate[site][1])
    authhandler = urllib2.HTTPBasicAuthHandler(passman)
    authenticateURLopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj),authhandler)
    urllib2.install_opener(authenticateURLopener)

if __name__ == '__main__':
    import version, doctest
    print 'Pywikipediabot %s' % version.getversion()
    print 'Python %s' % sys.version
    doctest.testmod()
    
    
