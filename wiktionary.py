#!/usr/bin/python
# -*- coding: utf-8  -*-

wiktionaryformats = {
	'nl': {
		'langheader':	u'{{-%%ISOLangcode%%-}}',
		'translang':	u':*{{%%ISOLangcode%%}}',
		'beforeexampleterm': u"'''",
		'afterexampleterm': u"'''",
		'gender': u"{{%%gender%%}}",
		'posheader': {
				'noun':	u'{{-noun-}}',
				'adjective': u'{{-adj-}}',
				'verb': u'{{-verb-}}',
				},
		'translationsheader': u"{{-trans-}}",
		'transbefore': u'{|border=0 width=100%\n|-\n|bgcolor="{{bgclr}}" valign=top width=48%|\n{|\n',
		'transinbetween': u'|}\n| width=1% |\n|bgcolor="{{bgclr}}" valign=top width=48%|\n{|\n',
		'transafter': u'|}\n|}',
		'transnoAtoM': u'<-- Vertalingen van A tot M komen hier>',
		'transnoNtoZ': u'<-- Vertalingen van N tot Z komen hier>',
		'synonymsheader': u"{{-syn-}}",
		'relatedheader': u'{{-rel-}}',
		},
	'en': {
		'langheader':	u'== %%langname%% ==',
		'translang':	u'*%%langname%%',
		'beforeexampleterm': u"'''",
		'afterexampleterm': u"'''",
		'gender': u"''%%gender%%''",
		'posheader': {
				'noun': u'=== Noun ===',
				'adjective': u'=== Adjective ===',
				'verb': u'=== Verb ===',
				},
		'translationsheader': u"==== Translations ====",
		'transbefore': u'{|border=0 width=100%\n|-\n|bgcolor="#FFFFE0" valign=top width=48%|\n{|\n',
		'transinbetween': u'|}\n| width=1% |\n|bgcolor="#FFFFE0" valign=top width=48%|\n{|\n',
		'transafter': u'|}\n|}',
		'transnoAtoM': u'<-- Translations from A tot M go here>',
		'transnoNtoZ': u'<-- Translations from N tot Z go here>',
		'synonymsheader': u"==== Synonyms ====",
		'relatedheader': u'=== Related words ===',
		}
}
			   
langnames = {
	'nl':	{
		'nl' : u'Nederlands',
		'en' : u'Engels',
		'de' : u'Duits',
		'fr' : u'Frans',
		'it' : u'Italiaans',
		'eo' : u'Esperanto',
		'es' : u'Spaans',
		},
	 'de':	{
		'nl' : u'Niederländisch',
		'en' : u'Englisch',
		'de' : u'Deutsch',
		'fr' : u'Französisch',
		'it' : u'Italienisch',
		'eo' : u'Esperanto',
		'es' : u'Spanisch',
		},
	 'en':	{
		'nl' : u'Dutch',
		'en' : u'English',
		'de' : u'German',
		'fr' : u'French',
		'it' : u'Italian',
		'eo' : u'Esperanto',
		'es' : u'Spanish',
		},
	'eo':	{
		'nl' : u'Nederlanda',
		'en' : u'Angla',
		'de' : u'Germana',
		'fr' : u'Franca',
		'it' : u'Italiana',
		'eo' : u'Esperanto',
		'es' : u'Hispana',
		},
	'it':	{
		'nl' : u'olandese',
		'en' : u'inglese',
		'de' : u'tedesco',
		'fr' : u'francese',
		'it' : u'italiano',
		'eo' : u'esperanto',
		'es' : u'spagnuolo',
		},
	'fr':	{
		'nl' : u'nEEEerlandais',
		'en' : u'anglais',
		'de' : u'allemand',
		'fr' : u'franCCCais',
		'it' : u'italien',
		'eo' : u'espEEEranto',
		'es' : u'espagnol',
		},
	'es':	{
		'nl' : u'olandEEEs',
		'en' : u'inglEEEs',
		'de' : u'alemAAAn',
		'fr' : u'francEEEs',
		'it' : u'italiano',
		'eo' : u'esperanto',
		'es' : u'espaNNNol',
		},
}

# A big thanks to Rob Hooft for the following:
class sortonname:
	def __init__(self, lang):
		self.lang = lang

	def __call__(self, one, two):
		return cmp(self.lang[one], self.lang[two])

			   
class WiktionaryEntry:
	"""	This class contains all that can appear on one Wiktionary page
	"""
	def __init__(self,wikilang,term):	# wikilang here refers to the language of the Wiktionary
	  """	Constructor
		Called with two parameters:
		- the language of the Wiktionary it belongs to
		- the term that is described on this page
	  """
		self.wikilang=wikilang
		self.term=term
		self.subentries = {}		# subentries is a dictionary of subentry objects indexed by subentrylang
		self.sortedsubentries = []
		
	def addSubEntry(self,subentry):
	  """	Add a subentry object to this entry  """
		self.subentries.setdefault(subentry.subentrylang, []).append(subentry)
	
	def listSubentries(self):
	  """	Returns a dictionary of subentry objects for this entry  """
		return self.subentries

	def sortSubentries(self):
	  """	Sorts the sortedsubentries list containing the keys of the subentry objects dictionary for this entry  """
		
		if not self.subentries == {}:
			self.sortedsubentries = self.subentries.keys()
			self.sortedsubentries.sort(sortonname(langnames[self.wikilang]))
			
			i = 0
			while i< len(self.sortedsubentries):
				x = self.sortedsubentries[i]
				if x == self.wikilang:	# search the subentry of the same language of the Wiktionary
					samelangsubentry = self.sortedsubentries[i]
					del self.sortedsubentries[i]
					self.sortedsubentries.reverse()
					self.sortedsubentries.append(samelangsubentry)
					self.sortedsubentries.reverse()	# and put it before all the others
					break # FIXME: If there is a cleaner way of accomplishing this
				i+=1

	def wikiwrap(self):
	  """	Returns a string that is ready to be submitted to Wiktionary for this entry  """
		entry = ''
		self.sortSubentries()
#		print "sorted: %s",self.sortedsubentries
		first = 1
		for index in self.sortedsubentries:
			for subentry in self.subentries[index]:
				if first==0:
					entry = entry + '\n----\n'
				else:
					first = 0
				entry= entry + subentry.wikiwrap(self.wikilang)

		# TODO Here something needs to be inserted for treating interwiktionary links
			
		return entry
	
	def showcontents(self):
	  """	Prints the contents of all the subobjects contained in this entry.
		Every subobject is indented a little further on the screen.
		The primary purpose is to help keep your sanity while debugging.
	  """
		indentation = 0
		print ' ' * indentation + 'wikilang = %s'% self.wikilang

		print ' ' * indentation + 'term = %s'% self.term

		subentrieskeys = self.subentries.keys()
		for subentrieskey in subentrieskeys:
			for subentry in self.subentries[subentrieskey]:
				subentry.showcontents(indentation+2)

class SubEntry:
	"""	This class contains the subentries that belong together on one page.
		On Wiktionaries that are still on first character capitalization, this means both [[Kind]] and [[kind]].
		Terms in different languages can be described. Each of these subentries probably represents another language.
	"""
	def __init__(self,subentrylang):
	  """	Constructor
		Called with one parameter:
		- the language of this subentry
	  """
		self.subentrylang=subentrylang
		self.meanings = {} # a dictionary containing the meanings for this term grouped by part of speech
		self.posorder = [] # we don't want to shuffle the order of the parts of speech, so we keep a list to keep the order they were encountered
		
	def addMeaning(self,meaning):
	  """	Lets you add another meaning to this subentry  """
		term = meaning.termi # fetch the term, in order to be able to determine its part of speech in the next step
		self.meanings.setdefault( term.pos, [] ).append(meaning)
		if not term.pos in self.posorder:	# we only need each part of speech once in our list where we keep track of the order
			self.posorder.append(term.pos)
	
	def getMeanings(self):
	  """	Returns a dictionary containing all the meaning objects for this subentry  """
		return self.meanings

	def wikiwrap(self,wikilang):
	  """	Returns a string for this subentry in a format ready for Wiktionary  """
		subentry = wiktionaryformats[wikilang]['langheader'].replace('%%langname%%',langnames[wikilang][self.subentrylang]).replace('%%ISOLangcode%%',self.subentrylang) + '\n'

		for pos in self.posorder:
			meanings = self.meanings[pos]
		
			subentry += wiktionaryformats[wikilang]['posheader'][pos]
			subentry +='\n'	
			
			for meaning in meanings:
				term=meaning.term
			
				subentry = subentry + term.wikiwrapasexample(wikilang) + '; ' + meaning.definition
			
				subentry +='\n'	
			subentry +='\n'	
			if meaning.hasSynonyms():
				subentry = subentry + wiktionaryformats[wikilang]['synonymsheader'] + '\n'
				for meaning in meanings:
					subentry += meaning.wikiwrapSynonyms(wikilang)
				subentry +='\n'	
			
			if meaning.hasTranslations():
				subentry = subentry + wiktionaryformats[wikilang]['translationsheader'] + '\n'
				for meaning in meanings:
					subentry += meaning.wikiwrapTranslations(wikilang,self.subentrylang)
				subentry +='\n'	
		return subentry

	def showcontents(self,indentation):
	  """	Prints the contents of all the subobjects contained in this entry.
		Every subobject is indented a little further on the screen.
		The primary purpose is to help keep your sanity while debugging.
	  """
		print ' ' * indentation + 'subentrylang = %s'% self.subentrylang

		print ' ' * indentation + 'posorder:' + repr(self.posorder)

		meaningkeys = self.meanings.keys()
		for meaningkey in meaningkeys:
			for meaning in self.meanings[meaningkey]:
				meaning.showcontents(indentation+2)

		
			
class Meaning:	
	"""	This class contains one meaning for a word or an expression.
	"""
	def __init__(self,term,definition='',etymology='',synonyms=[],translations={}):
	  """	Constructor
		Generally called with one parameter:
		- The Term object we are describing

		- definition (string) for this term is optional
		- etymology (string) is optional
		- synonyms (list of Term objects) is optional
		- translations (dictionary of Term objects, ISO639 is the key) is optional
	  """
		self.term=term
		self.definition=definition
		self.etymology=etymology
		self.synonyms= synonyms
		self.translations= translations
		
	def setDefinition(self,definition):
	  """	Provide a definition  """
		self.definition=definition
	
	def getDefinition(self):
	  """	Returns the definition  """
		return self.definition
	
	def setEtymology(self,etymology):
	  """	Provide the etymology  """
		self.etymology=etymology
	
	def getEtymology(self):
	  """	Returns the etymology  """
		return self.etymology
	
	def setSynonyms(self,synonyms):
	  """	Provide the synonyms  """
		self.synonyms=synonyms
	
	def getSynonyms(self):
	  """	Returns the list of synonym Term objects  """
		return self.synonyms

	def hasSynonyms(self):
	  """	Returns True if there are synonyms
	  	Returns False if there are no synonyms
	  """
		if self.synonyms == []:
			return False
		else:
			return True
	
	def setTranslations(self,translations):
	  """	Provide the translations  """
		self.translations=translations
	
	def getTranslations(self):
	  """	Returns the translations dictionary containing translation Term objects for this meaning   """
		return self.translations

	def addTranslation(self,translation):
	  """	Add a translation Term object to the dictionary for this meaning
	  	The lang property of the Term object will be used as the key of the dictionary
	  """
	    	self.translations.setdefault( translation.lang, [] ).append( translation )

	def hasTranslations(self):
	  """	Returns True if there are translations
	  	Returns False if there are no translations
	  """
		if self.translations == {}:
			return 0
		else:
			return 1
	
	def wikiwrapSynonyms(self,wikilang):
	  """	Returns a string with all the synonyms in a format ready for Wiktionary  """
		first = 1
		wrappedsynonyms = ''
		for synonym in self.synonyms:
			if first==0:
				wrappedsynonyms += ', '
			else:
				first = 0
			wrappedsynonyms = wrappedsynonyms + synonym.wikiwrapforlist(wikilang)
		return wrappedsynonyms + '\n'
		
	def wikiwrapTranslations(self,wikilang,subentrylang):
	  """	Returns a string with all the translations in a format ready for Wiktionary
	  	The behavior changes with the circumstances.
		For a subentry in the same language as the Wiktionary the full list of translations is output, excluding the local language itself
		- This list of translations has to end up in a table with two columns
		- The first column of this table contains language with names from A to M, the second contains N to Z
		- If a column in this list remains empty a html comment is put in that column
		For a subentry in a foreign language only the translation towards the local language is output.
	  """
		if wikilang == subentrylang:
			# When treating a subentry of the same lang as the Wiktionary, we want to output the translations in such a way that they end up sorted alphabetically on the language name in the language of the current Wiktionary
			alllanguages=self.translations.keys()
			alllanguages.sort(sortonname(langnames[wikilang]))
			wrappedtranslations = wiktionaryformats[wikilang]['transbefore']
			alreadydone = 0
			for language in alllanguages:
				if language == wikilang: continue # don't output translation for the wikilang itself
				# split translations into two column table
				if not alreadydone and langnames[wikilang][language][0:1].upper() > 'M':
					wrappedtranslations = wrappedtranslations + wiktionaryformats[wikilang]['transinbetween']
					alreadydone = 1
				# Indicating the language according to the wikiformats dictionary
				wrappedtranslations = wrappedtranslations + wiktionaryformats[wikilang]['translang'].replace('%%langname%%',langnames[wikilang][language]).replace('%%ISOLangcode%%',language) + ': '
				rst = 1
				for translation in self.translations[language]:
					term=translation.term
					if first==0:
						wrappedtranslations += ', '
					else:					
						first = 0
					wrappedtranslations = wrappedtranslations + translation.wikiwrapastranslation(wikilang)
				wrappedtranslations += '\n'
			if not alreadydone:
				wrappedtranslations = wrappedtranslations + wiktionaryformats[wikilang]['transinbetween'] + '\n' + wiktionaryformats[wikilang]['transnoNtoZ'] + '\n'
				alreadydone = 1
			wrappedtranslations = wrappedtranslations + wiktionaryformats[wikilang]['transafter'] + '\n'
		else:
			# For the other subentries we want to output the translation in the language of the Wiktionary
			wrappedtranslations = wiktionaryformats[wikilang]['translang'].replace('%%langname%%',langnames[wikilang][wikilang]).replace('%%ISOLangcode%%',wikilang) + ': '
			first = 1
			for translation in self.translations[wikilang]:
				term=translation.term
				if first==0:
					wrappedtranslations += ', '
				else:					
					first = 0
				wrappedtranslations = wrappedtranslations + translation.wikiwrapastranslation(wikilang)
		return wrappedtranslations			
			
	def showcontents(self,indentation):
	  """	Prints the contents of this meaning.
		Every subobject is indented a little further on the screen.
		The primary purpose is to help keep your sanity while debugging.
	  """
		print ' ' * indentation + 'term: '
		self.term.showcontents(indentation+2)
		print ' ' * indentation + 'definition = %s'% self.definition
		print ' ' * indentation + 'etymology = %s'% self.etymology

		print ' ' * indentation + 'Synonyms:'
		for synonym in self.synonyms:
			synonym.showcontents(indentation+2)

		print ' ' * indentation + 'Translations:'
		translationkeys = self.translations.keys()
		for translationkey in translationkeys:
			for translation in self.translations[translationkey]:
				translation.showcontents(indentation+2)

			
		
class Term:
	"""	This is a superclass for terms.
	"""
	def __init__(self,lang,term,relatedwords=[]):
	  """	Constructor
		Generally called with two parameters:
		- The language of the term
		- The term (string)

		- relatedwords (list of Term objects) is optional
	  """
		self.lang=lang	
		self.term=term
		self.relatedwords=relatedwords
	
	def __getitem__(self):
	  """	Documenting as an afterthought is a bad idea
	  	I don't know anymore why I added this, but I'm pretty sure it was in response to an error message
	  """
		return self

	def setTerm(self,term):
		self.term=term
	
	def getTerm(self):
		return self.term

	def setLang(self,lang):
		self.lang=lang

	def getLang(self):
		return self.lang

	def wikiwrapgender(self,wikilang):
	  """	Returns a string with the gender in a format ready for Wiktionary, if it is applicable
	  """
		if self.gender:
			return ' ' + wiktionaryformats[wikilang]['gender'].replace('%%gender%%',self.gender)
		else:
			return ''
		
	def wikiwrapasexample(self,wikilang):
	  """	Returns a string with the gender in a format ready for Wiktionary, if it is applicable
	  """
		return wiktionaryformats[wikilang]['beforeexampleterm'] + self.term + wiktionaryformats[wikilang]['afterexampleterm'] + self.wikiwrapgender(wikilang)
			
	def wikiwrapforlist(self,wikilang):
	  """	Returns a string with this term as a link followed by the gender in a format ready for Wiktionary
	  """
		return '[[' + self.term + ']]' + self.wikiwrapgender(wikilang)
	
	def wikiwrapastranslation(self,wikilang):
	  """	Returns a string with this term as a link followed by the gender in a format ready for Wiktionary
	  """
		return '[[' + self.term + ']]' + self.wikiwrapgender(wikilang)
	
	def showcontents(self,indentation):
	  """	Prints the contents of this Term.
		Every subobject is indented a little further on the screen.
		The primary purpose is to help keep your sanity while debugging.
	  """
		print ' ' * indentation + 'lang = %s'% self.lang
		print ' ' * indentation + 'pos = %s'% self.pos
		print ' ' * indentation + 'term = %s'% self.term
		print ' ' * indentation + 'relatedwords = %s'% self.relatedwords

class Noun(Term):
	"""	This is class inherits from Term.
		It adds properties and methods specific to nouns
	"""
	def __init__(self,lang,term,gender=''):
	  """	Constructor
		Generally called with two parameters:
		- The language of the term
		- The term (string)

		- gender is optional
	  """
		self.pos='noun'		# part of speech
		self.gender=gender
		Term.__init__(self,lang,term)

	def setGender(self,gender):
		self.gender=gender
		
	def getGender(self):
		return(self.gender)
	
	def showcontents(self,indentation):
		Term.showcontents(self,indentation)
		print ' ' * indentation + 'gender = %s'% self.gender

class Adjective(Term):
	def __init__(self,lang,term,gender=''):
		self.pos='adjective'		# part of speech
		self.gender=gender
		Term.__init__(self,lang,term)

	def setGender(self,gender):
		self.gender=gender
		
	def getGender(self):
		return(self.gender)

	def showcontents(self,indentation):
		Term.showcontents(self,indentation)
		print ' ' * indentation + 'gender = %s'% self.gender

if __name__ == '__main__':
	apage = WiktionaryEntry('nl',u'iemand')
#	print 'Wiktionary language: %s'%apage.wikilang
#	print 'Wiktionary apage: %s'%apage.term
#	print
	aword = Noun('nl',u'iemand')
#	print 'Noun: %s'%aword.term
	aword.setGender('m')
#	print 'Gender: %s'%aword.gender
	frtrans = Noun('fr',u"quelqu'un")
	frtrans.setGender('m')
	entrans1 = Noun('en',u'somebody')
	entrans2 = Noun('en',u'someone')
#	print 'frtrans: %s'%frtrans

	ameaning = Meaning(u'een persoon',aword)
	ameaning.addTranslation(frtrans)
#	print ameaning.translations
	ameaning.addTranslation(entrans1)
#	print ameaning.translations
	ameaning.addTranslation(entrans2)
#	print ameaning.translations
	ameaning.addTranslation(aword) # This is for testing whether the order of the translations is correct

	asubentry = SubEntry('en')
	asubentry.addMeaning(ameaning)

	apage.addSubEntry(asubentry)

	print
	t=apage.wikiwrap()
	print t
	apage.wikilang = 'en'
	print
	t=apage.wikiwrap()
	print t

	apage = WiktionaryEntry('nl',u'Italiaanse')
	aword = Noun('nl',u'Italiaanse','f')
	ameaning = Meaning(u'vrouwelijke persoon die uit [[Italië]] komt',aword)

#	{{-rel-}}
#	* [[Italiaan]]
	detrans = Noun('de',u'Italienerin','f')
	entrans = Noun('en',u'Italian')
	frtrans = Noun('fr',u'Italienne','f')
	ittrans = Noun('it',u'italiana','f')

	ameaning.addTranslation(detrans)
	ameaning.addTranslation(entrans)
	ameaning.addTranslation(frtrans)
	ameaning.addTranslation(ittrans)
	
	asubentry = SubEntry('nl')
	asubentry.addMeaning(ameaning)

	apage.addSubEntry(asubentry)

	aword = Adjective('nl',u'Italiaanse')
	ameaning = Meaning(u'uit Italië afkomstig',aword)
	anothermeaning = Meaning(u'gerelateerd aan de Italiaanse taal',aword)

	detrans = Noun('de',u'italienisch')
	entrans = Noun('en',u'Italian')
	frtrans = Noun('fr',u'italien','m')
	frtrans2 = Noun('fr',u'italienne','f')
	ittrans = Noun('it',u'italiano','m')
	ittrans2 = Noun('it',u'italiana','f')

	ameaning.addTranslation(detrans)
	ameaning.addTranslation(entrans)
	ameaning.addTranslation(frtrans)
	ameaning.addTranslation(frtrans2)
	ameaning.addTranslation(ittrans)
	ameaning.addTranslation(ittrans2)
	
	anothermeaning.addTranslation(detrans)
	anothermeaning.addTranslation(entrans)
	anothermeaning.addTranslation(frtrans)
	anothermeaning.addTranslation(frtrans2)
	anothermeaning.addTranslation(ittrans)
	anothermeaning.addTranslation(ittrans2)

	asubentry.addMeaning(ameaning)
	asubentry.addMeaning(anothermeaning)

	apage.addSubEntry(asubentry)

	print
	u=apage.wikiwrap()
	print u

#	{{-syn-}}
#	* [[Italiaans]]
	
	
#	{{-nl-}}
#	{{-noun-}}
#	'''Italiaanse''' {{f}}; vrouwelijke persoon die uit [[Italië]] komt

#	{{-rel-}}
#	* [[Italiaan]]

#	{{-trans-}}
#	*{{de}}: [[Italienierin]] {{f}}
#	*{{en}}: [[Italian]]
#	*{{fr}}: [[Italienne]] {{f}}
#	*{{it}}: [[italiana]] {{f}}

#	{{-adj-}}
#	#'''Italiaanse'''; uit Italië afkomstig
#	#'''Italiaanse'''; gerelateerd aan de Italiaanse taal

#	{{-syn-}}
#	* [[Italiaans]]
	
