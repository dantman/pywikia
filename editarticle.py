#!/usr/bin/python

# Edit a Wikipedia article with your favourite editor. Requires Python 2.3.
#
# (C) Gerrit Holl 2004
# Distributed under the terms of the MIT license.

# Version 0.4.
#
# TODO: - non existing pages
#       - edit conflicts
#       - minor edits
#       - watch/unwatch
#       - ...

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

class TextEditor:
    def __init__(self):
        pass

    def command(self, tempFilename, text, jumpIndex = None):
        command = config.editor
        if jumpIndex:
            # Some editors make it possible to mark occurences of substrings, or
            # to jump to the line of the first occurence.
            # TODO: Find a better solution than hardcoding these, e.g. a config
            # option.
            line = text[:jumpIndex].count('\n')
            column = jumpIndex - (text[:jumpIndex].rfind('\n') + 1)
        else:
            line = column = 0
        if config.editor == 'kate':
            command += " -l %i -c %i" % (line, column)
        elif config.editor == 'gedit':
            command += " +%i" % (line + 1) # seems not to support columns
        elif config.editor == 'emacs':
            command += " +%i" % (line + 1) # seems not to support columns
        elif config.editor == 'jedit':
            command += " +line:%i" % (line + 1) # seems not to support columns
        elif config.editor == 'vim':
            command += " +%i" % (line + 1) # seems not to support columns
        elif config.editor == 'nano':
            command += " +%i,%i" % (line + 1, column + 1)
        command += ' %s' % tempFilename
        #print command
        return command

    def edit(self, text, jumpIndex = None, highlight = None):
        """
        Calls the editor and thus allows the user to change the text.
        Returns the modified text. Halts the thread's operation until the editor
        is closed.
        
        Returns None if the user didn't save the text file in his text editor.
        
        Parameters:
            * text      - a Unicode string
            * jumpIndex - an integer: position at which to put the caret
            * highlight - a substring; each occurence will be highlighted
        """
        if config.editor:
            tempFilename = '%s.%s' % (tempfile.mktemp(), config.editor_filename_extension)
            tempFile = open(tempFilename, 'w')
            tempFile.write(text.encode(config.editor_encoding))
            tempFile.close()
            creationDate = os.stat(tempFilename).st_mtime
            command = self.command(tempFilename, text, jumpIndex)
            os.system(command)
            lastChangeDate = os.stat(tempFilename).st_mtime
            if lastChangeDate == creationDate:
                # Nothing changed
                return None
            else:
                newcontent = open(tempFilename).read().decode(config.editor_encoding)
                os.unlink(tempFilename)
                return newcontent
        else:
            return wikipedia.ui.editText(text, jumpIndex = jumpIndex, highlight = highlight)

class ArticleEditor:
    joinchars = string.letters + '[]' + string.digits # join lines if line starts with this ones

    def __init__(self):
        self.set_options()
        self.setpage()
        self.site = wikipedia.getSite()

    def set_options(self):
        """Parse commandline and set options attribute"""
        my_args = []
        for arg in wikipedia.handleArgs():
            my_args.append(arg)
        parser = optparse.OptionParser()
        parser.add_option("-r", "--edit_redirect", action="store_true", default=False, help="Ignore/edit redirects")
        parser.add_option("-p", "--page", help="Page to edit")
        parser.add_option("-w", "--watch", action="store_true", default=False, help="Watch article after edit")
        #parser.add_option("-n", "--new_data", default="", help="Automatically generated content")
        (self.options, args) = parser.parse_args(args=my_args)

        # for convenience, if we have an arg, stuff it into the opt, so we
        # can act like a normal editor.
        if (len(args) == 1):
            self.options.page = args[0]

    def setpage(self):
        """Sets page and page title"""
        site = wikipedia.getSite()
        pageTitle = self.options.page or wikipedia.input(u"Page to edit:")
        self.page = wikipedia.Page(site, pageTitle)
        if not self.options.edit_redirect and self.page.isRedirectPage():
            self.page = wikipedia.Page(site, self.page.getRedirectTarget())

    def repair(self, content):
        """
        Removes single newlines.
        """
        #####
        # This method was disabled because its functionality belong into
        # cosmetic_changes.py, not here.
        return content
        #
        #####
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
        return s

    def handle_edit_conflict(self):
        fn = os.path.join(tempfile.gettempdir(), self.page.title())
        fp = open(fn, 'w')
        fp.write(new)
        fp.close()
        wikipedia.output(u"An edit conflict has arisen. Your edit has been saved to %s. Please try again." % fn)
    
    def run(self):
        try:
            old = self.page.get(get_redirect = self.options.edit_redirect)
        except wikipedia.NoPage:
            old = ""
        textEditor = TextEditor()
        new = textEditor.edit(old)
        if new and old != new:
            new = self.repair(new)
            wikipedia.showDiff(old, new)
            comment = wikipedia.input(u"What did you change?") + sig
            try:
                self.page.put(new, comment = comment, minorEdit = False, watchArticle=self.options.watch)
            except wikipedia.EditConflict:
                self.handle_edit_conflict(new)
        else:
            wikipedia.output(u"Nothing changed")

def main():
    app = ArticleEditor()
    app.run()

if __name__ == "__main__":
    try:
        main()
    except:
        wikipedia.stopme()
        raise
    wikipedia.stopme()

