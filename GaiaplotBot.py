# -*- coding: utf-8  -*-
"""
This bot is used by the Gaiapedia/Plotwiki network to update the current events list on Gaiapedia with page links on Plotwiki.
"""

import sys, sre, re
import wikipedia, pagegenerators, catlib, config

msg = {
       'en':u'GaiaplotBot current events update.',
       }

def main():
	gaia = wikipedia.getSite(code=u'en', fam=u'gaia')
	plot = wikipedia.getSite(code=u'en', fam=u'plotwiki')
	
	wikipedia.setAction(wikipedia.translate(gaia, msg))
	wikipedia.setAction(wikipedia.translate(plot, msg))
	
	final = u'<noinclude><!-- Do not edit this page, this page is automatically created by a Bot. -->\n'
	final+= u'==Most Recent Events==</noinclude>\n'
	
	nonrecent = u'<noinclude>==Older Events==\n'
	end = u'\n\'\'View everything here on the [[Plotwiki:|plotwiki...]]\'\'</noinclude>'
	
	moreYears = True
	year = 04
	
	events = []
	temp = []
	while moreYears:
		y = str(year)
		page = wikipedia.Page(plot, u'Template:Pnav%s' % y.zfill(2))
		
		try:
			text = page.get()
			
			r = sre.compile(u'^.*<span style=".*normal.*">(.*)</span>.*$', sre.UNICODE | sre.MULTILINE | sre.DOTALL)
			text = sre.sub(r, u'\\1', text)
			r = sre.compile(u'\s+\|\s+', sre.UNICODE | sre.MULTILINE | sre.DOTALL)
			pages = sre.split(r, text)
			
			r = sre.compile(u'\[\[([^|]*)(\|.*)?\]\]', sre.UNICODE)
			for p in pages:
				temp.append(sre.sub(r, u'\\1', p))
			
			year+=1
		except wikipedia.NoPage:
			moreYears = False
	for e in temp:
		if not e in events:
			events.append(e)
	
	events = reversed(list(events));
	x = 1
	for e in events:
		final+=u'* [[Plotwiki:%s|]]\n' % e
		x+=1
		if x==6:
			final+=nonrecent
	if x<=6:
		final+=end
	final+=end
	
	page = wikipedia.Page(gaia, u'Plotwiki Current Events')
	page.put(final)

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()