# -*- coding: utf-8  -*-
"""
"""

from __future__ import generators
import sys, re, codecs, os
import wikipedia, pagegenerators, catlib, config

__version__='$Id$'

search_in_google=True
search_in_yahoo=True
exclude_quote = True
search_request_retry=10
max_query_for_page=25

pages_for_exclusion_database = [
('en', 'Wikipedia:Mirrors_and_forks/Abc', 'Abc.txt'),
('en', 'Wikipedia:Mirrors_and_forks/Def', 'Def.txt'),
('en', 'Wikipedia:Mirrors_and_forks/Ghi', 'Ghi.txt'),
('en', 'Wikipedia:Mirrors_and_forks/Jkl', 'Jkl.txt'),
('en', 'Wikipedia:Mirrors_and_forks/Mno', 'Mno.txt'),
('en', 'Wikipedia:Mirrors_and_forks/Pqr', 'Pqr.txt'),
('en', 'Wikipedia:Mirrors_and_forks/Stu', 'Stu.txt'),
('en', 'Wikipedia:Mirrors_and_forks/Vwxyz', 'Vwxyz.txt'),
('it', 'Wikipedia:Cloni', 'Cloni.txt'),
]

def exclusion_file_list():
 import mediawiki_messages
 for i in pages_for_exclusion_database:
  path = 'copyright/' + i[0] + '/' + i[2]
  mediawiki_messages.makepath(path)
  p = wikipedia.Page(wikipedia.getSite(i[0]),i[1])
  yield p, path

def load_pages():
 import time, os
 write = False
 for page, path in exclusion_file_list():
  try:
    file_age = time.time() - os.path.getmtime(path)
    if file_age > 24 * 60 * 60:
      print 'Updating source pages to exclude new URLs...'
      write = True
  except OSError:
      write = True

  if write:
      f = codecs.open(path, 'w', 'utf-8')
      f.write(page.get())
      f.close()
 return

def check_list(text, cl):
   for entry in cl:
     if entry:
       if text.find(entry) != -1:
         print 'SKIP URL ' + text
#         print 'DEBUG: ' + entry
         return True

def exclusion_list():
	import glob
	prelist = []
        load_pages()
	for page, path in exclusion_file_list():
		f = codecs.open(path, "r", 'utf-8')
		data = f.read()
		f.close()
                # wikipedia:en:Wikipedia:Mirrors and forks
		prelist += re.findall("(?i)url\s*=\s*<nowiki>(?:http://)?(.*?)</nowiki>", data)
		prelist += re.findall("(?i)\*\s*Site:\s*\[?(?:http://)?(.*?)\]?", data)
		# wikipedia:it:Wikipedia:Cloni
                if 'copyright/it/Cloni.txt' in path:
                  prelist += re.findall('(?i)^==(?!=)\s*\[?\s*(?:<nowiki>)?(?:http://)?(.*?)(?:</nowiki>)?\s*\]?\s*==', data)
#		  prelist += re.findall("(?i)<h2>\s*(?:http://)?(.*?)\s*</h2>", data)
	list1 = []
	for entry in prelist:
		list1 += entry.split(", ")
	list2 = []
	for entry in list1:
		list2 += entry.split("and ")
	list3 = []
	for entry in list2:
		entry = re.sub("http://", "", entry)
		if entry:
		        if '/' in entry:
		          list3 += [re.sub(" .*", "", entry[:entry.rfind('/')])]
                        else:
                          list3 += [re.sub(" .*", "", entry)]
#			list3 += [re.sub("/.*", "", entry)]
	f = codecs.open('copyright/exclusion_list.txt', 'r','utf-8')
          list3 += re.sub(" ?#.*","",f.read()).splitlines()
	f.close()
	return list3

def write_log(text, filename = "copyright/output.txt"):
    file1=codecs.open(filename, 'a', 'utf-8')
    file1.write(text)
    file1.close()

def cleanwikicode(text):
    if not text:
      return ""
#    wikipedia.output(text)
    text = text.replace("<br>", "")
    text = text.replace("<br/>", "")
    text = text.replace("<br />", "")
    text = re.sub('<!--.*?-->', '', text)

    if exclude_quote:
      text = re.sub("(?i){{quote|.*?}}", "", text)
      text = re.sub("^:''.*?''\.?\s*((\(|<ref>).*?(\)|</ref>))?\.?$", "", text)
      text = re.sub('^[:*]?["][^"]+["]\.?\s*((\(|<ref>).*?(\)|</ref>))?\.?$', "", text)
      text = re.sub('^[:*]?[«][^»]+[»]\.?\s*((\(|<ref>).*?(\)|</ref>))?\.?$', "", text)
      text = re.sub('^[:*]?[“][^”]+[”]\.?\s*((\(|<ref>).*?(\)|</ref>))?\.?$', "", text)

    text = re.sub('http://[a-z/._%0-9]+ ', ' ', text)
    text = re.sub('\[\[[^\|]+\|(.*?)\]\]', '\\1', text)
    text = re.sub('{{.*?}}', '', text)
    text = text.replace("''", "")
    text = text.replace("[", "")
    text = text.replace("]", "")
    text = re.sub('^[*:;]', '', text)

    text = text.replace("<!--", "")
    text = text.replace("-->", "")

    #wikipedia.output("CLEANED: %s" % (text))
    return text

excl_list = exclusion_list()

def query(lines = [], max_query_len = 1300):
# Google max_query_len = 1480?
# - '-Wikipedia ""' = 1467
 output = u""
 n_query = 0

 for line in lines:
  line = cleanwikicode(line)
  if len(line)>200:
    n_query+=1
    if n_query>max_query_for_page:
      print "Max query limit for page reached"
      return output
    if len(line)>max_query_len:
      line=line[:max_query_len]
      glen=len(line)
      while line[glen-1] != ' ':
        glen -= 1
        line = line[:glen]
#    wikipedia.output(line)
    results = get_results(line)
    for url, engine in results:
       output += '\n*%s - %s' % (engine, url)
    if results:
       output += '\n**' + line
 return output

def check_urllist(url, add_item):
    for i in range(len(url)):
      if add_item in url[i]:
         url[i] = (add_item, 'google, yahoo')
         return True
    return False

def get_results(query, numresults = 10):
  url = list()
  if search_in_google:
    import google
    google.LICENSE_KEY = config.google_key
    print "  google query..."
    search_request_retry = 6
    while search_request_retry:
#SOAP.faultType: <Fault SOAP-ENV:Server: Exception from service object: Daily limit of 1000 queries exceeded for key xxx>
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
    data = yahoo.search.web.WebSearch(config.yahoo_appid, query='"' + query.encode('utf_8')+'" -Wikipedia', results=numresults)
    search_request_retry = 6
    while search_request_retry:
     try:
      for entry in data.parse_results():
        if not check_urllist(url, entry.Url):
          url.append((entry.Url, 'yahoo'))
      search_request_retry = 0
     except Exception, err:
        print "Got an error ->", err
        search_request_retry -= 1

  offset = 0
  for i in range(len(url)):
    if check_list(url[i+offset][0], excl_list):
       url.pop(i+offset)
       offset+=-1
  return url

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

    	    wikipedia.output(page.title())

	    if original_text:
                output = query(lines=original_text.splitlines())
                if output:
                   write_log('=== [[' + page.title() + ']] ===' + output + '\n')

def main():
    global search_in_google, search_in_yahoo
    gen = None
    # Can either be 'xmldump', 'textfile' or 'userinput'.
    source = None
    # the textfile's path, either absolute or relative, which will be used when
    # source is 'textfile'.
    textfilename = None
    # the category name which will be used when source is 'category'.
    categoryname = None
    # pages which will be processed when the -page parameter is used
    PageTitles = []
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
    # Which page to start
    startpage = None
    repeat = False

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
        elif arg.startswith('-new'):
            if len(arg) >=5:
              gen = pagegenerators.NewpagesPageGenerator(number=int(arg[5:]), repeat = repeat)
            else:
              gen = pagegenerators.NewpagesPageGenerator(number=80, repeat = repeat)
        elif arg.startswith('-file'):
            if len(arg) >= 6:
                textfilename = arg[6:]
            gen = pagegenerators.TextfilePageGenerator(textfilename)
        elif arg.startswith('-cat'):
            if len(arg) == 4:
                categoryname = wikipedia.input(u'Please enter the category name:')
            else:
                categoryname = arg[5:]
            cat = catlib.Category(wikipedia.getSite(), 'Category:%s' % categoryname)
            gen = pagegenerators.CategorizedPageGenerator(cat)
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

    if not gen:
        # syntax error, show help text from the top of this file
        wikipedia.output(__doc__, 'utf-8')
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
