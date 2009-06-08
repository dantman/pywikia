# -*- coding: utf-8  -*-
"""
This bot is used by the Wikia Anime Project to copy userboxes across the wikia in the project.
Info: http://en.anime.wikia.com/wiki/Project:Bots/UserBox
"""

import sys, re
import wikipedia, pagegenerators, catlib, config
try:
    set # introduced in Python 2.4: faster and future
except NameError:
    # fallback solution for Python 2.3
    from sets import Set as set

msg = {
       'en':u'[[Anime:Project:Bots/UserBox|UserBoxBot]].',
       }

def main():
    #Setup Familys for Wikia Involved
    anime = wikipedia.getSite(code=u'en', fam=u'anime')
    wikipedia.setAction(wikipedia.translate(anime, msg))
    siteList = []
    templateList = []
    
    #Get Project Wiki Listing
    wikiaIds = []
    page = wikipedia.Page(anime, u'Bots/Wiki', None, 4)#4=Project Namespace
    try:
        text = page.get()
        r = re.compile(u'^.*<!-- \|\|START\|\| -->\n?', re.UNICODE | re.DOTALL)
        text = re.sub(r, u'', text)
        r = re.compile(u'\n?<!-- \|\|END\|\| -->.*$', re.UNICODE | re.DOTALL)
        text = re.sub(r, u'', text)
        r = re.compile(u'\n', re.UNICODE | re.DOTALL)
        wikilist = re.split(r, text)
        r = re.compile(u'^#|^\s*$|^\[', re.UNICODE | re.MULTILINE | re.DOTALL)
        for wiki in wikilist:
            if not re.match(r, wiki):
                siteList.append(wikipedia.getSite(code=u'en', fam=wiki))
    except wikipedia.NoPage:
        return False
    
    #Get Userboxes and General pages.
    ProjectUserboxes = u'{{SharedUserBox}}\nInformation about userboxes is located on the [[{{animeNetwork|anime|home}}|{{animeNetwork|anime|name}}]], you may find it [[{{animeNetwork|anime|interwiki}}Project:Userboxes|here]].\n\n[[Category:Userboxes| ]]'
    ProjectBabel = u'{{SharedUserBox}}\nInformation about babel boxes is located on the [[{{animeNetwork|anime|home}}|{{animeNetwork|anime|name}}]], you may find it [[{{animeNetwork|anime|interwiki}}Project:Babel|here]].\n\n[[Category:User Babel| ]]'
    UserBoxCategorys = []
    UserBoxes = []
    
    catpage = wikipedia.Page(anime, u'Userboxes', None, 14)#14=Category Namespace
    cat = catlib.Category(anime, catpage.title())
    UserBoxCategorys.append(cat)
    pagelist = catlib.unique(cat.articles(True))
    
    for page in pagelist:
        title = page.title()
        r = re.compile(u'^Template:', re.UNICODE | re.DOTALL)
        if not re.match(r, title):
            continue
        r = re.compile(u'^Template:Userbox$', re.UNICODE | re.DOTALL)
        if re.match(r, title):
            continue
        UserBoxes.append(page)

    catlist = cat.subcategories(True)

    for category in catlist:
        UserBoxCategorys.append(category)
    
    for category in UserBoxCategorys:
        categorySource = u'{{SharedUserBox|category}}\n%s' % category.get()

        if categorySource != u'':
            for site in siteList:
                siteCategory = catlib.Category(site, category.title())
                siteSource = u''
                try:
                    siteSource = siteCategory.get()
                except wikipedia.NoPage:
                    wikipedia.output(u'Site %s has no %s category, creating it' % (site, category.title()))
                if siteSource != categorySource:
                    wikipedia.output(u'Site \'%s\' category status: Needs Updating' % site)
                    wikipedia.output(u'Updating category on %s' % site)
                    siteCategory.put(categorySource)
                else:
                    wikipedia.output(u'Site \'%s\' category status: Ok' % site)
        else:
            wikipedia.output(u'Category %s is blank, skipping category' % category.title())

    for userbox in UserBoxes:
        userboxSource = u'<noinclude>{{SharedUserBox|userbox}}\n</noinclude>%s' % userbox.get()

        if userboxSource != u'':
            for site in siteList:
                siteUserbox = wikipedia.Page(site, userbox.title())
                siteSource = u''
                try:
                    siteSource = siteUserbox.get()
                except wikipedia.NoPage:
                    wikipedia.output(u'Site %s has no %s userbox, creating it' % (site, userbox.title()))
                if siteSource != userboxSource:
                    wikipedia.output(u'Site \'%s\' userbox status: Needs Updating' % site)
                    wikipedia.output(u'Updating userbox on %s' % site)
                    siteUserbox.put(userboxSource)
                else:
                    wikipedia.output(u'Site \'%s\' userbox status: Ok' % site)
        else:
            wikipedia.output(u'UserBox %s is blank, skipping userbox' % userbox.title())

    
    for site in siteList:
        sitePage = wikipedia.Page(site, u'Project:Userboxes')
        siteSource = u''
        try:
            siteSource = sitePage.get()
        except wikipedia.NoPage:
            wikipedia.output(u'Site %s has no Project:Userboxes page, creating it' % site)
        if siteSource != ProjectUserboxes:
            wikipedia.output(u'Site \'Project:Userboxes\' status: Needs Updating' % site)
            wikipedia.output(u'Updating \'Project:Userboxes\' on %s' % site)
            sitePage.put(ProjectUserboxes)
        else:
            wikipedia.output(u'Site \'Project:Userboxes\' status: Ok' % site)
		
        sitePage = wikipedia.Page(site, u'Project:Babel')
        siteSource = u''
        try:
            siteSource = sitePage.get()
        except wikipedia.NoPage:
            wikipedia.output(u'Site %s has no Project:Babel page, creating it' % site)
        if siteSource != ProjectUserboxes:
            wikipedia.output(u'Site \'Project:Babel\' status: Needs Updating' % site)
            wikipedia.output(u'Updating \'Project:Babel\' on %s' % site)
            sitePage.put(ProjectBabel)
        else:
            wikipedia.output(u'Site \'Project:Babel\' status: Ok' % site)
    
if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
