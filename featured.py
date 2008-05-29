#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This script understands various command-line arguments:

* -interactive       : ask before changing page

* -nocache           : doesn't include /featured/cache file to remembers if the
                       article already was verified.

* -fromlang:xx[,yy[,...]]] : xx,.. are the languages to be verified. Another
                             possible with range the languages -fromlang:ar--fi

* -fromall           : to verify all languages.

* -after:zzzz        : process pages after and including page zzzz

* -top               : using -top if you want moving {{Link FA|lang}} to top of interwiki.
                       DEFAULT: placing {{Link FA|lang}} right next to corresponding interwiki.

usage: featured.py [-interactive] [-nocache] [-top] [-after:zzzz] [-fromlang:xx,yy,zz|-fromall]

"""
__version__ = '$Id$'

#
# (C) Maxim Razin, 2005
# (C) Leonardo Gregianin, 2006-2007
#
# Distributed under the terms of the MIT license.
#

import sys, re, pickle, os.path
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
    'ar': u'بوت: وصلة مقالة مختارة ل[[%s:%s]]',
    'bs': u'Bot: Interwiki za izabrane članke za [[%s:%s]]',
    'en': u'Bot: Featured article link for [[%s:%s]]',
    'cs': u'Bot: Nejlepší článek:  [[%s:%s]]',
    'fi': u'Bot: Suositeltu artikkeli -tähti: [[%s:%s]]',
    'fr': u'Bot: Lien AdQ pour [[%s:%s]]',
    'he': u'בוט: קישור לערך מומלץ עבור [[%s:%s]]',
    'hr': u'Bot: Interwiki za izabrane članke za [[%s:%s]]',
    'it': u'Bot: collegamento articolo in vetrina [[%s:%s]]',
    'ja': u'ロボットによる: 秀逸な項目へのリンク [[%s:%s]]',
    'ka': u'ბოტი: რჩეული სტატიის ბმული გვერდისათვის [[%s:%s]]',
    'ko': u'로봇：알찬 글 [[%s:%s]] 를 가리키는 링크',
    'lt': u'Bot: Pavyzdinis straipsnis [[%s:%s]]',
    'nl': u'Bot: Etalage-artikel link voor [[%s:%s]]',
    'no': u'bot: [[%s:%s]] er en utmerka artikkel',
    'nn': u'bot: [[%s:%s]] er ein god artikkel',
    'pl': u'Bot: Link do artykułu wyróżnionego [[%s:%s]]',
    'pt': u'Bot: Ligando artigos destacados para [[%s:%s]]',
    'ru': u'Робот: исправление двойных перенаправлений',
    'sr': u'Bot: Међувики за изабране чланке за [[%s:%s]]',
    'sv': u'Bot: [[%s:%s]] är en utmärkt artikel',
    'th': u'บอต: ลิงก์บทความคัดสรร [[%s:%s]]',
    'vo': u'Bot: Yüm yegeda gudik tefü [[%s:%s]]',
    'zh': u'機器人: 連結特色條目 [[%s:%s]]',
}

template = {
    'af': ['Link FA'],
    'ar': [u'وصلة مقالة مختارة', 'Link FA'],
    'bg': ['Link FA'],
    'br': ['Liamm PuB'],
    'bs': ['Link FA'],
    'ca': [u'Enllaç AD'],
    'da': ['Link FA'],
    'de': ['Link FA'],
    'en': ['Link FA'],
    'eo': ['LigoElstara'],
    'es': ['destacado'],
    'fr': ['Lien AdQ', 'Link FA'],
    'he': ['Link FA'],
    'hr': ['Link FA'],
    'ia': ['Link FA'],
    'io': ['Link FA'],
    'it': ['Link AdQ'],
    'ja': ['Link FA'],
    'ka': ['Link FA'],
    'ko': ['Link FA'],
    'lt': ['Link FA'],
    'lv': ['Link FA'],
    'nl': ['Link FA'],
    'no': ['Link UA'],
    'nn': ['Link FA'],
    'pl': ['Link FA'],
    'pt': ['Link FA'],
    'ru': ['Link FA'],
    'sl': ['Link FA'],
    'sr': ['Link FA'],
    'sv': ['UA'],
    'th': ['Link FA'],
    'tr': ['Link FA'],
    'vi': [u'Liên kết chọn lọc'],
    'vo': [u'Yüm YG'],
    'zh': ['Link FA'],
    'zh-classical': ['Link FA'],
    'zh-yue': ['Link FA'],
    'zh-min-nan': ['Link FA'],
}

featured_name = {
    'af': (BACK, u"Sjabloon:Voorbladartikel"),
    'am': (CAT, u"Category:Wikipedia:Featured_article"),
    'ast': (BACK, u"Plantilla:Destacaos"),
    'ar': (CAT, u"تصنيف:مقالات مختارة"),
    # az: Vikipediya:Fəal məzmun
    #'be': (BACK, u"Шаблён:Выбраны артыкул"),
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
    'ko': (CAT, u"분류:알찬 글 문서"),
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
    'simple': (BACK, u"template:vgood-large"),
    'sk': (BACK, u"Šablóna:Perfektný článok"),
    'sl': (CAT, u"Category:Izbrani članki"),
    'sq': (BACK, u"Template:Perfekt"),
    'sr': (BACK, u"Шаблон:Изабрани"),
    'sv': (CAT, u"Kategori:Wikipedia:Utmärkta artiklar"),
    'ta': (BACK, u"வார்ப்புரு:சிறப்பு"),
    'th': (CAT,u"หมวดหมู่:บทความคัดสรร"),
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
    wikipedia.output('\03{lightred}** wikipedia:%s has %i featured articles\03{default}' % (site.lang, len(arts)))
    return arts

def findTranslated(page, oursite=None):
    if not oursite:
        oursite=wikipedia.getSite()
    if page.isRedirectPage():
        page = page.getRedirectTarget()
    try:
        iw=page.interwiki()
    except:
        wikipedia.output(u"%s -> no interwiki, giving up" % page.title())
        return None
    ourpage=None
    for p in iw:
        if p.site()==oursite:
            ourpage=p
            break
    if not ourpage:
        wikipedia.output(u"%s -> no corresponding page in %s" % (page.title(), oursite))
        return None
    if not ourpage.exists():
        wikipedia.output(u"%s -> our page doesn't exist: %s" % (page.title(), ourpage.title()))
        return None
    if ourpage.isRedirectPage():
        ourpage = ourpage.getRedirectTarget()
    wikipedia.output(u"%s -> corresponding page is %s" % (page.title(), ourpage.title()))
    if ourpage.namespace() != 0:
        wikipedia.output(u"%s -> not in the main namespace, skipping" % page.title())
        return None
    if ourpage.isRedirectPage():
        wikipedia.output(u"%s -> double redirect, skipping" % page.title())
        return None
	if not ourpage.exists():
	    wikipedia.output(u"%s -> page doesn't exist, skipping" % ourpage.title())
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
        wikipedia.output(u"%s -> no back interwiki ref" % page.title())
        return None
    if backpage==page:
        # everything is ok
        return ourpage
    if backpage.isRedirectPage():
        backpage = backpage.getRedirectTarget()
    if backpage==page:
        # everything is ok
        return ourpage
    wikipedia.output(u"%s -> back interwiki ref target is %s" % (page.title(), backpage.title()))
    return None

def featuredWithInterwiki(fromsite, tosite, template_on_top):
    if not fromsite.lang in cache:
        cache[fromsite.lang]={}
    if not tosite.lang in cache[fromsite.lang]:
        cache[fromsite.lang][tosite.lang]={}
    cc=cache[fromsite.lang][tosite.lang]
    if nocache:
        cc={}

    templatelist = wikipedia.translate(wikipedia.getSite(), template)
    findtemplate = '(' + '|'.join(templatelist) + ')'
    re_Link_FA=re.compile(ur"\{\{%s\|%s\}\}" % (findtemplate.replace(u' ', u'[ _]'), fromsite.lang), re.IGNORECASE)
    re_this_iw=re.compile(ur"\[\[%s:[^]]+\]\]" % fromsite.lang)

    arts=featuredArticles(fromsite)

    pairs=[]
    for a in arts:
        if a.title()<afterpage:
            continue
        if u"/" in a.title() and a.namespace() != 0:
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

                        ### Moving {{Link FA|xx}} to top of interwikis ###  
                        if template_on_top == True:
                            text=wikipedia.replaceCategoryLinks(text+(u"{{%s|%s}}"%(templatelist[0], fromsite.lang)), atrans.categories())

                        ### Placing {{Link FA|xx}} right next to corresponding interwiki ###
                        else:
                            text=(text[:m.end()]
                                  + (u" {{%s|%s}}" % (templatelist[0], fromsite.lang))
                                  + text[m.end():])

                        try:
                            atrans.put(text, comment)
                        except wikipedia.LockedPage:
                            wikipedia.output(u'Page %s is locked!' % atrans.title())

                cc[a.title()]=atrans.title()
        except wikipedia.PageNotSaved, e:
            wikipedia.output(u"Page not saved")

if __name__=="__main__":
    template_on_top = False
    fromlang=[]
    for arg in wikipedia.handleArgs():
        if arg == '-interactive':
            interactive=1
        elif arg == '-nocache':
            nocache=1
        elif arg.startswith('-fromlang:'):
            fromlang=arg[10:].split(",")
            try:
                # BUG: range with zh-min-nan (3 "-")
                if len(fromlang)==1 and fromlang[0].index("-")>=0:
                    ll1,ll2=fromlang[0].split("--",1)
                    if not ll1: ll1=""
                    if not ll2: ll2="zzzzzzz"
                    fromlang=[ll for ll in featured_name.keys() if ll>=ll1 and ll<=ll2]
            except:
                pass
        elif arg == '-fromall':
            fromlang=featured_name.keys()
        elif arg.startswith('-after:'):
            afterpage=arg[7:]
        elif arg == '-top':
            template_on_top = True
        
    if not fromlang:
        wikipedia.showHelp('featured')
        sys.exit(1)

    fromlang.sort()
    try:
        for ll in fromlang:
            fromsite = wikipedia.getSite(ll)
            if  fromsite != wikipedia.getSite():
                featuredWithInterwiki(fromsite, wikipedia.getSite(),
                                      template_on_top)
    finally:
        wikipedia.stopme()
        if not nocache:
            pickle.dump(cache,file("featured/cache","wb"))
                
