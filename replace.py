"""
This bot parse articles and replace a text by another. This is
a development script and should not be used on live wikipedia
cause you will break things using it.

Author: Ashar Voultoiz 2004.

Parts of this code have been copied from the project:

		Python Wikipedia Robot Framework
		http://pywikipediabot.sf.net/

which include code from (in no particular order):
	Andre Engels
	Christian List
	Ashar Voultoiz
	Rob W.W. Hooft
	Thomas R. Koll

		
Arguments:
	-file : file containing the articles to be fixed
	
	-search : file name containing text we will search for

	-subst  : file name containing text using to replace

	The text file MUST be encoded using iso-8859-1 for now.
	
The others arguments are append to the list of articles.


TODO:
-search and -subst should have default filename such as:
	replace_search.txt
	replace_subst.txt

"""

import sys, re, wikipedia

articlelist = []
textsearch=""
textsubst=""
comment = "bot replacing text"

""" functions """

def parseFile(filename):
# function used to parse the file and build the article list
# that will be parsed

	global articlelist

	# open the file and prepare the line format
	f=open(filename,'r')
	R=re.compile(r'.*\[\[([^\]]*)\]\].*')
	
	# parse the file
	for line in f.readlines():
		# try to find an article
		m = R.match(line)
		if m:
			# add it to the list for future use
			articlelist.append(m.group(1))
		else:
			print "ERROR: Did not understand %s line:\n%s" % (arg[6:], repr(line))
	
	f.close()
	
	return True


# parse arguments
for arg in sys.argv[1:]:
	# bot understand common arguments
	if wikipedia.argHandler(arg):
		pass
	# file containing the list of articles
	elif arg.startswith('-file:'):
		parseFile(arg[6:])
	elif arg.startswith('-search:'):
		f=open(arg[8:])
		textsearch = f.read()
	elif arg.startswith('-subst:'):
		f=open(arg[7:])
		textsubst = f.read()
	else:
		articlelist.append(arg)
	
# main loop passing through each articles		
for article in articlelist:
	text = ""
	# new article object
	pl = wikipedia.PageLink(wikipedia.mylang, article)
	try:
		text = pl.get()
	except wikipedia.NoPage:
		print "ERROR: couldn't find " + article
	
	newtext = re.sub(unicode(textsearch,'iso-8859-1'), unicode(textsubst,'iso-8859-1'), text, 1)
	
	if newtext!=text:
		print "Replacing matching text"
		pl.put(newtext, comment)