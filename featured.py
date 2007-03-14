#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This script understands various command-line arguments:

* -interactive     : ask before changing page

* -nocache         : doesn't include /featured/cache file to remembers if the
                     article already was verified.

* -fromlang:xx,yy  : xx is your language and yy the language was verified or
                    using -fromall to verified all languages.

usage: featured.py [-interactive] [-nocache] [-fromlang:xx,yy|-fromall]

"""
__version__ = '$Id$'

import sys, re
import wikipedia, catlib, config

def CAT(site,name):
    cat=catlib.Category(site, name)
    return cat.articles()

def BACK(site,name):
    p=wikipedia.Page(site, name)
    return [page for page in p.getReferences(follow_redirects = False)]

def LINKS(site,name, ignore=[]):
    p=wikipedia.Page(site, name)
    links=p.linkedPages()
    for n in links[:]:
        t=n.titleWithoutNamespace()
        if t[0] in u"/#" or t in ignore:
            links.remove(n)
    links.sort()
    return links

msg = {
    'bs': u'Interwiki za izabrane članke za [[%s:%s]]',
    'en': u'Featured article link for [[%s:%s]]',
    'fi': u'Suositeltu artikkeli -tähti: [[%s:%s]]',
    'fr': u'Lien AdQ pour [[%s:%s]]', 
    'he': u'קישור לערך מומלץ עבור [[%s:%s]]',
    'hr': u'Interwiki za izabrane članke za [[%s:%s]]',
    'lt': u'Pavyzdinis straipsnis [[%s:%s]]',
    'nl': u'Etalage artikel link voor [[%s:%s]]',
    'pl': u'Link do artykułu wyróżnionego [[%s:%s]]',
    'pt': u'Ligando artigos destacados para [[%s:%s]]',
    'sr': u'Међувики за изабране чланке за [[%s:%s]]',
}

# default is en:Link FA
template = {
    'bg': 'Link FA',
    'br': 'Liamm PuB',
    'bs': 'Link FA',
    'ca': 'Enllaç AD',
    'da': 'Link FA',
    'de': 'Link FA',
    'en': 'Link FA',
    'eo': 'LigoElstara',
    'es': 'destacado',
    'fr': 'lien AdQ',
    'hr': 'Link FA',
    'it': 'Link AdQ',
    'lt': 'Link FA',
    'lv': 'Link FA',
    'nl': 'Link FA',
    'no': 'Link UA',
    'pl': 'Link FA',
    'pt': 'Link FA',
    'ru': 'Link FA',
    'sl': 'Link FA',
    'sr': 'Link FA',
    'sv': 'UA',
    'tr': 'Link FA',
    'vi': 'Liên kết chọn lọc',
}
    
featured_name = {
    'bs': (BACK, u"Šablon:Wiki članak"),
    'cs': (BACK, u"Šablona:Nejlepší článek"),
    'de': (CAT, u"Kategorie:Exzellenter Artikel"),
    'el': (BACK, u"Πρότυπο:ΕπιλεγμένοΆρθρο"),
    'eo': (BACK, u"Ŝablono:Elstara"),
    'en': (CAT, u"Category:Wikipedia featured articles"),
    'es': (CAT, u"Categoría:Wikipedia:Artículos destacados"),
    'fi': (BACK, u"Malline:Suositeltu"),
    'fr': (CAT, u"Catégorie:Articles de qualité"),
    'he': (CAT, u"קטגוריה:ערכים מומלצים"),
    'hr': (BACK, u"Predložak:Izdvojeni članak"),
    'id': (BACK, u"Templat:Pilihan"),
    'is': (CAT, u"Flokkur:Úrvalsgreinar"),
    'it': (CAT, u"Categoria:Articoli in vetrina"),
    'ja': (BACK, u"Template:秀逸"),
    'lt': (CAT, u"Kategorija:Vikipedijos pavyzdiniai straipsniai"),
    'nl': (BACK, u"Sjabloon:Etalage"),
    'no': (CAT, u"Kategori:Utmerkede artikler"),
    'pl': (CAT, u"Kategoria:Artykuły na medal"),
    'pt': (CAT, u"Categoria:!Artigos destacados"),
    'ro': (CAT, u"Categorie:Articole de calitate"),
    'ru': (CAT, u"Категория:Википедия:Избранные статьи"),
    'sh': (CAT, u"Category:Izabrani članci"),
    'sk': (BACK, u"Šablóna:Perfektný článokka"),
    'sl': (CAT, u"Category:Izbrani članki"),
    'sr': (BACK, u"Шаблон:Изабрани"),
    'sv': (CAT, u"Kategori:Wikipedia:Utvalda artiklar"),
    'ta': (BACK, u"வார்ப்புரு:சிறப்பு"),
    'tl': (BACK, u"Template:Napiling artikulo"),
    'uk': (CAT, u"Категорія:Вибрані статті"),
    'vi': (CAT, u"Thể loại:Bài viết chọn lọc"),
    'zh': (CAT, u"Category:特色条目"),
}

# globals
interactive=0
nocache=0
afterpage=u"!"

try:
    import pickle
    cache=pickle.load(file("featured/cache","rb"))
except:
    cache={}

def featuredArticles(site):
    method=featured_name[site.lang][0]
    name=featured_name[site.lang][1]
    args=featured_name[site.lang][2:]
    raw=method(site, name, *args)
    arts=[]
    for p in raw:
        if p.namespace()==0: # Article
            arts.append(p)
        elif p.namespace()==1: # Article talk (like in English)
            arts.append(wikipedia.Page(p.site(), p.titleWithoutNamespace()))
    return arts

def findTranslated(page, oursite=None):
    if not oursite:
        oursite=wikipedia.getSite()
    if page.isRedirectPage():
        page=wikipedia.Page(page.site(), page.getRedirectTarget())
    try:
        iw=page.interwiki()
    except:
        wikipedia.output(u"no interwiki, giving up")
        return None
    ourpage=None
    for p in iw:
        if p.site()==oursite:
            ourpage=p
            break
    if not ourpage:
        wikipedia.output(u"No corresponding page in "+`oursite`)
        return None
    if not ourpage.exists():
        wikipedia.output(u"Our page doesn't exist: "+ourpage.title())
        return None
    if ourpage.isRedirectPage(): 
        ourpage=wikipedia.Page(ourpage.site(),ourpage.getRedirectTarget())
    wikipedia.output(u"Corresponding page is "+ourpage.title())
    if ourpage.namespace() != 0:
        wikipedia.output(u"...not in the main namespace, skipping")
        return None
    if ourpage.isRedirectPage(): 
        wikipedia.output(u"double redirect, skipping")
        return None
	if not ourpage.exists():
	    wikipedia.output(u"page doesn't exist, skipping")
        return None
    try:
        iw=ourpage.interwiki()
    except:
	    return None
    backpage=None
    for p in iw:
        if p.site()==page.site():
            backpage=p
            break
    if not backpage:
        wikipedia.output(u"no back interwiki ref")
        return None
    if backpage==page:
        # everything is ok
        return ourpage
    if backpage.isRedirectPage():
        backpage=wikipedia.Page(backpage.site(),backpage.getRedirectTarget())
    if backpage==page:
        # everything is ok
        return ourpage
    wikipedia.output(u"back interwiki ref target is "+backpage.title())
    return None

def featuredWithInterwiki(fromsite, tosite):
    if not fromsite.lang in cache:
        cache[fromsite.lang]={}
    if not tosite.lang in cache[fromsite.lang]:
        cache[fromsite.lang][tosite.lang]={}
    cc=cache[fromsite.lang][tosite.lang]
    if nocache:
        cc={}

    findtemplate = wikipedia.translate(wikipedia.getSite(), template)
    re_Link_FA=re.compile(ur"\{\{%s\|%s\}\}" % (findtemplate, fromsite.lang))
    re_this_iw=re.compile(ur"\[\[%s:[^]]+\]\]" % fromsite.lang)

    arts=featuredArticles(fromsite)
        
    pairs=[]
    for a in arts:
        if a.title()<afterpage:
            continue
        if u"/" in a.title():
            wikipedia.output(u"%s is a subpage" % a.title())
            continue
        if a.title() in cc:
            wikipedia.output(u"(cached) %s -> %s"%(a.title(), cc[a.title()]))
            continue
        if a.isRedirectPage():
            a=wikipedia.Page(a.site(),a.getRedirectTarget())
        try:
            if not a.exists():
                wikipedia.output(u"source page doesn't exist: %s" % a.title())
                continue
            atrans=findTranslated(a,tosite)
            if atrans:
                text=atrans.get()
                m=re_Link_FA.search(text)
                if m:
                    wikipedia.output(u"(already done)")
                else:
                    # insert just before interwiki
                    if (not interactive or 
                        wikipedia.input(u'Connecting %s -> %s. Proceed? [Y/N]'%(a.title(), atrans.title())) in ['Y','y']
                        ):
                        m=re_this_iw.search(text)
                        if not m:
                            wikipedia.output(u"no interwiki record, very strange")
                            continue
                        comment = wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg) % (fromsite.lang, a.title()))
                        text=wikipedia.replaceCategoryLinks(text+(u"{{%s|%s}}"%(findtemplate, fromsite.lang)), atrans.categories()) 
                        atrans.put(text, comment)
                                                
                cc[a.title()]=atrans.title()
        except wikipedia.PageNotSaved, e:
            wikipedia.output(u"Page not saved")

if __name__=="__main__":
    
    fromlang=[]
    for arg in wikipedia.handleArgs():
        if arg == '-interactive':
            interactive=1
        elif arg == '-nocache':
            nocache=1
        elif arg.startswith('-fromlang:'):
            fromlang=arg[10:].split(",")
            if len(fromlang)==1 and fromlang[0].index("-")>=0:
                ll1,ll2=fromlang[0].split("-",1)
                if not ll1: ll1=""
                if not ll2: ll2="zzzzzzz"
                fromlang=[ll for ll in featured_name.keys() if ll>=ll1 and ll<=ll2]
        elif arg == '-fromall':
            fromlang=featured_name.keys()
        elif arg.startswith('-after:'):
            afterpage=arg[7:]

    if not fromlang:
        wikipedia.showHelp('featured')
        sys.exit(1)

    fromlang.sort()
    try:
        for ll in fromlang:
            fromsite=wikipedia.Site(ll)
            if not fromsite==wikipedia.getSite():
                featuredWithInterwiki(fromsite, wikipedia.getSite())
    finally:
        wikipedia.stopme()
        if not nocache:
            import pickle
            pickle.dump(cache,file("featured/cache","wb"))
