#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This script understands various command-line arguments:

* -interactive       : ask before changing page

* -nocache           : doesn't include /featured/cache file to remembers if the
                       article already was verified.

* -fromlang:xx[,yy[,...]]] : xx,.. are the languages to be verified.

* -fromall           : to verifiy all languages.
				
* -after:zzzz        : process pages after and including page zzzz

usage: featured.py [-interactive] [-nocache] [-after:zzzz] [-fromlang:xx,yy,zz|-fromall]

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
    'bs': u'Bot: Interwiki za izabrane članke za [[%s:%s]]',
    'en': u'Bot: Featured article link for [[%s:%s]]',
    'cs': u'Bot: Nejlepší článek:  [[%s:%s]]',
    'fi': u'Bot: Suositeltu artikkeli -tähti: [[%s:%s]]',
    'fr': u'Bot: Lien AdQ pour [[%s:%s]]',
    'he': u'בוט: קישור לערך מומלץ עבור [[%s:%s]]',
    'hr': u'Bot: Interwiki za izabrane članke za [[%s:%s]]',
    'it': u'Bot: collegamento articolo in vetrina [[%s:%s]]',
    'ka': u'ბოტი: რჩეული სტატიის ბმული გვერდისათვის [[%s:%s]]',
    'lt': u'Bot: Pavyzdinis straipsnis [[%s:%s]]',
    'nl': u'Bot: Etalage-artikel link voor [[%s:%s]]',
    'no': u'bot: [[%s:%s]] er en utmerka artikkel',
    'pl': u'Bot: Link do artykułu wyróżnionego [[%s:%s]]',
    'pt': u'Bot: Ligando artigos destacados para [[%s:%s]]',
    'sr': u'Bot: Међувики за изабране чланке за [[%s:%s]]',
    'vo': u'Bot: Yüm yegeda gudik tefü [[%s:%s]]',
}

# default is en:Link FA
template = {
    'bg': u'Link FA',
    'br': u'Liamm PuB',
    'bs': u'Link FA',
    'ca': u'Enllaç AD',
    'da': u'Link FA',
    'de': u'Link FA',
    'en': u'Link FA',
    'eo': u'LigoElstara',
    'es': u'destacado',
    'fr': u'Lien AdQ',
    'he': u'Link FA',
    'hr': u'Link FA',
    'it': u'Link AdQ',
    'ka': u'Link FA',
    'lt': u'Link FA',
    'lv': u'Link FA',
    'nl': u'Link FA',
    'no': u'Link UA',
    'pl': u'Link FA',
    'pt': u'Link FA',
    'ru': u'Link FA',
    'sl': u'Link FA',
    'sr': u'Link FA',
    'sv': u'UA',
    'tr': u'Link FA',
    'vi': u'Liên kết chọn lọc',
    'vo': u'Yüm YG'
}

featured_name = {
    'am': (CAT, u"Category:Wikipedia:Featured_article"),
    'ast': (BACK, u"Plantilla:Destacaos"),
    'ar': (BACK, u"قالب:مقالات مختارة"),
    # az: Vikipediya:Fəal məzmun
    'be': (BACK, u"Шаблён:Выбраны артыкул"),
    'bg': (BACK, u"Шаблон:Избрана статия"),
    'bn': (BACK, u"Template:নির্বাচিত নিবন্ধ"),	
    'bs': (BACK, u"Šablon:Wiki članak"),
    'ca': (BACK, u"Plantilla:Article de qualitat"),
    'cs': (BACK, u"Šablona:Nejlepší článek"),
    'de': (BACK, u"Vorlage:Exzellent"),
    'el': (BACK, u"Πρότυπο:ΕπιλεγμένοΆρθρο"),
    'eo': (BACK, u"Ŝablono:Elstara"),
    'en': (CAT, u"Category:Wikipedia featured articles"),
    'es': (CAT, u"Categoría:Wikipedia:Artículos destacados"),
    # et: Vikipeedia:Eeskujulikud artiklid    
    'fi': (BACK, u"Malline:Suositeltu"),
    'fr': (CAT, u"Catégorie:Article de qualité"),
    'he': (CAT, u"קטגוריה:ערכים מומלצים"),
    'hi': (BACK, u"Template:निर्वाचित लेख"),
    'hr': (BACK, u"Predložak:Izdvojeni članak"),
    'hu': (BACK, u"Sablon:Kiemelt"),
    'id': (BACK, u"Templat:Pilihan"),
    'is': (BACK, u"Snið:Úrvalsgrein"),
    'it': (CAT, u"Categoria:Voci in vetrina"),
    'ja': (BACK, u"Template:秀逸"),
    'ka': (BACK, u"თარგი:რჩეული"),
    'lt': (CAT, u"Kategorija:Vikipedijos pavyzdiniai straipsniai"),
    'lv': (CAT, u"Kategorija:Nedēļas raksti"),
    'ml': (BACK, u"Template:Featured"),
    'nl': (BACK, u"Sjabloon:Etalage"),
    'nn': (BACK, u"Mal:God artikkel"),
    'no': (CAT, u"Kategori:Utmerkede artikler"),
    'pl': (CAT, u"Kategoria:Artykuły na medal"),
    'pt': (CAT, u"Categoria:!Artigos destacados"),
    'ro': (CAT, u"Categorie:Articole de calitate"),
    'ru': (CAT, u"Категория:Википедия:Избранные статьи"),
    'sh': (CAT, u"Category:Izabrani članci"),
    'sk': (BACK, u"Šablóna:Perfektný článok"),
    'sl': (CAT, u"Category:Izbrani članki"),
    'sq': (BACK, u"Template:Perfekt"),
    'sr': (BACK, u"Шаблон:Изабрани"),
    'sv': (CAT, u"Kategori:Wikipedia:Utmärkta artiklar"),
    'ta': (BACK, u"வார்ப்புரு:சிறப்பு"),
    'tl': (BACK, u"Template:Napiling artikulo"),
    'uk': (CAT, u"Категорія:Вибрані статті"),
    'vi': (CAT, u"Thể loại:Bài viết chọn lọc"),
    'vo': (CAT, u"Klad:Yegeds gudik"),
    'zh': (CAT, u"Category:特色条目"),
    'zh-yue': (BACK, u"Template:正文"),
    'zh-classical': (BACK, u"Template:絕妙好文"),
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
    try:
        method=featured_name[site.lang][0]
    except KeyError, ex:
        print 'Error: language %s doesn\'t have feature category source.' % ex
        sys.exit()
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
    wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"% page.title())
    if page.isRedirectPage():
        page = page.getRedirectTarget()
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
        ourpage = ourpage.getRedirectTarget()
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
        backpage = backpage.getRedirectTarget()
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
    re_Link_FA=re.compile(ur"\{\{%s\|%s\}\}" % (findtemplate, fromsite.lang), re.IGNORECASE)
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
            a=a.getRedirectTarget()
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

                        # TODO: create commandline for this
                        ### Placing {{Link FA|xx}} right next to corresponding interwiki ###
                        text=(text[:m.end()]
                              + (u" {{%s|%s}}" % (findtemplate, fromsite.lang))
                              + text[m.end():])
                        ### Moving {{Link FA|xx}} to top of interwikis ###
                        # text=wikipedia.replaceCategoryLinks(text+(u"{{%s|%s}}"%(findtemplate, fromsite.lang)), atrans.categories())
                        
                        try:
                            atrans.put(text, comment)
                        except wikipedia.LockedPage:
                            wikipedia.output(u'Page %s is locked!' % atrans.title())

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
            try:
                if len(fromlang)==1 and fromlang[0].index("-")>=0:
                    ll1,ll2=fromlang[0]
                    if not ll1: ll1=""
                    if not ll2: ll2="zzzzzzz"
                    fromlang=[ll for ll in featured_name.keys() if ll>=ll1 and ll<=ll2]
            except:
                pass
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
