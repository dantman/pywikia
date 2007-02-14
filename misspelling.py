# -*- coding: utf-8  -*-
"""
This script works similar to solve_disambiguation.py. It is supposed to fix
links that contain common spelling mistakes. This is only possible on wikis
that have a template for these misspellings.

Command line options:

   -always:XY  instead of asking the user what to do, always perform the same
               action. For example, XY can be "r0", "u" or "2". Be careful with
               this option, and check the changes made by the bot. Note that
               some choices for XY don't make sense and will result in a loop,
               e.g. "l" or "m".

   -main       only check pages in the main namespace, not in the talk,
               wikipedia, user, etc. namespaces.
"""

# (C) Daniel Herding, 2007
#
# Distributed under the terms of the MIT license.

import wikipedia, solve_disambiguation, pagegenerators

class MisspellingRobot(solve_disambiguation.DisambiguationRobot):

    misspellingTemplate = {
        'de': u'Falschschreibung',
        #'en': u'Template:Misspelling', # rarely used on en:
        'pt': u'Pseudo-redirect',
    }

    msg = {
        'de': u'Bot: korrigiere Link auf Falschschreibung: %s',
        'en': u'Robot: Fixing misspelled link to %s',
        'pl': u'Robot poprawia literówkę w linku do %s',
        'pt': u'Bot: Corrigindo link com erro ortográfico para %s'
    }

    def __init__(self, always, main_only):
        solve_disambiguation.DisambiguationRobot.__init__(self, always, [], True, self.createPageGenerator(), False, main_only)

    def createPageGenerator(self):
        misspellingTemplateName = 'Template:%s' % self.misspellingTemplate[wikipedia.getSite().lang]
        misspellingTemplate = wikipedia.Page(wikipedia.getSite(), misspellingTemplateName)
        generator = pagegenerators.ReferringPageGenerator(misspellingTemplate, onlyTemplateInclusion = True)
        preloadingGen = pagegenerators.PreloadingGenerator(generator)
        return preloadingGen

    # Overrides the DisambiguationRobot method.
    def findAlternatives(self, disambPage):
        for templateName, params in disambPage.templatesWithParams():
            if templateName in self.misspellingTemplate[wikipedia.getSite().lang]:
                # The correct spelling is in the last paramter.
                # This works for de:, not tested with others.
                self.alternatives.append(params[-1])
                return True

    # Overrides the DisambiguationRobot method.
    def setSummaryMessage(self, disambPage):
        comment = wikipedia.translate(self.mysite, self.msg) % disambPage.title()
        wikipedia.setAction(comment)

def main():
    # the option that's always selected when the bot wonders what to do with
    # a link. If it's None, the user is prompted (default behaviour).
    always = None
    main_only = False

    for arg in wikipedia.handleArgs():
        if arg.startswith('-always:'):
            always = arg[8:]
        elif arg == '-main':
            main_only = True

    bot = MisspellingRobot(always, main_only)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
