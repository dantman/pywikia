#!/usr/bin/python
# -*- coding: utf-8  -*-

#from editarticle import EditArticle
#import wikipedia

isolangs = ['af','sq','ar','an','hy','ast','tay','ay','az','bam','eu','bn','my','bi','bs','br','bg','sro','ca','zh','chp','rmr','co','dgd','da','de','eml','en','eo','et','fo','fi','fr','cpf','fy','fur','gl','ka','el','gu','hat','haw','he','hi','hu','io','ga','is','gil','id','ia','it','ja','jv','ku','kok','ko','hr','lad','la','lv','ln','li','lt','lb','src','ma','ms','mg','mt','mnc','mi','mr','mh','mas','myn','mn','nah','nap','na','nds','no','ny','oc','uk','oen','grc','pau','pap','pzh','fa','pl','pt','pa','qu','rap','roh','ra','ro','ja-ro','ru','smi','sm','sa','sc','sco','sr','sn','si','sk','sl','so','sov','es','scn','su','sw','tl','tt','th','ti','tox','cs','che','tn','tum','tpn','tr','ts','tvl','ur','vi','vo','wa','cy','be','wo','xh','zu','sv']

wiktionaryformats = {
    'nl': {
        'langheader': u'{{-%%ISOLangcode%%-}}',
        'translang': u':*{{%%ISOLangcode%%}}',
        'beforeexampleterm': u"'''",
        'afterexampleterm': u"'''",
        'gender': u"{{%%gender%%}}",
        'posheader': {
                'noun': u'{{-noun-}}',
                'adjective': u'{{-adj-}}',
                'verb': u'{{-verb-}}',
                },
        'translationsheader': u"{{-trans-}}",
        'transbefore': u'{{top}}',
        'transinbetween': u'{{mid}}',
        'transafter': u'{{after}}',
        'transnoAtoM': u'<!-- Vertalingen van A tot M komen hier-->',
        'transnoNtoZ': u'<!-- Vertalingen van N tot Z komen hier-->',
        'synonymsheader': u"{{-syn-}}",
        'relatedheader': u'{{-rel-}}',
        },
    'en': {
        'langheader': u'==%%langname%%==',
        'translang': u'*%%langname%%',
        'beforeexampleterm': u"'''",
        'afterexampleterm': u"'''",
        'gender': u"''%%gender%%''",
        'posheader': {
                'noun': u'===Noun===',
                'adjective': u'===Adjective===',
                'verb': u'===Verb===',
                },
        'translationsheader': u"====Translations====",
        'transbefore': u'{{top}}',
        'transinbetween': u'{{mid}}',
        'transafter': u'{{after}}',
        'transnoAtoM': u'<!-- Translations from A tot M go here-->',
        'transnoNtoZ': u'<!-- Translations from N tot Z go here-->',
        'synonymsheader': u"====Synonyms====",
        'relatedheader': u'===Related words===',
        }
}

langnames = {
    'nl':    {
        'translingual' : u'Taalonafhankelijk',
        'nl' : u'Nederlands',
        'en' : u'Engels',
        'de' : u'Duits',
        'fr' : u'Frans',
        'it' : u'Italiaans',
        'eo' : u'Esperanto',
        'es' : u'Spaans',
        },
     'de':    {
        'nl' : u'Niederländisch',
        'en' : u'Englisch',
        'de' : u'Deutsch',
        'fr' : u'Französisch',
        'it' : u'Italienisch',
        'eo' : u'Esperanto',
        'es' : u'Spanisch',
        },
     'en':    {
        'translingual' : u'Translingual',
        'nl' : u'Dutch',
        'en' : u'English',
        'de' : u'German',
        'fr' : u'French',
        'it' : u'Italian',
        'eo' : u'Esperanto',
        'es' : u'Spanish',
        },
    'eo':    {
        'nl' : u'Nederlanda',
        'en' : u'Angla',
        'de' : u'Germana',
        'fr' : u'Franca',
        'it' : u'Italiana',
        'eo' : u'Esperanto',
        'es' : u'Hispana',
        },
    'it':    {
        'nl' : u'olandese',
        'en' : u'inglese',
        'de' : u'tedesco',
        'fr' : u'francese',
        'it' : u'italiano',
        'eo' : u'esperanto',
        'es' : u'spagnuolo',
        },
    'fr':    {
        'nl' : u'néerlandais',
        'en' : u'anglais',
        'de' : u'allemand',
        'fr' : u'français',
        'it' : u'italien',
        'eo' : u'espéranto',
        'es' : u'espagnol',
        },
    'es':    {
        'nl' : u'olandés',
        'en' : u'inglés',
        'de' : u'alemán',
        'fr' : u'francés',
        'it' : u'italiano',
        'eo' : u'esperanto',
        'es' : u'español',
        },
}

def invertlangnames():
    '''
    On the English Wiktionary it is customary to use full language names. For
    parsing we need a dictionary to efficiently convert these back to iso
    abbreviations.
    '''
    invertedlangnames = {}
    for ISOKey in langnames.keys():
        for ISOKey2 in langnames[ISOKey].keys():
            lowercaselangname=langnames[ISOKey][ISOKey2].lower()
            #Put in the names of the languages so we can easily do a reverse lookup lang name -> iso abbreviation
            invertedlangnames.setdefault(lowercaselangname, ISOKey2)
            # Now all the correct forms are in, but we also want to be able to find them when there are typos in them
            for pos in range(1,len(lowercaselangname)):
                # So first we create all the possibilities with one letter gone
                invertedlangnames.setdefault(lowercaselangname[:pos]+lowercaselangname[pos+1:], ISOKey2)
                # Then we switch two consecutive letters
                invertedlangnames.setdefault(lowercaselangname[:pos-1]+lowercaselangname[pos]+lowercaselangname[pos-1]+lowercaselangname[pos+1:], ISOKey2)
                # There are of course other typos possible, but this caters for a lot of possibilities already
                # TODO One other treatment that would make sense is to filter out the accents.
    return invertedlangnames

# A big thanks to Rob Hooft for the following class:
# It may not seem like much, but it magically allows the translations to be sorted on
# the names of the languages. I would never have thought of doing it like this myself.
class sortonname:
    '''
    This class sorts translations alphabetically on the name of the language,
    instead of on the iso abbreviation that is used internally.
    '''
    def __init__(self, lang):
        self.lang = lang

    def __call__(self, one, two):
        return cmp(self.lang[one], self.lang[two])

class WiktionaryPage:
    """ This class contains all that can appear on one Wiktionary page """

    def __init__(self,wikilang,term):    # wikilang here refers to the language of the Wiktionary this page belongs to
        """ Constructor
            Called with two parameters:
            - the language of the Wiktionary the page belongs to
            - the term that is described on this page
        """
        self.wikilang=wikilang
        self.term=term
        self.entries = {}        # entries is a dictionary of entry objects indexed by entrylang
        self.sortedentries = []
        self.interwikilinks = []

    def setWikilang(self,wikilang):
        """ This method allows to switch the language on the fly """
        self.wikilang=wikilang

    def addEntry(self,entry):
        """ Add an entry object to this page object """
#        self.entries.setdefault(entry.entrylang, []).append(entry)
        self.entries[entry.entrylang]=entry

    def listEntries(self):
        """ Returns a dictionary of entry objects for this entry """
        return self.entries

    def sortEntries(self):
        """ Sorts the sortedentries list containing the keys of the entry
            objects dictionary for this entry
        """

        if not self.entries == {}:
            self.sortedentries = self.entries.keys()
            self.sortedentries.sort(sortonname(langnames[self.wikilang]))

            i = 0
            while i< len(self.sortedentries):
                x = self.sortedentries[i]
                if x == self.wikilang:    # search the entry of the same language of the Wiktionary
                    samelangentry = self.sortedentries[i]
                    del self.sortedentries[i]
                    self.sortedentries.reverse()
                    self.sortedentries.append(samelangentry)
                    self.sortedentries.reverse()    # and put it before all the others
                    break # FIXME: If there is a cleaner way of accomplishing this
                i+=1

            # The same needs to be done to get the translingual on top

            i = len(self.sortedentries)-1

            while i>0 :
                x = self.sortedentries[i]
                if x == u'translingual':    # search the Translingual entry
                    translingualentry = self.sortedentries[i]
                    del self.sortedentries[i]
                    self.sortedentries.reverse()
                    self.sortedentries.append(translingualentry)
                    self.sortedentries.reverse()    # and put it before all the others
                    break # FIXME: If there is a cleaner way of accomplishing this
                i-=1

    def wikiWrap(self):
        """ Returns a string that is ready to be submitted to Wiktionary for
            this page
        """
        page = ''
        self.sortEntries()
        # print "sorted: %s",self.sortedentries
        first = True
        print "SortedEntries:", self.sortedentries, len(self.sortedentries)
        for index in self.sortedentries:
            print "Entries:", self.entries[index]
            entry = self.entries[index]
            print entry
            if first == False:
                page = page + '\n----\n'
            else:
                first = False
            page = page + entry.wikiWrap(self.wikilang)
        # Add interwiktionary links at bottom of page
        for link in self.interwikilinks:
            page = page + '[' + link + ':' + self.term + ']\n'

        return page

    def showContents(self):
        """ Prints the contents of all the subobjects contained in this page.
            Every subobject is indented a little further on the screen.
            The primary purpose is to help keep one's sanity while debugging.
        """
        indentation = 0
        print ' ' * indentation + 'wikilang = %s' % self.wikilang

        print ' ' * indentation + 'term = %s' % self.term

        entrieskeys = self.entries.keys()
        for entrieskey in entrieskeys:
            for entry in self.entries[entrieskey]:
                entry.showContents(indentation+2)

class Entry:
    """ This class contains the entries that belong together on one page.
        On Wiktionaries that are still on first character capitalization, this means both [[Kind]] and [[kind]].
        Terms in different languages can be described. Usually there is one entry for each language.
    """

    def __init__(self,entrylang,meaning=""):
        """ Constructor
            Called with one parameter:
            - the language of this entry
	    and can optionally be initialized with a first meaning
        """
        self.entrylang=entrylang
        self.meanings = {} # a dictionary containing the meanings for this term grouped by part of speech
	if meaning:
            addMeaning(meaning)
        self.posorder = [] # we don't want to shuffle the order of the parts of speech, so we keep a list to keep the order in which they were encountered

    def addMeaning(self,meaning):
        """ Lets you add another meaning to this entry """
        term = meaning.term # fetch the term, in order to be able to determine its part of speech in the next step

        self.meanings.setdefault( term.pos, [] ).append(meaning)
        if not term.pos in self.posorder:    # we only need each part of speech once in our list where we keep track of the order
            self.posorder.append(term.pos)

    def getMeanings(self):
        """ Returns a dictionary containing all the meaning objects for this entry
        """
        return self.meanings

    def wikiWrap(self,wikilang):
        """ Returns a string for this entry in a format ready for Wiktionary
        """
        entry = wiktionaryformats[wikilang]['langheader'].replace('%%langname%%',langnames[wikilang][self.entrylang]).replace('%%ISOLangcode%%',self.entrylang) + '\n'

        for pos in self.posorder:
            meanings = self.meanings[pos]

            entry += wiktionaryformats[wikilang]['posheader'][pos]
            entry +='\n'
            if wikilang=='en':
                entry = entry + meanings[0].term.wikiWrapAsExample(wikilang) + '\n\n'
                for meaning in meanings:
                    entry = entry + '#' + meaning.getLabel() + ' ' + meaning.definition + '\n'
                    entry = entry + meaning.wikiWrapExamples()
                entry +='\n'

            if wikilang=='nl':
                for meaning in meanings:
                    term=meaning.term
                    entry = entry + meaning.getLabel() + term.wikiWrapAsExample(wikilang) + '; ' + meaning.definition + '\n'
                    entry = entry + meaning.wikiWrapExamples()
                entry +='\n'

            if meaning.hasSynonyms():
                entry = entry + wiktionaryformats[wikilang]['synonymsheader'] + '\n'
                for meaning in meanings:
                    entry = entry + '*' + meaning.getLabel() + "'''" + meaning.getConciseDef() + "''': " + meaning.wikiWrapSynonyms(wikilang)
                entry +='\n'

            if meaning.hasTranslations():
                entry = entry + wiktionaryformats[wikilang]['translationsheader'] + '\n'
                for meaning in meanings:
                    entry = entry + meaning.getLabel() + "'''" + meaning.getConciseDef() + "'''" + '\n' + meaning.wikiWrapTranslations(wikilang,self.entrylang) + '\n\n'
                entry +='\n'
        return entry

    def showContents(self,indentation):
        """ Prints the contents of all the subobjects contained in this entry.
            Every subobject is indented a little further on the screen.
            The primary purpose is to help keep your sanity while debugging.
        """
        print ' ' * indentation + 'entrylang = %s'% self.entrylang

        print ' ' * indentation + 'posorder:' + repr(self.posorder)

        meaningkeys = self.meanings.keys()
        for meaningkey in meaningkeys:
            for meaning in self.meanings[meaningkey]:
                meaning.showContents(indentation+2)

class Meaning:
    """ This class contains one meaning for a word or an expression.
    """
    def __init__(self,term,definition='',etymology='',synonyms=[],translations={},label='',concisedef='',examples=[]):
        """ Constructor
            Generally called with one parameter:
            - The Term object we are describing

            - definition (string) for this term is optional
            - etymology (string) is optional
            - synonyms (list of Term objects) is optional
            - translations (dictionary of Term objects, ISO639 is the key) is optional
        """
        self.term=term
        self.definition=definition
	self.concisedef=concisedef
        self.etymology=etymology
        self.synonyms=synonyms
        self.examples=examples

        if translations: # Why this has to be done explicitly is beyond me, but it doesn't work correctly otherwise
            self.translations=translations
        else:
            self.translations={}
        self.label=label

    def setDefinition(self,definition):
        """ Provide a definition  """
        self.definition=definition

    def getDefinition(self):
        """ Returns the definition  """
        return self.definition

    def setEtymology(self,etymology):
        """ Provide the etymology  """
        self.etymology=etymology

    def getEtymology(self):
        """ Returns the etymology  """
        return self.etymology

    def setSynonyms(self,synonyms):
        """ Provide the synonyms  """
        self.synonyms=synonyms

    def getSynonyms(self):
        """ Returns the list of synonym Term objects  """
        return self.synonyms

    def hasSynonyms(self):
        """ Returns True if there are synonyms
            Returns False if there are no synonyms
        """
        if self.synonyms == []:
            return False
        else:
            return True

    def setTranslations(self,translations):
        """ Provide the translations  """
        self.translations=translations

    def getTranslations(self):
        """ Returns the translations dictionary containing translation
            Term objects for this meaning
        """
        return self.translations

    def addTranslation(self,translation):
        """ Add a translation Term object to the dictionary for this meaning
            The lang property of the Term object will be used as the key of the dictionary
        """
        self.translations.setdefault( translation.lang, [] ).append( translation )

    def addTranslations(self,*translations):
        """ This method calls addTranslation as often as necessary to add
            all the translations it receives
        """
        for translation in translations:
            self.addTranslation(translation)

    def hasTranslations(self):
        """ Returns True if there are translations
            Returns False if there are no translations
        """
        if self.translations == {}:
            return 0
        else:
            return 1

    def setLabel(self,label):
        self.label=label.replace('<!--','').replace('-->','')

    def getLabel(self):
        if self.label:
            return u'<!--' + self.label + u'-->'

    def getConciseDef(self):
        if self.concisedef:
            return self.concisedef

    def getExamples(self):
        """ Returns the list of example strings for this meaning
        """
        return self.examples

    def addExample(self,example):
        """ Add a translation Term object to the dictionary for this meaning
            The lang property of the Term object will be used as the key of the dictionary
        """
        self.examples.append(example)

    def addExamples(self,*examples):
        """ This method calls addExample as often as necessary to add
            all the examples it receives
        """
        for example in examples:
            self.addExample(example)

    def hasExamples(self):
        """ Returns True if there are examples
            Returns False if there are no examples
        """
        if self.examples == []:
            return 0
        else:
            return 1

    def wikiWrapSynonyms(self,wikilang):
        """ Returns a string with all the synonyms in a format ready for Wiktionary
        """
        first = 1
        wrappedsynonyms = ''
        for synonym in self.synonyms:
            if first==0:
                wrappedsynonyms += ', '
            else:
                first = 0
            wrappedsynonyms = wrappedsynonyms + synonym.wikiWrapForList(wikilang)
        return wrappedsynonyms + '\n'

    def wikiWrapTranslations(self,wikilang,entrylang):
        """ Returns a string with all the translations in a format
            ready for Wiktionary
            The behavior changes with the circumstances.
            For an entry in the same language as the Wiktionary the full list of translations is contained in the output, excluding the local
	    language itself
            - This list of translations has to end up in a table with two columns
            - The first column of this table contains languages with names from A to M, the second contains N to Z
            - If a column in this list remains empty a html comment is put in that column
            For an entry in a foreign language only the translation towards the local language is output.
        """
        if wikilang == entrylang:
            # When treating an entry of the same lang as the Wiktionary, we want to output the translations in such a way that they end up sorted alphabetically on the language name in the language of the current Wiktionary
            alllanguages=self.translations.keys()
            alllanguages.sort(sortonname(langnames[wikilang]))
            wrappedtranslations = wiktionaryformats[wikilang]['transbefore'] + '\n'
            alreadydone = 0
            for language in alllanguages:
                if language == wikilang: continue # don't output translation for the wikilang itself
                # split translations into two column table
                if not alreadydone and langnames[wikilang][language][0:1].upper() > 'M':
                    wrappedtranslations = wrappedtranslations + wiktionaryformats[wikilang]['transinbetween'] + '\n'
                    alreadydone = 1
                # Indicating the language according to the wikiformats dictionary
                wrappedtranslations = wrappedtranslations + wiktionaryformats[wikilang]['translang'].replace('%%langname%%',langnames[wikilang][language]).replace('%%ISOLangcode%%',language) + ': '
                first = 1
                for translation in self.translations[language]:
                    term=translation.term
                    if first==0:
                        wrappedtranslations += ', '
                    else:
                        first = 0
                    wrappedtranslations = wrappedtranslations + translation.wikiWrapAsTranslation(wikilang)
                wrappedtranslations += '\n'
            if not alreadydone:
                wrappedtranslations = wrappedtranslations + wiktionaryformats[wikilang]['transinbetween'] + '\n' + wiktionaryformats[wikilang]['transnoNtoZ'] + '\n'
                alreadydone = 1
            wrappedtranslations = wrappedtranslations + wiktionaryformats[wikilang]['transafter'] + '\n'
        else:
            # For the other entries we want to output the translation in the language of the Wiktionary
            wrappedtranslations = wiktionaryformats[wikilang]['translang'].replace('%%langname%%',langnames[wikilang][wikilang]).replace('%%ISOLangcode%%',wikilang) + ': '
            first = True
            for translation in self.translations[wikilang]:
                term=translation.term
                if first==False:
                    wrappedtranslations += ', '
                else:
                    first = False
                wrappedtranslations = wrappedtranslations + translation.wikiWrapAsTranslation(wikilang)
        return wrappedtranslations

    def showContents(self,indentation):
        """ Prints the contents of this meaning.
            Every subobject is indented a little further on the screen.
            The primary purpose is to help keep one's sanity while debugging.
        """
        print ' ' * indentation + 'term: '
        self.term.showContents(indentation+2)
        print ' ' * indentation + 'definition = %s'% self.definition
        print ' ' * indentation + 'etymology = %s'% self.etymology

        print ' ' * indentation + 'Synonyms:'
        for synonym in self.synonyms:
            synonym.showContents(indentation+2)

        print ' ' * indentation + 'Translations:'
        translationkeys = self.translations.keys()
        for translationkey in translationkeys:
            for translation in self.translations[translationkey]:
                translation.showContents(indentation+2)

    def wikiWrapExamples(self):
        """ Returns a string with all the examples in a format ready for Wiktionary
        """
        wrappedexamples = ''
        for example in self.examples:
            wrappedexamples = wrappedexamples + "#:'''" + example + "'''\n"
        return wrappedexamples


class Term:
    """ This is a superclass for terms.  """
    def __init__(self,lang,term,relatedwords=[],label=''):
        """ Constructor
            Generally called with two parameters:
            - The language of the term
            - The term (string)

            - relatedwords (list of Term objects) is optional
        """
        self.lang=lang
        self.term=term
        self.relatedwords=relatedwords
        self.label=label

    def __getitem__(self):
        """ Documenting as an afterthought is a bad idea
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

    def setLabel(self,label):
        self.label=label.replace('<!--','').replace('-->','')

    def getLabel(self):
        if self.label:
            return '<!--' + self.label + '-->'

    def wikiWrapGender(self,wikilang):
        """ Returns a string with the gender in a format ready for Wiktionary, if it is applicable
        """
        if self.gender:
            return ' ' + wiktionaryformats[wikilang]['gender'].replace('%%gender%%',self.gender)
        else:
            return ''

    def wikiWrapAsExample(self,wikilang):
        """ Returns a string with the gender in a format ready for Wiktionary, if it exists
        """
        return wiktionaryformats[wikilang]['beforeexampleterm'] + self.term + wiktionaryformats[wikilang]['afterexampleterm'] + self.wikiWrapGender(wikilang)

    def wikiWrapForList(self,wikilang):
        """ Returns a string with this term as a link followed by the gender in a format ready for Wiktionary
        """
        return '[[' + self.term + ']]' + self.wikiWrapGender(wikilang)

    def wikiWrapAsTranslation(self,wikilang):
        """    Returns a string with this term as a link followed by the gender in a format ready for Wiktionary
        """
        return '[[' + self.term + ']]' + self.wikiWrapGender(wikilang)

    def showContents(self,indentation):
        """ Prints the contents of this Term.
            Every subobject is indented a little further on the screen.
            The primary purpose is to help keep your sanity while debugging.
        """
        print ' ' * indentation + 'lang = %s'% self.lang
        print ' ' * indentation + 'pos = %s'% self.pos
        print ' ' * indentation + 'term = %s'% self.term
        print ' ' * indentation + 'relatedwords = %s'% self.relatedwords

class Noun(Term):
    """ This class inherits from Term.
        It adds properties and methods specific to nouns
    """
    def __init__(self,lang,term,gender=''):
        """ Constructor
            Generally called with two parameters:
            - The language of the term
            - The term (string)

            - gender is optional
        """
        self.pos='noun'        # part of speech
        self.gender=gender
        Term.__init__(self,lang,term)

    def setGender(self,gender):
        self.gender=gender

    def getGender(self):
        return(self.gender)

    def showContents(self,indentation):
        Term.showContents(self,indentation)
        print ' ' * indentation + 'gender = %s'% self.gender

class Adjective(Term):
    def __init__(self,lang,term,gender=''):
        self.pos='adjective'        # part of speech
        self.gender=gender
        Term.__init__(self,lang,term)

    def setGender(self,gender):
        self.gender=gender

    def getGender(self):
        return(self.gender)

    def showContents(self,indentation):
        Term.showContents(self,indentation)
        print ' ' * indentation + 'gender = %s'% self.gender

class Header:
    def __init__(self,line):
        """ Constructor
            Generally called with one parameter:
            - The line read from a Wiktonary page
              after determining it's probably a header
        """
        self.type=''        # The type of header, i.e. lang, pos, other
        self.contents=''    # If lang, which lang? If pos, which pos?
        self.level=0
        if line.count('=')>1:
            self.level = line.count('=') // 2 # integer floor division without fractional part
            self.header = line.replace('=','').strip()

        elif not line.find('{{')==-1:
            self.header = line.replace('{{-','').replace('-}}','').strip()
        else:
            self.header = ''

        print self.level
        print '|',self.header,'|'

def parseWikiPage(ofn):
    content = open(ofn).readlines()
    for line in content:
        if len(line) <2: continue
#        print 'line0:',line[0], 'line-2:',line[-2],'|','stripped line-2',line.rstrip()[-2]
        if line.strip()[0]=='='and line.rstrip()[-2]=='=' or not line.find('{{-')==-1 and not line.find('-}}')==-1:
            context=Header(line)

def temp():
    """
    apage = WiktionaryPage('nl',u'iemand')
#    print 'Wiktionary language: %s'%apage.wikilang
#    print 'Wiktionary apage: %s'%apage.term
#    print
    aword = Noun('nl',u'iemand')
#    print 'Noun: %s'%aword.term
    aword.setGender('m')
#    print 'Gender: %s'%aword.gender
    frtrans = Noun('fr',u"quelqu'un")
    frtrans.setGender('m')
    entrans1 = Noun('en',u'somebody')
    entrans2 = Noun('en',u'someone')
#    print 'frtrans: %s'%frtrans

    ameaning = Meaning(aword, definition=u'een persoon')
    ameaning.addTranslation(frtrans)
#    print ameaning.translations
    ameaning.addTranslation(entrans1)
#    print ameaning.translations
    ameaning.addTranslation(entrans2)
#    print ameaning.translations
    ameaning.addTranslation(aword) # This is for testing whether the order of the translations is correct

    anentry = Entry('en')
    anentry.addMeaning(ameaning)

    apage.addEntry(anentry)

    print
    t=apage.wikiWrap()
    print t
    apage.wikilang = 'en'
    print
    t=apage.wikiWrap()
    print t
    """
    apage = WiktionaryPage('nl',u'Italiaanse')
    aword = Noun('nl',u'Italiaanse','f')
    FemalePersonFromItalymeaning = Meaning(aword,definition = u'vrouwelijke persoon die uit [[Italië]] komt', label=u'NFemalePersonFromItaly', concisedef=u'vrouwelijke persoon uit Italië',examples=['Die vrouw is een Italiaanse'])

#    {{-rel-}}
#    * [[Italiaan]]
    detrans = Noun('de',u'Italienerin','f')
    entrans = Noun('en',u'Italian')
    frtrans = Noun('fr',u'Italienne','f')
    ittrans = Noun('it',u'italiana','f')

    FemalePersonFromItalymeaning.addTranslations(detrans, entrans, frtrans, ittrans)

    Italiaanseentry = Entry('nl')
    Italiaanseentry.addMeaning(FemalePersonFromItalymeaning)

    apage.addEntry(Italiaanseentry)


    aword = Adjective('nl',u'Italiaanse')
    asynonym = Adjective('nl',u'Italiaans')
    FromItalymeaning = Meaning(aword, definition = u'uit Italië afkomstig', synonyms=[asynonym], label=u'AdjFromItaly', concisedef=u'uit/van Italië',examples=['De Italiaanse mode'])
    RelatedToItalianLanguagemeaning = Meaning(aword, definition = u'gerelateerd aan de Italiaanse taal', synonyms=[asynonym], label=u'AdjRelatedToItalianLanguage', concisedef=u'm.b.t. de Italiaanse taal',examples=['De Italiaanse werkwoorden','De Italiaanse vervoeging'])

    detrans = Adjective('de',u'italienisches','n')
    detrans2 = Adjective('de',u'italienischer','m')
    detrans3 = Adjective('de',u'italienische','f')
    entrans = Adjective('en',u'Italian')
    frtrans = Adjective('fr',u'italien','m')
    frtrans2 = Adjective('fr',u'italienne','f')
    ittrans = Adjective('it',u'italiano','m')
    ittrans2 = Adjective('it',u'italiana','f')

    FromItalymeaning.addTranslations(detrans, detrans2, detrans3, entrans)
    FromItalymeaning.addTranslations(frtrans2, frtrans, ittrans, ittrans2)

    RelatedToItalianLanguagemeaning.addTranslations(detrans, detrans2, detrans3, entrans)
    RelatedToItalianLanguagemeaning.addTranslations(frtrans2, frtrans, ittrans, ittrans2)

    Italiaanseentry.addMeaning(FromItalymeaning)
    Italiaanseentry.addMeaning(RelatedToItalianLanguagemeaning)

    apage.addEntry(Italiaanseentry)

    print
    u=apage.wikiWrap()
    print u

    apage.setWikilang('en')
    print apage.wikiWrap()


#    {{-nl-}}
#    {{-noun-}}
#    '''Italiaanse''' {{f}}; vrouwelijke persoon die uit [[Italië]] komt

#    {{-rel-}}
#    * [[Italiaan]]

#    {{-trans-}}
#    *{{de}}: [[Italienierin]] {{f}}
#    *{{en}}: [[Italian]]
#    *{{fr}}: [[Italienne]] {{f}}
#    *{{it}}: [[italiana]] {{f}}

#    {{-adj-}}
#    #'''Italiaanse'''; uit Italië afkomstig
#    #'''Italiaanse'''; gerelateerd aan de Italiaanse taal

#    {{-syn-}}
#    * [[Italiaans]]

def run():
    ea = EditArticle(['-p', 'Andorra', '-e', 'bluefish'])
    ea.initialise_data()
    try:
        ofn, old = ea.fetchpage()

        parseWikiPage(ofn)
        new = ea.edit(ofn)
    except wikipedia.LockedPage:
        sys.exit("You do not have permission to edit %s" % self.pagelink.sectionFreeTitle())
    if old != new:
        new = ea.repair(new)
        ea.showdiff(old, new)
        comment = ea.getcomment()
        try:
            ea.pagelink.put(new, comment=comment, minorEdit=False, watchArticle=ea.options.watch, anon=ea.options.anonymous)
        except wikipedia.EditConflict:
            ea.handle_edit_conflict()
    else:
        wikipedia.output(u"Nothing changed")

if __name__ == '__main__':

    print invertlangnames()

#    temp()
#    run()

#    ofn = '/home/jo/tmp/unitest.txt'
#    parseWikiPage(ofn)
