import unittest
import xml.sax

import sys
# get the xmlreader module one level under
sys.path.append('..')

import xmlreader

class XmlReaderTestCase(unittest.TestCase):
    def test_XmlDump(self):
        pages = [r for r in xmlreader.XmlDump("article-pear.xml", allrevisions=True).parse()]
        self.assertEquals(4, len(pages))
        self.assertNotEquals("", pages[0].comment)
    def test_MediaWikiXmlHandler(self):
        handler = xmlreader.MediaWikiXmlHandler()
        pages = []
        def pageDone(page):
            pages.append(page)
        handler.setCallback(pageDone)
        xml.sax.parse("article-pear.xml", handler)
        self.assertEquals(4, len(pages))
        self.assertNotEquals("", pages[0].comment)

if __name__ == '__main__':
    unittest.main()
