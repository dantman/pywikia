#!/usr/bin/python

wiktionaryformats = {
			'nl': {
				'langheader':	u'{{-%%ISOLangcode%%-}}',
				'beforeexampleterm': u"'''",
				'afterexampleterm': u"'''",
				'gender': u"{{%%gender%%}}",
				'posheader': {
						'noun':	u'{{-noun-}}'
						}
				},
			'en': {
				'langheader':	u'==%%langname%%==',
				'beforeexampleterm': u"'''",
				'afterexampleterm': u"'''",
				'gender': u"''%%gender%%''",
				'posheader': {
						'noun': u'=== Noun ==='
						}
				}
		            }
#print wiktionaryformats['nl']['langheader']
#print wiktionaryformats['en']['langheader']
#print wiktionaryformats['nl']['posheader']['noun']
#print wiktionaryformats['en']['posheader']['noun']
			   
langnames =	{'nl':	{
			'nl' : 'Nederlands',
			'en' : 'Engels',
			'de' : 'Duits',
			'fr' : 'Frans',
			},
		 'de':	{
			'nl' : 'Niederländisch',
			'en' : 'Englisch',
			'de' : 'Deutsch',
			'fr' : 'Französisch',
			},
		 'en':	{
			'nl' : 'Dutch',
			'en' : 'English',
			'de' : 'German',
			'fr' : 'French',
			}
		}
print langnames
# A big thanks to Rob for the following:
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
			entry= entry + subentry.wikiwrap(self.wikilang) + '\n\n'

		# Here something needs to be inserted for treating interwiktionary links
		# that will have to wait for the moment
			
		return entry

class SubEntry:					# On one page, different terms in different languages can be described
	def __init__(self,subentrylang):
		self.subentrylang=subentrylang
		self.meanings = []
		
	def addMeaning(self,meaning):
		self.meanings.append(meaning)	# meanings is a list of meaning subentry objects
	
	def getMeanings(self):
		return self.meanings

	def wikiwrap(self,wikilang):
		for meaning in self.meanings:
			subentry=wiktionaryformats[wikilang]['langheader'] + '\n'
			term=meaning.term

			subentry += wiktionaryformats[wikilang]['posheader'][term.pos]
			subentry +='\n'	
			subentry = subentry + term.wikiwrapasexample(wikilang) + '; ' + meaning.definition
			subentry +='\n\n'
			first = 1
			for synonym in meaning.synonyms:
				if not first:
					subentry += ', '
					first = 0
				subentry = subentry + synonym.term.wikiwrapforlist(wikilang)
			first = 1
			subentry +='\n'	

			alllanguages=meaning.translations.keys()

			alllanguages.sort(sortonname(langnames[wikilang]))
			for language in alllanguages:
				print meaning.translations[language]
#			for translation in meaning.translations:
#				term=translation.term
#				print translation
#				if not first:
#					subentry += ', '
#					first = 0
#				subentry = subentry + translation.wikiwrapastranslation(wikilang)
#			return subentry
			
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
	
	def setTranslations(self,translations):
		self.translations=translations
	
	def getTranslations(self):
		return self.translations

	def addTranslation(self,translation):
	    	self.translations.setdefault( translation.lang, [] ).append( translation )

		
class Term:
	def __init__(self,lang,term):
		self.lang=lang			# lang here refers to the language of the term
		self.term=term
		self.relatedwords=[]
		
	def setTerm(self,term):
		self.term=term
	
	def getTerm(self):
		return self.term

	def setLang(self,lang):
		self.lang=lang

	def getLang(self):
		return self.lang

	def wikiwrapasexample(self,wikilang):
		term=wiktionaryformats[wikilang]['beforeexampleterm'] + self.term + wiktionaryformats[wikilang]['afterexampleterm']
		if self.gender:
			term = term + ' ' + wiktionaryformats[wikilang]['gender'].replace('%%gender%%',self.gender)
			
		return term
	
	def wikiwrapforlist(self,wikilang):
		term='[[' + self.term + ']]'
		if self.gender:
			term = term + ' ' + wiktionaryformats[wikilang]['gender'].replace('%%gender%%',self.gender)
		return term
	
	def wikiwrapastranslation(self,wikilang):
		term='[[' + self.term + ']]'
		if self.gender:
			term = term + ' ' + wiktionaryformats[wikilang]['gender'].replace('%%gender%%',self.gender)
		return term

class Noun(Term):
	def __init__(self,lang,term):
		self.pos='noun'		# part of speech
		self.gender=''
		Term.__init__(self,lang,term)

	def setGender(self,gender):
		self.gender=gender
		
	def getGender(self):
		return(self.gender)

	def wikiwrap(self,wikilang):
		return()
		

if __name__ == '__main__':
	apage = WiktionaryEntry('nl',u'iemand')
	print 'Wiktionary language: %s'%apage.wikilang
	print 'Wiktionary apage: %s'%apage.term
	print
	aword = Noun('nl',u'iemand')
	print 'Noun: %s'%aword.term
	aword.setGender('m')
	print 'Gender: %s'%aword.gender
        frtrans = Noun('fr',u"quelqu'un")
	frtrans.setGender('m')
	entrans1 = Noun('en',u'somebody')
	entrans2 = Noun('en',u'someone')

	print 'frtrans: %s'%frtrans

	ameaning = Meaning(u'een persoon',aword)
	ameaning.addTranslation(frtrans)
	print ameaning.translations
	ameaning.addTranslation(entrans1)
	print ameaning.translations
	ameaning.addTranslation(entrans2)
	print ameaning.translations
			
	asubentry = SubEntry('nl')
	asubentry.addMeaning(ameaning)

	apage.addSubEntry(asubentry)

	print
	t=apage.wikiwrap()
	print t
	
#	{{-nl-}}
#	{{-noun-}}
#	'''Italiaanse''' {{f}}; vrouwelijke persoon die uit [[Itali]] komt

#	{{-rel-}}
#	* [[Italiaan]]

#	{{-trans-}}
#	*{{de}}: [[Italienierin]] {{f}}
#	*{{en}}: [[Italian]]
#	*{{fr}}: [[Italienne]] {{f}}
#	*{{it}}: [[italiana]] {{f}}

#	{{-adj-}}
#	#'''Italiaanse'''; uit Itali afkomstig
#	#'''Italiaanse'''; gerelateerd aan de Italiaanse taal

#	{{-syn-}}
#	* [[Italiaans]]
	
