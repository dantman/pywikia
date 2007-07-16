# -*- coding: utf-8 -*-
#!/usr/bin/python

import wikipedia, editarticle
"""
Script to remove links that are being or have been spammed.
Usage:

spamremove.py spammedsite.com

It will use Special:Linksearch to find the pages on the wiki that link to
that site, then for each page make a proposed change consisting of removing
all the lines where that url occurs. You can choose to:
* accept the changes as proposed
* edit the page yourself to remove the offending link
* not change the page in question
"""

try:
   msg = {'en': 'Removing links to spammed site %s',
          'nl': 'Links naar gespamde site %s verwijderd',
          }
   site = ''
   for arg in wikipedia.handleArgs():
      site = arg
   if not site:
      print "No site specified."
      sys.exit()
   mysite = wikipedia.getSite()
   pages = list(mysite.linksearch(site))
   wikipedia.getall(mysite,pages)
   for p in pages:
      if not site in p.get():
         continue
      print
      wikipedia.output(u"=== %s ==="%p)
      lines = p.get().split('\n')
      newpage = []
      lastok = ""
      for line in lines:
         if site in line:
            if lastok:
               print lastok
            wikipedia.output(line,colors = [12] * len(line))
            lastok = None
         else:
            newpage.append(line)
            if line.strip():
               if lastok is None:
                  print line
               lastok = line
      answer = "blablabla"
      while not answer in "yYnNeE":
         answer = wikipedia.input("Delete the red lines ([Y]es, [N]o, [E]dit)?")[0]
      if answer in "nN":
         continue
      elif answer in "eE":
         editor = editarticle.TextEditor()
         newtext = editor.edit(page.get(), highlight = site)
      else:
         newtext = "\n".join(newpage)
      if newtext != p.get():
         p.put(newtext, wikipedia.translate(mysite, msg) % site)
   
finally:
   wikipedia.stopme()
