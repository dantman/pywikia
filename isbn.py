#!/usr/bin/python
# -*- coding: utf-8  -*-

"""
This bot goes over multiple pages of the home wiki, and converts all ISBN-10
codes to the ISBN-13 format.

This script understands various command-line arguments:

    -start:        used as -start:page_name, specifies that the robot should
                   go alphabetically through all pages on the home wiki,
                   starting at the named page.

    -file:         used as -file:file_name, read a list of pages to treat
                   from the named textfile. Page titles should be enclosed
                   in [[double-squared brackets]].

    -ref:          used as -start:page_name, specifies that the robot should
                   touch all pages referring to the named page.

    -links:        used as -links:page_name, specifies that the robot should
                   touch all pages referred to from the named page.

    -cat:          used as -cat:category_name, specifies that the robot should
                   touch all pages in the named category.

All other parameters will be regarded as a page title; in this case, the bot
will only touch a single page.

#####################################################################
#                           ATTENTION                               #
#####################################################################
# The ISBN-13 standard is scheduled to be used as of 2007-01-01.    #
# I expect that some libraries and online bookstores will have some #
# problems with the conversion, so we shouldn't start changing      #
# ISBNs at new year's eve.                                          #
# As most online bookstores and library catalogs will probably be   #
# backwards compatible, we shouldn't change anything before all     #
# major sites have managed the conversion process.                  #
#####################################################################

The bot code is unfinished, although the ISBN conversion code seems
to work fine already. --Daniel
"""

__version__='$Id$'

import wikipedia, pagegenerators, catlib, config
import sys

class IsbnBot:
    def __init__(self, generator):
        self.generator = generator

    def run(self):
        for page in self.generator:
            try:
                text = page.get(get_redirect = self.touch_redirects)
                # convert ISBN numbers
                page.put(text)
            except wikipedia.NoPage:
                print "Page %s does not exist?!" % page.aslink()
            except wikipedia.IsRedirectPage:
                print "Page %s is a redirect; skipping." % page.aslink()
            except wikipedia.LockedPage:
                print "Page %s is locked?!" % page.aslink()

def mainBackup():
    #page generator
    gen = None
    # If the user chooses to work on a single page, this temporary array is
    # used to read the words from the page title. The words will later be
    # joined with spaces to retrieve the full title.
    pageTitle = []
    for arg in wikipedia.handleArgs():
        if arg.startswith('-start:'):
            page = wikipedia.Page(wikipedia.getSite(), arg[7:])
            gen = pagegenerators.AllpagesPageGenerator(page.titleWithoutNamespace(), namespace = page.namespace())
        elif arg.startswith('-ref:'):
            referredPage = wikipedia.Page(wikipedia.getSite(), arg[5:])
            gen = pagegenerators.ReferringPageGenerator(referredPage)
        elif arg.startswith('-links:'):
            linkingPage = wikipedia.Page(wikipedia.getSite(), arg[7:])
            gen = pagegenerators.LinkedPageGenerator(linkingPage)
        elif arg.startswith('-file:'):
            gen = pagegenerators.TextfilePageGenerator(arg[6:])
        elif arg.startswith('-cat:'):
            cat = catlib.Category(wikipedia.getSite(), arg[5:])
            gen = pagegenerators.CategorizedPageGenerator(cat)
        # TODO: add -xml: option
        else:
            pageTitle.append(arg)

    if pageTitle:
        # work on a single page
        page = wikipedia.Page(wikipedia.getSite(), ' '.join(pageTitle))
        gen = iter([page])
    if not gen:
        wikipedia.showHelp('isbn')
    else:
        preloadingGen = pagegenerators.PreloadingGenerator(gen)
        bot = IsbnBot(preloadingGen)
        bot.run()

class InvalidIsbnException(wikipedia.Error):
    """Invalid ISBN"""

class ISBN13:
    def __init__(self, isbn10):
        """
        Creates a 13-digit ISBN from a 10-digit ISBN by prefixing the GS1
        prefix '978' and recalculating the checksum.
        The hyphenation structure is taken from the format of the original
        ISBN number.
        TODO: Find out if there is a feasible way to fix hyphenation mistakes.
        Seems to be difficult, as each country/region can set its own
        hyphenation rules. However, the converter at isbn.org knows where to
        place hyphens.
        """
        self.isbn10 = isbn10
        self.isbn10.checkValidity()
        self.code = '978-' + self.isbn10.code[:-1]
        cs = self.calculateChecksum()
        self.code += str(cs)
    
    def digits(self):
        """
        Returns a list of the digits in the ISBN code.
        """
        result = []
        for c in self.code:
            if c.isdigit():
                result.append(int(c))
            elif c != '-':
                raise InvalidIsbnException('The ISBN contains invalid characters.')
        return result
    
    def calculateChecksum(self):
        # See http://en.wikipedia.org/wiki/ISBN#Check_digit_in_ISBN_13
        sum = 0
        for i in range(0, len(self.digits()), 2):
            sum += self.digits()[i]
        for i in range(1, len(self.digits()), 2):
            sum += 3 * self.digits()[i]
        return 10 - (sum % 10)
   
      
class ISBN10:
    def __init__(self, code):
        self.code = code
        self.checkValidity()

    def digits(self):
        """
        Returns a list of the digits and Xs in the ISBN code.
        """
        result = []
        for c in self.code:
            if c.isdigit() or c == 'X':
                result.append(c)
            elif c != '-':
                raise InvalidIsbnException('The ISBN contains invalid characters.')
        return result

    def checkChecksum(self):
        """
        Raises an InvalidIsbnException if the checksum shows that the
        ISBN is incorrect.
        """
        # See http://en.wikipedia.org/wiki/ISBN#Check_digit_in_ISBN_10
        sum = 0
        for i in range(0, 9):
            sum += (i + 1) * int(self.digits()[i])
        #print sum
        checksum = sum % 11
        #print checksum
        lastDigit = self.digits()[-1]
        #print lastDigit
        if not ((checksum == 10 and lastDigit == 'X') or (lastDigit.isdigit() and checksum == int(lastDigit))):
            raise InvalidIsbnException('The checksum is incorrect.')

    def checkValidity(self):
        if len(self.digits()) != 10:
            raise InvalidIsbnException('The ISBN is not 10 digits long.')
        if 'X' in self.digits()[:-1]:
            raise InvalidIsbnException('X is only allowed at the end of the ISBN.')
        self.checkChecksum()

def main():
    # test code
    isbn10 = ISBN10(u'3-86640-001-2')
    isbn13 = ISBN13(isbn10)
    print isbn13.code

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
 
