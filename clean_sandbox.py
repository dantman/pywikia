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
    'de': u'{{Bitte erst NACH dieser Zeile schreiben! (Begrüßungskasten)}}\n',
    'en': u'{{Please leave this line alone (sandbox heading)}}\n <!-- Hello! Feel free to try your formatting and editing skills below this line. As this page is for editing experiments, this page will automatically be cleaned every 12 hours. -->',
    'pt': u'<!--não apague esta linha-->{{página de testes}}<!--não apagar-->\n',
    }

msg = {
    'de': u'Bot: reset',
    'en': u'Robot: This page will automatically be cleaned.',
    'pt': u'Bot: Limpeza da página de testes',
    }
    
page = {
    'de': u'Wikipedia:Spielwiese',
    'en': u'Wikipedia:Sandbox',
    'pt': u'Wikipedia:Página de testes',
    }

def SandboxBot(hours):
    seg = hours*3600
    mysite = wikipedia.getSite()
    now = time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime())
    page_translate = wikipedia.translate(mysite, page)
    title = wikipedia.Page(mysite, page_translate)
    try:
        wikipedia.output(u'\nSleeping %s hours, now %s' % (hours, now))
        time.sleep(seg)
        msg_translate = wikipedia.translate(mysite, msg)
        content_translate = wikipedia.translate(mysite, content)
        title.put(content_translate, msg_translate)
        SandboxBot(hours)
    except wikipedia.EditConflict:
        wikipedia.output(u'*** Loading again because of edit conflict.\n')
        wikipedia.output(u'\nSleeping %s hours, now %s' % (hours, now))
        time.sleep(seg)
        SandboxBot(hours)
    
if __name__ == "__main__":
    try:
        for arg in wikipedia.handleArgs():
            if arg.startswith('-hours:'):
                hours = float(arg[7:])
                SandboxBot(hours)
            else:
                wikipedia.showHelp('clean_sandbox')
    except:
        wikipedia.stopme()
