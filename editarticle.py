#!/usr/bin/python

# Edit a Wikipedia article with your favourite editor. Requires Python 2.3.
#
# (C) Gerrit Holl 2004
# Distribute under the terms of the PSF license.

# Version 0.1.
#
# TODO: - logging in
#       - correct encoding
#       - ...
#

__version__ = "$Id$"

import sys
import os
import getpass
import optparse
import tempfile

import wikipedia

def options(args):
    parser = optparse.OptionParser()
    parser.add_option("-a", "--anonymous", action="store_true", default=False, help="Login anonymously")
    parser.add_option("-u", "--username", help="Username to login with (ignored with -a)")
    parser.add_option("-p", "--page", help="Page to edit")
    parser.add_option("-e", "--editor", help="Editor to use")
##    parser.add_option("-p", "--password", help="Password to login with")
    return parser.parse_args(args=args)

def main():
    args = []
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg)
        if arg:
            args.append(arg)
    opts, otherargs = options(args)
    if not opts.anonymous:
        raise NotImplementedError("logging in is not implemented yet, please use -a")
    page = opts.page or raw_input("Page to edit: ")
    editor = opts.editor or raw_input("Editor to use: ")
    pl = wikipedia.PageLink(wikipedia.getSite(), page)
    ofn = tempfile.mktemp()
    ofp = open(ofn, 'w')
    oldcontent = pl.get()
    ofp.write(oldcontent.encode('utf-8')) # FIXME: encoding of wiki
    ofp.close()
    os.system("%s %s" % (editor, ofn))
    newcontent = open(ofn).read().decode('utf-8')
    if oldcontent != newcontent:
        pl.put(newcontent, comment=raw_input("What did you change? "), anon=True)
    else:
        print "Nothing changed"


if __name__ == "__main__":
    main()
