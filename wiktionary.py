#!/usr/bin/python
# -*- coding: utf-8  -*-

wiktionaryformats = {
	'nl': {
		'langheader':	u'{{-%%ISOLangcode%%-}}',
		'translang':	u'*{{%%ISOLangcode%%}}',
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
		'transnoMtoZ': u'<-- Vertalingen van N tot Z komen hier>',
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
		'transnoMtoZ': u'<-- Translations from N tot Z go here>',
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

			   
class WiktionaryEntry:				# This refers to an entire page
	def __init__(self,wikilang,term):	# wikilang here refers to the language of the Wiktionary
		self.wikilang=wikilang
		self.term=term
		self.subentries = {}		# subentries is a dictionary of subentry objects indexed by subentrylang
		self.sortedsubentries = []
		
	def addSubEntry(self,subentry):
#	    	self.translations.setdefault( translation.lang, [] ).append( translation )
		print "already available subentries: %s"%self.subentries
		self.subentries.setdefault(subentry.subentrylang, []).append(subentry)
	
	def listSubentries(self):
		return self.subentries

	def sortSubentries(self):
		
		print self.subentries
		if not self.subentries == {}:
			self.sortedsubentries = self.subentries.keys()
			self.sortedsubentries.sort(sortonname(langnames[self.wikilang]))
			
			print "should now be sorted: %s"%self.sortedsubentries
			i = 0
			while i< len(self.sortedsubentries):
				x = self.sortedsubentries[i]
				if x == self.wikilang:	# search the subentry of the same language of the Wiktionary
					samelangsubentry = self.sortedsubentries[i]
					del self.sortedsubentries[i]
					self.sortedsubentries.reverse()
					self.sortedsubentries.append(samelangsubentry)
					self.sortedsubentries.reverse()	# and put it before all the others
					break
				i+=1

	def wikiwrap(self):
		entry = ''
		self.sortSubentries()
		print "sorted: %s",self.sortedsubentries
		for index in self.sortedsubentries:
			for subentry in self.subentries[index]:
				entry= entry + subentry.wikiwrap(self.wikilang) + '\n----\n'

		# TODO Here something needs to be inserted for treating interwiktionary links
			
		return entry
	
	def showcontents(self):
		indentation = 0
		print ' ' * indentation + 'wikilang = %s'% self.wikilang

		print ' ' * indentation + 'term = %s'% self.term

#		print self.subentries
		subentrieskeys = self.subentries.keys()
#		print subentrieskeys
		for subentrieskey in subentrieskeys:
#			print 'subentrieskey ' + subentrieskey
#			self.subentries[subentrieskey].showcontents(indentation+2)
			for subentry in self.subentries[subentrieskey]:
#				print 'subentry ' + subentry
				subentry.showcontents(indentation+2)

class SubEntry:		# On one page, terms with the same spelling in different languages can be described
	def __init__(self,subentrylang):
		self.subentrylang=subentrylang
		self.meanings = {} # a dictionary containing the meanings grouped by part of speech
		self.posorder = [] # we don't want to shuffle the order of the parts of speech, so we keep a list to keep the order they were found
		
	def addMeaning(self,meaning):
		term = meaning.term
		self.meanings.setdefault( term.pos, [] ).append(meaning)
		if not term.pos in self.posorder:	# we only need each part of speech once
			self.posorder.append(term.pos)
	
	def getMeanings(self):
		return self.meanings

	def wikiwrap(self,wikilang):
		print "wikilang: %s"%wikilang
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
					subentry += meaning.wikiwrapTranslations(wikilang)
				subentry +='\n'	
		return subentry

	def showcontents(self,indentation):
		print ' ' * indentation + 'subentrylang = %s'% self.subentrylang

		print ' ' * indentation + 'posorder:' + repr(self.posorder)

		meaningkeys = self.meanings.keys()
		for meaningkey in meaningkeys:
			for meaning in self.meanings[meaningkey]:
				meaning.showcontents(indentation+2)

		
			
class Meaning:					# On one page, different terms in different languages can be described
	def __init__(self,definition,term):
		self.definition=definition
		self.term=term
		self.etymology=""
		self.synonyms= []
		self.translations= {}
		
	def setDefinition(self,definition):
		self.definition=definition
	
	def getDefinition(self):
		return self.definition
	
	def setEtymology(self,etymology):
		self.etymology=etymology
	
	def getEtymology(self):
		return self.etymology
	
	def setSynonyms(self,synonyms):
		self.synonyms=synonyms
	
	def getSynonyms(self):
		return self.synonyms

	def hasSynonyms(self):
		if self.synonyms == []:
			return 0
		else:
			return 1
	
	def setTranslations(self,translations):
		self.translations=translations
	
	def getTranslations(self):
		return self.translations

	def addTranslation(self,translation):
	    	self.translations.setdefault( translation.lang, [] ).append( translation )

	def hasTranslations(self):
		if self.translations == []:
			return 0
		else:
			return 1
	
	def wikiwrapSynonyms(self,wikilang):
		first = 1
		wrappedsynonyms = ''
		for synonym in self.synonyms:
			if first==0:
				wrappedsynonyms += ', '
			else:
				first = 0
			wrappedsynonyms = wrappedsynonyms + synonym.wikiwrapforlist(wikilang)
		return wrappedsynonyms + '\n'
		
	def wikiwrapTranslations(self,wikilang):
		# We want to output the translations in such a way that they end up sorted alphabetically on the language name in the language of the current Wiktionary
		alllanguages=self.translations.keys()
		alllanguages.sort(sortonname(langnames[wikilang]))
		wrappedtranslations = wiktionaryformats[wikilang]['transbefore']
		alreadydone = 0
		for language in alllanguages:
			# Indicating the language according to the wikiformats dictionary
			if not alreadydone and langnames[wikilang][language][0:1].upper() > 'M':
				wrappedtranslations = wrappedtranslations + wiktionaryformats[wikilang]['transinbetween']
				alreadydone = 1
			wrappedtranslations = wrappedtranslations + wiktionaryformats[wikilang]['translang'].replace('%%langname%%',langnames[wikilang][language]).replace('%%ISOLangcode%%',language) + ': '
			first = 1
			for translation in self.translations[language]:
				term=translation.term
				if first==0:
					wrappedtranslations += ', '
				else:					
					first = 0
				wrappedtranslations = wrappedtranslations + translation.wikiwrapastranslation(wikilang)
			wrappedtranslations += '\n'
		if not alreadydone:
			wrappedtranslations = wrappedtranslations + wiktionaryformats[wikilang]['transinbetween'] + '\n' + wiktionaryformats[wikilang]['transnoMtoZ'] + '\n'
			alreadydone = 1
		return wrappedtranslations + wiktionaryformats[wikilang]['transafter'] + '\n'
	
	def showcontents(self,indentation):
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
	def __init__(self,lang,term):
		self.lang=lang			# lang here refers to the language of the term
		self.term=term
		self.relatedwords=[]
	def __getitem__(self):
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
		if self.gender:
			return ' ' + wiktionaryformats[wikilang]['gender'].replace('%%gender%%',self.gender)
		else:
			return ''
		
	def wikiwrapasexample(self,wikilang):
		return wiktionaryformats[wikilang]['beforeexampleterm'] + self.term + wiktionaryformats[wikilang]['afterexampleterm'] + self.wikiwrapgender(wikilang)
			
	def wikiwrapforlist(self,wikilang):
		return '[[' + self.term + ']]' + self.wikiwrapgender(wikilang)
	
	def wikiwrapastranslation(self,wikilang):
		return '[[' + self.term + ']]' + self.wikiwrapgender(wikilang)

	def showcontents(self,indentation):
		print ' ' * indentation + 'lang = %s'% self.lang
		print ' ' * indentation + 'pos = %s'% self.pos
		print ' ' * indentation + 'term = %s'% self.term
		print ' ' * indentation + 'relatedwords = %s'% self.relatedwords

class Noun(Term):
	def __init__(self,lang,term,gender=''):
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
	
