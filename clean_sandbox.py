# -*- coding: utf-8 -*-
"""
This bot makes the cleaned of the page of tests.

Syntax:
6 hours: clean_sandbox.py -hours:6
1 second: clean_sandbox.py -hours:0.001

"""
import wikipedia
import time

content = {
    'ar': u'{{من فضلك اترك هذا السطر ولا تعدله (عنوان ساحة اللعب)}}\n <!-- مرحبا! خذ راحتك في تجربة مهارتك في التنسيق والتحرير أسفل هذا السطر. هذه الصفحة لتجارب التعديل ، سيتم تفريغ هذه الصفحة كل 6 ساعات. -->',
    'de': u'{{Bitte erst NACH dieser Zeile schreiben! (Begrüßungskasten)}}\r\n',
    'en': u'{{Please leave this line alone (sandbox heading)}}\n <!-- Hello! Feel free to try your formatting and editing skills below this line. As this page is for editing experiments, this page will automatically be cleaned every 12 hours. -->',
    'nl': u'{{subst:Wikipedia:Zandbak/schoon zand}}',
    'pl': u'{{Prosimy - NIE ZMIENIAJ, NIE KASUJ, NIE PRZENOŚ tej linijki - pisz niżej}}',
    'pt': u'<!--não apague esta linha-->{{página de testes}}<!--não apagar-->\r\n',
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
    }

class SandboxBot:
    def __init__(self, hours):
        self.hours = hours

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
            wikipedia.output(u'\nSleeping %s hours, now %s' % (self.hours, now))
            time.sleep(self.hours * 60 * 60)

def main():
    for arg in wikipedia.handleArgs():
        if arg.startswith('-hours:'):
            hours = float(arg[7:])
        else:
            wikipedia.showHelp('clean_sandbox')

        if hours:
            bot = SandboxBot(hours)
            bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
