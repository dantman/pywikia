#!/usr/bin/python

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
		print 'testing'
		for subentry in self.subentries:
			print 'testing'
			entry='test'
#			entry=subentry.wikiwrap(wikilang) + '\n\n'

		# Here something needs to be inserted for treating interwiktionary links
		# that will have to wait for the moment
			
		return entry

class SubEntry:					# On one page, different terms in different languages can be described
	def __init__(self,subentrylang):
		self.subentrylang=subentrylang
#		self.pos=pos			# part of speech
		self.meanings = []
		
	def addMeaning(self,meaning):
		self.meanings.append(meaning)	# meanings is a list of meaning subentry objects
	
	def getMeanings(self):
		return self.meanings

	def wikiwrap(self,wikilang):
		for meaning in self.meanings:
			subentry=langheader(wikilang) + '\n'	# langheader is a dictionary that has the proper way to create a header indicating the language of a subentry for this Wiktionary
			term=meaning.term
			subentry+=posheader(wikilang,term.pos)	# posheader is a dictionary that has the proper way to create headers indicating part of speech
			subentry+='\n'	
			subentry+=term.getTerm + ' ' + term.getGender + ' ' + meaning.definition
			subentry+='\n\n'
			return subentry
			
class Meaning:					# On one page, different terms in different languages can be described
	def __init__(self,definition,term):
		self.definition=definition
		self.term=term
		self.etymology=""
		self.synonyms= []
		self.translations= []
		
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
		self.translations.append(translation)

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

class Noun(Term):
	def __init__(self,lang,term):
		self.gender=''
		Term.__init__(self,lang,term)

	def setGender(self,gender):
		self.gender=gender
		
	def getGender(self):
		return(gender)

	def wikiwrap(self,wikilang):
		return()
		

if __name__ == '__main__':
	apage = WiktionaryEntry('nl',u'iets')
	print 'Wiktionary language: %s'%apage.wikilang
	print 'Wiktionary apage: %s'%apage.term
	print
	aword = Noun('nl',u'iets')
	print 'Noun: %s'%aword.term
	aword.setGender('o')
	print 'Gender: %s'%aword.gender
        frtrans = Noun('fr',u"quelque'chose")
	frtrans.setGender('f')
	entrans = Noun('en',u'something')
	
	ameaning = Meaning(u'een ding',aword)
	ameaning.addTranslation(frtrans)
	ameaning.addTranslation(entrans)
			
	asubentry = SubEntry('nl')
	asubentry.addMeaning(ameaning)

	apage.addSubEntry(asubentry)

	print
	t= apage.wikiwrap
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
	
