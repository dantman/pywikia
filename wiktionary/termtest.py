#!/usr/bin/python
# -*- coding: utf-8  -*-

"""Unit tests for term.py"""

import term
import unittest

class KnownValues(unittest.TestCase):
    knownValues = (
                    ('en','noun','en','example','', "'''example'''", '[[example]]'),
                    ('en','noun','nl','voorbeeld','n', "'''voorbeeld''' ''n''", "[[voorbeeld]] ''n''"),
                    ('nl','noun','nl','voorbeeld','n', "'''voorbeeld''' {{n}}", "[[voorbeeld]] {{n}}"),
                    ('en','verb','en','to show','', "'''to show'''", 'to [[show]]'),
                    ('en','verb','nl','tonen','', "'''tonen'''", "[[tonen]]"),
                    ('nl','verb','nl','tonen','', "'''tonen'''", "[[tonen]]"),
                  )

    def testTermKnownValuesWikiWrapAsExample(self):
        """WikiWrap output correct for a term as an example"""
        for wikilang, pos, termlang, thisterm, termgender, asexample, forlist in self.knownValues:
            if pos=='noun':
                aterm = term.Noun(termlang, thisterm, gender=termgender)
            if pos=='verb':
                aterm = term.Verb(termlang, thisterm)
            result = aterm.wikiWrapAsExample(wikilang)
            self.assertEqual(asexample, result)

    def testTermKnownValuesWikiWrapForList(self):
        """WikiWrap output correct for a term when used in a list"""
        for wikilang, pos, termlang, thisterm, termgender, asexample, forlist in self.knownValues:
            if pos=='noun':
                aterm = term.Noun(termlang, thisterm, gender=termgender)
            if pos=='verb':
                aterm = term.Verb(termlang, thisterm)
            result = aterm.wikiWrapForList(wikilang)
            self.assertEqual(forlist, result)

    def testTermKnownValuesWikiWrapAsTranslation(self):
        """WikiWrap output correct for a term when as a translation"""
        for wikilang, pos, termlang, thisterm, termgender, asexample, forlist in self.knownValues:
            if pos=='noun':
                aterm = term.Noun(termlang, thisterm, gender=termgender)
            if pos=='verb':
                aterm = term.Verb(termlang, thisterm)
            result = aterm.wikiWrapAsTranslation(wikilang)
            self.assertEqual(forlist, result)

if __name__ == "__main__":
    unittest.main()