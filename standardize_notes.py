# -*- coding: utf-8  -*-
"""
This bot will standardize footnote references. It will retrieve information on
which pages might need changes either from an SQL dump or a text file, or only
change a single page.

At present it converts to [[Wikipedia:Footnote3]] format (ref/note).

You can run the bot with the following commandline parameters:

-sql         - Retrieve information from a local SQL dump (cur table, see
               http://download.wikimedia.org).
               Argument can also be given as "-sql:filename".
-file        - Work on all pages given in a local text file.
               Will read any [[wiki link]] and use these articles.
               Argument can also be given as "-file:filename".
-cat         - Work on all pages which are in a specific category.
               Argument can also be given as "-cat:categoryname".
-page        - Only edit a single page.
               Argument can also be given as "-page:pagename". You can give this
               parameter multiple times to edit multiple pages.
-regex       - Make replacements using regular expressions.  (Obsolete; always True)
-except:XYZ  - Ignore pages which contain XYZ. If the -regex argument is given,
               XYZ will be regarded as a regular expression.
-namespace:n - Namespace to process. Works only with a sql dump
-always      - Don't prompt you for each replacement
other:       - First argument is the old text, second argument is the new text.
               If the -regex argument is given, the first argument will be
               regarded as a regular expression, and the second argument might
               contain expressions like \\1 or \g<name>.
      
NOTE: Only use either -sql or -file or -page, but don't mix them.
"""
# Derived from replace.py
#
# (C) Daniel Herding, 2004
# Copyright Scot E. Wilcoxon 2005
#
# Distributed under the terms of the PSF license.
#
__version__ = '$Id$'
#

from __future__ import generators
import sys, re, random
import socket, urllib2
import wikipedia, pagegenerators, config

from datetime import date

# Summary messages in different languages
msg = {
       'de':u'Bot: Automatisierte Textersetzung %s',
       'en':u'Robot: Automated reference formatting %s',
       'es':u'Robot: Reemplazo automático de texto %s',
       'fr':u'Bot : Remplacement de texte automatisé %s',
       'hu':u'Robot: Automatikus szövegcsere %s',
       'is':u'Vélmenni: breyti texta %s',
       'pt':u'Bot: Mudança automática %s',
       }

fixes = {
    # These replacements will convert alternate reference formats to format used by this tool. 
    'ALTREFS': {
        'regex': True,
        # We don't want to mess up pages which discuss HTML tags, so we skip
        # all pages which contain nowiki tags.
        'exceptions':  ['<nowiki>'],
        'msg': {
               'en':u'Robot: converting/fixing footnotes',
              },
        'replacements': [
            # Everything case-insensitive (?i)
            # These translate variations of footnote templates to ref|note format.
            (r'(?i){{an\|(.*?)}}':              r"{{ref|\1}}"),
            (r'(?i){{anb\|(.*?)}}':             r"{{note|\1}}"),
            (r'(?i){{endnote\|(.*?)}}':         r"{{note|\1}}"),
            (r'(?i){{fn\|(.*?)}}':              r"{{ref|fn\1}}"),
            (r'(?i){{fnb\|(.*?)}}':             r"{{note|fn\1}}"),
            r'(?i){{mn\|(.*?)\|(.*?)}}':              r"{{ref|mn\1_\2}}"),
            r'(?i){{mnb\|(.*?)\|(.*?)}}':             r"{{note|mn\1_\2}}"),
            # a header where only spaces are in the same line
            r'(?i)([\r\n]) *<h1> *([^<]+?) *</h1> *([\r\n])':  r"\1= \2 =\3"),
            r'(?i)([\r\n]) *<h2> *([^<]+?) *</h2> *([\r\n])':  r"\1== \2 ==\3"),
            r'(?i)([\r\n]) *<h3> *([^<]+?) *</h3> *([\r\n])':  r"\1=== \2 ===\3"),
            r'(?i)([\r\n]) *<h4> *([^<]+?) *</h4> *([\r\n])':  r"\1==== \2 ====\3"),
            r'(?i)([\r\n]) *<h5> *([^<]+?) *</h5> *([\r\n])':  r"\1===== \2 =====\3"),
            r'(?i)([\r\n]) *<h6> *([^<]+?) *</h6> *([\r\n])':  r"\1====== \2 ======\3"),
        ]
    }
}

class ReplacePageGenerator:
    """
    Generator which will yield Pages for pages that might contain text to
    replace. These pages might be retrieved from a local SQL dump file or a
    text file, or as a list of pages entered by the user.

    Arguments:
        * source       - Where the bot should retrieve the page list from.
                         Can be 'sqldump', 'textfile' or 'userinput'.
        * replacements - A dictionary where keys are original texts and values
                         are replacement texts.
        * exceptions   - A list of strings; pages which contain one of these
                         won't be changed.
        * regex        - If the entries of replacements and exceptions should
                         be interpreted as regular expressions
        * namespace    - Namespace to process in case of a SQL dump. -1 means
                         that all namespaces should be searched.
        * textfilename - The textfile's path, either absolute or relative, which
                         will be used when source is 'textfile'.
        * sqlfilename  - The dump's path, either absolute or relative, which
                         will be used when source is 'sqldump'.
        * pagenames    - a list of pages which will be used when source is
                         'userinput'.
    """
    def __init__(self, source, replacements, exceptions, regex = False, namespace = -1, textfilename = None, sqlfilename = None, categoryname = None, pagenames = None):
        self.source = source
        self.replacements = replacements
        self.exceptions = exceptions
        self.regex = regex
        self.namespace = namespace
        self.textfilename = textfilename
        self.sqlfilename = sqlfilename
        self.categoryname = categoryname
        self.pagenames = pagenames
    
    def read_pages_from_sql_dump(self):
        """
        Generator which will yield Pages to pages that might contain text to
        replace. These pages will be retrieved from a local sql dump file
        (cur table).
    
        Arguments:
            * sqlfilename  - the dump's path, either absolute or relative
            * replacements - a dictionary where old texts are keys and new texts
                             are values
            * exceptions   - a list of strings; pages which contain one of these
                             won't be changed.
            * regex        - if the entries of replacements and exceptions should
                             be interpreted as regular expressions
        """
        mysite = wikipedia.getSite()
        import sqldump
        dump = sqldump.SQLdump(self.sqlfilename, wikipedia.myencoding())
        for entry in dump.entries():
            skip_page = False
            if self.namespace != -1 and self.namespace != entry.namespace:
                continue
            else:
                for exception in self.exceptions:
                    if self.regex:
                        exception = re.compile(exception)
                        if exception.search(entry.text):
                            skip_page = True
                            break
                    else:
                        if entry.text.find(exception) != -1:
                            skip_page = True
                            break
            if not skip_page:
                for old, new in self.replacements:
                    if self.regex:
                        old = re.compile(old)
                        if old.search(entry.text):
                            yield wikipedia.Page(mysite, entry.full_title())
                            break
                    else:
                        if entry.text.find(old) != -1:
                            yield wikipedia.Page(mysite, entry.full_title())
                            break
    
    def read_pages_from_category(self):
        """
        Generator which will yield pages that are listed in a text file created by
        the bot operator. Will regard everything inside [[double brackets]] as a
        page name, and yield Pages for these pages.
    
        Arguments:
            * textfilename - the textfile's path, either absolute or relative
        """
        import catlib
        category = catlib.Category(wikipedia.getSite(), self.categoryname)
        for page in category.articles(recurse = False):
            yield page

    def read_pages_from_text_file(self):
        """
        Generator which will yield pages that are listed in a text file created by
        the bot operator. Will regard everything inside [[double brackets]] as a
        page name, and yield Pages for these pages.
    
        Arguments:
            * textfilename - the textfile's path, either absolute or relative
        """
        f = open(self.textfilename, 'r')
        # regular expression which will find [[wiki links]]
        R = re.compile(r'.*\[\[([^\]]*)\]\].*')
        m = False
        for line in f.readlines():
            # BUG: this will only find one link per line.
            # TODO: use findall() instead.
            m=R.match(line)
            if m:
                yield wikipedia.Page(wikipedia.getSite(), m.group(1))
        f.close()
    
    def read_pages_from_wiki_page(self):
        '''
        Generator which will yield pages that are listed in a wiki page. Will
        regard everything inside [[double brackets]] as a page name, except for
        interwiki and category links, and yield Pages for these pages.
    
        Arguments:
            * pagetitle - the title of a page on the home wiki
        '''
        listpage = wikipedia.Page(wikipedia.getSite(), self.pagetitle)
        list = wikipedia.get(listpage)
        # TODO - UNFINISHED
    
    # TODO: Make MediaWiki's search feature available.
    def __iter__(self):
        '''
        Starts the generator.
        '''
        if self.source == 'sqldump':
            for pl in self.read_pages_from_sql_dump():
                yield pl
        elif self.source == 'textfile':
            for pl in self.read_pages_from_text_file():
                yield pl
        elif self.source == 'category':
            for pl in self.read_pages_from_category():
                yield pl
        elif self.source == 'userinput':
            for pagename in self.pagenames:
                yield wikipedia.Page(wikipedia.getSite(), pagename)

class ReplaceRobot:
    def __init__(self, generator, replacements, refsequence, references, refusage, exceptions = [], regex = False, acceptall = False):
        self.generator = generator
        self.replacements = replacements
        self.exceptions = exceptions
        self.regex = regex
        self.acceptall = acceptall
        self.references = references
        self.refsequence = refsequence
        self.refusage = refusage

    def checkExceptions(self, original_text):
        """
        If one of the exceptions applies for the given text, returns the 
        substring. which matches the exception. Otherwise it returns None.
        """
        for exception in self.exceptions:
            if self.regex:
                exception = re.compile(exception)
                hit = exception.search(original_text)
                if hit:
                    return hit.group(0)
            else:
                hit = original_text.find(exception)
                if hit != -1:
                    return original_text[hit:hit + len(exception)]
        return None

    def doReplacements(self, new_text):
        """
        Returns the text which is generated by applying all replacements to the
        given text.
        """

        # For any additional replacements, loop through them
        for old, new in self.replacements:
            if self.regex:
                # TODO: compiling the regex each time might be inefficient
                oldR = re.compile(old)
                new_text = oldR.sub(new, new_text)
            else:
                new_text = new_text.replace(old, new)

        # Read existing References section contents into references list
        wikipedia.output( u"Reading existing References section" )
        self.doReadReferencesSection( new_text )
        # Convert any external links to footnote references
        wikipedia.output( u"Converting external links" )
        new_text = self.doConvertExternalLinks( new_text )
        # Accumulate ordered list of all references
        wikipedia.output( u"Collecting references" )
        (duplicatefound, self.refusage) = self.doBuildSequenceListOfReferences( new_text )
        # Rewrite references, including dealing with duplicates.
        wikipedia.output( u"Rewriting references" )
        new_text = self.doRewriteReferences( new_text, self.refusage )
        # Reorder References to match sequence of ordered list
        wikipedia.output( u"Collating references" )
        self.references = self.doReorderReferences( self.references, self.refusage)
        # Rebuild References section
        wikipedia.output( u"Rebuilding References section" )
        new_text = self.doUpdateReferencesSection( new_text, self.refusage )
        return new_text
        
    def doConvertExternalLinks(self, original_text):
        """
        Returns the text which is generated by converting external links to References.
        Adds References to reference list.
        """
        new_text = ''				# Default is no text
        skipsection = False
        for text_line in original_text.splitlines(True):  # Scan all text line by line
            # Check for protected sections
            m = re.search("== *(?P<sectionname>[^\]\|=]*) *==", text_line)
            # TODO: support subheadings within References section
            # TODO: support References in alphabetic order
            # TODO: support References in other orders
            if m:	# if in a section, check if should skip this section
                if m.group('sectionname').lower().strip() in [ 'external link', 'external links', 'links', 'reference', 'references', 'external links and references', 'notes' ]:
                    skipsection = True		# skipsection left True so no further links converted
            if skipsection:
                new_text = new_text + text_line		# skip section, so retain text.
            else:
                # TODO: recognize {{inline}} invisible footnotes when something can be done with them
                #
                # Fix erroneous external links in double brackets
                Rextlink = re.compile(r'(?i)\[\[(?P<linkname>http://[^\]]+?)\]\]')
                # TODO: compiling the regex each time might be inefficient
                text_lineR = re.compile(Rextlink)
                MOextlink = text_lineR.search(text_line)
                while MOextlink:	# find all links on line
                    extlink_linkname = MOextlink.group('linkname')
                    # Rewrite double brackets to single ones
                    text_line=text_line[:MOextlink.start()] + '[%s]' % extlink_linkname + text_line[MOextlink.end(0):]
                    MOextlink = text_lineR.search(text_line,MOextlink.start(0)+1)
                # Regular expression to look for external link [linkname linktext] - linktext is optional.
                # Also accepts erroneous pipe symbol as separator.
                # Accepts wikilinks within <linktext>
                Rextlink = re.compile(r'[^\[]\[(?P<linkname>[h]*[ft]+tp:[^ [\]\|]+?)(?P<linktext>[ \|]+(( *[^\]\|]*)|( *\[\[.+?\]\])*)+)*\][^\]]')
                # TODO: compiling the regex each time might be inefficient
                text_lineR = re.compile(Rextlink)
                MOextlink = text_lineR.search(text_line)
                while MOextlink:	# find all links on line
                    extlink_linkname = MOextlink.group('linkname')
                    extlink_linktext = MOextlink.group('linktext')
                    self.refsequence += 1
                    ( refname, reftext ) = self.doConvertLinkTextToReference(self.refsequence, extlink_linkname, extlink_linktext)
                    self.references.append( reftext )	# append new entry to References
                    if extlink_linktext:
                        # If there was text as part of link, reinsert text before footnote.
                        text_line=text_line[:MOextlink.start(0)+1] + '%s{{ref|%s}}' % (extlink_linktext, refname) + text_line[MOextlink.end(0):]
                    else:
                        text_line=text_line[:MOextlink.start(0)+1] + '{{ref|%s}}' % refname + text_line[MOextlink.end(0)-1:]
                    MOextlink = text_lineR.search(text_line,MOextlink.start(0)+1)
                # Search for {{doi}}
                Rdoi = re.compile(r'(?i){{doi\|(?P<doilink>[^}|]*)}}')
                # TODO: compiling the regex each time might be inefficient
                doiR = re.compile(Rdoi)
                MOdoi = doiR.search(text_line)
                while MOdoi:		# find all doi on line
                    doi_link = MOdoi.group('doilink')
                    if doi_link:
                        self.refsequence += 1
                        ( refname, reftext ) = self.doConvertDOIToReference( self.refsequence, doi_link )
                        self.references.append( reftext )		# append new entry to References
                        text_line=text_line[:MOdoi.start(0)] + '{{ref|%s}}' % refname + text_line[MOdoi.end(0):]
                        MOdoi = doiR.search(text_line, MOdoi.start(0)+1)
                new_text = new_text + text_line	# append new line to new text
        if new_text == '':
            new_text = original_text	# If somehow no new text, return original text
        return new_text
        
    def doRewriteReferences(self, original_text, refusage):
        """
        Returns the text which is generated by rewriting references, including duplicate refs.
        """
        new_text = ''				# Default is no text
        skipsection = False
        for text_line in original_text.splitlines(True):  # Scan all text line by line
            # Check for protected sections
            m = re.search("== *(?P<sectionname>[^\]\|=]*) *==", text_line)
            if m:	# if in a section, check if should skip this section
                if m.group('sectionname').lower().strip() in [ 'external link', 'external links', 'links', 'reference', 'references', 'external links and references', 'notes' ]:
                    skipsection = True		# skipsection left True so no further links converted
            if skipsection:
                new_text = new_text + text_line		# skip section, so retain text.
            else:
                # TODO: recognize {{inline}} invisible footnotes when something can be done with them
                #
                # Data structure: refusage[reference_key] = [ sequence_in_document, count, count_during_dup_handling ]
                # Check for various references
                # TODO: compiling the regex each time might be inefficient
                Rtext_line = re.compile(r'(?i){{(?P<reftype>ref|ref_num|ref_label)\|(?P<refname>[^}|]+?)}}')
                m = Rtext_line.search( text_line )
                alphabet26 = u'abcdefghijklmnopqrstuvwxyz'
                while m:	# if found a reference
                    if m.group('reftype').lower() in ( 'ref', 'ref_num', 'ref_label' ):	# confirm ref
                        refkey = m.group('refname').strip()
                        if refkey != '':
                            if refusage.has_key( refkey ):
                                # wikipedia.output( u'refusage[%s] = %s' % (refkey,refusage[refkey]) )
                                if refusage[refkey][2] == 0:	# if first use of reference
                                    text_line=text_line[:m.start(0)] + '{{ref|%s}}' % (refkey) + text_line[m.end(0):]
                                    refusage[refkey][2] += 1	# count use of reference
                                else:				# else not first use of reference
                                    text_line=text_line[:m.start(0)] + '{{ref_label|%s|%d|%s}}' % (refkey,(refusage[refkey][0])+1,alphabet26[((refusage[refkey][2])-1)%26]) + text_line[m.end(0):]
                                    refusage[refkey][2] += 1	# count use of reference
                            else:
                                # Odd, because refusage list is populated the key should exist already.
                                refusage[refkey] = [len(refusage),1,1]	# remember this reference
                                text_line=text_line[:m.start(0)] + '{{ref|%s}}' % refkey + text_line[m.end(0):]
                    m = Rtext_line.search( text_line, m.start(0)+1 )
                new_text = new_text + text_line	# append new line to new text
        if new_text == '':
            new_text = original_text	# If somehow no new text, return original text
        return new_text

    def doGetTitleFromURL(self, extlink_linkname ):
        """
        Returns text derived from between <title>...</title> tags through a URL.
        """
        # if no descriptive text get from web site, if not PDF
        urltitle = u''
        if len(extlink_linkname) > 5 and extlink_linkname[-4:] != '.pdf':
            socket.setdefaulttimeout( 20 )	# timeout in seconds
            wikipedia.get_throttle()	# throttle down to Wikipedia rate
            try: 
                urlobj = urllib2.urlopen( extlink_linkname )
            except IOError, e:
                if e and e.code:
                    wikipedia.output( u'Error accessing URL, %s' % e.code )
                else:
                    wikipedia.output( u'Error accessing URL.' )
            else:
                if urlobj != None:
                    wikipedia.output( u':::URL: ' + extlink_linkname )
                    # urlinfo = urlobj.info()
                    aline = urlobj.read()
                    while aline and urltitle == '':
                        titleRE = re.search("(?i)<title>(?P<HTMLtitle>[^<>]+)", aline)
                        if titleRE:
                            urltitle = unicode(titleRE.group('HTMLtitle'), 'utf-8')
                            urltitle = u' '.join(urltitle.split())	# merge whitespace
                            break	# found a title so stop looking
                        else:
                            aline = urlobj.read()
                    if urltitle != '': wikipedia.output( u'title: ' + urltitle )
            socket.setdefaulttimeout( 200 )	# timeout in seconds
        return urltitle

    def doConvertLinkTextToReference(self, refsequence, extlink_linkname, extlink_linktext):
        """
        Returns the text which is generated by converting a link to
        a format suitable for the References section.
        """
        now = date.today()
        refname = u'refbot.%d' % refsequence
        m = re.search("[\w]+://([\w]\.)*(?P<siteend>[\w.]+)[/\Z]", extlink_linkname)
        if m:
            refname = m.group('siteend') + u'.%d' % refsequence	# use end of site URL as reference name
        if extlink_linktext == None or len(extlink_linktext) < 20:
            urltitle = self.doGetTitleFromURL( extlink_linkname )	# try to get title from URL
            for newref in self.references:		# scan through all references
                if extlink_linkname in newref:		# if undescribed linkname same as a previous entry
                    if urltitle:
                        extlink_linktext = urltitle + ' (See above)'
                    else:
                        extlink_linktext = extlink_linkname + ' (See above)'
            if extlink_linktext == None or len(extlink_linktext) < 20:
                new_text = u'# {{note|%s}} {{Web reference_simple | title=%s | URL=%s | date= %s %d | year= %s }}' % ( refname, urltitle, extlink_linkname, now.strftime('%B'), now.month, now.strftime('%Y') ) + '\n'
            else:
                new_text = u'# {{note|%s}} {{Web reference_simple | title=%s | URL=%s | date= %s %d | year= %s }}' % ( refname, extlink_linktext, extlink_linkname, now.strftime('%B'), now.month, now.strftime('%Y') ) + '\n'
        else:
            new_text = u'# {{note|%s}} {{Web reference_simple | title=%s | URL=%s | date= %s %d | year= %s }}' % ( refname, extlink_linktext, extlink_linkname, now.strftime('%B'), now.month, now.strftime('%Y') ) + '\n'
        return (refname, new_text)

    def doConvertDOIToReference(self, refsequence, doi_linktext):
        """
        Returns the text which is generated by converting a DOI reference to
        a format suitable for the References section.
        """
        # TODO: look up DOI info and create full reference
        urltitle = self.doGetTitleFromURL( 'http://dx.doi.org/' + doi_linktext ) # try to get title from URL
        refname = 'refbot%d' % refsequence
        if urltitle:
	    new_text = '# {{note|%s}} %s {{doi|%s}}' % (refname, urltitle, doi_linktext) + '\n'
        else:
	    new_text = '# {{note|%s}} {{doi|%s}}' % (refname, doi_linktext) + '\n'
        return (refname, new_text)

    def doBuildSequenceListOfReferences(self, original_text):
        """
        Returns a list with all found references and sequence numbers.
        """
        duplicatefound = False
        refusage = {}		# Nothing found yet
        # Data structure: refusage[reference_key] = [ sequence_in_document, count, count_during_dup_handling ]
        for text_line in original_text.splitlines(True):  # Scan all text line by line
            # Check for various references
            Rtext_line = re.compile(r'(?i){{(?P<reftype>ref|ref_num|ref_label)\|(?P<refname>[^}|]+?)}}')
            m = Rtext_line.search( text_line )
            while m:	# if found a reference
                if m.group('reftype').lower() in ( 'ref', 'ref_num', 'ref_label' ):	# confirm ref
                    refkey = m.group('refname').strip()
                    if refkey != '':
                        if refusage.has_key(refkey):
                            refusage[refkey][1] += 1	# duplicate use of reference
                            duplicatefound = True
                        else:
                            refusage[refkey] = [len(refusage),0,0]	# remember this reference
                m = Rtext_line.search( text_line, m.end() )
        return (duplicatefound, refusage)

    def doReadReferencesSection(self, original_text):
        """
        Returns the text which is generated by reading the References section.
        Also appends references to self.references.
        Contents of all References sections will be read.
        """
        new_text = ''		# Default is no text
        intargetsection = False
        for text_line in original_text.splitlines(True):  # Scan all text line by line
            # Check for target section
            m = re.search("== *(?P<sectionname>[^\]\|=]*) *==", text_line)
            if m:	# if in a section, check if References section
                if m.group('sectionname').lower().strip() in ( 'reference', 'references', 'notes' ):
                    intargetsection = True			# flag as being in section
                    new_text = new_text + text_line
                else:
                    intargetsection = False			# flag as not being in section
            else:
                if intargetsection:	# if inside target section, remember this reference line
                    if text_line.strip() != '':
                        if text_line.lstrip()[0] in u'[{':	# if line starts with non-Ref WikiSyntax
                            intargetsection = False		# flag as not being in section
                        # TODO: need better way to handle special cases at end of refs
                        if text_line.strip() == u'<!--READ ME!! PLEASE DO NOT JUST ADD NEW NOTES AT THE BOTTOM. See the instructions above on ordering. -->':	# This line ends some References sections
                            intargetsection = False		# flag as not being in section
                    if intargetsection:	# if still inside target section
                        # Convert any # wiki list to *; will be converted later if a reference
                        if text_line[0] == '#':
                            text_line = '*' + text_line[1:]	# replace # with * wiki
                        self.references.append( text_line.rstrip() + '\n' )	# Append line to references
                        new_text = new_text + text_line
        return new_text

    def doReorderReferences(self, references, refusage):
        """
        Returns the new references list after reordering to match refusage list
        Non-references are moved to top, unused references to bottom.
        """
        # TODO: add tests for duplicate references/Ibid handling.
        newreferences = []
        if references != [] and refusage != {}:
            for i in range(len(references)):		# move nonrefs to top of list
                text_line = references[i]
                # TODO: compile search?
                m = re.search(r'(?i)[*#][\s]*{{(?P<reftype>note)\|(?P<refname>[^}|]+?)}}', text_line)
                if not m:	# if no ref found
                    newreferences.append(text_line)	# add nonref to new list
                    references[i] = None
            refsort = {}
            for refkey in refusage.keys():		# build list of keys in document order
                refsort[ refusage[refkey][0] ] = refkey	# refsort contains reference key names
            alphabet26 = u'abcdefghijklmnopqrstuvwxyz'
            for i in range(len(refsort)):		# collect references in document order
                for search_num in range(len(references)):	# find desired entry
                    search_line = references[search_num]
                    if search_line:
                        # TODO: compile search?
                        # Note that the expression finds all neighboring note|note_label expressions.
                        m2 = re.search(r'(?i)[*#]([\s]*{{(?P<reftype>note|note_label)\|(?P<refname>[^}|]+?)}})+', search_line)
                        if m2:
                            refkey = m2.group('refname').strip()
                            if refkey == refsort[i]:	# if expected ref found
                                # Rewrite references
                                note_text = '# {{note|%s}}' % refkey	# rewrite note tag
                                if refusage[refkey][1] > 1:		# if more than one reference to citation
                                    for n in range(refusage[refkey][1]):	# loop through all repetitions
                                        note_text = note_text + '{{note_label|%s|%d|%s}}' % (refkey,(refusage[refkey][0])+1,alphabet26[n%26])
                                search_line=search_line[:m2.start(0)] + note_text + search_line[m2.end(0):]
                                newreferences.append(search_line)	# found, add entry
                                del references[search_num]		# delete used reference
                                break	# stop the search loop after entry found
            newreferences = newreferences + references		# append any unused references
        return newreferences

    def doUpdateReferencesSection(self, original_text, refusage):
        """
        Returns the text which is generated by rebuilding the References section.
        Rewrite References section from references list.
        """
        new_text = ''		# Default is no text
        intargetsection = False
        for text_line in original_text.splitlines(True):  # Scan all text line by line
            # Check for target section
            m = re.search("== *(?P<sectionname>[^\]\|=]*) *==", text_line)
            if m:	# if in a section, check if References section
                if m.group('sectionname').lower().strip() in ( 'reference', 'references', 'notes' ):
                    intargetsection = True			# flag as being in section
                    new_text = new_text + text_line	# copy section headline
                    if self.references != []:
                        for newref in self.references:		# scan through all references
                            if newref != None:
                                new_text = new_text + newref    # insert references
                        self.references = []			# empty references
                else:
                    intargetsection = False			# flag as not being in section
                    new_text = new_text + text_line	# append new line to new text
            else:
                if intargetsection:
                    if text_line.strip() != '':
                        if text_line.lstrip()[0] in u'[{':	# if line starts with non-Ref WikiSyntax
                            intargetsection = False		# flag as not being in section
                        # TODO: need better way to handle special cases at end of refs
                        if text_line.strip() == u'<!--READ ME!! PLEASE DO NOT JUST ADD NEW NOTES AT THE BOTTOM. See the instructions above on ordering. -->':	# This line ends some References sections
                            intargetsection = False		# flag as not being in section
                if not intargetsection:			# if not in References section, remember line
                    new_text = new_text + text_line	# append new line to new text
        # If references list not emptied, there was no References section found
        if self.references != []:			# empty references
            # New References section needs to be created at bottom.
            text_line_counter = 0		# current line
            last_text_line_counter_value = 0	# number of last line of possible text
            for text_line in original_text.splitlines(True):  # Search for last normal text line
                text_line_counter += 1		# count this line
                if text_line.strip() != '':
                    if text_line.lstrip()[0].isalpha():	# if line starts with alpha
                        last_text_line_counter = text_line_counter	# number of last line of possible text
            text_line_counter = 0		# current line
            for text_line in original_text.splitlines(True):  # Search for last normal text line
                text_line_counter += 1		# count this line
                if last_text_line_counter == text_line_counter:	# if found insertion point
                    new_text = new_text + text_line	# append new line to new text
                    new_text = new_text + '== References ==\n'	# set to standard name
                    if self.references != []:
                        for newref in self.references:		# scan through all references
                            if newref != None:
                                new_text = new_text + newref    # insert references
                        self.references = []			# empty references
                else:
                    new_text = new_text + text_line	# append new line to new text
        if new_text == '':
            new_text = original_text	# If somehow no new text, return original text
        return new_text

    def run(self):
        """
        Starts the robot.
        """
        # Run the generator which will yield Pages to pages which might need to be
        # changed.
        for pl in self.generator:
            print ''
            try:
                # Load the page's text from the wiki
                original_text = pl.get()
                if pl.editRestriction:
                    wikipedia.output(u'Skipping locked page %s' % pl.title())
                    continue
            except wikipedia.NoPage:
                wikipedia.output(u'Page %s not found' % pl.title())
                continue
            except wikipedia.IsRedirectPage:
                continue
            match = self.checkExceptions(original_text)
            # skip all pages that contain certain texts
            if match:
                wikipedia.output(u'Skipping %s because it contains %s' % (pl.title(), match))
            else:
                new_text = self.doReplacements(original_text)
                if new_text == original_text:
                    wikipedia.output('No changes were necessary in %s' % pl.title())
                else:
                    wikipedia.output(u'>>> %s <<<' % pl.title())
                    wikipedia.showDiff(original_text, new_text)
                    if not self.acceptall:
                        choice = wikipedia.input(u'Do you want to accept these changes? [y|n|a(ll)]')
                        if choice in ['a', 'A']:
                            self.acceptall = True
                    if self.acceptall or choice in ['y', 'Y']:
                        pl.put(new_text)
    
def main():
    # How we want to retrieve information on which pages need to be changed.
    # Can either be 'sqldump', 'textfile' or 'userinput'.
    source = None
    # Array which will collect commandline parameters.
    # First element is original text, second element is replacement text.
    commandline_replacements = []
    # A dictionary where keys are original texts and values are replacement texts.
    replacements = {}
    # Don't edit pages which contain certain texts.
    exceptions = []
    # Should the elements of 'replacements' and 'exceptions' be interpreted
    # as regular expressions?
    regex = False
    # the dump's path, either absolute or relative, which will be used when source
    # is 'sqldump'.
    sqlfilename = None
    # the textfile's path, either absolute or relative, which will be used when
    # source is 'textfile'.
    textfilename = None
    # the category name which will be used when source is 'category'.
    categoryname = None
    # a list of pages which will be used when source is 'userinput'.
    pagenames = []
    # will become True when the user presses a ('yes to all') or uses the -always
    # commandline paramater.
    acceptall = False
    # Which namespace should be processed when using a SQL dump
    # default to -1 which means all namespaces will be processed
    namespace = -1
    # Load default summary message.
    wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg))
    # List of references in References section
    references = []
    # Reference sequence number
    refsequence = random.randrange(1000)
    # Dictionary of references used in sequence
    refusage = {}

    # Read commandline parameters.
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg, 'replace')
        if arg:
            if arg == '-regex':
                regex = True
            elif arg.startswith('-file'):
                if len(arg) == 5:
                    textfilename = wikipedia.input(u'Please enter the filename:')
                else:
                    textfilename = arg[6:]
                source = 'textfile'
            elif arg.startswith('-cat'):
                if len(arg) == 4:
                    categoryname = wikipedia.input(u'Please enter the category name:')
                else:
                    categoryname = arg[5:]
                source = 'category'
            elif arg.startswith('-sql'):
                if len(arg) == 4:
                    sqlfilename = wikipedia.input(u'Please enter the SQL dump\'s filename:')
                else:
                    sqlfilename = arg[5:]
                source = 'sqldump'
            elif arg.startswith('-page'):
                if len(arg) == 5:
                    pagenames.append(wikipedia.input(u'Which page do you want to chage?'))
                else:
                    pagenames.append(arg[6:])
                source = 'userinput'
            elif arg.startswith('-except:'):
                exceptions.append(arg[8:])
            elif arg == '-always':
                acceptall = True
            elif arg.startswith('-namespace:'):
                namespace = int(arg[11:])
            else:
                commandline_replacements.append(arg)

    if source == None or len(commandline_replacements) not in [0, 2]:
        # syntax error, show help text from the top of this file
        wikipedia.output(__doc__, 'utf-8')
        wikipedia.stopme()
        sys.exit()
    if (len(commandline_replacements) == 2):
        replacements[commandline_replacements[0]] = commandline_replacements[1]
        wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg ) % ' (-' + commandline_replacements[0] + ' +' + commandline_replacements[1] + ')')
    else:
        change = ''
        default_summary_message =  wikipedia.translate(wikipedia.getSite(), msg) % change
        wikipedia.output(u'The summary message will default to: %s' % default_summary_message)
        summary_message = wikipedia.input(u'Press Enter to use this default message, or enter a description of the changes your bot will make:')
        if summary_message == '':
            summary_message = default_summary_message
        wikipedia.setAction(summary_message)

        # Perform the predefined actions.
        try:
            fix = fixes['ALTREFS']
        except KeyError:
            wikipedia.output(u'Available predefined fixes are: %s' % fixes.keys())
            wikipedia.stopme()
            sys.exit()
        if fix.has_key('regex'):
            regex = fix['regex']
        if fix.has_key('msg'):
            wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), fix['msg']))
        if fix.has_key('exceptions'):
            exceptions = fix['exceptions']
        replacements = fix['replacements']

    gen = ReplacePageGenerator(source, replacements, exceptions, regex, namespace,  textfilename, sqlfilename, categoryname, pagenames)
    preloadingGen = pagegenerators.PreloadingGenerator(gen, pageNumber = 20)
    bot = ReplaceRobot(preloadingGen, replacements, refsequence, references, refusage, exceptions, regex, acceptall)
    bot.run()


if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
