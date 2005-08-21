"""Unit test for Wiktionary.py"""

import wiktionary
import unittest

class KnownValues(unittest.TestCase):
    knownValues = (
                    ('==English==', 'en', 2, 'lang'),
                    ('==={{en}}===', 'en', 3, 'lang'),
                    ('{{-en-}}', 'en', None, 'lang'),
                    ('===Noun===', 'noun', 3, 'pos'),
                    ('==={{noun}}===', 'noun', 3, 'pos'),
                    ('{{-noun-}}', 'noun', None, 'pos'),
                    ('===Verb===', 'verb', 3, 'pos'),
                    ('==={{verb}}===', 'verb', 3, 'pos'),
                    ('{{-verb-}}', 'verb', None, 'pos'),
                    ('====Translations====', 'trans', 4, 'other'),
                    ('===={{trans}}====', 'trans', 4, 'other'),
                    ('{{-trans-}}', 'trans', None, 'other'),
                  )

    def testHeaderInitKnownValuesContents(self):
        """Header __init__ should give known result with known input for contents"""
        for wikiline, contents, level, type in self.knownValues:
            result = wiktionary.Header(wikiline).contents
            self.assertEqual(contents, result)

    def testHeaderInitKnownValuesLevel(self):
        """Header __init__ should give known result with known input for level"""
        for wikiline, contents, level, type in self.knownValues:
            result = wiktionary.Header(wikiline).level
            self.assertEqual(level, result)

    def testHeaderInitKnownValuesType(self):
        """Header __init__ should give known result with known input for type"""
        for wikiline, contents, level, type in self.knownValues:
            result = wiktionary.Header(wikiline).type
            self.assertEqual(type, result)

'''
class ToRomanBadInput(unittest.TestCase):
    def testTooLarge(self):
        """toRoman should fail with large input"""
        self.assertRaises(roman.OutOfRangeError, roman.toRoman, 4000)
'''

if __name__ == "__main__":
    unittest.main()   

