#!/usr/bin/python
# -*- coding: utf-8  -*-

"""Unit tests for meaning.py"""

import meaning
import unittest

class KnownValues(unittest.TestCase):

    knownParserValues = (
                ("*German: [[wichtig]]",
                    ('de','wichtig','',1,False)
                ),
                ("*[[Esperanto]]: [[grava]]",
                    ('es','grava','',1,False)
                ),
                ("*{{fr}}: [[importante]] {{f}}",
                    ('fr','importante','f',1,False)
                ),
                ("*Dutch: [[voorbeelden]] ''n, pl'', [[instructies]] {{f}}, {{p}}''",
                    ('nl','voorbeelden','n',2,False),
                    ('nl','instructies', 'f',2,False)
                ),
                ("*Russian: [[шесток]] ''m'' (shestok)",
                    ('ru','шесток','m',1,False)
                ),
                ("*Kazakh: сәлем, салам, сәлеметсіздер(respectable)",
                    ('ka','сәлем','',1,False),
                    ('ka','салам','',1,False),
                    ('ka','сәлеметсіздер','',1,False)
                ),
                ("*Chinese(Mandarin):[[你好]](ni3 hao3), [[您好]](''formal'' nin2 hao3)",
                    ('zh','你好','',1,False),
                    ('zh','您好','',1,False)
                ),
                ("*Italian: [[pronto#Italian|pronto]]",
                    ('it','pronto','',1,False)
                ),
                         )

    def testParser(self):
        '''self.term, self.gender and self.number parsed correctly from Wiki format'''
        for wikiline, results in self.knownParserValues:
            ameaning = meaning.Meaning(
            termlang, '', wikiline=wikiline)
            for termlang, thisterm, termgender, termnumber in results:
                self.assertEqual(aterm.getTerm(), thisterm)
                self.assertEqual(aterm.getGender(), termgender)
                self.assertEqual(aterm.getNumber(), termnumber)

if __name__ == "__main__":
    unittest.main()
    
