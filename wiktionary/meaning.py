#!/usr/bin/python
# -*- coding: utf-8  -*-

import term
import structs

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
        self.label=label

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
            wrappedtranslations = structs.wiktionaryformats[wikilang]['transbefore'] + '\n'
            alreadydone = 0
            for language in alllanguages:
                if language == wikilang: continue # don't output translation for the wikilang itself
                # split translations into two column table
                if not alreadydone and langnames[wikilang][language][0:1].upper() > 'M':
                    wrappedtranslations = wrappedtranslations + structs.wiktionaryformats[wikilang]['transinbetween'] + '\n'
                    alreadydone = 1
                # Indicating the language according to the wikiformats dictionary
                wrappedtranslations = wrappedtranslations + structs.wiktionaryformats[wikilang]['translang'].replace('%%langname%%',langnames[wikilang][language]).replace('%%ISOLangcode%%',language) + ': '
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
                wrappedtranslations = wrappedtranslations + structs.wiktionaryformats[wikilang]['transinbetween'] + '\n' + structs.wiktionaryformats[wikilang]['transnoNtoZ'] + '\n'
                alreadydone = 1
            wrappedtranslations = wrappedtranslations + structs.wiktionaryformats[wikilang]['transafter'] + '\n'
        else:
            # For the other entries we want to output the translation in the language of the Wiktionary
            wrappedtranslations = structs.wiktionaryformats[wikilang]['translang'].replace('%%langname%%',langnames[wikilang][wikilang]).replace('%%ISOLangcode%%',wikilang) + ': '
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