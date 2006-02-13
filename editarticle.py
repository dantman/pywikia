#!/usr/bin/python

# Edit a Wikipedia article with your favourite editor. Requires Python 2.3.
#
# (C) Gerrit Holl 2004
# Distributed under the terms of the MIT license.

# Version 0.4.
#
# TODO: - non existing pages
#       - correct encoding
#       - use cookies to remember login
#       - edit conflicts
#       - minor edits
#       - watch/unwatch
#       - ...
#
# Removed features:
#       - editing anonymously

__metaclass__ = type
__version__ = "$Id$"
sig = u" (edited with editarticle.py 0.4)"

import sys
import os
import string
import optparse
import tempfile

import wikipedia
import config

class EditArticle:
    joinchars = string.letters + '[]' + string.digits # join lines if line starts with this ones

    def __init__(self, args):
        """Takes one argument, usually this is sys.argv[1:]"""
        self.all_args = args
        self.set_options()
        self.site = wikipedia.getSite()

    def initialise_data(self):
        """Set editor, page and pagelink attributes"""
        self.editor = self.options.editor or wikipedia.input(u"Editor to use:")
        self.setpage()

    def set_options(self):
        """Parse commandline and set options attribute"""
        my_args = []
        for arg in self.all_args:
            arg = wikipedia.argHandler(arg, 'editarticle')
            if arg:
                my_args.append(arg)
        parser = optparse.OptionParser()
##        parser.add_option("-a", "--anonymous", action="store_true", default=False, help="Login anonymously")
        parser.add_option("-r", "--edit_redirect", action="store_true", default=False, help="Ignore/edit redirects")
        parser.add_option("-p", "--page", help="Page to edit")
        parser.add_option("-e", "--editor", help="Editor to use")
        parser.add_option("-j", "--join_lines", action="store_true", default=False, help="Join consecutive lines if possible")
        parser.add_option("-w", "--watch", action="store_true", default=False, help="Watch article after edit")
        parser.add_option("-n", "--new_data", default="", help="Automatically generated content")
        self.options = parser.parse_args(args=my_args)[0]

    def setpage(self):
        """Sets page and pagelink"""
        self.page = self.options.page or wikipedia.input(u"Page to edit:")
        self.pagelink = wikipedia.Page(self.site, self.page)
        if not self.options.edit_redirect and self.pagelink.isRedirectPage():
            self.pagelink = wikipedia.Page(site, self.pagelink.getRedirectTarget())

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
        os.system("%s %s" % (self.editor, ofn))
        newcontent = open(ofn).read().decode(config.console_encoding)
        os.unlink(ofn)
        return oldcontent, newcontent

    def getcomment(self):
        comment = wikipedia.input(u"What did you change? ") + sig
        return comment

    def handle_edit_conflict(self):
        fn = os.path.join(tempfile.gettempdir(), self.page)
        fp = open(fn, 'w')
        fp.write(new)
        fp.close()
        wikipedia.output(u"An edit conflict has arisen. Your edit has been saved to %s. Please try again." % fn)
    
    def run(self):
        self.initialise_data()
        old, new = self.edit()
        if old != new:
            new = self.repair(new)
            wikipedia.showDiff(old, new)
            comment = self.getcomment()
            try:
                self.pagelink.put(new, comment=comment, minorEdit=False, watchArticle=self.options.watch)#, anon=self.options.anonymous)
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

