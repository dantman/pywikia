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

    -start:XY  goes through all misspellings in the category on your wiki
               that is defined (to the bot) as the category containing misspelling
               pages, starting at XY. If the -start argument is not given, it starts
               at the beginning.

   -main       only check pages in the main namespace, not in the talk,
               wikipedia, user, etc. namespaces.
"""
__version__ = '$Id$'

# (C) Daniel Herding, 2007
#
# Distributed under the terms of the MIT license.

import wikipedia, solve_disambiguation, catlib, pagegenerators

class MisspellingRobot(solve_disambiguation.DisambiguationRobot):

    misspellingTemplate = {
        'de': u'Falschschreibung',
        #'en': u'Template:Misspelling', # rarely used on en:
        'en': None,                     # en: uses simple redirects
        #'pt': u'Pseudo-redirect',      # replaced by another system on pt:
    }

    # Optional: if there is a category, one can use the -start
    # parameter.
    misspellingCategory = {
        'de': u'Kategorie:Wikipedia:Falschschreibung',
        'en': u'Redirects from misspellings',
        #'pt': u'Categoria:!Pseudo-redirects',
    }

    msg = {
	    'ar': u'روبوت: إصلاح وصلة خاطئة إلى %s',
        'de': u'Bot: korrigiere Link auf Falschschreibung: %s',
        'en': u'Robot: Fixing misspelled link to %s',
        'he': u'בוט: מתקן קישור עם שגיאה לדף %s',
        'nds': u'Bot: rut mit verkehrt schreven Lenk op %s',
        'pl': u'Robot poprawia literówkę w linku do %s',
        'pt': u'Bot: Corrigindo link com erro ortográfico para %s'
    }

    def __init__(self, always, firstPageTitle, main_only):
        solve_disambiguation.DisambiguationRobot.__init__(self, always, [], True, self.createPageGenerator(firstPageTitle), False, main_only)

    def createPageGenerator(self, firstPageTitle):
        if self.misspellingCategory.has_key(wikipedia.getSite().lang):
            misspellingCategoryTitle = self.misspellingCategory[wikipedia.getSite().lang]
            misspellingCategory = catlib.Category(wikipedia.getSite(), misspellingCategoryTitle)
            generator = pagegenerators.CategorizedPageGenerator(misspellingCategory, recurse = True, start = firstPageTitle)
        else:
            misspellingTemplateName = 'Template:%s' % self.misspellingTemplate[wikipedia.getSite().lang]
            misspellingTemplate = wikipedia.Page(wikipedia.getSite(), misspellingTemplateName)
            generator = pagegenerators.ReferringPageGenerator(misspellingTemplate, onlyTemplateInclusion = True)
            if firstPageTitle:
                wikipedia.output(u'-start parameter unsupported on this wiki because there is no category for misspellings.')
        preloadingGen = pagegenerators.PreloadingGenerator(generator)
        return preloadingGen

    # Overrides the DisambiguationRobot method.
    def findAlternatives(self, disambPage):
        if disambPage.isRedirectPage():
            self.alternatives.append(disambPage.getRedirectTarget().title())
            return True
        elif self.misspellingTemplate[disambPage.site().lang] is not None:
            for templateName, params in disambPage.templatesWithParams():
                if templateName in self.misspellingTemplate[wikipedia.getSite().lang]:
                    # The correct spelling is in the last paramter.
                    # This works for de:, not tested with others.
                    self.alternatives.append(params[-1])
                    return True

    # Overrides the DisambiguationRobot method.
    def setSummaryMessage(self, disambPage, new_targets, unlink):
        # TODO: setSummaryMessage() in solve_disambiguation now has parameters
        # new_targets and unlink. Make use of these here.
        comment = wikipedia.translate(self.mysite, self.msg) % disambPage.title()
        wikipedia.setAction(comment)

def main():
    # the option that's always selected when the bot wonders what to do with
    # a link. If it's None, the user is prompted (default behaviour).
    always = None
    main_only = False
    firstPageTitle = None

    for arg in wikipedia.handleArgs():
        if arg.startswith('-always:'):
            always = arg[8:]
        elif arg.startswith('-start'):
            if len(arg) == 6:
                firstPageTitle = wikipedia.input(u'At which page do you want to start?')
            else:
                firstPageTitle = arg[7:]
        elif arg == '-main':
            main_only = True
            

    bot = MisspellingRobot(always, firstPageTitle, main_only)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
