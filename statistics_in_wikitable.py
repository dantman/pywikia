#!/usr/bin/python
# -*- coding: utf-8  -*-
"""


\03{lightyellow}This bot renders statistics provided by [[Special:Statistics]] in a table on a wiki page.\03{default}
Thus it creates and updates a Statistics wikitable.

The following parameters are supported:

\03{lightred}-screen\03{default}     If True, doesn't do any changes, but only shows the statistics.

\03{lightgreen}-page\03{default}	On what page statistics are rendered.
		If not existing yet, it is created.
		If existing, it is updated.
"""
__version__ = '$Id$'
import wikipedia, pagegenerators, query
import simplejson, time

# This is the title of the wikipage where to render stats.
your_page = "Logstats"

summary_update = {
    'en':u'Updating some statistics.',
    }
summary_creation = {
    'en':u'Creating statistics log page.',
    }


class StatisticsBot:
	def __init__ (self, screen, your_page):
		"""
		Constructor. Parameter:
		    * screen    - If True, doesn't do any real changes, but only shows
		                  some stats.
		"""
		self.screen = screen
		self.your_page = your_page
		self.dict = self.getdata() # Try to get data.

	def run(self):
		if self.screen:
			wikipedia.output("Bot is running to output stats.")
			self.idle(1) # Run a function to idle
			self.outputall()
		if not self.screen:
			self.outputall() # Output all datas on screen.
			wikipedia.output("\nBot is running. Going to treat \03{lightpurple}%s\03{default}..." % self.your_page )
			self.idle(2)
			self.treat()

	def getdata(self): # getdata() returns a dictionnary of the query to api.php?action=query&meta=siteinfo&siprop=statistics
		# This method return data in a dictionnary format.
		# View data with: api.php?action=query&meta=siteinfo&siprop=statistics&format=jsonfm
		params = {
		'action'    :'query',
		'meta'      :'siteinfo',
		'siprop'    :'statistics',
		}
		wikipedia.output("\nQuerying api for json-formatted data...")
		try:
			data = query.GetData(params,
								 useAPI = True, encodeTitle = False)
		except:
			site = wikipedia.getSite()
			url = site.protocol() + '://' + site.hostname() + site.api_address()
			wikipedia.output("The query has failed. Have you check the API? Cookies are working?")
			wikipedia.output(u"\n>> \03{lightpurple}%s\03{default} <<" % url)
		if data != None:
			wikipedia.output("Extracting statistics...")
			data = data['query']      # "query" entry of data.
			dict = data['statistics'] # "statistics" entry of "query" dict.
			return dict

	def treat(self):
			site = wikipedia.getSite()
			page = wikipedia.Page(site, self.your_page)
			if page.exists():
				wikipedia.output(u'\nWikitable on \03{lightpurple}%s\03{default} will be completed with:\n' % self.your_page )
				text = page.get()
				newtext = self.newraw()
				wikipedia.output(newtext)
				choice = wikipedia.inputChoice(u'Do you want to add these on wikitable?', ['Yes', 'No'], ['y', 'N'], 'N')
				text = text[:-3] + newtext
				summ = wikipedia.translate(site, summary_update)
				if choice == 'y':
					try:
						page.put(u''.join(text), summ)
					except:
						wikipedia.output(u'Impossible to edit. It may be an edit conflict... Skipping...')
			else:
				wikipedia.output(u'\nWikitable on \03{lightpurple}%s\03{default} will be created with:\n' % self.your_page )
				newtext = self.newtable()+self.newraw()
				wikipedia.output(newtext)
				summ = wikipedia.translate(site, summary_creation)
				choice = wikipedia.inputChoice(u'Do you want to accept this page creation?', ['Yes', 'No'], ['y', 'N'], 'N')
				if choice == 'y':
					try:
						page.put(newtext, summ)
					except wikipedia.LockedPage:
						wikipedia.output(u"Page %s is locked; skipping." % title)
					except wikipedia.EditConflict:
						wikipedia.output(u'Skipping %s because of edit conflict' % title)
					except wikipedia.SpamfilterError, error:
						wikipedia.output(u'Cannot change %s because of spam blacklist entry %s' % (title, error.url))

	def newraw(self):
		newtext = ('\n|----\n!\'\''+ self.date() +'\'\'')	# new raw for date and stats
		for name in self.dict:
			newtext += '\n|'+str(abs(self.dict[name]))
		newtext += '\n|----\n|}'
		return newtext

	def newtable(self):
		newtext = ('\n{| class=wikitable style=text-align:center\n!'+ "date")	# create table
		for name in self.dict:
			newtext += '\n|'+name
		return newtext

	def	date(self):
		rightime = time.localtime(time.time())
		year = str(rightime[0])
		month = str(rightime[1])
		day = str(rightime[2])
		date = year+'/'+month+'/'+day
		return date
	def outputall(self):
		list = self.dict.keys()
		list.sort()
		for name in self.dict:
			wikipedia.output("There are "+str(self.dict[name])+" "+name)
	def idle(self, retry_idle_time):
		time.sleep(retry_idle_time)
		wikipedia.output(u"Starting in %i second..." % retry_idle_time)
		time.sleep(retry_idle_time)

def main(your_page):
	screen = False # If True it would not edit the wiki, only output statistics
	_page = None

	wikipedia.output("\nBuilding the bot...")
	for arg in wikipedia.handleArgs():	# Parse command line arguments
		if arg.startswith('-page'):
			if len(arg) == 5:
				_page = wikipedia.input(u'On what page do you want to add statistics?')
			else:
				_page = arg[6:]
		if arg.startswith("-screen"):
			screen = True
	if not _page:
		_page = your_page
		if not screen:
			wikipedia.output("The bot will add statistics on %s.\n" % _page )
	bot = StatisticsBot(screen, _page) # Launch the instance of a StatisticsBot
	bot.run() # Execute the 'run' method

if __name__ == "__main__":
    try:
        main(your_page)
    finally:
        wikipedia.stopme()
