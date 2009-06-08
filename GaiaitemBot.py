# -*- coding: utf-8  -*-
"""
This bot is used for quick creation of Item Articles.
"""

import sys, sre, re
import wikipedia, pagegenerators, catlib, config

msg = {
       'en':u'GaiaitemBot Partial Item Creation.',
       }

def main():
	finished = False
	
	gaia = wikipedia.getSite(code=u'en', fam=u'gaia')
	wikipedia.setAction(wikipedia.translate(gaia, msg))
	wikipedia.output(u'Welcome to the Gaiabot Item Creatior.')
	
	blank = sre.compile(u'^$', sre.UNICODE)
	
	while not finished:
		wikipedia.output(u'Begining Process...')
		choice = wikipedia.inputChoice(u'Do you wish to create a item?',  ['Yes', 'No'], ['y', 'N'], 'N')
		if choice in ['n', 'N']:
			finished = True
		else:
			wikipedia.output(u'Please enter the asked values to create a Item partial.')
			name = u''
			image = u''
			thumb = False
			price = u''
			store = u''
			gender = u''
			description = u''
			month = u''
			year = u''
			isDonation = False
			alt = u''
			otheritem = u''
			
			intro = u''
			
			trivia = []
			external = []
			groups = []
			animalHats = False
			animalMasks = False
			masks = False
			headgear = False
			
			while name.isspace() or sre.match(blank, name) != None:
				name = wikipedia.input(u'Please enter the item name: ').strip(u' ').strip(u'	')
			choice = wikipedia.inputChoice(u'Is this a donation Item?',  ['Yes', 'No'], ['y', 'N'], 'N')
			if choice in ['y', 'Y']:
				isDonation = True
				alt = wikipedia.input(u'(Optional)Please enter the item\'s alternate name if it has one: ').strip(u' ').strip(u'	')
				otheritem = wikipedia.input(u'(Optional)Please enter the name of other item released this month: ').strip(u' ').strip(u'	')
			else:
				intro = wikipedia.input(u'Please enter the intro statement for the item: ').strip(u' ').strip(u'	')
			image = wikipedia.input(u'If it has one, please enter the name of the image for the Item. No Item: Prefix: ').strip(u' ').strip(u'	')
			if not image.isspace() and sre.match(blank, image) == None:
				choice = wikipedia.inputChoice(u'Does this image need to become a thumbnail for space (Large Images only.)?',  ['Yes', 'No'], ['y', 'N'], 'N')
				if choice in ['y', 'Y']:
					thumb = True
			price = wikipedia.input(u'Please enter the item\'s price, if it is not sold in stores leave blank: ').strip(u' ').strip(u'	')
			store = wikipedia.input(u'Please enter the name of the store that the item is sold at: ').strip(u' ').strip(u'	')
			gender = wikipedia.input(u'Please enter the gender that the item can be equiped to, leave blank for Any: ').strip(u' ').strip(u'	')
			description = wikipedia.input(u'Please enter the item description: ').strip(u' ').strip(u'	')
			choice = wikipedia.inputChoice(u'What Month was this item released in?',  ['January', 'Fenuary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Unknown'], ['jan', 'feb', 'mar', 'apr', 'may', 'june', 'july', 'aug', 'sept', 'oct', 'nov', 'dec', 'u'], 'u')
			if choice in ['jan', 'Jan', 'january', 'January']:
				month = u'January'
			elif choice in ['feb', 'Feb', 'feburary', 'Febuary']:
				month = u'Febuary'
			elif choice in ['mar', 'Mar', 'march', 'March']:
				month = u'March'
			elif choice in ['apr', 'Apr', 'april', 'April']:
				month = u'April'
			elif choice in ['may', 'May']:
				month = u'May'
			elif choice in ['june', 'June']:
				month = u'June'
			elif choice in ['july', 'July']:
				month = u'July'
			elif choice in ['aug', 'Aug', 'august', 'August']:
				month = u'August'
			elif choice in ['sep', 'Sep', 'sept', 'Sept', 'september', 'September']:
				month = u'September'
			elif choice in ['oct', 'Oct', 'october', 'October']:
				month = u'October'
			elif choice in ['nov', 'Nov', 'november', 'November']:
				month = u'November'
			elif choice in ['dec', 'Dec', 'december', 'December']:
				month = u'December'
			year = wikipedia.input(u'What year was this item released in?').strip(u' ').strip(u'	')
			incomplete = True
			while incomplete:
				t = wikipedia.input(u'You may enter multiple entrys for the trivia section here. Leave the box blank when you are finished: ').strip(u' ').strip(u'	')
				if not t.isspace() and sre.match(blank, t) == None:
					trivia.append(t)
				else:
					incomplete = False
			incomplete = True
			while incomplete:
				e = wikipedia.input(u'Please enter a URL for the External links section. Use Blank when finished: ').strip(u' ').strip(u'	')
				if not e.isspace() and sre.match(blank, e) == None:
					c = wikipedia.input(u'Please enter a caption for this URL if you wish: ').strip(u' ').strip(u'	')
					external.append((e, c))
				else:
					incomplete = False
			incomplete = True
			while incomplete:
				g = wikipedia.input(u'Please enter the names of the normal Item Groups this Item is in. Leave the box blank when you are finished(Do not use special groups): ').strip(u' ').strip(u'	')
				if not g.isspace() and sre.match(blank, g) == None:
					groups.append(g)
				else:
					incomplete = False
			incomplete = True
			choice = wikipedia.inputChoice(u'Is this a in the Special group "Animal Hats"?',  ['Yes', 'No'], ['y', 'N'], 'N')
			if choice in ['y', 'Y']:
				animalHats = True
			choice = wikipedia.inputChoice(u'Is this a in the Special group "Animal Masks"?',  ['Yes', 'No'], ['y', 'N'], 'N')
			if choice in ['y', 'Y']:
				animalMasks = True
			choice = wikipedia.inputChoice(u'Is this a in the Special group "Masks"?',  ['Yes', 'No'], ['y', 'N'], 'N')
			if choice in ['y', 'Y']:
				masks = True
			choice = wikipedia.inputChoice(u'Is this a in the Special group "Headgear"?',  ['Yes', 'No'], ['y', 'N'], 'N')
			if choice in ['y', 'Y']:
				headgear = True
			outputTo = wikipedia.input(u'(Required)Please enter the article name you wish to output the Item Partial to: ').strip(u' ').strip(u'	')
			
			if not outputTo.isspace() and sre.match(blank, outputTo) == None:
				pageData = u''
				if isDonation:
					pageData+=u'{{donationIntro|name=%s|' % name
					if not alt.isspace() and sre.match(blank, alt) == None:
						pageData+=u'alt=%s|' % alt
					pageData+=u'month=%s|year=%s|other=%s}}\n' % (month, year, other)
				else:
					pageData+=u'%s\n' % intro
				pageData+=u'{{item|name=%s' % name
				if not image.isspace() and sre.match(blank, image) == None:
					pageData+=u'|image=%s' % image
					if thumb:
						pageData+=u'|thumb=true'
				if not price.isspace() and sre.match(blank, price) == None:
					pageData+=u'|price=%s' % price
				if not store.isspace() and sre.match(blank, store) == None:
					pageData+=u'|store=%s' % store
				if not gender.isspace() and sre.match(blank, gender) == None:
					pageData+=u'|gender=%s' % gender
				pageData+=u'|description=%s' % description
				if not month.isspace() and sre.match(blank, month) == None:
					pageData+=u'|month=%s' % month
				if not year.isspace() and sre.match(blank, year) == None:
					pageData+=u'|year=%s' % year
				pageData+=u'}}\n'
				pageData+=u'==Trivia==\n'
				if len(trivia) > 0:
					for t in trivia:
						pageData+=u'%s\n\n' % t
				else:
					pageData+=u'???\n\n'
				pageData+=u'==External Links==\n'
				for url, comment in external:
					pageData+=u'* %s' % url
					if not comment.isspace() and sre.match(blank, comment) == None:
						pageData+=u' - %s' % comment
					pageData+=u'\n'
				pageData+=u'\n'
				pageData+=u'{{itemGroups'
				for g in groups:
					pageData+=u'|%s' % g
				if animalHats:
					pageData+=u'|Animal Hats'
				if animalMasks:
					pageData+=u'|Animal Masks'
				if masks:
					pageData+=u'|Masks'
				if headgear:
					pageData+=u'|Headgear'
				pageData+=u'}}'
				
				page = wikipedia.Page(gaia, u'%s' % outputTo)
				old = u''
				try:
					old = page.get()
				except wikipedia.NoPage:
					old = u''
				page.put(old + pageData)
			

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()