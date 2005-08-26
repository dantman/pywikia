#!/usr/bin/python
# -*- coding: utf-8  -*-

import structs

class Term:
    """ This is a superclass for terms.  """
    def __init__(self,lang,term,relatedwords=[]): # ,label=''):
        """ Constructor
            Generally called with two parameters:
            - The language of the term
            - The term (string)

            - relatedwords (list of Term objects) is optional
        """
        self.lang=lang
        self.term=term
        self.relatedwords=relatedwords
#        self.label=label

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

#    def setLabel(self,label):
#        self.label=label.replace('<!--','').replace('-->','')

#    def getLabel(self):
#        if self.label:
#            return '<!--' + self.label + '-->'

    def wikiWrapGender(self,wikilang):
        """ Returns a string with the gender in a format ready for Wiktionary, if it is applicable
        """
        if self.gender:
            return ' ' + structs.wiktionaryformats[wikilang]['gender'].replace('%%gender%%',self.gender)
        else:
            return ''

    def wikiWrapAsExample(self,wikilang):
        """ Returns a string with the gender in a format ready for Wiktionary, if it exists
        """
        return structs.wiktionaryformats[wikilang]['beforeexampleterm'] + self.term + structs.wiktionaryformats[wikilang]['afterexampleterm']

    def wikiWrapForList(self,wikilang):
        """ Returns a string with this term as a link followed by the gender in a format ready for Wiktionary
        """
        return '[[' + self.term + ']]'

    def wikiWrapAsTranslation(self,wikilang):
        """    Returns a string with this term as a link followed by the gender in a format ready for Wiktionary
        """
        return '[[' + self.term + ']]'

    def showContents(self,indentation):
        """ Prints the contents of this Term.
            Every subobject is indented a little further on the screen.
            The primary purpose is to help keep one's sanity while debugging.
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

    def wikiWrapAsExample(self,wikilang):
        """ Returns a string with the gender in a format ready for Wiktionary, if it exists
        """
        return Term.wikiWrapAsExample(self, wikilang) + Term.wikiWrapGender(self,wikilang)

    def wikiWrapForList(self,wikilang):
        """ Returns a string with this term as a link followed by the gender in a format ready for Wiktionary
        """
        return Term.wikiWrapForList(self, wikilang) + Term.wikiWrapGender(self, wikilang)

    def wikiWrapAsTranslation(self,wikilang):
        """    Returns a string with this term as a link followed by the gender in a format ready for Wiktionary
        """
        return Term.wikiWrapAsTranslation(self, wikilang) + Term.wikiWrapGender(self, wikilang)

class Adjective(Term):
    def __init__(self,lang,term,gender=''):
        self.pos='adjective'        # part of speech
        self.gender=gender
        Term.__init__(self,lang,term)

    def setGender(self,gender):
        self.gender=gender

    def getGender(self):
        return(self.gender)

    def wikiWrapAsExample(self,wikilang):
        """ Returns a string with the gender in a format ready for Wiktionary, if it exists
        """
        return Term.wikiWrapAsExample(self, wikilang) + Term.wikiWrapGender(self,wikilang)

    def wikiWrapForList(self,wikilang):
        """ Returns a string with this term as a link followed by the gender in a format ready for Wiktionary
        """
        return Term.wikiWrapForList(self, wikilang) + Term.wikiWrapGender(self, wikilang)

    def wikiWrapAsTranslation(self,wikilang):
        """    Returns a string with this term as a link followed by the gender in a format ready for Wiktionary
        """
        return Term.wikiWrapAsTranslation(self, wikilang) + Term.wikiWrapGender(self, wikilang)

class Verb(Term):
    def __init__(self,lang,term):
        self.pos='verb'        # part of speech
        Term.__init__(self,lang,term)

    def showContents(self,indentation):
        Term.showContents(self,indentation)

    def wikiWrapForList(self,wikilang):
        """ Returns a string with this term as a link in a format ready for Wiktionary
        """
        if wikilang=='en':
            pos=self.term.lower().find('to ')
            if pos==0:
                return 'to [[' + self.term[3:] + ']]'
        return Term.wikiWrapForList(self, wikilang)

    def wikiWrapAsTranslation(self,wikilang):
        """ Returns a string with this term as a link in a format ready for Wiktionary
        """
        return Verb.wikiWrapForList(self, wikilang)
