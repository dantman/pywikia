#!/usr/bin/python

# Edit a Wikipedia article with your favourite editor. Requires Python 2.3.
#
# (C) Gerrit Holl 2004
# Distribute under the terms of the PSF license.

# Version 0.3.
#
# Features:
#       - logging in
#       - editing anonymously
#
# TODO: - non existing pages
#       - correct encoding
#       - use cookies to remember login
#       - edit conflicts
#       - difflib
#       - minor edits
#       - watch/unwatch
#       - ...
#

__version__ = "$Id$"
sig = u" (edited with editarticle.py 0.3)"

import sys
import os
import httplib
import urllib
import string
import getpass
import difflib
import optparse
import tempfile

import wikipedia
import login
import config

class EditArticle(object):
    joinchars = string.letters + '[]' + string.digits # join lines if line starts with this ones

    def __init__(self, args):
        """Takes one argument, usually this is sys.argv[1:]"""
        self.all_args = args
        self.set_options()

    def initialise_data(self):
        """Login, set editor, page and pagelink attributes"""
        self.login(anonymous=self.options.anonymous)
        self.editor = self.options.editor or wikipedia.input(u"Editor to use: ", encode=True)
        self.setpage()

    def login(self, anonymous):
        """Initialises site and username data, or anonymous"""
        if anonymous:
            self.site = wikipedia.getSite(user=None)
        else:
            self.username = self.options.username or wikipedia.input(u"Username: ", encode=True)
            self.site = wikipedia.getSite(user=self.username)
            self.site._fill() # load cookies
            if not self.site._loggedin:
                password = getpass.getpass("Password: ")
                cookie = login.login(self.site, self.username, password)
                if not cookie:
                    sys.exit("Login failed")
                login.storecookiedata(cookie, self.site, self.username)
                wikipedia.output(u"Login succesful")

    def set_options(self):
        """Parse commandline and set options attribute"""
        my_args = []
        for arg in self.all_args:
            arg = wikipedia.argHandler(arg)
            if arg:
                my_args.append(arg)
        parser = optparse.OptionParser()
        parser.add_option("-a", "--anonymous", action="store_true", default=False, help="Login anonymously")
        parser.add_option("-r", "--edit_redirect", action="store_true", default=False, help="Ignore/edit redirects")
        parser.add_option("-u", "--username", help="Username to login with (ignored with -a)")
        parser.add_option("-p", "--page", help="Page to edit")
        parser.add_option("-e", "--editor", help="Editor to use")
        parser.add_option("-j", "--join_lines", action="store_true", default=False, help="Join consecutive lines if possible")
        parser.add_option("-w", "--watch", action="store_true", default=False, help="Watch article after edit")
        parser.add_option("-n", "--new_data", default="", help="Automatically generated content")
        self.options = parser.parse_args(args=my_args)[0]

    def setpage(self):
        """Sets page and pagelink"""
        self.page = self.options.page or wikipedia.input(u"Page to edit: ", encode=True)
        self.pagelink = wikipedia.PageLink(self.site, self.page)
        if not self.options.edit_redirect and self.pagelink.isRedirectPage():
            self.pagelink = wikipedia.PageLink(site, self.pagelink.getRedirectTo())

    def repair(self, content):
        """Removes single newlines and prepare encoding for local wiki"""
        if self.options.join_lines:
            lines = content.splitlines()
            result = []
            for i, line in enumerate(lines):
                try:
                    nextline = lines[i+1]
                except IndexError:
                    nextline = "last"
                result.append(line)
                if line.strip() == "" or line[0] not in self.joinchars or \
                   nextline.strip() == "" or nextline[0] not in self.joinchars:
                    result.append('\n')
                else:
                    result.append(" ")
            s = "".join(result)
        else:
            s = content
        return wikipedia.unicode2html(s, self.site.encoding())

    def edit(self):
        """Edit the page using the editor.
        
        It returns two strings: the old version and the new version."""
        ofn = tempfile.mktemp()
        ofp = open(ofn, 'w')
        try:
            oldcontent = self.pagelink.get()
        except wikipedia.NoPage:
            oldcontent = ""
        except wikipedia.IsRedirectPage:
            if self.options.redirect:
                oldcontent = self.pagelink.get(force=True, get_redirect=redirect)
            else:
                raise
        if self.options.new_data == '':
            ofp.write(oldcontent.encode(config.console_encoding)) # FIXME: encoding of wiki
        else:		
#            ofp.write(oldcontent.encode('utf-8')+'\n===========\n'+self.options.new_data) # FIXME: encoding of wiki
            ofp.write(oldcontent.encode(config.console_encoding)+'\n===========\n'+self.options.new_data) # FIXME: encoding of wiki
        ofp.close()
        os.system("%s %s" % (self.options.editor, ofn))
        newcontent = open(ofn).read().decode(config.console_encoding)
        os.unlink(ofn)
        return oldcontent, newcontent

    def getcomment(self):
        comment = wikipedia.input(u"What did you change? ") + sig
        comment = wikipedia.unicode2html(comment, self.site.encoding())
        return wikipedia.unicode2html(comment, self.site.encoding())

    def handle_edit_conflict(self):
        fn = os.path.join(tempfile.gettempdir(), self.page)
        fp = open(fn, 'w')
        fp.write(new)
        fp.close()
        wikipedia.output(u"An edit conflict has arisen. Your edit has been saved to %s. Please try again." % fn)
    
    def showdiff(self,old, new):
        diff = difflib.context_diff(old.splitlines(), new.splitlines())
        wikipedia.output(u"\n".join(diff))

    def run(self):
        self.initialise_data()
        try:
            old, new = self.edit()
        except wikipedia.LockedPage:
            sys.exit("You do not have permission to edit %s" % self.pagelink.hashfreeLinkname())

        if old != new:
            new = self.repair(new)
            self.showdiff(old, new)
            comment = self.getcomment()
            try:
                self.pagelink.put(new, comment=comment, minorEdit=False, watchArticle=self.options.watch, anon=self.options.anonymous)
            except wikipedia.EditConflict:
                self.handle_edit_conflict()
        else:
            wikipedia.output(u"Nothing changed")

def main():
    app = EditArticle(sys.argv[1:])
    app.run()

if __name__ == "__main__":
    try:
        main()
    except:
        wikipedia.stopme()
        raise
    wikipedia.stopme()

