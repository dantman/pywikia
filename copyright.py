#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
This robot check copyright text in Google and Yahoo.

Google search requires to install the pyGoogle module from http://pygoogle.sf.net
and get a Google API license key from http://www.google.com/apis/index.html.

Yahoo! search requires pYsearch module http://pysearch.sourceforge.net and
a Yahoo AppID http://developer.yahoo.com. 

You can run the bot with the following commandline parameters:

-g           - Use Google search engine (default)
-ng          - Do not use Google
-y           - Use Yahoo! search engine
-ny          - Do not use Yahoo!
-maxquery    - Stop after a specified number of queries for page (default: 25)
-new
-repeat
-output      - Append results to a specified file (default: 'copyright/output.txt')
-file        - Work on all pages given in a local text file.
               Will read any [[wiki link]] and use these articles.
               Argument can also be given as "-file:filename".
-cat         - Work on all pages which are in a specific category.
               Argument can also be given as "-cat:categoryname".
-subcat      - When the pages to work on have been chosen by -cat, pages in
               subcategories of the selected category are also included.
               When -cat has not been selected, this has no effect.
-page        - Only check a specific page.
               Argument can also be given as "-page:pagetitle". You can give this
               parameter multiple times to check multiple pages.
-ref         - Work on all pages that link to a certain page.
               Argument can also be given as "-ref:referredpagetitle".
-filelinks   - Works on all pages that link to a certain image.
               Argument can also be given as "-filelinks:ImageName".
-links       - Work on all pages that are linked to from a certain page.
               Argument can also be given as "-links:linkingpagetitle".
-start       - Work on all pages in the wiki, starting at a given page.
-namespace:n - Number of namespace to process. The parameter can be used
               multiple times.

Examples:

If you want to check first 50 new articles using Yahoo! and Google search
engine then use this command:

    python copyright.py -new:50 -g -y

If you want to check a category with no limit for number of queries to
request, use this:

    python copyright.py -cat:"Wikipedia featured articles" -maxquery:0

"""

#
# (C) Francesco Cosoleto, 2006
#
# Distributed under the terms of the MIT license.
#

from __future__ import generators
import sys, re, codecs, os, time
import wikipedia, pagegenerators, catlib, config, mediawiki_messages

__version__='$Id$'

search_in_google=True
search_in_yahoo=False
search_in_msn=False
check_in_source_google=False
check_in_source_yahoo=True
exclude_quote = True
search_request_retry=10
max_query_for_page=25
appdir = "copyright/"
output_file = appdir + "output.txt"

pages_for_exclusion_database = [
('it', 'User:RevertBot/Lista_di_esclusione', 'exclusion_list.txt'),
('en', 'Wikipedia:Mirrors_and_forks/Abc', 'Abc.txt'),
('en', 'Wikipedia:Mirrors_and_forks/Def', 'Def.txt'),
('en', 'Wikipedia:Mirrors_and_forks/Ghi', 'Ghi.txt'),
('en', 'Wikipedia:Mirrors_and_forks/Jkl', 'Jkl.txt'),
('en', 'Wikipedia:Mirrors_and_forks/Mno', 'Mno.txt'),
('en', 'Wikipedia:Mirrors_and_forks/Pqr', 'Pqr.txt'),
('en', 'Wikipedia:Mirrors_and_forks/Stu', 'Stu.txt'),
('en', 'Wikipedia:Mirrors_and_forks/Vwxyz', 'Vwxyz.txt'),
#('de', 'Wikipedia:Weiternutzung', 'Weiternutzung.txt'),
('it', 'Wikipedia:Cloni', 'Cloni.txt'),
#('pl', 'Wikipedia:Mirrory_i_forki_polskiej_Wikipedii', 'Mirrory_i_forki_polskiej_Wikipedii.txt'),
#('pt', 'Wikipedia:Clones_da_Wikip�dia', 'Clones_da_Wikip�dia.txt'),
#('sv', 'Wikipedia:Spegelsidor', 'Spegelsidor.txt'),
]

def exclusion_file_list():
    for i in pages_for_exclusion_database:
        path = appdir + i[0] + '/' + i[2]
        mediawiki_messages.makepath(path)
        p = wikipedia.Page(wikipedia.getSite(i[0]),i[1])
        yield p, path

def load_pages(force_update = False):
    for page, path in exclusion_file_list():
        try:
            length = 0
            length = os.path.getsize(path)
            file_age = time.time() - os.path.getmtime(path)
            if file_age > 24 * 60 * 60:
                print 'Updating page [[' + page.title() + ']] to exclude new URLs...'
                length = 0
        except OSError:
            pass

        if length == 0 or force_update:
            try:
                data = page.get()
                f = codecs.open(path, 'w', 'utf-8')
                f.write(data)
                f.close()
            except wikipedia.IsRedirectPage:
                data = page.get(get_redirect=True)
            except:
                print 'Getting page failed'
    return

def check_list(text, cl, debug=False):
    for entry in cl:
        if entry:
            if text.find(entry) != -1:
                #print entry
                if debug:
                    print 'SKIP URL ' + text
                return True

def exclusion_list():
    prelist = []
    result_list = []
    load_pages()

    for page, path in exclusion_file_list():
        if 'exclusion_list.txt' in path:
            result_list += re.sub("</?pre>","", read_file(path, cut_comment = True)).splitlines()
        else:
            data = read_file(path)
            # wikipedia:en:Wikipedia:Mirrors and forks
            prelist += re.findall("(?i)url\s*=\s*<nowiki>(?:http://)?(.*)</nowiki>", data)
            prelist += re.findall("(?i)\*\s*Site:\s*\[?(?:http://)?(.*)\]?", data)
            # wikipedia:it:Wikipedia:Cloni
            if 'it/Cloni.txt' in path:
                prelist += re.findall('(?mi)^==(?!=)\s*\[?\s*(?:<nowiki>)?\s*(?:http://)?(.*?)(?:</nowiki>)?\s*\]?\s*==', data)
    list1 = []
    for entry in prelist:
        list1 += entry.split(", ")
    list2 = []
    for entry in list1:
        list2 += entry.split("and ")
    for entry in list2:
        # Remove unnecessary part of URL
        entry = re.sub("http://", "", entry)
        entry = re.sub("www\.", "", entry)
        entry = re.sub("</?nowiki>", "", entry)
        if entry:
            if '/' in entry:
                result_list += [re.sub(" .*", "", entry[:entry.rfind('/')])]
            else:
                result_list += [re.sub(" .*", "", entry)]

    result_list += read_file(appdir + 'exclusion_list.txt', cut_comment = True).splitlines()
    return result_list

def read_file(filename, cut_comment = False):
    text = u""
    f = codecs.open(filename, 'r','utf-8')
    text = f.read()
    if cut_comment:
        text = re.sub(" ?#.*", "", text)
    f.close()
    return text

def write_log(text, filename = output_file):
    f = codecs.open(filename, 'a', 'utf-8')
    f.write(text)
    f.close()

def cleanwikicode(text):
    if not text:
        return ""
    #write_log(text+'\n', "debug_cleanwikicode1.txt")
    text = re.sub('(?i)<br(\s*/)?>', '', text)
    text = re.sub('<!--.*?-->', '', text)
    text = re.sub('&lt;', '<', text)
    text = re.sub('&gt;', '>', text)

    if exclude_quote:
        text = re.sub("(?i){{quote|.*?}}", "", text)
        text = re.sub("^[:*]?\s*''.*?''\.?\s*((\(|<ref>).*?(\)|</ref>))?\.?$", "", text)
        text = re.sub('^[:*]?\s*["][^"]+["]\.?\s*((\(|<ref>).*?(\)|</ref>))?\.?$', "", text)
        text = re.sub('^[:*]?\s*[«][^»]+[»]\.?\s*((\(|<ref>).*?(\)|</ref>))?\.?$', "", text)
        text = re.sub('^[:*]?\s*[“][^”]+[”]\.?\s*((\(|<ref>).*?(\)|</ref>))?\.?$', "", text)
 
    # exclude <ref> notes
    text = re.sub ("<ref.*?>.*?</ref>", "", text)
    # exclude wikitable
    text = re.sub('^(\||{[^{]).*', "", text)
    # remove URL
    text = re.sub('http://[\w/.,;:@&=%#\\\?_!~*\'|()\"+-]+', ' ', text)
    # replace piped wikilink
    text = re.sub("\[\[[^\]]*?\|(.*?)\]\]", "\\1", text)
    # remove <nowiki> tags
    text = re.sub("</*nowiki>", "", text)
    # remove template
    text = re.sub('{{.*?}}', '', text)
    # remove LaTeX staff
    text = re.sub('<math>.*?</math>', '', text)
    #text = text.replace("''", "")
    text = text.replace("[", "")
    text = text.replace("]", "")
    text = re.sub('^[*:;]', '', text)

    text = text.replace("<!--", "")
    text = text.replace("-->", "")

    #if text:
    #    write_log(text+'\n', "debug_cleanwikicode2.txt")
    return text
 
excl_list = exclusion_list()

def exclusion_list_dump():
    res = ''
    for entry in excl_list:
        res += entry + '\n'
    f = open(appdir + 'exclusion_list.dump', 'w')
    f.write(res)
    f.close()

def n_index(text, n, sep):
    pos = 0
    while n>0:
        try:
            pos = text.index(sep, pos + 1)
            n -= 1
        except ValueError:
            return 0
    return pos

def mysplit(text, dim, sep):
    if not sep in text:
        return [text]
    t = text
    l = list()
    while t:
        if sep in t:
            n = n_index(t, dim, sep)
            if n>0:
                l.append(t[:n])
                t = t[n+1:]
                continue
        l.append(t)
        break
    return l

def query(lines = [], max_query_len = 1300):
    # Google max_query_len = 1480?
    # - '-Wikipedia ""' = 1467

    # Google limit queries to 32 words.

    output = u""
    n_query = 0
    previous_group_url = ''

    for line in lines:
        line = cleanwikicode(line)
        for search_words in mysplit(line,31," "):
            if len(search_words)>120:
                n_query += 1
                if max_query_for_page and n_query>max_query_for_page:
                    print "Max query limit for page reached"
                    return output
                if len(search_words)>max_query_len:
                    search_words=search_words[:max_query_len]
                    if " " in search_words:
                         search_words = search_words[:search_words.rindex(" ")]
                results = get_results(search_words)
                group_url = ''
                for url, engine in results:
                    group_url += '\n*%s - %s' % (engine, url)
                if results:
                    if previous_group_url == group_url:
                        output += '\n**' + search_words
                    else:
                        output += group_url + '\n**' + search_words
                    previous_group_url = group_url
    return output

source_seen = set()

def check_in_source(url):
    """
    Sources may be different from search engine database and include mentions of
    Wikipedia. This function avoid also errors in search results that can occurs
    either with Google and Yahoo! service.
    """
    import urllib2
    global excl_list, source_seen

    if url in source_seen:
        return False

    if check_list(url, excl_list):
        return False

    # very experimental code
    if not url[-4:] in [".pdf", ".doc"]:
        resp = urllib2.urlopen(url)
        text = resp.read().lower()
        #resp.close()
        if 'wikipedia' in text:
            excl_list += [url]
            #write_log(url + '\n', "copyright/sites_with_'wikipedia'.txt")
            return True
        else:
            #write_log(url + '\n', "copyright/sites_without_'wikipedia'.txt")
            source_seen.add(url)
    return False

def check_urllist(url, add_item):
    for i in range(len(url)):
        if add_item in url[i]:
            url[i] = (add_item, 'google, yahoo')
            return True
    return False

def get_results(query, numresults = 10):
    url = list()
    query = re.sub("[()\"<>]", "", query)
    #wikipedia.output(query)
    if search_in_google:
        import google
        google.LICENSE_KEY = config.google_key
        print "  google query..."
        search_request_retry = 6
        while search_request_retry:
        #SOAP.faultType: <Fault SOAP-ENV:Server: Exception from service object:
        # Daily limit of 1000 queries exceeded for key xxx>
            try:
                data = google.doGoogleSearch('-Wikipedia "' + query + '"')
                search_request_retry = 0
                for entry in data.results:
                    url.append((entry.URL, 'google'))
            except Exception, err:
                print "Got an error ->", err
                search_request_retry -= 1
    if search_in_yahoo:
        import yahoo.search.web
        print "  yahoo query..."
        data = yahoo.search.web.WebSearch(config.yahoo_appid, query='"' +
                                          query.encode('utf_8') +
                                          '" -Wikipedia', results=numresults)
        search_request_retry = 6
        while search_request_retry:
            try:
                for entry in data.parse_results():
                    if check_in_source_yahoo:
                        if check_in_source(entry.Url):
                            continue
                    if not check_urllist(url, entry.Url):
                        url.append((entry.Url, 'yahoo'))
                search_request_retry = 0
            except Exception, err:
                print "Got an error ->", err
                search_request_retry -= 1
    #if search_in_msn:
    #    from __SOAPpy import WSDL
    #    print "  msn query..."
    #    wsdl_url = 'http://soap.search.msn.com/webservices.asmx?wsdl'
    #    server = WSDL.Proxy(wsdl_url)
    #    params = {'AppID': config.msn_appid, 'Query': query, 'CultureInfo': 'en-US', 'SafeSearch': 'Off', 'Requests': {
    #             'SourceRequest':{'Source': 'Web', 'Offset': 0, 'Count': 10, 'ResultFields': 'All',}}}
    #    server_results = server.Search(Request=params)
    #    if server_results.Responses[0].Results:
    #        results = server_results.Responses[0].Results[0]
    #    for entry in results:
    #        url.append((entry.Url, 'msn'))

    offset = 0
    for i in range(len(url)):
        if check_list(url[i+offset][0], excl_list, debug=True):
            url.pop(i+offset)
            offset+=-1
    return url

def get_by_id(title, id):
    return wikipedia.getSite().getUrl("/w/index.php?title=%s&oldid=%s&action=raw" % (title, id))

def checks_by_ids(ids):
    for title, id in ids:
        original_text = get_by_id(title, id)
        if original_text:
            wikipedia.output(original_text)
            output = query(lines=original_text.splitlines())
            if output:
                write_log("=== [[" + title + "]] ===\n{{/box|%s|prev|%s|%s|00}}" % (title.replace(" ", "_").replace("\"", "%22"), id, "author") + output, "copyright/ID_output.txt")

class CheckRobot:
    def __init__(self, generator):
        """
        """
        self.generator = generator

    def run(self):
        """
        Starts the robot.
        """
        # Run the generator which will yield Pages which might need to be
        # checked.
        for page in self.generator:
            try:
                # Load the page's text from the wiki
                original_text = page.get()
            except wikipedia.NoPage:
                wikipedia.output(u'Page %s not found' % page.title())
                continue
            except wikipedia.IsRedirectPage:
                original_text = page.get(get_redirect=True)

#            colors = [13] * len(page.title())
    	    wikipedia.output(page.title())

	    if original_text:
                output = query(lines=original_text.splitlines())
                if output:
                   write_log('=== [[' + page.title() + ']] ===' + output + '\n', filename = output_file)

def main():
    global search_in_google, search_in_yahoo, max_query_for_page, output_file
    gen = None
    # Can either be 'xmldump', 'textfile' or 'userinput'.
    source = None
    # the textfile's path, either absolute or relative, which will be used when
    # source is 'textfile'.
    textfilename = None
    # the category name which will be used when source is 'category'.
    categoryname = None
    #
    catrecurse = False
    # pages which will be processed when the -page parameter is used
    PageTitles = []
    # IDs which will be processed when the -ids parameter is used
    ids = None
    # a page whose referrers will be processed when the -ref parameter is used
    referredPageTitle = None
    # an image page whose file links will be processed when the -filelinks parameter is used
    fileLinksPageTitle = None
    # a page whose links will be processed when the -links parameter is used
    linkingPageTitle = None
    # will become True when the user presses a ('yes to all') or uses the -always
    # commandline paramater.
    acceptall = False
    # Which namespaces should be processed?
    # default to [] which means all namespaces will be processed
    namespaces = []
    #
    repeat = False

    firstPageTitle = None

    # Read commandline parameters.
    for arg in wikipedia.handleArgs():
        if arg.startswith('-filelinks'):
            if len(arg) == 10:
                fileLinksPageTitle = wikipedia.input(u'Links to which image page should be processed?')
            else:
                fileLinksPageTitle = arg[11:]
            #TODO: Replace 'Image:' with something that automatically gets the name of images based on the language.
            fileLinksPage = wikipedia.Page(wikipedia.getSite(), 'Image:' + fileLinksPageTitle)
            gen = pagegenerators.FileLinksGenerator(fileLinksPage)
        elif arg.startswith('-repeat'):
            repeat = True
        elif arg.startswith('-y'):
            search_in_yahoo = True
        elif arg.startswith('-g'):
            search_in_google = True
        elif arg.startswith('-ny'):
            search_in_yahoo = False
        elif arg.startswith('-ng'):
            search_in_google = False
        elif arg.startswith('-output'):
            if len(arg) >= 8:
                output_file = arg[8:]
        elif arg.startswith('-maxquery'):
            if len(arg) >= 10:
                max_query_for_page = int(arg[10:])
        elif arg.startswith('-new'):
            if len(arg) >=5:
              gen = pagegenerators.NewpagesPageGenerator(number=int(arg[5:]), repeat = repeat)
            else:
              gen = pagegenerators.NewpagesPageGenerator(number=60, repeat = repeat)
        elif arg.startswith('-file'):
            if len(arg) >= 6:
                textfilename = arg[6:]
            gen = pagegenerators.TextfilePageGenerator(textfilename)
        #elif arg.startswith('-idfile'):
        #    if len(arg) >= 11:
        #        textfilename = arg[11:]
        #        ids = read_file(textfilename).splitlines()
        elif arg.startswith('-subcat'):
            catrecurse = True
        elif arg.startswith('-cat'):
            if len(arg) == 4:
                categoryname = wikipedia.input(u'Please enter the category name:')
            else:
                categoryname = arg[5:]
            cat = catlib.Category(wikipedia.getSite(), 'Category:%s' % categoryname)
            if firstPageTitle:
                gen = pagegenerators.CategorizedPageGenerator(cat, recurse = catrecurse, start = firstPageTitle)
            else:
                gen = pagegenerators.CategorizedPageGenerator(cat, recurse = catrecurse)

        elif arg.startswith('-xml'):
            if len(arg) == 4:
                xmlFilename = wikipedia.input(u'Please enter the XML dump\'s filename:')
            else:
                xmlFilename = arg[5:]
        elif arg.startswith('-page'):
            if len(arg) == 5:
                PageTitles.append(wikipedia.input(u'Which page do you want to change?'))
            else:
                PageTitles.append(arg[6:])
            source = 'specificPages'
        elif arg.startswith('-ref'):
            if len(arg) == 4:
                referredPageTitle = wikipedia.input(u'Links to which page should be processed?')
            else:
                referredPageTitle = arg[5:]
            referredPage = wikipedia.Page(wikipedia.getSite(), referredPageTitle)
            gen = pagegenerators.ReferringPageGenerator(referredPage)
        elif arg.startswith('-links'):
            if len(arg) == 6:
                linkingPageTitle = wikipedia.input(u'Links from which page should be processed?')
            else:
                linkingPageTitle = arg[7:]
            linkingPage = wikipedia.Page(wikipedia.getSite(), linkingPageTitle)
            gen = pagegenerators.LinkedPageGenerator(linkingPage)
        elif arg.startswith('-start'):
            if len(arg) == 6:
                firstPageTitle = wikipedia.input(u'Which page do you want to change?')
            else:
                firstPageTitle = arg[7:]
            namespace = wikipedia.Page(wikipedia.getSite(), firstPageTitle).namespace()
            firstPageTitle = wikipedia.Page(wikipedia.getSite(), firstPageTitle).titleWithoutNamespace()
            gen = pagegenerators.AllpagesPageGenerator(firstPageTitle, namespace)
        elif arg.startswith('-namespace:'):
            namespaces.append(int(arg[11:]))

    if PageTitles:
        pages = [wikipedia.Page(wikipedia.getSite(), PageTitle) for PageTitle in PageTitles]
        gen = iter(pages)

    if ids:
        checks_by_ids(ids)

    if not gen and not ids:
        # syntax error, show help text from the top of this file
        wikipedia.output(__doc__, 'utf-8')
    if not gen:
        wikipedia.stopme()
        sys.exit()
    if namespaces != []:
        gen =  pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
    preloadingGen = pagegenerators.PreloadingGenerator(gen, pageNumber = 20)
    bot = CheckRobot(preloadingGen)
    bot.run()
 
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
