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
						},
				'translationsheader': u"{{-trans-}}",
				'transbefore': u'{|border=0 width=100%\n|-\n|bgcolor="{{bgclr}}" valign=top width=48%|\n{|\n',
				'transinbetween': u'|}\n| width=1% |\n|bgcolor="{{bgclr}}" valign=top width=48%|\n{|\n',
				'transafter': u'|}\n|}',
				'transnoMtoZ': u'<-- Vertalingen van M tot Z komen hier>',
				'synonymsheader': u"{{-syn-}}",
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
						},
				'translationsheader': u"==== Translations ====",
				'transbefore': u'{|border=0 width=100%\n|-\n|bgcolor="#FFFFE0" valign=top width=48%|\n{|\n',
				'transinbetween': u'|}\n| width=1% |\n|bgcolor="#FFFFE0" valign=top width=48%|\n{|\n',
				'transafter': u'|}\n|}',
				'transnoMtoZ': u'<-- Translations from M tot Z go here>',
				'synonymsheader': u"==== Synonyms ====",
				}
		            }
#print wiktionaryformats['nl']['langheader']
#print wiktionaryformats['en']['langheader']
#print wiktionaryformats['nl']['posheader']['noun']
#print wiktionaryformats['en']['posheader']['noun']
			   
langnames =	{'nl':	{
			'nl' : u'Nederlands',
			'en' : u'Engels',
			'de' : u'Duits',
			'fr' : u'Frans',
			'it' : u'Italiaans',
			},
		 'de':	{
			'nl' : u'Niederländisch',
			'en' : u'Englisch',
			'de' : u'Deutsch',
			'fr' : u'Französisch',
			'it' : u'Italienisch',
			},
		 'en':	{
			'nl' : u'Dutch',
			'en' : u'English',
			'de' : u'German',
			'fr' : u'French',
			'it' : u'Italian',
			}
		}
#print langnames
# A big thanks to Rob Hooft for the following:
class sortonname:
	def __init__(self, lang):
#		print "lang in constructor: %s"%lang
		self.lang = lang

	def __call__(self, one, two):
#		print "one in call: %s"%one
#		print "two in call: %s"%two
#		print "self.lang: %s"%self.lang
#		print "self.lang[one]: %s"%self.lang[one]
#		print "self.lang[two]: %s"%self.lang[two]
		return cmp(self.lang[one], self.lang[two])

			   
class WiktionaryEntry:				# This refers to an entire page
	def __init__(self,wikilang,term):	# wikilang here refers to the language of the Wiktionary
		self.wikilang=wikilang
		self.term=term
		self.subentries = []

	def addSubEntry(self,subentry):
		self.subentries.append(subentry)	# subentries is a list of subentry objects
	
	def listSubentries(self):
		return self.subentries

	def wikiwrap(self):
		entry = ''
		for subentry in self.subentries:
			entry= entry + subentry.wikiwrap(self.wikilang) + '\n'

		# TODO Here something needs to be inserted for treating interwiktionary links
			
		return entry
	
class SubEntry:					# On one page, terms with the same spelling in different languages can be described
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
#		print self.subentrylang, self.meanings[0].term.term
		subentry = wiktionaryformats[wikilang]['langheader'].replace('%%langname%%',langnames[wikilang][self.subentrylang]).replace('%%ISOLangcode%%',self.subentrylang) + '\n'

		# We need to group all the same parts of speeches together

		# Then we need to print the POS-header
		# and list all the Definitions

		# followed by the synonyms and translations sections
		
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

class Noun(Term):
	def __init__(self,lang,term,gender=''):
		self.pos='noun'		# part of speech
		self.gender=gender
		Term.__init__(self,lang,term)

	def setGender(self,gender):
		self.gender=gender
		
	def getGender(self):
		return(self.gender)


class Adjective(Term):
	def __init__(self,lang,term,gender=''):
		self.pos='adjective'		# part of speech
		self.gender=gender
		Term.__init__(self,lang,term)

	def setGender(self,gender):
		self.gender=gender
		
	def getGender(self):
		return(self.gender)


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
	
