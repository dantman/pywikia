#!/usr/bin/python

# Edit a Wikipedia article with your favourite editor. Requires Python 2.3.
#
# (C) Gerrit Holl 2004
# Distribute under the terms of the PSF license.

# Version 0.2.
#
# Features:
#       - logging in
#       - editing anonymously
#
# TODO: - non existing pages
#       - correct encoding
#       - use cookies to remember login
#       - edit conflict
#       - difflib
#       - minor edits
#       - watch/unwatch
#       - remove tmpfiles (post-edit crash however...?)
#       - ...
#

__version__ = "$Id$"
sig = u" (edited with editarticle.py 0.2)"

import sys
import os
import httplib
import urllib
import getpass
import difflib
import optparse
import tempfile

import wikipedia
import login
import config

def options(args):
    parser = optparse.OptionParser()
    parser.add_option("-a", "--anonymous", action="store_true", default=False, help="Login anonymously")
    parser.add_option("-r", "--edit_redirect", action="store_true", default=False, help="Ignore (edit) redirects")
    parser.add_option("-u", "--username", help="Username to login with (ignored with -a)")
    parser.add_option("-p", "--page", help="Page to edit")
    parser.add_option("-e", "--editor", help="Editor to use")
    parser.add_option("-w", "--watch", action="store_true", default=False, help="Watch article after edit")
##    parser.add_option("-p", "--password", help="Password to login with")
    return parser.parse_args(args=args)

def editpage(pl, editor, redirect=False):
    """Edit a pagelink using an editor.
    
    Takes two arguments: page and editor.
    
    It returns two strings: the old version and the new version."""
    ofn = tempfile.mktemp()
    ofp = open(ofn, 'w')
    try:
        oldcontent = pl.get()
    except wikipedia.NoPage:
        oldcontent = ""
    except wikipedia.IsRedirectPage:
        if redirect:
            oldcontent = pl.get(force=True, get_redirect=redirect)
        else:
            raise
    ofp.write(oldcontent.encode(config.console_encoding)) # FIXME: encoding of wiki
    ofp.close()
    os.system("%s %s" % (editor, ofn))
    newcontent = open(ofn).read().decode(config.console_encoding)
    return oldcontent, newcontent

def main():
    args = []
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg)
        if arg:
            args.append(arg)
    opts, otherargs = options(args)
    if opts.anonymous:
        site = wikipedia.getSite()
    else:
        username = opts.username or wikipedia.input(u"Username: ", encode=True)
        site = wikipedia.getSite(user=opts.username)
        password = getpass.getpass("Password: ")
        cookie = login.login(site, username, password)
        if cookie:
            login.storecookiedata(cookie, site, username)
            wikipedia.output(u"Login succesful")
        else:
            sys.exit("Login failed")

    page = opts.page or wikipedia.input(u"Page to edit: ", encode=True)
    editor = opts.editor or wikipedia.input(u"Editor to use: ", encode=True)
    pl = wikipedia.PageLink(site, page)
    if not opts.edit_redirect and pl.isRedirectPage():
        pl = wikipedia.PageLink(site, pl.getRedirectTo())
    try:
        old, new = editpage(pl, editor, redirect=opts.edit_redirect)
    except wikipedia.LockedPage:
        sys.exit("You do not have permission to edit %s" % pl.hashfreeLinkname())
    if old != new:
        diff = difflib.context_diff(old.splitlines(), new.splitlines())
        wikipedia.output("\n".join(diff))
        print "watching:", opts.watch
        comment = wikipedia.input(u"What did you change? ") + sig
        print repr(comment)
        comment = wikipedia.unicode2html(comment, site.encoding())
        new = wikipedia.unicode2html(new, site.encoding())
        pl.put(new, comment=wikipedia.unicode2html(comment, site.encoding()), minorEdit=False, watchArticle=opts.watch, anon=opts.anonymous)
    else:
        wikipedia.output(u"Nothing changed")


if __name__ == "__main__":
    main()
