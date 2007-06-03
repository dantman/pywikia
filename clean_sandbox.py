# -*- coding: utf-8 -*-
"""
This bot cleans a sandbox by replacing the current contents with predefined
text.

This script understands the following command-line arguments:

    -hours:#       Use this parameter if to make the script repeat itself
                   after # hours. Hours can be defined as a decimal. 0.001
                   hours is one second.

"""
#
# (C) Leogregianin, 2006
# (C) Wikipedian, 2006-2007
# (C) Andre Engels, 2007
# (C) Siebrand Mazeland, 2007
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#

import wikipedia
import time

content = {
    'ar': u'{{من فضلك اترك هذا السطر ولا تعدله (عنوان ساحة اللعب)}}\n <!-- مرحبا! خذ راحتك في تجربة مهارتك في التنسيق والتحرير أسفل هذا السطر. هذه الصفحة لتجارب التعديل ، سيتم تفريغ هذه الصفحة كل 6 ساعات. -->',
    'de': u'{{Bitte erst NACH dieser Zeile schreiben! (Begrüßungskasten)}}\r\n',
    'en': u'{{Please leave this line alone (sandbox heading)}}\n <!-- Hello! Feel free to try your formatting and editing skills below this line. As this page is for editing experiments, this page will automatically be cleaned every 12 hours. -->',
    'nl': u'{{subst:Wikipedia:Zandbak/schoon zand}}',
    'pl': u'{{Prosimy - NIE ZMIENIAJ, NIE KASUJ, NIE PRZENOŚ tej linijki - pisz niżej}}',
    'pt': u'<!--não apague esta linha-->{{página de testes}}<!--não apagar-->\r\n',
    'commons': u'{{subst:Sandbox}}<!-- Please edit only below this line. -->\n'
    }

msg = {
    'ar': u'روبوت: هذه الصفحة سيتم تفريغها تلقائياً',
    'de': u'Bot: Setze Seite zurück.',
    'en': u'Robot: This page will automatically be cleaned.',
    'nl': u'Robot: Automatisch voorzien van schoon zand.',
    'pl': u'Robot czyści brudnopis',
    'pt': u'Bot: Limpeza da página de testes',
    }

sandboxTitle = {
    'ar': u'ويكيبيديا:ساحة اللعب',
    'de': u'Wikipedia:Spielwiese',
    'en': u'Wikipedia:Sandbox',
    'nl': u'Wikipedia:Zandbak',
    'pl': u'Wikipedia:Brudnopis',
    'pt': u'Wikipedia:Página de testes',
    'commons': u'Commons:Sandbox'
    }

class SandboxBot:
    def __init__(self, hours, no_repeat):
        self.hours = hours
        self.no_repeat = no_repeat

    def run(self):
        mySite = wikipedia.getSite()
        while True:
            now = time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime())
            localSandboxTitle = wikipedia.translate(mySite, sandboxTitle)
            sandboxPage = wikipedia.Page(mySite, localSandboxTitle)
            try:
                text = sandboxPage.get()
                translatedContent = wikipedia.translate(mySite, content)
                if text.strip() == translatedContent.strip():
                    wikipedia.output(u'The sandbox is still clean, no change necessary.')
                else:
                    translatedMsg = wikipedia.translate(mySite, msg)
                    sandboxPage.put(translatedContent, translatedMsg)
            except wikipedia.EditConflict:
                wikipedia.output(u'*** Loading again because of edit conflict.\n')
            if self.no_repeat:
                wikipedia.output(u'\nDone.')
                wikipedia.stopme()
                exit()
            else:
                wikipedia.output(u'\nSleeping %s hours, now %s' % (self.hours, now))
                time.sleep(self.hours * 60 * 60)

def main():
    hours = 1
    no_repeat = True
    for arg in wikipedia.handleArgs():
        if arg.startswith('-hours:'):
            hours = float(arg[7:])
            no_repeat = False
        else:
            wikipedia.showHelp('clean_sandbox')
            wikipedia.stopme()
            exit()

    bot = SandboxBot(hours, no_repeat)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
