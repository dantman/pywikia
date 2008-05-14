# -*- coding: utf-8 -*-
"""
This bot will search for references which are only made of a link 
without title, (i.e. <ref>[http://www.google.fr/]</ref> or 
<ref>http://www.google.fr/</ref>) and will fetch the html title from 
the link to use it as the title of the wiki link in the reference, i.e.
<ref>[http://www.google.fr/search?q=test test - Google Search]</ref>

The bot checks every 20 edits a special stop page : if
the page has been edited, it stops.

DumZiBoT is running that script on en: & fr: at every new dump, running it on de: is not allowed anymore.

As it uses it, you need to configure noreferences.py for your wiki, or it will not work.

pdfinfo is needed for parsing pdf titles.

See [[:en:User:DumZiBoT/refLinks]] for more information on the bot.

&params;

-limit:n                Stops after n edits

-xml:dump.xml           Should be used instead of a simple page fetching
                        method from pagegenerators.py for performance and
                        load issues

-xmlstart               Page to start with when using an XML dump

-ignorepdf              Do not handle PDF files (handy if you use Windows and 
                        can't get pdfinfo)

Basic pagegenerators commands, -page, etc...
"""
# (C) 2008 - Nicolas Dumazet ( en:User:NicDumZ )
#
# Distributed under the terms of the GPL

from BeautifulSoup import UnicodeDammit
import sys, re, urllib2, httplib, socket, codecs, ftplib
import wikipedia, pagegenerators, noreferences
import subprocess, tempfile, os

stopPage = {'fr':u'Utilisateur:DumZiBoT/EditezCettePagePourMeStopper',
            'de':u'Benutzer:DumZiBoT/EditThisPageToStopMe',
            'it':u'Utente:DumZiBoT/EditThisPageToStopMe',
            'ko':u'사용자:GrassnBreadRefBot/EditThisPageToStopMe1',
            'hu':'User:Damibot/EditThisPageToStopMe',
            'en':u'User:DumZiBoT/EditThisPageToStopMe'}

msg = { 'fr':u'Bot: Correction des refs. mal formatées (cf. [[Utilisateur:DumZiBoT/liensRefs|explications]])',
        'de':u'Bot: Korrektes Referenzformat (siehe [[:en:User:DumZiBoT/refLinks]])',
        'hu':u'Robot: Forráshivatkozások kibővítése a hivatkozott oldal címével',
        'ko':u'봇: url만 있는 주석을 보강, (영문)[[:en:User:DumZiBoT/refLinks]] 참조',
        'es':u'Formateando las referencias que no tuvieran titulos (Pruebas por [[Wikipedia:Bot/Autorizaciones#DumZiBoT]] )',
        'en':u'Bot: Converting bare references, see [[User:DumZiBoT/refLinks|FAQ]]'}

deadLinkTag = {'fr':u'%s {{lien mort}}',
               'de':u'',
               'hu':u'%s {{halott link}}',
               'ko':u'%s {{죽은 바깥 고리}}',
               'es':u'{{enlace roto2|%s}}',
               'en':u'%s {{dead link}}'}

comment = {'fr':u'Titre généré automatiquement',
           'de':u'Automatisch generierter titel',
           'hu':u'Robot generálta cím',
           'ko':u'봇이 따온 제목',
           'es':u'Título generado por un bot',
           'en':u'Bot generated title'}

soft404 = re.compile(ur'\D404(\D|\Z)|error|errdoc|Not.{0,3}Found|sitedown|eventlog', re.IGNORECASE)
dirIndex = re.compile(ur'^\w+://[^/]+/((default|index)\.(asp|aspx|cgi|htm|html|phtml|mpx|mspx|php|shtml|var))?$', re.IGNORECASE)
domain = re.compile(ur'^(\w+)://(?:www.|)([^/]+)')
badtitles = {'en':
                # is
                ur'(?is)(test|'
                # starts with
                +'^\W*(register|registration|(sign|log)[ \-]?in|subscribe|sign[ \-]?up|log[ \-]?on|untitled *(document|page|$))'
                # anywhere
                +'|(404|page|file).*not( *be)? *found'
                # ends with
                +'|(register|registration|(sign|log)[ \-]?in|subscribe|sign[ \-]?up|log[ \-]?on)\W*$'
                +')',
            'fr':
                #is
                ur'(?is)(test|'
                # starts with
                + ur'^\W*(register|registration|(sign|log)[ \-]?in|subscribe|sign[ \-]?up|log[ \-]?on|untitled *(document|page|$))'
                # anywhere
                +'|(404|page|file|site).*(not *found|en +travaux)'
                # ends with
                +'|(register|registration|(sign|log)[ \-]?in|subscribe|sign[ \-]?up|log[ \-]?on)\W*$'
                +')'}


linksInRef = re.compile(
	# bracketed URLs
	ur'(?i)<ref(?P<name>[^>]*)>\s*\[?(?P<url>(?:http|https|ftp)://(?:' +
	# unbracketed with()
	ur'^\[\]\s<>"]+\([^\[\]\s<>"]+[^\[\]\s\.:;\\,<>\?"]+|'+
	# unbracketed without ()
	ur'[^\[\]\s<>"]+[^\[\]\s\)\.:;\\,<>\?"]+|[^\[\]\s<>"]+))[!?,\s]*\]?\s*</ref>')
#http://www.twoevils.org/files/wikipedia/404-links.txt.gz
listof404pages = '404-links.txt'

class XmlDumpPageGenerator:
    def __init__(self, xmlFilename, xmlStart, namespaces):
        self.xmlFilename = xmlFilename
        self.xmlStart = xmlStart
        self.namespaces = namespaces
        self.skipping = bool(xmlStart)
        self.site = wikipedia.getSite()

        import xmlreader
        dump = xmlreader.XmlDump(self.xmlFilename)
        self.parser = dump.parse()

    def __iter__(self):
        return self
    
    def next(self):
        while True:
            try:
                entry = self.parser.next()
            except StopIteration:
                raise
            if self.skipping:
                if entry.title != self.xmlStart:
                    continue
                self.skipping = False
            page=wikipedia.Page(self.site, entry.title)
            if not self.namespaces == []:
                if page.namespace() not in self.namespaces:
                    continue
            if linksInRef.search(entry.text):
                return page

class RefLink:
    def __init__(self, link, name):
        self.refname = name
        self.link = link
        self.site = wikipedia.getSite()
        self.linkComment = wikipedia.translate(self.site, comment)
        self.url = re.sub(u'#.*', '', self.link)
        self.title = None

    def refTitle(self):
        return '<ref%s>[%s %s<!-- %s -->]</ref>' % (self.refname, self.link, self.title, self.linkComment)

    def refLink(self):
        return '<ref%s>%s</ref>' % (self.refname, self.link)
    
    def refDead(self):
        tag = wikipedia.translate(self.site, deadLinkTag) % self.link
        return '<ref%s>%s</ref>' % (self.refname, tag)

    def transform(self, ispdf = False):
        #convert html entities
        if not ispdf:
            self.title = wikipedia.html2unicode(self.title)
        self.title = re.sub(r'-+', '-', self.title)
        #remove formatting, i.e long useless strings
        self.title = re.sub(r'[\.+\-=]{4,}', ' ', self.title)
        #remove \n and \r and Unicode spaces from titles
        self.title = re.sub(r'(?u)\s', ' ', self.title)
        self.title = re.sub(r'[\n\r\t]', ' ', self.title)
        #remove extra whitespaces
        #remove leading and trailing ./;/,/-/_/+/ /
        self.title = re.sub(r' +', ' ', self.title.strip(r'=.;,-+_ '))

        self.avoid_uppercase()
        #avoid closing the link before the end
        self.title = self.title.replace(']', '&#93;')
        #avoid multiple } being interpreted as a template inclusion
        self.title = self.title.replace('}}', '}&#125;')
        #prevent multiple quotes being interpreted as '' or '''
        self.title = self.title.replace('\'\'', '\'&#39;')
        self.title = wikipedia.unicode2html(self.title, self.site.encoding())

    def avoid_uppercase(self):
        """
        If title has more than 6 characters and has 60% of uppercase
        characters, capitalize() it
        """
        if len(self.title) <= 6:
            return
        nb_upper = 0
        nb_letter = 0
        for letter in self.title:
            if letter.isupper():
                nb_upper += 1
            if letter.isalpha():
                nb_letter += 1
            if letter.isdigit():
                return
        if float(nb_upper)/(nb_letter+1) > .70:
            self.title = self.title.title()

class ReferencesRobot:
    def __init__(self, generator, acceptall = False, limit = None, ignorepdf = False ):
        self.generator = generator
        self.acceptall = acceptall
        self.limit = limit
        self.ignorepdf = ignorepdf
        self.site = wikipedia.getSite()
        self.stopPage = wikipedia.translate(self.site, stopPage)
        try :
            self.stopPageRevId = wikipedia.Page(self.site, 
                                                self.stopPage).latestRevision()
        except wikipedia.NoPage :
            wikipedia.output(u'The stop page %s does not exist' 
                                % self.stopPage.aslink())
            wikipedia.stopme()
        self.META_CONTENT = re.compile(ur'(?i)<meta[^>]*content\-type[^>]*>')
        self.CHARSET = re.compile(ur'(?i)charset\s*=\s*(?P<enc>[^\'";>/]*)')
        self.TITLE = re.compile(ur'(?is)(?<=<title>).*?(?=</title>)')
        self.NON_HTML = re.compile(ur'(?is)<script[^>]*>.*?</script>|<style[^>]*>.*?</style>|<!--.*?-->|<!\[CDATA\[.*?\]\]>')
        str = ur'application/(?:xhtml\+xml|xml)|text/(?:ht|x)ml'
        self.MIME = re.compile(str)
        self.titleBlackList = re.compile(wikipedia.translate(self.site, badtitles))   
        self.norefbot = noreferences.NoReferencesBot(None)
 
    def put_page(self, page, new):
        """
        Prints diffs between orginal and new (text), puts new text for page
        """
        wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" 
                         % page.title())
        wikipedia.showDiff(page.get(), new)
        if not self.acceptall:
            choice = wikipedia.inputChoice(u'Do you want to accept ' +
                                           u'these changes?', 
                                           ['Yes', 'No', 'All'], 
                                           ['y', 'N', 'a'], 'N')
            if choice in ['a', 'A']:
                self.acceptall = True
            if choice in ['y', 'Y']:
                page.put_async(new)
        if self.acceptall:
            try:
                page.put(new)
            except wikipedia.EditConflict:
                wikipedia.output(u'Skipping %s because of edit conflict' 
                                  % (page.title(),))
            except wikipedia.SpamfilterError, e:
                wikipedia.output(u'Cannot change %s because of blacklist entry %s' % (page.title(), e.url))
            except wikipedia.PageNotSaved, error:
                wikipedia.output(u'Error putting page: %s' % (error.args,))
            except wikipedia.LockedPage:
                wikipedia.output(u'Skipping %s (locked page)' 
                                  % (page.title(),))
            except wikipedia.ServerError, e:
                wikipedia.output(u'Server Error : %s' % e)

    def httpError(self, err_num, link, pagetitleaslink):
        """Log HTTP Error"""
        wikipedia.output(u'HTTP error (%s) for %s on %s' 
                          % (err_num, link, pagetitleaslink),
                         toStdout = True)
        f = codecs.open(
                wikipedia.config.datafilepath(
                    'reflinks-httpErrorLog', 
                    'reflinks-%s-%s.txt' % (self.site.family.name, 
                                            self.site.lang)),
                'a', 'utf-8')
        f.write(u'%s: %s from %s\n' % (err_num, link, pagetitleaslink))
        f.close()

    def getPDFTitle(self, ref, f): 
        wikipedia.output( u'PDF file.' )
        fd, infile = tempfile.mkstemp()
        urlobj = os.fdopen(fd, 'r+w')
        urlobj.write(f.read())
        try:
            pdfinfo_out = subprocess.Popen([r"pdfinfo","/dev/stdin"], stdin=urlobj, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False).communicate()[0]
            for aline in pdfinfo_out.splitlines():
                if aline.lower().startswith('title'):
                    ref.title = aline.split(None)[1:]
                    ref.title = ' '.join(ref.title)
                    if ref.title != '': wikipedia.output(u'title: ' +ref.title )
            wikipedia.output( u'PDF done.' )
        except ValueError:
            wikipedia.output( u'pdfinfo value error.' )
        except OSError:
            wikipedia.output( u'pdfinfo OS error.' )
        except:	# Ignore errors
            wikipedia.output( u'PDF processing error.' )
            pass
        finally:
            urlobj.close()
            os.unlink(infile)

    def replace(self, sub, text, repl):
        new_text = text
        for match in re.finditer(re.escape(sub), text):
            if wikipedia.isDisabled(text, match.start()):
                continue
            #blablah

    def run(self):
        """
        Runs the Bot
        """
        wikipedia.setAction(wikipedia.translate(self.site, msg))
        try:
            deadLinks = codecs.open(listof404pages, 'r', 'latin_1').read() 
        except IOError:
            wikipedia.output('You need to download http://www.twoevils.org/files/wikipedia/404-links.txt.gz and to ungzip it in the same directory')
            raise
        socket.setdefaulttimeout(30)
        editedpages = 0
        for page in self.generator:
            try:
                # Load the page's text from the wiki
                new_text = page.get()
                if not page.canBeEdited():
                    wikipedia.output(u"You can't edit page %s" 
                                      % page.aslink())
                    continue
            except wikipedia.NoPage:
                wikipedia.output(u'Page %s not found' % page.aslink())
                continue
            except wikipedia.IsRedirectPage:
                wikipedia.output(u'Page %s is a redirect' % page.aslink())
                continue

            for match in linksInRef.finditer(wikipedia.removeDisabledParts(page.get())):
            #for each link to change
                link = match.group(u'url')
                #debugging purpose
                #print link
                if u'jstor.org' in link:
                    #TODO: Clean URL blacklist
                    continue
                
                ref = RefLink(link, match.group('name'))
                f = None
                try:
                    socket.setdefaulttimeout(20)
                    f = urllib2.urlopen(ref.url)
                    #Try to get Content-Type from server
                    headers = f.info()
                    contentType = headers.getheader('Content-Type')
                    if contentType and not self.MIME.search(contentType):
                        if ref.link.lower().endswith('.pdf') and not self.ignorepdf:
                            # If file has a PDF suffix
                            self.getPDFTitle(ref, f)
                        else:
                            wikipedia.output(u'\03{lightyellow}WARNING\03{default} : media : %s ' % ref.link)
                        if ref.title:
                            if not re.match('(?i) *microsoft (word|excel|visio)', ref.title):
                                ref.transform(ispdf=True)
                                repl = ref.refTitle()
                            else:
                                wikipedia.output('\03{lightyellow}WARNING\03{default} : PDF title blacklisted : %s ' % ref.title)
                                repl = ref.refLink()
                        else:
                            repl = ref.refLink()
                        new_text = new_text.replace(match.group(), repl)
                        continue
                    # Test if the redirect was valid
                    redir = f.geturl()
                    if redir != ref.link and domain.findall(redir) == domain.findall(link):
                        if soft404.search(redir) and not soft404.search(ref.link):
                            wikipedia.output(u'\03{lightyellow}WARNING\03{default} : Redirect 404 : %s ' % ref.link)
                            continue
                        if dirIndex.match(redir) and not dirIndex.match(ref.link):
                            wikipedia.output(u'\03{lightyellow}WARNING\03{default} : Redirect to root : %s ' % ref.link)
                            continue

					# Read the first 1,000,000 bytes (0.95 MB)
                    linkedpagetext = f.read(1000000)
                    socket.setdefaulttimeout(None)

                except UnicodeError:
                    #example : http://www.adminet.com/jo/20010615¦/ECOC0100037D.html in [[fr:Cyanure]]
                    wikipedia.output(u'\03{lightred}Bad link\03{default} : %s in %s' % (ref.url, page.aslink()))
                    continue
                except urllib2.HTTPError, e:
                    self.httpError(e.code, ref.url, page.aslink())
                    if e.code == 410: # 410 Gone, indicates that the resource has been purposely removed
                        repl = ref.refDead()
                        new_text = new_text.replace(match.group(), repl)
                    elif e.code == 404 and (u'\t%s\t' % ref.url in deadLinks):
                        repl = ref.refDead()
                        new_text = new_text.replace(match.group(), repl)
                    continue
                except (urllib2.URLError, 
                        socket.error, 
                        IOError, 
                        httplib.error), e:
                #except (urllib2.URLError, socket.timeout, ftplib.error, httplib.error, socket.error), e:
                    wikipedia.output(u'Can\'t get page %s : %s' % (ref.url, e))
                    continue
                except ValueError:
                    #Known bug of httplib, google for :
                    #"httplib raises ValueError reading chunked content"
                    continue
                finally:
                    if f:
                        f.close()
                
                #remove <script>/<style>/comments/CDATA tags
                linkedpagetext = self.NON_HTML.sub('', linkedpagetext)

                meta_content = self.META_CONTENT.search(linkedpagetext)
                enc = []
                if meta_content:
                    tag = meta_content.group()
                    if not contentType: 
                        contentType = tag
                    s = self.CHARSET.search(tag)
                    if s: 
                        tmp = s.group('enc').strip("\"' ").lower()
                        enc.append(tmp)
                        if tmp in ("gb 2312", "gb2312", "gb-2312", "gb_2312"):
                            enc.append("gbk")
                        if tmp in ("shift jis", "shiftjis", "shift-jis", "shift_jis"):
                            enc.append("shift jis 2004")
                            enc.append("cp932")
                        if tmp in ("x euc jp", "x-euc-jp"):
                            enc.append("euc-jp")
                if not contentType:
                    wikipedia.output(u'No content-type found for %s' % ref.link)
                    continue
                elif not self.MIME.search(contentType):
                    wikipedia.output(u'\03{lightyellow}WARNING\03{default} : media : %s ' % ref.link)
                    repl = ref.refLink()
                    new_text = new_text.replace(match.group(), repl)
                    continue
                            
                if u'.ru' in ref.link or u'.su' in ref.link:
                    # see http://www.sci.aha.ru/ATL/ra13a.htm : no server encoding, no page encoding
                    enc = enc + ['koi8-r', 'windows-1251']
                elif u'.jp' in ref.link:
                    enc.append("shift jis 2004")
                    enc.append("cp932")
                elif u'.kr' in ref.link:
                    enc.append("euc-kr")
                    enc.append("cp949")
                elif u'.zh' in ref.link:
                    enc.append("gbk")
                
                #print(enc)
                u = UnicodeDammit(linkedpagetext, overrideEncodings = enc)
                #print(u.triedEncodings)
                
                
                if not u.unicode:
                    #Some page have utf-8 AND windows-1252 characters,
                    #Can't easily parse them. (~1 on 1000)
                    repl = ref.refLink()
                    new_text = new_text.replace(match.group(), repl)
                    wikipedia.output('%s : Hybrid encoding...' % ref.link)
                    continue
                

                for m in self.TITLE.finditer(u.unicode):
                    t = m.group()
                    if t:
                        ref.title = t
                        ref.transform()
                        if ref.title:
                            break;
                
                if not ref.title:
                    repl = ref.refLink()
                    new_text = new_text.replace(match.group(), repl)
                    wikipedia.output(u'%s : No title found...' % ref.link)
                    continue
                if enc and u.originalEncoding not in enc:
                    wikipedia.output(u'\03{lightpurple}ENCODING\03{default} : %s (%s)' % (ref.link, ref.title))
                
                if u'Ã©' in ref.title:
                    repl = ref.refLink()
                    new_text = new_text.replace(match.group(), repl)
                    wikipedia.output(u'%s : Hybrid encoding...' % ref.link)
                    continue
               
                if self.titleBlackList.search(ref.title):
                    repl = ref.refLink()
                    new_text = new_text.replace(match.group(), repl)
                    wikipedia.output(u'\03{lightred}WARNING\03{default} %s : Blacklisted title (%s)' % (ref.link, ref.title))
                    continue
                if len(ref.title) > 250:
                    ref.title = ref.title[:250] + "..."

                repl = ref.refTitle()
                new_text = new_text.replace(match.group(), repl)

            if new_text == page.get():
                wikipedia.output('No changes were necessary in %s' 
                                 % page.aslink())
                continue

            if self.norefbot.lacksReferences(new_text, verbose=False):
                new_text = self.norefbot.addReferences(new_text)
            editedpages += 1
            self.put_page(page, new_text)
            if self.limit and editedpages >= self.limit:
                wikipedia.output('Edited %s pages, stopping.' % self.limit)
                return
            if editedpages % 20 == 0:
                wikipedia.output('\03{lightgreen}Checking stop page...\03{default}')
                actualRev = wikipedia.Page(self.site, 
                                           self.stopPage).latestRevision()
                if actualRev != self.stopPageRevId:
                    wikipedia.output(u'[[%s]] has been edited : Someone wants us to stop.' % self.stopPage)
                    return

def main():
    genFactory = pagegenerators.GeneratorFactory()
    
    PageTitles = []
    xmlFilename = None
    always = False
    ignorepdf = False
    limit = None
    namespaces = []
    generator = None
    for arg in wikipedia.handleArgs():
        if arg.startswith('-page:'):
            PageTitles.append(arg[6:])
        elif arg.startswith('-namespace:'):
            try:
                namespaces.append(int(arg[11:]))
            except ValueError:
                namespaces.append(arg[11:])
        elif arg.startswith('-summary:'):
            wikipedia.setAction(arg[9:])
        elif arg == '-always':
            always = True
        elif arg == '-ignorepdf':
            ignorepdf= True
        elif arg.startswith('-limit:'):
            limit = int(arg[7:])
        elif arg.startswith('-xmlstart'):
            if len(arg) == 9:
                xmlStart = wikipedia.input(
                    u'Please enter the dumped article to start with:')
            else:
                xmlStart = arg[10:]
        elif arg.startswith('-xml'):
            if len(arg) == 4:
                xmlFilename = wikipedia.input(
                    u'Please enter the XML dump\'s filename:')
            else:
                xmlFilename = arg[5:]
        else:
            generator = genFactory.handleArg(arg)
    
    if xmlFilename:
        try:
            xmlStart
        except NameError:
            xmlStart = None
        generator = XmlDumpPageGenerator(xmlFilename, xmlStart, namespaces)
    elif PageTitles:
        pages= [wikipedia.Page(wikipedia.getSite(), PageTitle) for PageTitle in PageTitles]
        generator = iter(pages)
    if not generator:
        # syntax error, show help text from the top of this file
        wikipedia.showHelp('reflinks')
        wikipedia.stopme()
        sys.exit()
    generator = pagegenerators.PreloadingGenerator(generator, pageNumber = 50)
    generator = pagegenerators.RedirectFilterPageGenerator(generator)
    bot = ReferencesRobot(generator, always, limit, ignorepdf)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
