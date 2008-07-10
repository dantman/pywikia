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
# (C) Leonardo Gregianin, 2006
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
    'ar': u'{{من فضلك اترك هذا السطر ولا تعدله (عنوان ساحة التجربة)}}\n<!-- مرحبا! خذ راحتك في تجربة مهارتك في التنسيق والتحرير أسفل هذا السطر. هذه الصفحة لتجارب التعديل ، سيتم تفريغ هذه الصفحة كل 6 ساعات. -->',
    'da': u'{{subst:Sandkasse tekst}}',
    'de': u'{{Bitte erst NACH dieser Zeile schreiben! (Begrüßungskasten)}}\r\n',
    'en': u'{{Please leave this line alone (sandbox heading)}}\n <!-- Hello! Feel free to try your formatting and editing skills below this line. As this page is for editing experiments, this page will automatically be cleaned every 12 hours. -->',
    'fi': u'{{subst:Hiekka}}',
    'he': u'{{ארגז חול}}\n<!-- נא לערוך מתחת לשורה זו בלבד, תודה. -->',
    'id': u'{{Bakpasir}}\n<!-- Uji coba dilakukan di baris di bawah ini -->',
    'it': u'{{sandbox}}  <!-- Scrivi SOTTO questa riga senza cancellarla. Grazie. -->',
    'ja': u'{{subst:サンドボックス}}',
    'ko': u'{{연습장 안내문}}',
    'nl': u'{{subst:Wikipedia:Zandbak/schoon zand}}',
    'no': u'{{Sandkasse}}\n<!-- VENNLIGST EKSPERIMENTER NEDENFOR DENNE SKJULTE TEKSTLINJEN! SANDKASSEMALEN {{Sandkasse}} SKAL IKKE FJERNES! -->}}',
    'nn': u'{{sandkasse}}\n<!-- Ver snill og IKKJE FJERN DENNE LINA OG LINA OVER ({{sandkasse}}) Nedanføre kan du derimot ha det artig og prøve deg fram! Lykke til! :-)  -->',
    'pl': u'{{Prosimy - NIE ZMIENIAJ, NIE KASUJ, NIE PRZENOŚ tej linijki - pisz niżej}}',
    'pt': u'<!--não apague esta linha-->{{página de testes}}<!--não apagar-->\r\n',
    'commons': u'{{Sandbox}}\n<!-- Please edit only below this line. -->',
    'sr': u'{{песак}}\n<!-- Молимо, испробавајте испод ове линије. Хвала. -->',
    'sv': u'{{subst:Sandlådan}}',
    'th': u'{{กระบะทราย}} \n<!-- กรุณาอย่าแก้ไขบรรทัดนี้ ขอบคุณครับ/ค่ะ -- Please leave this line as they are. Thank you! -->',
    'zh': u'{{subst:User:Sz-iwbot/sandbox}}\r\n',
    }

msg = {
    'ar': u'روبوت: هذه الصفحة سيتم تفريغها تلقائيا',
    'da': u'Bot: Nyt sand',
    'de': u'Bot: Setze Seite zurück.',
    'en': u'Robot: This page will automatically be cleaned.',
    'fi': u'Botti siivosi hiekkalaatikon.',
    'he': u'בוט: דף זה ינוקה אוטומטית.',
    'id': u'Bot: Tata ulang',
    'it': u'Bot: pulitura sandbox',
    'ja': u'ロボットによる: 砂場ならし',
    'ko': u'로봇: 연습장 비움',
    'nl': u'Robot: Automatisch voorzien van schoon zand.',
    'no': u'bot: Rydder sandkassa.',
    'pl': u'Robot czyści brudnopis',
    'pt': u'Bot: Limpeza da página de testes',
    'commons': u'Bot: This page will automatically be cleaned.',
    'sr': u'Чишћење песка',
    'sv': u'Robot krattar sandlådan.',
    'th': u'โรบอต: กำลังจะเก็บกวาดหน้านี้โดยอัตโนมัติ',
    'zh': u'Bot: 本页被自动清理',
    }

sandboxTitle = {
    'ar': u'ويكيبيديا:ساحة التجربة',
    'da': u'Wikipedia:Sandkassen',
    'de': u'Wikipedia:Spielwiese',
    'en': u'Wikipedia:Sandbox',
    'fi': u'Wikipedia:Hiekkalaatikko',
    'he': u'ויקיפדיה:ארגז חול',
    'id': u'Wikipedia:Bak pasir',
    'it': u'Project:Pagina delle prove',
    'ja': u'Wikipedia:サンドボックス',
    'ko': u'위키백과:연습장',
    'nl': u'Wikipedia:Zandbak',
    'no': u'Wikipedia:Sandkasse',
    'pl': u'Wikipedia:Brudnopis',
    'pt': u'Wikipedia:Página de testes',
    'commons': u'Commons:Sandbox',
    'sr': u'Википедија:Песак', 
    'sv': u'Wikipedia:Sandlådan',
    'th': u'วิกิพีเดีย:ทดลองเขียน',
    'zh': u'wikipedia:沙盒',
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
            if type(localSandboxTitle) is list:
                titles = localSandboxTitle
            else:
                titles = [localSandboxTitle,]
            for title in titles:
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
                return
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
            return

    bot = SandboxBot(hours, no_repeat)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
