# -*- coding: utf-8 -*-
"""
Very simple script which gets a page and writes its contents to
standard output. This makes it possible to pipe the text to another
process.

Syntax: python get.py Title of the page

Example: python get.py Wikipedia | grep MediaWiki > results.txt
"""

# (C) Daniel Herding, 2005
#
# Distributed under the terms of the MIT license.

__version__='$Id$'

import wikipedia

def main():
    singlePageTitleParts = []
    for arg in wikipedia.handleArgs():
        singlePageTitleParts.append(arg)

    pageTitle = " ".join(singlePageTitleParts)
    page = wikipedia.Page(wikipedia.getSite(), pageTitle)

    # TODO: catch exceptions
    wikipedia.output(page.get(), toStdout = True)

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()

