"""
This script checks references to see if they are properly formatted.  Right now
it just counts the total number of transclusions of any number of given templates.

NOTE: This script is not capable of handling the <ref></ref> syntax. It just
handles the {{ref}} syntax, which is still used, but DEPRECATED on the English
Wikipedia.

Syntax: python refcheck.py command [arguments]

Command line options:

-count        Counts the number of times each template (passed in as an argument)
              is transcluded.
-namespace:   Filters the search to a given namespace.  If this is specified
              multiple times it will search all given namespaces

Examples:

Counts how many time {{ref}} and {{note}} are transcluded in articles.

     python refcheck.py -count ref note -namespace:0

"""
__version__ = '$Id$'

import wikipedia, config
import replace, pagegenerators
import re, sys, string

class ReferencesRobot:
    #def __init__(self):
        #Nothing
    def countRefs(self, templates, namespaces):
        mysite = wikipedia.getSite()
        finalText = [u'Number of transclusions per template',u'------------------------------------']
        for template in templates:
            gen = pagegenerators.ReferringPageGenerator(wikipedia.Page(mysite, mysite.template_namespace() + ':' + template), onlyTemplateInclusion = True)
            if namespaces:
                gen = pagegenerators.NamespaceFilterPageGenerator(gen, namespaces)
            count = 0
            for page in gen:
                count = count + 1
            finalText.append(u'%s: %d' % (template, count))
        for line in finalText:
            wikipedia.output(line)

def main():
    doCount = False
    argsList = []
    namespaces = []
    #templates = ['ref', 'note', 'ref label', 'note label']
    for arg in wikipedia.handleArgs():
        if arg == '-count':
            doCount = True
        elif arg.startswith('-namespace:'):
            try:
                namespaces.append(int(arg[len('-namespace:'):]))
            except ValueError:
                namespaces.append(arg[len('-namespace:'):])
        else:
            argsList.append(arg)

    if doCount:
        robot = ReferencesRobot()
        if argsList:
            robot.countRefs(argsList, namespaces)
        else:
            robot.countRefs(['ref', 'note', 'ref label', 'note label'], namespaces)
    else:
        wikipedia.showHelp('refcheck')

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()

    #preloadingGen = pagegenerators.PreloadingGenerator(gen, pageNumber=100)
    #for page in preloadingGen:
        #pagetext = page.get()
