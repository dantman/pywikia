# -*- coding: utf-8  -*-
"""
Library to get and put pages on a MediaWiki.

Contents of the library (objects and functions to be used outside, situation
late August 2004)

Classes:
Page: A MediaWiki page
    __init__: Page(xx,Title) - the page with title Title on language xx:
    linkname: The name of the page, in a form suitable for an interwiki link
    urlname: The name of the page, in a form suitable for a URL
    catname: The name of the page, with the namespace part removed
    section: The section of the page (the part of the name after '#')
    sectionFreeLinkname: The name without the section part
    aslink: The name of the page in the form [[family:xx:Title]]
    aslocallink: The name of the pagthroe in the form [[Title]]
    asselflink: The name of the page in the form family:xx:[[Title]]
    
    site: The wiki where this page is in
    encoding: The encoding the page is in

    get (*): The text of the page
    exists (*): True if the page actually exists, false otherwise
    isRedirectPage (*): True if the page is a redirect, false otherwise
    isEmpty (*): True if the page has 4 characters or less content, not
        counting interwiki and category links
    interwiki (*): The interwiki links from the page (list of Pages)
    categories (*): The categories the page is in (list of Pages)
    rawcategories (*): Like categories, but if the link contains a |, the
        part after the | is included.
    links (*): The normal links from the page (list of links)
    imagelinks (*): The pictures on the page (list of strings)
    templates(*): All templates referenced on the page (list of strings)
    getRedirectTo (*): The page the page redirects to
    isCategory: True if the page is a category, false otherwise
    isImage: True if the page is an image, false otherwise
    isDisambig (*): True if the page is a disambiguation page
    getReferences: The pages linking to the page
    namespace: The namespace in which the page is

    put(newtext): Saves the page
    delete: Deletes the page (requires being logged in)

    (*): This loads the page if it has not been loaded before

PageGroup: A group of Pages (internally ordered)
    __init__(list): Create a PageGroup of the list of Pages in list,
        which does not need to be ordered.
    __init__(): Create an empty PageGroup
    contains(pl): Boolean, true iff pl in the PageGroup
    merge(pg): Combine 2 groups
    add(pl): Add the page pl to the PageGroup; give an error if it already
        is in the group
    addforce(pl): Add the page pl to the PageGroup even if it is already in
    remove(pl): Remove all occurences of the page pl from the PageGroup
    remforce(pl): Remove the page pl from the PageGroup if it is in the group
    aslist(): Use the PageGroup as an ordinary list
    show(): Write down the contents of the PageGroup on the screen
    addall(list): Add all Pages from a (not necessarily ordered) list
    getone(): Get any one element
    isEmpty(): True IFF the group is empty

Other functions:
getall(xx,Pages): Get all pages in Pages (where Pages is a list of Pages,
    and xx: the language the pages are on)
PagesFromFile(fn): Get from fn a list of Pages in the form
    [[xx:Title]]
setAction(text): Use 'text' instead of "Wikipedia python library" in
    summaries
forSite(text,xx): Change 'text' such that it is usable on the given site xx
allpages(): Get all page titles in one's home language as Pages (or all
    pages from 'Start' if allpages(start='Start') is used).
checkLogin(): gives True if the bot is logged in on the home language, False
    otherwise
argHandler(text): Checks whether text is an argument defined on wikipedia.py
    (these are -family, -lang, and -log)
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
    with the languages as keys and either Pages or linknames as values
getCategoryLinks(text,xx): get all category links in text 'text' (links in the
    form xx:pagename)
removeCategoryLinks(text,xx): remove all category links in 'text'
replaceCategoryLinks(oldtext,new): replace the category links in oldtext by
    those in new (new a list of category Pages)
stopme(): Put this on a bot when it is not or not any more communicating
    with the Wiki. It will remove the bot from the list of running processes,
    and thus not slow down other bot threads any more.

"""
from __future__ import generators
#
# (C) Rob W.W. Hooft, Andre Engels, 2003-2004
#
# Distribute under the terms of the PSF license.
#
__version__ = '$Id$'
#
import os
import httplib
import socket
import traceback
import time
import math
import difflib
import re, urllib, codecs, sys
import xml.sax, xml.sax.handler
import warnings
import datetime

import config, mediawiki_messages
import htmlentitydefs

import locale
# we'll set the locale to system default. This will ensure correct string
# handling for non-latin characters on Python 2.3.x. For Python 2.4.x it's no
# longer needed.
locale.setlocale(locale.LC_ALL, '')

try:
    set # introduced in Python2.4: faster and future
except NameError:
    from sets import Set as set

# Keep the modification time of all downloaded pages for an eventual put.
# We are not going to be worried about the memory this can take.
edittime = {}

# Local exceptions

class Error(Exception):
    """Wikipedia error"""

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

class NoNamespace(Error):
    """Wikipedia page is not in a special namespace"""

class EditConflict(Error):
    """There has been an edit conflict while uploading the page"""

class PageInList(LookupError):
    """Trying to add page to list that is already included"""

class EmptyGroup(ValueError):
    """PageGroup is empty"""

class NotLoggedIn(Exception):
    """Anonymous editing Wikipedia is not possible"""

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
        title = title.strip()
        if title.startswith(':'):
             title = title[1:]
        title = link2url(title, site = self._site, insite = insite)
        title = title.split('%3A')
        if len(title) > 1:
            # translate a default namespace name into the local namespace name
            for ns in site.family.namespaces.keys():
                if title[0] == site.family.namespace('_default', ns):
                    title[0] = site.namespace(ns)
                    title[0] = link2url (title[0], site = self._site, insite = insite)
            # Capitalize the first non-namespace part
            for ns in site.family.namespaces.keys():
                if title[0] == site.namespace(ns):
                    if not site.nocapitalize:
                        try:
                            title[1] = title[1][0].upper()+title[1][1:]
                        except IndexError: # title[1] is empty
                            print "WARNING: Strange title %s"%'%3A'.join(title)
        title = '%3A'.join(title)
        self._urlname = title
        self._linkname = url2link(self._urlname, site = self._site, insite = self._tosite)

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
        return self._urlname

    def linkname(self, doublex = False):
        """The name of the page this Page refers to, in a form suitable
           for a wiki-link"""
        if doublex:
            ln=self._linkname
            # Double all x-es just to be sure...
            ln = ln.replace('&#265;','cx')
            ln = ln.replace('&#264;','Cx')
            ln = ln.replace('&#285;','gx')
            ln = ln.replace('&#284;','Gx')
            ln = ln.replace('&#293;','hx')
            ln = ln.replace('&#292;','Hx')
            ln = ln.replace('&#309;','jx')
            ln = ln.replace('&#308;','Jx')
            ln = ln.replace('&#349;','sx')
            ln = ln.replace('&#348;','Sx')
            ln = ln.replace('&#365;','ux')
            ln = ln.replace('&#364;','Ux')
            ln = ln.replace('x','xx')
            ln = ln.replace('X','Xx')
            return ln
        else:
            return self._linkname

    def catname(self, doublex = False):
        """The name of the page without the namespace part. Gives an error
        if the page is from the main namespace. Note that this is a raw way
        of doing things - it simply looks for a : in the name."""
        t=self.sectionFreeLinkname(doublex = doublex)
        p=t.split(':')
        p=p[1:]
        if p==[]:
            raise NoNamespace(self)
        return ':'.join(p)

    def section(self):
        """The name of the section this Page refers to. Sections are
           denominated by a # in the linkname(). If no section is referenced,
           None is returned."""
        ln = self.linkname()
        ln = re.sub('&#', '&hash;', ln)
        if not '#' in ln:
            return None
        else:
            hn = ln[ln.find('#') + 1:]
            hn = re.sub('&hash;', '&#', hn)
            return hn

    def sectionFreeLinkname(self, doublex=False):
        hn=self.section()
        ln=self.linkname(doublex=doublex)
        if hn:
            return ln[:-len(hn)-1]
        else:
            return ln
            
    def __str__(self):
        """A console representation of the pagelink"""
        return self.aslink().encode(config.console_encoding, 'replace')

    def __repr__(self):
        """A more complete string representation"""
        return "%s{%s}" % (self.__class__.__name__, str(self))

    def aslink(self, othersite = ()):
        """A string representation in the form of a link. The link will
           be an interwiki link if needed. Specify othersite if you want to
           use the link somewhere else than on the _tosite wiki (e.g. specify
           None to make the link complete."""
        if othersite == ():
            othersite = self._tosite
        return self._site.linkto(self.linkname(), othersite = othersite)

    def aslocallink(self):
        """A string representation in the form of a local link"""
        return "[[%s]]" % (self.linkname())

    def asselflink(self):
        """A string representation in the form of a local link, but prefixed by
           the language"""
        return "%s:[[%s]]" % (self._site.lang, self.linkname())
    
    def get(self, read_only = False, force = False, get_redirect=False, throttle = True):
        """The wiki-text of the page. This will retrieve the page if it has not
           been retrieved yet. This can raise the following exceptions that
           should be caught by the calling code:

            NoPage: The page does not exist

            IsRedirectPage: The page is a redirect. The argument of the
                            exception is the page it redirects to.

            LockedPage: The page is locked, and therefore it won't be possible
                        to change the page. This exception won't be raised
                        if the argument read_only is True.

            SectionError: The subject does not exist on a page with a # link
        """
        if self.site().language() == 'nb':
            return Page(getSite('no'),self.linkname()).get()
        if force:
            # When forcing, we retry the page no matter what. Old exceptions
            # and contents do not apply any more.
            for attr in ['_redirarg','_getexception','_contents']:
                if hasattr(self, attr):
                    delattr(self, attr)
        else:
            # Make sure we re-raise an exception we got on an earlier attempt
            if hasattr(self, '_redirarg'):
                if not get_redirect:
                    raise IsRedirectPage,self._redirarg
            elif hasattr(self, '_getexception'):
                raise self._getexception
        # Make sure we did try to get the contents once
        if not hasattr(self, '_contents'):
            try:
                self._contents, self._isWatched = getEditPage(self.site(), self.urlname(), read_only = read_only, get_redirect = get_redirect, throttle = throttle)
                hn = self.section()
                if hn:
                    hn = underline2space(hn)
                    m = re.search("== *%s *==" % hn, self._contents)
                    if not m:
                        output(u"WARNING: Section does not exist: %s" % self.linkname())
            # Store any exceptions for later reference
            except NoPage:
                self._getexception = NoPage
                raise
            except IsRedirectPage,arg:
                self._getexception = IsRedirectPage
                self._redirarg = arg
                if not get_redirect:
                    raise
            except LockedPage: # won't happen if read_only is True
                self._getexception = LockedPage
                raise
            except SectionError:
                self._getexception = SectionError
                raise
        return self._contents

    def exists(self):
        """True if the page exists (itself or as redirect), False if not"""
        try:
            self.get(read_only = True)
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
            self.get(read_only = True)
        except NoPage:
            return False
        except IsRedirectPage:
            return True
        return False
    
    def isEmpty(self):
        """True if the page except for language links and category links
           has less than 4 characters, False otherwise. Can return the same
           exceptions as get()
        """
        txt = self.get(read_only = True)
        txt = removeLanguageLinks(txt)
        txt = removeCategoryLinks(txt, site = self.site())
        if len(txt) < 4:
            return True
        else:
            return False

    def isCategory(self):
        """True if the page is a Category, false otherwise."""
        t=self.sectionFreeLinkname()
        # Look at the part before the first ':'
        p=t.split(':')
        if p[1:]==[]:
            return False
        if p[0] in self.site().category_namespaces():
            return True
        return False

    def isImage(self):
        """True if the page is an Image description page, false otherwise."""
        t=self.sectionFreeLinkname()
        # Look at the part before the first ':'
        p=t.split(':')
        if p[1:]==[]:
            return False
        if p[0]==self.site().image_namespace():
            return True
        return False

    def namespace(self):
        """Gives the number of the namespace of the page. Does not work for
           all namespaces in all languages, only when defined in family.py.
           If not defined, it will return 0 (the main namespace)"""
        t=self.sectionFreeLinkname()
        p=t.split(':')
        if p[1:]==[]:
            return 0
        for ns in self.site().family.namespaces:
            if p[0]==self.site().namespace(ns):
                return ns
        return 0

    def isDisambig(self):
        defdis = self.site().family.disambig( "_default" )
        locdis = self.site().family.disambig( self._site.lang )

        for tn in self.templates():
            tn = tn[:1].lower() + tn[1:]
            tn = tn.replace('_', ' ')
            if tn in defdis or tn in locdis:
                return True
        return False

    def getReferences(self, follow_redirects = True):
        """
        Returns a list of pages that link to the page.
        If follow_redirects is True, also returns pages
        that link to a redirect pointing to the page.
        """
        site = self.site()
        path = site.references_address(self.urlname())
        
        output(u'Getting references to %s' % (site.linkto(self.linkname())))
        txt = getUrl(site, path)
        # remove brackets which would disturb the regular expression cascadedListR
        # TODO: rewrite regex
        txt = txt.replace('<a', 'a')
        txt = txt.replace('</a', '/a')
        txt = txt.replace('<li', 'li')
        txt = txt.replace('</li', 'li')
        if not follow_redirects:
            # remove these links from HTML which are in an unordered
            # list at level > 1.
            cascadedListR = re.compile(r"(.*<ul>[^<]*)<ul>[^<]*<\/ul>([^<]*</\ul>.*)")
            # current index in txt string
            pos = 0
            while cascadedListR.search(txt):
                m = cascadedListR.search(txt)
                txt = m.group(1) + m.group(2)
        Rref = re.compile('li>a href.*="([^"]*)"')
        refTitles = Rref.findall(txt)
        refTitles.sort()
        refPages = []
        # create list of Page objects, removing duplicates
        for refTitle in refTitles:
            page = Page(site, refTitle)
            if page not in refPages:
                refPages.append(page)
        return refPages

    def put(self, newtext, comment=None, watchArticle = None, minorEdit = True):
        """Replace the new page with the contents of the first argument.
           The second argument is a string that is to be used as the
           summary for the modification

           If watchArticle is None, leaves the watchlist status unchanged.
        """
        if watchArticle == None:
            # if the page was loaded via get(), we know its status
            if hasattr(self, '_isWatched'):
                watchArticle = self._isWatched
            else:
                import watchlist
                watchArticle = watchlist.isWatched(self.linkname())
        if self.exists():
            newPage="0"
        else:
            newPage="1"
        return putPage(self.site(), self.urlname(), newtext, comment, watchArticle, minorEdit, newPage, self.site().getToken())

    def interwiki(self):
        """A list of interwiki links in the page. This will retrieve
           the page text to do its work, so it can raise the same exceptions
           that are raised by the get() method.

           The return value is a list of Page objects for each of the
           interwiki links in the page text.
        """
        result = []
        ll = getLanguageLinks(self.get(read_only = True), insite = self.site())
        for newsite,newname in ll.iteritems():
            if newname[0] == ':':
                print "ERROR> link from %s to %s:%s has leading :?!"%(self,repr(newsite),repr(newname))
            if newname[0] == ' ':
                print "ERROR> link from %s to %s:%s has leading space?!"%(self,repr(newsite),repr(newname))
            for pagenametext in self.site().family.pagenamecodes(self.site().language()):
                newname = newname.replace("{{"+pagenametext+"}}",self.linkname())
            try:
                result.append(self.__class__(newsite, newname, insite = self.site()))
            except UnicodeEncodeError:
                print "ERROR> link from %s to %s:%s is invalid encoding?!"%(self,repr(newsite),repr(newname))
            except NoSuchEntity:
                print "ERROR> link from %s to %s:%s contains invalid character?!"%(self,repr(newsite),repr(newname))
            except ValueError:
                print "ERROR> link from %s to %s:%s contains invalid unicode reference?!"%(self,repr(newsite),repr(newname))
        return result

    def categories(self):
        """A list of categories that the article is in. This will retrieve
           the page text to do its work, so it can raise the same exceptions
           that are raised by the get() method.

           The return value is a list of Page objects for each of the
           category links in the page text."""
        result = []
        ll = getCategoryLinks(self.get(read_only = True), self.site())
        for catname in ll:
            result.append(self.__class__(self.site(), title = catname))
        return result

    def rawcategories(self):
        """Just like categories, but gives the categories including the part
           after the |, if any. Of course these will thus be pagelinks to
           non-existing pages, but as long as we just use linkname() and
           such, that won't matter."""
        result = []
        ll = getCategoryLinks(self.get(read_only = True), self.site(), raw=True)
        for catname in ll:
            result.append(self.__class__(self.site(), title = catname))
        return result
        
    def __cmp__(self, other):
        """Pseudo method to be able to use equality and inequality tests on
           Page objects"""
        if not hasattr(other, 'site'):
            return -1
        if not self.site() == other.site():
            return cmp(self.site(), other.site())
        u1=html2unicode(self.linkname(), site = self.site())
        u2=html2unicode(other.linkname(), site = other.site())
        return cmp(u1,u2)

    def __hash__(self):
        """Pseudo method that makes it possible to store Page objects as
           keys in hash-tables. This relies on the fact that the string
           representation of an instance can not change after the construction.
        """
        return hash(str(self))

    def links(self):
        """Gives the normal (not-interwiki, non-category) pages the page
           links to, as a list of strings
        """
        result = []
        try:
            thistxt = removeLanguageLinks(self.get(read_only = True))
        except IsRedirectPage:
            return
        thistxt = removeCategoryLinks(thistxt, self.site())
        w=r'([^\]\|]*)'
        Rlink = re.compile(r'\[\['+w+r'(\|'+w+r')?\]\]')
        for l in Rlink.findall(thistxt):
            result.append(l[0])
        return result

    def imagelinks(self):
        """Gives the wiki-images the page shows, as a list of pagelink objects
        """
        result = []
        im=self.site().image_namespace() + ':'
        w1=r'('+im+'[^\]\|]*)'
        w2=r'([^\]]*)'
        Rlink = re.compile(r'\[\['+w1+r'(\|'+w2+r')?\]\]')
        for l in Rlink.findall(self.get(read_only = True)):
            result.append(Page(self._site,l[0]))
        w1=r'('+im.lower()+'[^\]\|]*)'
        w2=r'([^\]]*)'
        Rlink = re.compile(r'\[\['+w1+r'(\|'+w2+r')?\]\]')
        for l in Rlink.findall(self.get(read_only = True)):
            result.append(Page(self._site,l[0]))
        if im <> 'Image:':
            im='Image:'
            w1=r'('+im+'[^\]\|]*)'
            w2=r'([^\]]*)'
            Rlink = re.compile(r'\[\['+w1+r'(\|'+w2+r')?\]\]')
            for l in Rlink.findall(self.get(read_only = True)):
                result.append(Page(self._site,l[0]))
            w1=r'('+im.lower()+'[^\]\|]*)'
            w2=r'([^\]]*)'
            Rlink = re.compile(r'\[\['+w1+r'(\|'+w2+r')?\]\]')
            for l in Rlink.findall(self.get(read_only = True)):
                result.append(Page(self._site,l[0]))
        return result

    def templates(self):
        """Gives a list of template names used on a page (strings).
        """
        try:
            thistxt = self.get(read_only = True)
        except IsRedirectPage:
            return []
                
        result = []
        w=r'([^\}\|]*)'
        Rlink = re.compile(r'\{\{'+w+r'(\|'+w+r')?\}\}')
        for l in Rlink.findall(thistxt):
            if l[0].startswith('msg:'):
                result.append(l[0][4:])
            else:
                result.append(l[0])
        return result

    def getRedirectTo(self, read_only = False):
        """
        If the page is a redirect page, gives the title of the page it
        redirects to. Otherwise it will raise an IsNotRedirectPage exception.
        
        This function can raise a NoPage exception, and unless the argument 
        read_only is True, a LockedPage exception as well.
        """
        try:
            self.get(read_only = True)
        except NoPage:
            raise NoPage(self)
        except LockedPage:
            raise LockedPage(self)
        except IsRedirectPage, arg:
            if '|' in arg:
                warnings.warn("%s has a | character, this makes no sense", Warning)
            return arg[0]
        else:
            raise IsNotRedirectPage(self)
            
            
    def getVersionHistory(self, forceReload = False):
        """
        Loads the version history page and returns a list of tuples, where each
        tuple represents one edit and is built of edit date/time, user name, and edit
        summary.
        """
        site = self.site()
        path = site.family.version_history_address(site, self.urlname())

        if not hasattr(self, '_versionhistory') or forceReload:
            output(u'Getting version history of %s' % self.linkname())
            txt = getUrl(site, path)
            self._versionhistory = txt
            
        # regular expression matching one edit in the version history.
        # results will have 3 groups: edit date/time, user name, and edit
        # summary.
        editR = re.compile('<li>.*?<a href=".*?" title=".*?">([^<]*)</a> <span class=\'user\'><a href=".*?" title=".*?">(.*?)</a></span>.*?(?:<em>(.*?)</em>)?</li>')
        edits = editR.findall(self._versionhistory)
        return edits
        
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
                          
    def delete(pl, reason = None, prompt = True):
        """Deletes the page from the wiki. Requires administrator status. If
           reason is None, asks for a reason. If prompt is True, asks the user
           if he wants to delete the page.
        """
        # TODO: Find out if bot is logged in with an admin account, raise exception
        # or show error message otherwise
        # TODO: Find out if deletion was successful or e.g. if file has already been
        # deleted by someone else
    
        # taken from lib_images.py and modified UGLY COPY
        def post_multipart(host, selector, fields, cookies):
            """
            Post fields and files to an http host as multipart/form-data.
            fields is a sequence of (name, value) elements for regular form
            fields. files is a sequence of (name, filename, value) elements for 
            data to be uploaded as files. Return the server's response page.
            """
            content_type, body = encode_multipart_formdata(fields)
            h = httplib.HTTP(host)
            h.putrequest('POST', selector)
            h.putheader('content-type', content_type)
            h.putheader('content-length', str(len(body)))
            h.putheader("User-agent", "PythonWikipediaBot/1.0")
            h.putheader('Host', host)
            if cookies:
                h.putheader('Cookie', cookies)
            h.endheaders()
            h.send(body)
            errcode, errmsg, headers = h.getreply()
            return h.file.read()
        
        # taken from lib_images.py and modified UGLY COPY
        def encode_multipart_formdata(fields):
            """
            fields is a sequence of (name, value) elements for regular form fields.
            files is a sequence of (name, filename, value) elements for data to be uploaded as files
            Return (content_type, body) ready for httplib.HTTP instance
            """
            BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
            CRLF = '\r\n'
            L = []
            for (key, value) in fields:
                L.append('--' + BOUNDARY)
                L.append('Content-Disposition: form-data; name="%s"' % key)
                L.append('')
                L.append(value)
            L.append('--' + BOUNDARY + '--')
            L.append('')
            body = CRLF.join(L)
            content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
            return content_type, body
    
        if reason == None:
            reason = input(u'Please enter a reason for the deletion:', myencoding())
        answer = 'y'
        if prompt:
            answer = input(u'Do you want to delete %s? [y|N]' % pl.linkname())
        if answer in ['y', 'Y']:
            output(u'Deleting page %s...' % pl.linkname())
            token = pl.site().getToken()
            returned_html = post_multipart(pl.site().hostname(),
                                           pl.site().delete_address(pl.urlname()),
                                           (('wpReason', reason),
                                            ('wpConfirm', '1'),
                                            ('wpEditToken', token)),
                            pl.site().cookies())
            # check if deletion was successful
            # therefore, we need to know what the MediaWiki software says after
            # a successful deletion
            deleted_msg = mediawiki_messages.get('actioncomplete')
            deleted_msg = re.escape(deleted_msg)
            deleted_msgR = re.compile(deleted_msg)
            if deleted_msgR.search(returned_html):
                output(u'Deletion successful.')
            else:
                output(u'Deletion failed:.')
                try:
                    ibegin = returned_html.index('<!-- start content -->') + 22
                    iend = returned_html.index('<!-- end content -->')
                except ValueError:
                    # if begin/end markers weren't found, show entire HTML file
                    output(returned_html, myencoding())
                else:
                    # otherwise, remove the irrelevant sections
                    returned_html = returned_html[ibegin:iend]
                output(returned_html, myencoding())

class PageGroup(object):
    # A PageGroup is an ordered set of Page objects

    def __init__(self,list=[]):
        self._list=list
        self._list=self._sorted(self._list)

    def _sorted(self,list):
        # Sorting a list of Pages. We're using mergesort        
        if len(list) <= 1:
            return list
        else:
            i = len(list) // 2
            return self._merge(list[:i],list[i:])

    def _quickmerge(self,l1,l2):
        # Merge two lists by normal means or by repeated inclusion
        # depending on the size of the lists.
        i1 = len(l1)
        i2 = len(l2)
        if i1*i1 < i2:
            return self._adall(l2,l1)
        elif i2*i2 < i1:
            return self._adall(l1,l2)
        else:
            return self._merge(l1,l2)

    def _merge(self,l1,l2):
        if len(l1) == 0:
            return l2
        elif len(l2) == 0:
            return l1
        elif self._compare(l1[0],l2[0]):
            return [l1[0]] + self._merge(l1[1:],l2)
        else:
            return [l2[0]] + self._merge(l1,l2[1:])

    def _compare(self,p1,p2):
        # Compare two pagelinks. True iff p1 <= p2
        if p1.linkname() < p2.linkname():
            return True
        elif p2.linkname() < p1.linkname():
            return False
        elif p1.site().sitename() <= p2.site().sitename():
            return True
        return False

    def _find(self,list,pl):
        # Where in the list could pl be inserted? Returns a pair of numbers
        # [x,y] with x<=y, such that pl[:x] are smaller, pl[y:] are larger
        # and pl[x:y] are equal.
        if len(list) == 0:
            raise EmptyGroup
        if len(list) == 1:
            if list[0] == pl:
                return [0,1]
            elif self._compare(list[0],pl):
                return [1,1]
            else:
                return [0,0]
        else:
            i = len(list) // 2
            if list[i] == pl:
                return [self._findleft(list[:i],pl),i + self._findright(list[i:],pl)]
            elif self._compare(list[i],pl):
                res = self._find(list[i:],pl)
                return [i+res[0], i+res[1]]
            else:
                return self._find(list[:i],pl)

    def _findleft(self,list,pl):
        if len(list) == 1:
            if self._compare(pl,list[0]):
                return 0
            else:
                return 1
        else:
            i = len(list) // 2
            if self._compare(pl,list[i]):
                return self._findleft(list[:i],pl)
            else:
                return self._findleft(list[i:],pl)+i

    def _findright(self,list,pl):
        if len(list) == 1:
            if self._compare(list[0],pl):
                return 1
            else:
                return 0
        else:
            i = len(list) // 2
            if self._compare(list[i],pl):
                return self._findright(list[i:],pl)+i
            else:
                return self._findright(list[:i],pl)


    def _add(self,list,pl,force=False):
        try:
            res = self._find(list,pl)
        except EmptyGroup:
            return [pl]
        x = res[0]
        y = res[1]
        if not force:
            if x != y:
                raise PageInList()
        return(list[:y]+[pl]+list[y:])

    def _addall(self,l1,l2):
        l=l1
        for i in l2:
            l = self._add(l,i)
        return l

    def contains(self,pl):
        try:
            res = self._find(self._list,pl)
        except EmptyGroup:
            return False
        x = res[0]
        y = res[1]
        if x == y:
            return False
        else:
            return True

    def merge(self,pg):
        self._list = self._quickmerge(self._list,pg._list)

    def add(self,pl):
        self._list = self._add(self._list,pl)

    def addforce(self,pl):
        self._list = self._add(self._list,pl,force=True)

    def remove(self,pl):
        try:
            res = self._find(self._list,pl)
        except EmptyGroup:
            pass
        x = res[0]
        y = res[1]
        self._list = self._list[:x] + self._list[y:]

    def aslist(self):
        return self._list

    def show(self):
        for pl in self._list:
            output(u''+pl.linkname())

    def addall(self,pagelist):
        self._list=self._addall(self._list,pagelist)

    def getone(self):
        try:
            return self._list[0]
        except IndexError:
            raise EmptyGroup

    def isEmpty(self):
        return len(self._list) == 0

# Regular expression recognizing redirect pages
def redirectRe(site):
    if site.redirect():
        txt = '(?:redirect|'+'|'.join(site.redirect())+')'
    else:
        txt = 'redirect'
    return re.compile(r'\#'+txt+':? *\[\[(.*?)(\]|\|)', re.I)

# Shortcut get to get multiple pages at once
class WikimediaXmlHandler(xml.sax.handler.ContentHandler):
    def setCallback(self, callback):
        self.callback = callback
        
    def startElement(self, name, attrs):
        self.destination = None
        if name == 'page':
            self.text=u''
            self.title=u''
            self.timestamp=u''
        elif name == 'text':
            self.destination = 'text'
            self.text=u''
        elif name == 'title':
            self.destination = 'title'
            self.title=u''
        elif name == 'timestamp':
            self.destination = 'timestamp'
            self.timestamp=u''

    def endElement(self, name):
        if name == 'revision':
            # All done for this.
            text = self.text
            # Remove trailing newlines and spaces
            while text and text[-1] in '\n ':
                text = text[:-1]
            # Replace newline by cr/nl
            text = u'\r\n'.join(text.split('\n'))
            # Decode the timestamp
            timestamp = (self.timestamp[0:4]+
                         self.timestamp[5:7]+
                         self.timestamp[8:10]+
                         self.timestamp[11:13]+
                         self.timestamp[14:16]+
                         self.timestamp[17:19])
            # Report back to the caller
            self.callback(self.title.strip(), timestamp, text)
            
    def characters(self, data):
        if self.destination == 'text':
            self.text += data
        elif self.destination == 'title':
            self.title += data
        elif self.destination == 'timestamp':
            self.timestamp += data
            
class GetAll(object):
    def __init__(self, site, pages, throttle):
        """First argument is Site object.
        Second argument is list (should have .append and be iterable)"""
        self.site = site
        self.pages = []
        self.throttle = throttle
        for pl in pages:
            if not hasattr(pl,'_contents') and not hasattr(pl,'_getexception'):
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
        handler = WikimediaXmlHandler()
        handler.setCallback(self.oneDone)
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
                if self.site.lang == 'eo':
                    if pl.sectionFreeLinkname() != pl.sectionFreeLinkname(doublex = True):
                        # Maybe we have used x-convention when we should not?
                        try:
                            pl.get(force = True, throttle = self.throttle)
                        except (NoPage, IsRedirectPage, LockedPage, SectionError):
                            pass
                    else:
                        pl._getexception = NoPage
                else:
                    pl._getexception = NoPage
            if hasattr(pl,'_contents') and pl.site().lang=="eo":
                # Edit-pages on eo: use X-convention, XML export does not.
                # Double X-es where necessary so that we can submit a changed
                # page later.
                for c in 'CGHJSU':
                    for c2 in c,c.lower():
                        for x in 'Xx':
                            pl._contents = pl._contents.replace(c2+x,c2+x+x)

    def oneDone(self, title, timestamp, text):
        pl = Page(self.site, title)
        for pl2 in self.pages:
            if Page(self.site, pl2.sectionFreeLinkname()) == pl:
                if not hasattr(pl2,'_contents') and not hasattr(pl2,'_getexception'):
                    break
        else:
            print repr(title)
            print repr(pl)
            print repr(self.pages)
            print "BUG> bug, page not found in list"
            raise PageNotFound
        m = redirectRe(self.site).match(text)
        if m:
            edittime[repr(self.site), link2url(title, site = self.site)] = timestamp
            redirectto=m.group(1)
            if pl.site().lang=="eo":
                for c in 'CGHJSU':
                    for c2 in c,c.lower():
                        for x in 'Xx':
                            redirectto = redirectto.replace(c2+x,c2+x+x+x+x)
            pl2._getexception = IsRedirectPage
            pl2._redirarg = redirectto
        else:
            if len(text)<50:
                output(u"DBG> short text in %s:" % pl2.aslink())
                output(text)
        hn = pl2.section()
        if hn:
            m = re.search("== *%s *==" % hn, text)
            if not m:
                output(u"WARNING: Section does not exist: %s" %pl2.linkname())
            else:
                # Store the content
                pl2._contents = text
                # Store the time stamp
                edittime[repr(self.site), link2url(title, site = self.site)] = timestamp
        else:
            # Store the content
            pl2._contents = text
            # Store the time stamp
            edittime[repr(self.site), link2url(title, site = self.site)] = timestamp

    def getData(self):
        if not self.pages:
            return
        address = self.site.export_address()
        # In the next line, we assume that what we got for eo: is NOT in x-convention
        # but SHOULD be. This is worst-case; to avoid not getting what we need, if we
        # find nothing, we will retry the normal way with an unadapted form.
        pagenames = u'\r\n'.join([x.sectionFreeLinkname(doublex = False) for x in self.pages])
        if type(pagenames) != type(u''):
            print 'Warning: wikipedia.WikipediaXMLHandler.getData() got non-unicode page names. Please report this.'
            print pagenames

        pagenames = forSite(pagenames, self.site)
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
    
def getall(site, pages, throttle = True):
    output(u'Getting %d pages from %s...' % (len(pages), site))
    return GetAll(site, pages, throttle).run()
    
# Library functions

def PagesFromFile(fn, site = None):
    """Read a file of page links between double-square-brackets, and return
       them as a list of Page objects. 'fn' is the name of the file that
       should be read."""
    if site is None:
        site = getSite()
    f=open(fn, 'r')
    R=re.compile(r'\[\[(.*)]\]')
    for line in f.readlines():
        m=R.match(line)
        if m:
            part = m.group(1).split(':')
            i = 0
            try:
                fam=Family(part[i], fatal = False)
                i += 1
            except ValueError:
                fam=site.family
            if part[i] in fam.langs:
                code = part[i]
                i += 1
            else:
                code = site.lang
            pagename = ':'.join(part[i:])
            thesite = getSite(code = code, fam = fam)
            #print "DBG> Pagename", repr(thesite),pagename
            yield Page(thesite, pagename)
        else:
            print "ERROR: Did not understand %s line:\n%s" % (fn, repr(line))
    f.close()
    
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

def putPage(site, name, text, comment = None, watchArticle = False, minorEdit = True, newPage = False, token = None, gettoken = False):
    """Upload 'text' on page 'name' to the 'site' wiki.
       Use of this routine can normally be avoided; use Page.put
       instead.
    """
    safetuple = () # safetuple keeps the old value, but only if we did not get a token yet could
    if site.version() >= "1.4":
        if gettoken or not token:
            token = site.getToken(getagain = gettoken)
        else:
            safetuple = (site,name,text,comment,watchArticle,minorEdit,newPage)
    # Check whether we are not too quickly after the previous putPage, and
    # wait a bit until the interval is acceptable
    put_throttle()
    # Which web-site host are we submitting to?
    host = site.hostname()
    # Get the address of the page on that host.
    address = site.put_address(space2underline(name))
    # If no comment is given for the change, use the default
    if comment is None:
        comment=action
    # Prefix the comment with the user name if the user is not logged in.
    if not site.loggedin():
        print "Anonymous editing is not possible."
        raise NotLoggedIn
    # Use the proper encoding for the comment
    comment = comment.encode(site.encoding())
    try:
        # Encode the text into the right encoding for the wiki
        if type(text) != type(u''):
            print 'Warning: wikipedia.putPage() got non-unicode page content. Please report this.'
            print text
        text = forSite(text, site)
        predata = [
            ('wpSave', '1'),
            ('wpSummary', comment),
            ('wpTextbox1', text)]
        # Except if the page is new, we need to supply the time of the
        # previous version to the wiki to prevent edit collisions
        if newPage and newPage != '0':
            predata.append(('wpEdittime', ''))
        else:
            predata.append(('wpEdittime', edittime[repr(site), link2url(name, site = site)]))
        # Pass the minorEdit and watchArticle arguments to the Wiki.
        if minorEdit and minorEdit != '0':
            predata.append(('wpMinoredit', '1'))
        if watchArticle and watchArticle != '0':
            predata.append(('wpWatchthis', '1'))
        # Give the token, but only if one is supplied.
        if token:
            predata.append(('wpEditToken', token))
        # Encode all of this into a HTTP request
        data = urlencode(tuple(predata))
    
    except KeyError:
        print edittime
	raise
    if newPage and newPage!= '0':
        output(url2unicode("Creating page %s"%site.linkto(name), site = site))
    else:
        output(url2unicode("Changing page %s"%site.linkto(name), site = site))
    # Submit the prepared information
    conn = httplib.HTTPConnection(host)

    conn.putrequest("POST", address)
    conn.putheader('Content-Length', str(len(data)))
    conn.putheader("Content-type", "application/x-www-form-urlencoded")
    conn.putheader("User-agent", "PythonWikipediaBot/1.0")
    if site.cookies():
        conn.putheader('Cookie',site.cookies())
    conn.endheaders()
    conn.send(data)

    # Prepare the return values
    response = conn.getresponse()
    data = response.read()
    conn.close()
    if data != '':
        if "<title>Edit conflict" in data: # FIXME: multi-lingual
            raise EditConflict()
        elif "<title>500 Internal Server Error" in data:
            print "Anonymous editing currently not possible."
            raise NotLoggedIn
        elif safetuple and "<" in data:
            # We might have been using an outdated token
            print "Changing page has failed. Retrying."
            putPage(safetuple[0], safetuple[1], safetuple[2], comment=safetuple[3],
                    watchArticle=safetuple[4], minorEdit=safetuple[5], newPage=safetuple[6],
                    token=None,gettoken=True)
        else:
            output(data, decoder = myencoding())
    return response.status, response.reason, data

def forSite(text, site):
    """Prepare the unicode string 'text' for inclusion into a page for
       wiki 'site'. All of the characters in the text should be encodable,
       otherwise this will fail! This condition is normally met, except if
       you would copy text verbatim from an UTF-8 language into a iso-8859-1
       language, and none of the robots in the package should do such things"""
    if type(text) == type(u''):
        text = text.encode(site.encoding())
    return text

class MyURLopener(urllib.FancyURLopener):
    version="PythonWikipediaBot/1.0"
    
def getUrl(site, path):
    """Low-level routine to get a URL from the wiki.

       site is a Site object, path is the absolute path.

       Returns the HTML text of the page converted to unicode.
    """
    #print host,address
    uo = MyURLopener()
    if site.cookies():
        uo.addheader('Cookie', site.cookies())
    #print ('Opening: http://%s%s'%(host, address))
    f = uo.open('http://%s%s'%(site.hostname(), path))
    text = f.read()
    #print f.info()
    ct = f.info()['Content-Type']
    R = re.compile('charset=([^\'\"]+)')
    m = R.search(ct)
    if m:
        charset = m.group(1)
    else:
        print "WARNING: No character set found"
        # Latin-1 as default
        charset = 'iso8859-1'
    site.checkCharset(charset)
    # convert HTML to unicode
    # TODO: We might want to use error='replace' in case of bad encoding.
    return unicode(text, charset)
    
def getEditPage(site, name, read_only = False, do_quote = True, get_redirect=False, throttle = True):
    """
    Get the contents of page 'name' from the 'site' wiki
    Do not use this directly; for 99% of the possible ideas you can
    use the Page object instead.
   
    Arguments:
        site          - the wiki site
        name          - the page name
        read_only     - If true, doesn't raise LockedPage exceptions.
        do_quote      - ??? (TODO: what is this for?)
        get_redirect  - Get the contents, even if it is a redirect page
 
    This routine returns a unicode string containing the wiki text.
    """
    isWatched = False
    name = re.sub(' ', '_', name)
    output(url2unicode(u'Getting page %s' % site.linkto(name), site = site))
    # A heuristic to encode the URL into %XX for characters that are not
    # allowed in a URL.
    if not '%' in name and do_quote: # It should not have been done yet
        if name != urllib.quote(name):
            print "DBG> quoting",name
        name = urllib.quote(name)
    path = site.edit_address(name)
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
        text = getUrl(site, path)
        get_throttle.setDelay(time.time() - starttime)\

        # Look for the edit token
        R = re.compile(r"\<input type='hidden' value=\"(.*?)\" name=\"wpEditToken\"")
        tokenloc = R.search(text)
        if tokenloc:
            site.puttoken(tokenloc.group(1))
        elif not site.getToken(getalways = False):
            site.puttoken('')

        # Look if the page is on our watchlist
        R = re.compile(r"\<input tabindex='[\d]+' type='checkbox' name='wpWatchthis' checked='checked'")
        matchWatching = R.search(text)
        if matchWatching:
            isWatched = True
        if not read_only:
            # check if we're logged in
            p=re.compile('userlogin')
            if p.search(text) != None:
                output(u'Warning: You\'re probably not logged in on %s:' % repr(site))
        m = re.search('value="(\d+)" name=\'wpEdittime\'',text)
        if m:
            edittime[repr(site), link2url(name, site = site)] = m.group(1)
        else:
            m = re.search('value="(\d+)" name="wpEdittime"',text)
            if m:
                edittime[repr(site), link2url(name, site = site)] = m.group(1)
            else:
                edittime[repr(site), link2url(name, site = site)] = "0"

        # Extract the actual text from the textedit field
        try:
            i1 = re.search('<textarea[^>]*>', text).end()
        except AttributeError:
            # We assume that the server is down. Wait some time, then try again.
            print "WARNING: No text area found on %s%s. Maybe the server is down. Retrying in %i minutes..." % (site.hostname(), path, retry_idle_time)
            time.sleep(retry_idle_time * 60)
            # Next time wait longer, but not longer than half an hour
            retry_idle_time *= 2
            if retry_idle_time > 30:
                retry_idle_time = 30
            continue
        i2 = re.search('</textarea>', text).start()
        if i2-i1 < 2:
            raise NoPage(site, name)
        m = redirectRe(site).match(text[i1:i2])
        if m and not get_redirect:
            output(u"DBG> %s is redirect to %s" % (url2unicode(name, site = site), m.group(1)))
            raise IsRedirectPage(m.group(1))
        if edittime[repr(site), link2url(name, site = site)] == "0" and not read_only:
            output(u"DBG> page may be locked?!")
            raise LockedPage()

        x = text[i1:i2]
        x = unescape(x)
        while x and x[-1] in '\n ':
            x = x[:-1]

        return x, isWatched

def newpages(number = 10, repeat = False, site = None):
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
    if site is None:
        site = getSite()
    seen = set()
    while True:
        path = site.newpages_address()
        get_throttle()
        html = getUrl(site, path)

        # TODO: Use regular expressions!
        entryR = re.compile('<li>(?P<date>.+?) <a href=".+?" title="(?P<title>.+?)">.+?</a> \((?P<length>\d+)(.+?)\) \. \. (?P<loggedin><a href=".+?" title=".+?">)?(?P<username>.+?)(</a>)?( <em>\((?P<comment>.+?)\)</em>)?</li>')
        for m in entryR.finditer(html):
            date = m.group('date')
            title = m.group('title')
            title = title.replace('&quot;', '"')
            length = int(m.group('length'))
            loggedIn = (m.group('loggedin') != None)
            username = m.group('username')
            comment = m.group('comment')

            if title not in seen:
                seen.add(title)
                page = Page(site, title)
                yield page, date, length, loggedIn, username, comment
        if not repeat:
            break

def allpages(start = '!', site = None, namespace = 0, throttle = True):
    """Generator which yields all articles in the home language in
       alphanumerical order, starting at a given page. By default,
       it starts at '!', so it should yield all pages.

       The objects returned by this generator are all Page()s.
    """
    if site == None:
        site = getSite()
    while True:
        # encode Non-ASCII characters in hexadecimal format (e.g. %F6)
        start = link2url(start, site = site)
        # load a list which contains a series of article names (always 480)
        path = site.allpages_address(start, namespace)
        print 'Retrieving Allpages special page for %s from %s, namespace %i' % (repr(site), start, namespace)
        returned_html = getUrl(site, path)
        # Try to find begin and end markers
        try:
            # In 1.4, another table was added above the navigational links
            if site.version() < "1.4":
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
        if site.version()=="1.2":
            R = re.compile('/wiki/(.*?)" *class=[\'\"]printable')
        else:
            R = re.compile('title ?="(.*?)"')
        # Count the number of useful links on this page
        n = 0
        for hit in R.findall(returned_html):
            # count how many articles we found on the current page
            n = n + 1
            if site.version()=="1.2":
                yield Page(site, url2link(hit, site = site, insite = site))
            else:
                yield Page(site, hit)
            # save the last hit, so that we know where to continue when we
            # finished all articles on the current page. Append a '!' so that
            # we don't yield a page twice.
            start = hit + '!'
        # A small shortcut: if there are less than 100 pages listed on this
        # page, there is certainly no next. Probably 480 would do as well,
        # but better be safe than sorry.
        if n < 100:
            break
        
# Part of library dealing with interwiki links

def getLanguageLinks(text, insite = None):
    """Returns a dictionary of other language links mentioned in the text
       in the form {code:pagename}. Do not call this routine directly, use
       Page objects instead"""
    if insite == None:
        insite = getSite()
    result = {}
    # This regular expression will find every link that is possibly an
    # interwiki link.
    # NOTE: This assumes that language codes only consist of non-capital
    # ASCII letters and hyphens.
    interwikiR = re.compile(r'\[\[([a-z\-]+):([^\]]*)\]\]')
    for lang, pagetitle in interwikiR.findall(text):
        if not pagetitle:
            print "ERROR: empty link to %s:" % lang
        # Check if it really is in fact an interwiki link to a known
        # language, or if it's e.g. a category tag or an internal link
        elif lang in insite.family.obsolete:
            lang=insite.family.obsolete[lang]
        if lang in insite.family.langs:
            if '|' in pagetitle:
                # ignore text after the pipe
                pagetitle = pagetitle[:pagetitle.index('|')]
            if insite.lang == 'eo':
                pagetitle=pagetitle.replace('xx','x')
            if not pagetitle:
                output(u"ERROR: ignoring impossible link to %s:%s" % (lang, pagetitle))
            else:
                result[insite.getSite(code=lang)] = pagetitle
    return result

def removeLanguageLinks(text, site = None):
    """Given the wiki-text of a page, return that page with all interwiki
       links removed. If a link to an unknown language is encountered,
       a warning is printed."""
    if site == None:
        site = getSite()
    # This regular expression will find every link that is possibly an
    # interwiki link, plus trailing whitespace. The language code is grouped.
    # NOTE: This assumes that language codes only consist of non-capital
    # ASCII letters and hyphens.
    interwikiR = re.compile(r'\[\[([a-z\-]+):[^\]]*\]\][\s]*')
    # How much of the text we have looked at so far
    index = 0
    done = False
    while not done:
        # Look for possible interwiki links in the remaining text
        match = interwikiR.search(text, index)
        if not match:
            done = True
        else:
            # Extract what would be the language code
            code = match.group(1)
            if code in site.family.langs:
                # We found a valid interwiki link. Remove it.
                text = text[:match.start()] + text[match.end():]
                # continue the search on the remaining text
                index = match.start()
            else:
                index = match.end()
                if len(code) == 2 or len(code) == 3:
                    print "WARNING: Link to unknown language %s" % (match.group(1))
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
        if site.language() in config.interwiki_attop:
            newtext = s + config.interwiki_text_separator + s2
        elif site.language() in config.categories_last:
            cats = getCategoryLinks(s2, site = site)
            s3 = []
            for catname in cats:
                s3.append(Page(site, catname))
            s2 = removeCategoryLinks(s2, site) + config.interwiki_text_separator + s
            newtext = replaceCategoryLinks(s2, s3, site=site)
        else:
            newtext = s2 + config.interwiki_text_separator + s
    else:
        newtext = s2
    return newtext
    
def interwikiFormat(links, insite = None):
    """Create a suitable string encoding all interwiki links for a wikipedia
       page.

       'links' should be a dictionary with the language names as keys, and
       either Page objects or the link-names of the pages as values.

       The string is formatted for inclusion in insite (defaulting to your own).
    """
    if insite is None:
        insite = getSite()
    if not links:
        return ''
    # Security check: site may not refer to itself.
    for pl in links.values():
        if pl==insite.language():
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
                    if not insite.interwiki_putfirst_doubled(ar):
                        del ar[ar.index(site)]
                    ar2 = ar2 + [site]
        ar = ar2 + ar
    for site in ar:
        try:
            s.append(links[site].aslink())
        except AttributeError:
            s.append(site.linkto(links[site],othersite=insite))
    if insite.lang in config.interwiki_on_one_line:
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

def getCategoryLinks(text, site, raw=False):
    """Returns a list of category links.
       in the form {code:pagename}. Do not call this routine directly, use
       Page objects instead"""
    result = []
    ns = site.category_namespaces()
    for prefix in ns:
        if raw:
            R = re.compile(r'\[\['+prefix+':([^\]]*)\]')
        else:
            R = re.compile(r'\[\['+prefix+':([^\]\|]*)(?:\||\])')
        for t in R.findall(text):
            if t:
                # remove leading / trailing spaces
                t = t.strip()
                if site.language() == 'eo':
                    t = t.replace('xx','x')
                t = t[:1].capitalize() + t[1:]
                result.append(ns[0]+':'+t)
            else:
                print "ERROR: empty category link"
    return result

def removeCategoryLinks(text, site):
    """Given the wiki-text of a page, return that page with all category
       links removed. """
    ns = site.category_namespaces()
    for prefix in ns:
        text = re.sub(r'\[\['+prefix+':([^\]]*)\]\]', '', text)
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
    if not site.lang in config.categories_last:
        interwiki_links = getLanguageLinks(oldtext, insite = site)
        oldtext = removeLanguageLinks(oldtext, site = site)
    s = categoryFormat(new, insite = site)
    s2 = removeCategoryLinks(oldtext, site = site)
    if s:
        if site.language() in config.category_attop:
            newtext = s + config.category_text_separator + s2
        else:
            newtext = s2 + config.category_text_separator + s
    else:
        newtext = s2
    # now re-add interwiki links
    if not site.lang in config.categories_last:
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
    result = underline2space(percentname)
    x = url2unicode(result, site = site)
    return unicode2html(x, insite.encoding())
    
def link2url(name, site, insite = None):
    """Convert an interwiki link name of a page to the proper name to be used
       in a URL for that page. code should specify the language for the link"""
    if site.language() == 'eo':
        name = name.replace('cx','&#265;')
        name = name.replace('Cx','&#264;')
        name = name.replace('CX','&#264;')
        name = name.replace('gx','&#285;')
        name = name.replace('Gx','&#284;')
        name = name.replace('GX','&#284;')
        name = name.replace('hx','&#293;')
        name = name.replace('Hx','&#292;')
        name = name.replace('HX','&#292;')
        name = name.replace('jx','&#309;')
        name = name.replace('Jx','&#308;')
        name = name.replace('JX','&#308;')
        name = name.replace('sx','&#349;')
        name = name.replace('Sx','&#348;')
        name = name.replace('SX','&#348;')
        name = name.replace('ux','&#365;')
        name = name.replace('Ux','&#364;')
        name = name.replace('UX','&#364;')
        name = name.replace('XX','X')
        name = name.replace('Xx','X')
        name = name.replace('xx','x')
        name = name.replace('&#265;x','cx')
        name = name.replace('&#264;x','Cx')
        name = name.replace('&#264;X','CX')
        name = name.replace('&#285;x','gx')
        name = name.replace('&#284;x','Gx')
        name = name.replace('&#284;X','GX')
        name = name.replace('&#293;x','hx')
        name = name.replace('&#292;x','Hx')
        name = name.replace('&#292;X','HX')
        name = name.replace('&#309;x','jx')
        name = name.replace('&#308;x','Jx')
        name = name.replace('&#308;X','JX')
        name = name.replace('&#349;x','sx')
        name = name.replace('&#348;x','Sx')
        name = name.replace('&#348;X','SX')
        name = name.replace('&#365;x','ux')
        name = name.replace('&#364;x','Ux')
        name = name.replace('&#364;X','UX')
    if '%' in name:
        # There might be %XX encoding. Just try to decode, if that fails
        # we must ignore the % sign and it is apparently in the title.
        try:
            name = url2unicode(name, site = site)
        except UnicodeError:
            name = html2unicode(name, site = site, altsite = insite)
    else:
        name = html2unicode(name, site = site, altsite = insite)

    #print "DBG>",repr(name)
    # Remove spaces from beginning and the end
    name = name.strip()
    # Standardize capitalization
    if name:
        if not site.nocapitalize:
            name = name[0].upper()+name[1:]
    #print "DBG>",repr(name)
    try:
        result = str(name.encode(site.encoding()))
    except UnicodeError:
        #print "Cannot convert %s into a URL for %s" % (repr(name), code)
        # Put entities in there. The URL will not be found.
        result = addEntity(name)
        #print "Using entities instead",result
        #print "BUG> This is probably a bug in the robot that did not recognize an interwiki link!"
        #raise
    result = space2underline(result)
    return urllib.quote(result)

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
##            if cord in htmlentitydefs.codepoint2name:
##                html.append("&%s;" % htmlentitydefs.codepoint2name[cord])
##            else:
##                html.append('&#%d;'%cord)
    #print
    return ''.join(html)

def url2unicode(percentname, site):
    # Does the input string contain non-ascii characters? In that case,
    # it is not really an url, and we do not have to unquote it....
    for c in percentname:
        if ord(c)>128:
            x=percentname
            break
    else:
        # Before removing the % encoding, make sure it is an ASCII string.
        # unquote doesn't work on unicode strings.
        x=urllib.unquote(str(percentname))
    #print "DBG> ",language,repr(percentname),repr(x)
    # Try utf-8 first. It almost cannot succeed by accident!
    for encoding in ('utf-8',)+site.encodings():
        try:
            encode_func, decode_func, stream_reader, stream_writer = codecs.lookup(encoding)
            x,l = decode_func(x)
            #print "DBG> ",encoding,repr(x)
            return x
        except UnicodeError:
            pass
    raise UnicodeError("Could not decode %s" % repr(percentname))

def unicode2html(x, encoding):
    """
    We have a unicode string. We can attempt to encode it into the desired
    format, and if that doesn't work, we encode the unicode into html #
    entities. If it does work, we return it unchanged.
    """
    try:
        encode_func, decode_func, stream_reader, stream_writer = codecs.lookup(encoding)
        y,l = encode_func(x)
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

def addEntity(name):
    """Convert a unicode name into ascii name with entities"""
    result = ''
    for c in name:
        if ord(c) < 128:
            result += str(c)
        else:
            for k, v in htmlentitydefs.entitydefs.iteritems():
                if (len(v) == 1 and ord(c) == ord(v)) or v == '&#%d;'%ord(c):
                    result += '&%s;' % k
                    break
            else:
                result += '&#%d;' % ord(c)
    #print "DBG> addEntity:", repr(name), repr(result)
    return result

def unicodeName(name, site, altsite = None):
    #print "DBG> ", repr(site), site.encodings()
    for encoding in site.encodings():
        try:
            if type(name)==type(u''):
                return name
            else:
                return unicode(name, encoding)
        except UnicodeError:
            print "UnicodeError"
            print name
            print encoding
            continue
    if altsite is not None:
        print "DBG> Using local encoding!", repr(altsite), "to", repr(site), repr(name)
        for encoding in altsite.encodings():
            try:
                return unicode(name, encoding)
            except UnicodeError:
                continue
    raise Error("Cannot decode")
    #return unicode(name,code2encoding(inlanguage))
    
def html2unicode(name, site, altsite=None):
    name = unicodeName(name, site, altsite)
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
        if self.lang == 'commons':
            self.family._addlang(self.lang,'commons.wikimedia.org',{4:'Commons', 5:'Commons talk'})
        if self.lang not in self.family.langs:
            raise KeyError("Language %s does not exist in family %s"%(self.lang,self.family.name))

        self.nocapitalize = self.lang in self.family.nocapitalize
        self.user = user
        self._token = None
        
    def cookies(self):
        if not hasattr(self,'_cookies'):
            self._fill()
        return self._cookies

    def loggedin(self, check = False):
        if not hasattr(self,'_loggedin'):
            self._fill()
        if check:
            path = self.get_address('Non-existing page')
            txt = getUrl(self, path)
            self._loggedin = 'Userlogin' not in txt
        return self._loggedin

    def _fill(self):
        """Retrieve session cookies for login"""
        #if self.user is None:
        #    u = ""
        #else:
        #    u = self.user + "-"
        #fn = 'login-data/%s-%s-%slogin.data' % (self.family.name, self.lang, u)
        fn = 'login-data/%s-%s-login.data' % (self.family.name, self.lang)
        if not os.path.exists(fn):
            fn = 'login-data/%s-login.data' % self.lang
        if not os.path.exists(fn):
            #print "Not logged in"
            self._cookies = None
            self._loggedin = False
        else:
            f = open(fn)
            self._cookies = '; '.join([x.strip() for x in f.readlines()])
            self._loggedin = True
            f.close()

    def __repr__(self):
        return self.family.name+":"+self.lang
    
    def linkto(self, linkname, othersite = None):
        if not othersite or othersite.family != self.family:
            s = self.family.name+":"
        else:
            s = ""
        if s or othersite.lang!=self.lang:
            s += self.lang+":"
        return "[[" + s + linkname + "]]"

    def encoding(self):
        return self.family.code2encoding(self.lang)

    def encodings(self):
        return self.family.code2encodings(self.lang)

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
        return self.lang in config.category_on_one_line

    def redirect(self,default=False):
        if default:
            return self.family.redirect.get(self.lang,"REDIRECT")
        else:
            return self.family.redirect.get(self.lang,None)
                
    def interwiki_putfirst(self):
        return self.family.interwiki_putfirst.get(self.lang,None)

    def interwiki_putfirst_doubled(self,list_of_links):
        try:
            return len(list_of_links) >= self.family.interwiki_putfirst_doubled[self.lang]
        except:
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
            if ns != None:
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

    def getToken(self, getalways = True, getagain = False):
        if getagain or (getalways and not self._token):
            output(u"Getting page to get a token.")
            try:
                Page(self, url2link("Non-existing page", self, self)).get(force = True)
            except Error:
                pass
        if not self._token:
            return False
        return self._token

    def puttoken(self,value):
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
    
def checkLogin(site = None):
    if not site:
        site = getSite()
    return site.loggedin(check=True)
    
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
        try:
            exec('import %s as module' % moduleName)
            output(module.__doc__, 'utf-8')
        except:
            output(u'Sorry, no help available for %s' % moduleName)
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

# Get the name of the user for submit messages
username = config.username
if not config.username:
    print "Please make a file user-config.py, and put in there:"
    print "One line saying \"username='yy'\""
    print "One line saying \"mylang='xx'\""
    print "....filling in your real name and home wikipedia."
    print "for other possible configuration variables check config.py"
    sys.exit(1)
default_family = config.family
default_code = config.mylang
logfile = None
# Check
getSite()

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
    if code=='lb':
        return ['de','fr']
    if code in ['an','ast','ay','ca','gn','nah','qu']:
        return ['es']
    if code=='eu':
        return ['es','fr']
    if code=='gl':
        return ['es','pt']
    if code in ['br','ht','ln','lo','th','vi','wa']:
        return ['fr']
    if code in ['ie','oc']:
        return ['ie','oc','fr']
    if code=='als':
        return ['fr','de']
    if code=='co':
        return ['fr','it']
    if code in ['sc','scn']:
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
    if code in ['av','be','cv','hy','lt','lv','tt','uk']:
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
        return ['no','nb','nn','da']
    if code=='sv':
        return ['da','no','nb']
    if code=='se':
        return ['no','nb','sv','fi','da','nn']
    if code in ['id','jv','ms','su']:
        return ['id','ms','jv','su']
    if code in ['bs','hr','mk','sh','sr']:
        return ['hr','sr','bs']
    if code=='ia':
        return ['la','es','fr','it']
    if code=='sa':
        return ['hi']
    if code=='yi':
        return ['he']
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

# Taken from interwiki.py. 
def showDiff(oldtext, newtext):
    sep = '\r\n'
    ol = oldtext.split(sep)
    if len(ol) == 1:
        sep = '\n'
        ol = oldtext.split(sep)
    nl = newtext.split(sep)
    for line in difflib.ndiff(ol,nl):
        if line[0] in ['+','-']:
            output(line)

def colorize(text, color):
    if sys.platform=='win32':
        return text
    else:
        return '\x1b[' + color + ';1m' + text + '\x1b[0m'


def showColorDiff(oldtext, newtext):
    """
    Returns a string showing the differences between oldtext and newtext.
    The differences are highlighted (only seems to work on Unix systems) using
    the dictionary replacements, which describes which changes were made.
    If regex is true, the dictionary contents are interpreted as regular
    expressions.
    """
    # For information on difflib, see http://pydoc.org/2.3/difflib.html
    def printLastLine(lastline, lastcolor):
        # highlight the minus red or the plus green
        if lastline != None:
            lastline = colorize(lastline[0], lastcolor) + lastline[1:]
            output(lastline)
        
    # This will store the last line beginning with + or -.
    # It will be printed as soon as a line beginning with a ? or another line
    # starting with + or - occurs.
    lastline = None
    lastcolor = None
    # For testing only: show original diff
    #for line in difflib.ndiff(oldtext.splitlines(), newtext.splitlines()):
    #    output(line)
    for line in difflib.ndiff(oldtext.splitlines(), newtext.splitlines()):
        if line[0] == '-':
            # if lastline wasn't followed by a line starting with ?
            printLastLine(lastline, lastcolor)
            lastline = line
            lastcolor = '91' # red
        elif line[0] == '+':
            printLastLine(lastline, lastcolor)
            lastline = line
            lastcolor = '92' # green
        elif line[0] == '?':
            # iterate backwards over the whole line
            for i in range(len(line)-1, -1, -1):
                # The original diff marks changes with a ^ under the changed
                # part. We'll highlight with colors instead.
                # If the line seperator is changed, the ? line would be one byte
                # longer than the +/- line, causing an out of bounds exception,
                # so we check if i<len(line)-1.
                if line[i] != ' ' and i<len(line)-1:
                    lastline = lastline[:i] + colorize(lastline[i], lastcolor) + lastline[i+1:]
            output(lastline)
            lastline = None
    printLastLine(lastline, lastcolor)
    
def activateLog(logname):
    global logfile
    try:
        logfile = codecs.open('logs/%s' % logname, 'a', 'utf-8')
    except IOError:
        logfile = codecs.open('logs/%s' % logname, 'w', 'utf-8')
    
def output(text, decoder = None, newline = True):
    """Works like print, but uses the encoding used by the user's console
       (console_encoding in the configuration file) instead of ASCII. If
       decoder is None, text should be a unicode string. Otherwise it
       should be encoded in the given encoding."""
    # If a character can't be displayed, it will be replaced with a
    # question mark.
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
    if newline:
        print text.encode(config.console_encoding, 'replace')
    else:
        # comma means 'don't print newline after question'
        print text.encode(config.console_encoding, 'replace'),

def input(question, encode = False, decoder=None):
    """Works like raw_input(), but returns a unicode string instead of ASCII.
       if encode is True, it will encode the entered string into a format
       suitable for the local wiki (utf-8 or iso8859-1). Otherwise it will
       return Unicode. If decoder is None, question should be a unicode
       string. Otherwise it should be encoded in the given encoding.
       Unlike raw_input, this function automatically adds a space after the
       question.
    """
    output(question, decoder=decoder, newline=False)
    text = raw_input()
    text = unicode(text, config.console_encoding)
    if encode:
        text = text.encode(myencoding())
    return text

def stopme():
    """This should be run when a bot does not interact with the Wiki, or
       when it has stopped doing so. After a bot has run stopme() it will
       not slow down other bots any more.
    """
    get_throttle.drop()
