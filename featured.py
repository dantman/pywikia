#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This script understands various command-line arguments:

-interactive:     ask before changing each page

-nocache          doesn't include /cache/featured or /cache/good file
                  to remember if the article already was verified.

-fromlang:xx,yy   xx,yy,zz,.. are the languages to be verified.
-fromlang:ar--fi  Another possible with range the languages

-fromall          to verify all languages.

-after:zzzz       process pages after and including page zzzz

-top              use -top if you want to move all {{Link FA|lang}} to the top of
                  interwiki links. Default is placing {{Link FA|lang}} right next to
                  the corresponding interwiki link.
                  
-count            Only counts how many featured/good articles exist
                  on all wikis (given with the "-fromlang" argument) or
                  on several language(s) (when using the "-fromall" argument). 
                  Example: featured.py -fromlang:en,he -count
                  counts how many featured articles exist in the en and he wikipedias.

-good             use this script for good articles instead of featured articles.

usage: featured.py [-interactive] [-nocache] [-top] [-after:zzzz] [-fromlang:xx,yy--zz|-fromall]

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
    name = site.namespace(14) + ':' + name
    cat=catlib.Category(site, name)
    return cat.articles()

def BACK(site,name):
    name = site.namespace(10) + ':' + name
    p=wikipedia.Page(site, name)
    return [page for page in p.getReferences(follow_redirects = False)]

msg = {
    'als': u'Bötli: [[%s:%s]] isch en bsunders glungener Artikel',
    'ar': u'بوت: [[%s:%s]] هي مقالة مختارة',
    'bat-smg': u'robots: Pavīzdėnė straipsnė nūruoda [[%s:%s]]',
    'be-x-old': u'Робат: [[%s:%s]] — абраны артыкул',
    'bs': u'Bot: Interwiki za izabrane članke za [[%s:%s]]',
    'cs': u'Robot přidal nejlepší článek: [[%s:%s]]',
    'cy': u'Robot: Mae [[%s:%s]] yn erthygl ddethol',
    'de': u'Bot: [[%s:%s]] ist ein ausgezeichneter Artikel',
    'dsb': u'Bot: [[%s:%s]] jo wuběrny nastawk',
    'en': u'Bot: [[%s:%s]] is a featured article',
    'eo': u'roboto: [[%s:%s]] estas artikolo elstara',
    'es': u'Bot: Enlace a artículo destacado para: [[%s:%s]]',
    'fa': u' ربات: [[%s:%s]] یک مقاله برگزیده‌است',
    'fi': u'Botti: [[%s:%s]] on suositeltu artikkeli',
    'fr': u'Bot: Lien AdQ pour [[%s:%s]]',
    'he': u'בוט: קישור לערך מומלץ עבור [[%s:%s]]',
    'hr': u'Bot: Interwiki za izabrane članke za [[%s:%s]]',
    'hsb': u'Bot: [[%s:%s]] je wuběrny nastawk',
    'hu': u'Bot: a(z) [[%s:%s]] kiemelt szócikk',
    'ia': u'Robot: Ligamine verso articulo eminente [[%s:%s]]',
    'it': u'Bot: collegamento articolo in vetrina [[%s:%s]]',
    'ja': u'ロボットによる: 秀逸な項目へのリンク [[%s:%s]]',
    'ka': u'ბოტი: რჩეული სტატიის ბმული გვერდისათვის [[%s:%s]]',
    'ko': u'로봇: 알찬 글 [[%s:%s]] 를 가리키는 링크',#로봇이：?
    'ksh': u'bot: [[%s:%s]] ess_enen ußjezëijshneten Atikkel',
    'lb': u'Bot: Exzellenten Arikel Link op [[%s:%s]]',
    'lt': u'Bot: Pavyzdinis straipsnis [[%s:%s]]',
    'nl': u'Bot: verwijzing naar etalage-artikel voor [[%s:%s]]',
    'no': u'bot: [[%s:%s]] er en utmerka artikkel',
    'nn': u'bot: [[%s:%s]] er ein god artikkel',
    'mk': u'Бот: Интервики за избрани статии за [[%s:%s]]',
    'pl': u'Bot: Link do artykułu wyróżnionego [[%s:%s]]',
    'pt': u'Bot: Ligando artigos destacados para [[%s:%s]]',
    'ru': u'Робот: избранная статья [[%s:%s]]',
    'sk': u'Bot: [[%s:%s]] je najlepší článok',
    'sr': u'Bot: Међувики за изабране чланке за [[%s:%s]]',
    'sv': u'Bot: [[%s:%s]] är en utmärkt artikel',
    'th': u'บอต: ลิงก์บทความคัดสรร [[%s:%s]]',
    'tr': u'Bot değişikliği: [[%s:%s]] madde bağlantısı eklendi',
    'vo': u'Bot: Yüm yegeda gudik tefü [[%s:%s]]',
    'zh': u'機器人: 連結特色條目 [[%s:%s]]',
}

msg_good = {
    'als': u'Bötli: [[%s:%s]] isch en glungener Artikel',
    'ar': u'بوت: [[%s:%s]] هي مقالة جيدة',
    'cy': u'Robot: Mae [[%s:%s]] yn erthygl dda',
    'de': u'Bot: [[%s:%s]] ist ein lesenswerter Artikel',
    'en': u'Bot: [[%s:%s]] is a good article',
    'eo': u'roboto: [[%s:%s]] estas artikolo leginda',
    'es': u'Bot: Enlace a artículo bueno para: [[%s:%s]]',
    'fr': u'Bot: Lien BA pour [[%s:%s]]',
    'no': u'bot: [[%s:%s]] er en anbefalt artikkel',
    'nn': u'bot: [[%s:%s]] er ein god artikkel',
    'pl': u'Bot: Link do dobrego artykułu: [[%s:%s]]',
    'ru': u'Робот: хорошая статья [[%s:%s]]',
    'sv': u'Bot: [[%s:%s]] är en läsvärd artikel',
}
# ALL wikis use 'Link FA', and sometimes other localized templates.
# We use _default AND the localized ones
template = {
    '_default': ['Link FA'],
    'als': ['LinkFA'],
    'an': ['Destacato', 'Destacau'],
    'ar': [u'وصلة مقالة مختارة'],
    'ast':['Enllaz AD'],
    'az': ['Link FM'],
    'br': ['Liamm PuB', 'Lien AdQ'],
    'ca': [u'Enllaç AD', 'Destacat'],
    'cy': ['Cyswllt erthygl ddethol', 'Dolen ED'],
    'eo': ['LigoElstara'],
    'es': ['Destacado'],
    'eu': ['NA lotura'],
    'fr': ['Lien AdQ'],
    'fur':['Leam VdC'],
    'ga': ['Nasc AR'],
    'hi': ['Link FA', 'Lien AdQ'],
    'is': [u'Tengill ÚG'],
    'it': ['Link AdQ'],
    'no': ['Link UA'],
    'oc': ['Ligam AdQ', 'Lien AdQ'],
    'ro': [u'Legătură AF'],
    'sv': ['UA', 'Link UA'],
    'tr': ['Link SM'],
    'vi': [u'Liên kết chọn lọc'],
    'vo': [u'Yüm YG'],
    'yi': [u'רא'],
}

template_good = {
    '_default': ['Link GA'],
    'ar': [u'وصلة مقالة جيدة'],
    'da': ['Link GA', 'Link AA'],
    'eo': ['LigoLeginda'],
    'es': ['Bueno'],
    'fr': ['Lien BA'],
    'is': ['Tengill GG'],
    'nn': ['Link AA'],
    'no': ['Link AA'],
   #'tr': ['Link GA', 'Link KM'],
    'vi': [u'Liên kết bài chất lượng tốt'],
    'wo': ['Lien BA'],
}

featured_name = {
    'af': (BACK,u"Voorbladster"),
    'als':(CAT, u"Wikipedia:Bsunders glungener Artikel"),
    'am': (CAT, u"Wikipedia:Featured article"),
    'an': (CAT, u"Articlos destacatos"),
    'ar': (CAT, u"مقالات مختارة"),
    'ast':(CAT, u"Uiquipedia:Artículos destacaos"),
    'az': (BACK,u"Seçkin məqalə"),
    'bar':(CAT, u"Berig"),
    'bat-smg': (CAT, u"Vikipedėjės pavīzdėnē straipsnē"),
    'be-x-old':(CAT, u"Вікіпэдыя:Выбраныя артыкулы"),
    'bg': (CAT, u"Избрани статии"),
    'bn': (BACK,u"নির্বাচিত নিবন্ধ"),
    'br': (CAT, u"Pennadoù eus an dibab"),
    'bs': (CAT, u"Odabrani članci"),
    'ca': (CAT, u"Llista d'articles de qualitat"),
    'ceb':(CAT, u"Mga napiling artikulo"),
    'cs': (CAT, u"Nejlepší články"),
    'cy': (CAT, u"Erthyglau dethol"),
    'da': (CAT, u"Fremragende artikler"),
    'de': (CAT, u"Wikipedia:Exzellent"),
   #'dsb':(CAT, u"Ekscelentny"),
    'dv': (BACK, u"Featured article"),
   #'dv': (CAT, u"Featured Articles"),
    'el': (BACK,u"Αξιόλογο άρθρο"),
    'eo': (CAT, u"Elstaraj artikoloj"),
    'en': (CAT, u"Featured articles"),
    'es': (CAT, u"Wikipedia:Artículos destacados"),
    'et': (CAT, u"Eeskujulikud artiklid"),
    'eu': (CAT, u"Nabarmendutako artikuluak"),
    'ext':(BACK,u"Destacau"),
    'fa': (BACK,u"نوشتار برگزیده"),
    'fi': (CAT, u"Suositellut sivut"),
    'fo': (CAT, u"Mánaðargrein"),
    'fr': (CAT, u"Article de qualité"),
    'gv': (CAT, u"Artyn reiht"),
    'he': (CAT, u"ערכים מומלצים"),
    'hi': (BACK,u"निर्वाचित लेख"),
    'hr': (CAT, u"Izabrani članci"),
    'hsb':(CAT, u"Ekscelentny"),
    'hu': (CAT, u"Kiemelt cikkek"),
    'hy': (BACK,u"Ընտրված հոդված"),
    'ia': (CAT, u"Articulos eminente"),
    'id': (BACK, u"Featured article"),
   #'id': (CAT, u"Artikel bagus utama"),
    'is': (CAT, u"Wikipedia:Úrvalsgreinar"),
    'it': (CAT, u"Voci in vetrina"),
    'ja': (BACK,u"Featured article"),
    'ka': (CAT, u"რჩეული სტატიები"),
    'km': (BACK,u"អត្ថបទពិសេស"),
    'kn': (BACK,u"ವಿಶೇಷ ಲೇಖನ"),
    'ko': (CAT, u"알찬 글"),
    'ksh':(CAT, u"Exzälenter Aatikkel"),
    'la': (CAT, u"Paginae mensis"),
    'li': (CAT, u"Wikipedia:Sjterartikele"),
    'lmo':(CAT, u"Articol ben faa"),
    'lo': (CAT, u"ບົດຄວາມດີເດັ່ນ"),
    'lt': (CAT, u"Vikipedijos pavyzdiniai straipsniai"),
    'lv': (CAT, u"Vērtīgi raksti"),
   #'lv': (CAT, u"Nedēļas raksti"),
    'mk': (CAT, u"Избрани статии на главната страница"),
    'ml': (BACK,u"Featured"),
    'mr': (CAT, u"मुखपृष्ठ सदर लेख"),
    'ms': (BACK,u"Rencana pilihan"),
    'nah':(BACK,u"Featured article"),
    'nds-nl': (BACK, u"Etelazie"),
    'nl': (CAT, u"Wikipedia:Etalage-artikelen"),
    'nn': (BACK,u"God artikkel"),
    'no': (CAT, u"Utmerkede artikler"),
    'oc': (CAT, u"Article de qualitat"),
    'pl': (CAT, u"Artykuły na medal"),
    'pt': (CAT, u"!Artigos destacados"),
    'ro': (CAT, u"Articole de calitate"),
    'ru': (CAT, u"Википедия:Избранные статьи"),
    'sco':(CAT, u"Featurt"),
    'sh': (CAT, u"Izabrani članci"),
    'simple': (CAT, u"Very good articles"),
    'sk': (BACK,u"Perfektný článok"),
    'sl': (CAT, u"Vsi izbrani članki"),
    'sq': (BACK,u"Artikulli perfekt"),
    'sr': (CAT, u"Изабрани"),
    'sv': (CAT, u"Wikipedia:Utmärkta artiklar"),
    'sw': (BACK,u"Makala_nzuri_sana"),
    'szl':(CAT, u"Wyrůžńůne artikle"),
    'ta': (CAT, u"சிறப்புக் கட்டுரைகள்"),
    'te': (CAT, u"విశేషవ్యాసాలు"),
    'th': (BACK,u"บทความคัดสรร"),
    'tl': (BACK,u"Napiling artikulo"),
    'tr': (BACK,u"Seçkin madde"),
   #'tt': (CAT, u"Şäp mäqälä"),
    'uk': (CAT, u"Вибрані статті"),
    'ur': (CAT, u"منتخب مقالے"),
    'uz': (CAT, u"Vikipediya:Tanlangan maqolalar"),
    'vec':(BACK,u"Vetrina"),
    'vi': (CAT, u"Bài viết chọn lọc"),
    'vo': (CAT, u"Yegeds gudik"),
    'wa': (CAT, u"Raspepyî årtike"),
    'yi': (CAT, u"רעקאמענדירטע ארטיקלען"),
    'yo': (BACK,u"Ayoka pataki"),
    'zh': (CAT, u"特色条目"),
    'zh-classical': (CAT, u"卓著"),
    'zh-yue': (BACK, u"正文"),
}

good_name = {
    'ar': (CAT, u"مقالات جيدة"),
    'ca': (CAT, u"Llista d'articles bons"),
    'cs': (CAT, u"Wikipedie:Dobré články"),
    'da': (CAT, u"Gode artikler"),
    'de': (CAT, u"Wikipedia:Lesenswert"),
   #'dsb':(CAT, u"Naraźenje za pógódnośenje"),
    'en': (CAT, u"Wikipedia good articles"),
    'eo': (CAT, u"Legindaj artikoloj"),
    'es': (CAT, u"Wikipedia:Artículos buenos"),
    'et': (CAT, u"Head artiklid"),
    'fi': (CAT, u"Hyvät artikkelit"),
    'fr': (CAT, u"Bon article"),
    'hsb':(CAT, u"Namjet za pohódnoćenje"),
    'id': (BACK,u"Artikel bagus"),
   #'id': (CAT, u"Artikel bagus"),
    'is': (CAT, u"Wikipedia:Gæðagreinar"),
    'ja': (CAT, u"おすすめ記事"),
    'lt': (CAT, u"Vertingi straipsniai"),
    'lv': (CAT, u"Labi raksti"),
    'no': (CAT, u"Anbefalte artikler"),
    'oc': (CAT, u"Bon article"),
    'pl': (CAT, u"Dobre artykuły"),
    'ru': (CAT, u"Википедия:Хорошие статьи"),
    'simple': (CAT, u"Good articles"),
    'sr': (BACK,u"Иконица добар"),
    'sv': (CAT, u"Wikipedia:Läsvärda artiklar"),
    'tr': (BACK,u"Kaliteli madde"),
    'uk': (CAT, u"Вікіпедія:Добрі статті"),
    'uz': (CAT, u"Vikipediya:Yaxshi maqolalar"),
    'yi': (CAT, u"וויקיפעדיע גוטע ארטיקלען"),
    'zh': (CAT, u"優良條目"),
    'zh-classical': (CAT, u"正典"),
}

# globals
interactive=0
nocache=0
afterpage=u"!"
cache={}

def featuredArticles(site, good):
    arts=[]
    if good:
        feature = u'good'
    else:
        feature = u'feature'
    try:
        if good:
	    method=good_name[site.lang][0]
        else:
	    method=featured_name[site.lang][0]
    except KeyError:
        wikipedia.output(u'Error: language %s doesn\'t has %s category source.' % (site.lang, feature))
        return arts
    if good:
        name=good_name[site.lang][1]
    else:
        name=featured_name[site.lang][1]
    raw=method(site, name)
    for p in raw:
        if p.namespace()==0: # Article
            arts.append(p)
        elif p.namespace()==1 and site.lang <> 'el': # Article talk (like in English)
            arts.append(wikipedia.Page(p.site(), p.titleWithoutNamespace()))
    wikipedia.output('\03{lightred}** wikipedia:%s has %i %s articles\03{default}' % (site.lang, len(arts), feature))
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

def featuredWithInterwiki(fromsite, tosite, template_on_top, good):
    if not fromsite.lang in cache:
        cache[fromsite.lang]={}
    if not tosite.lang in cache[fromsite.lang]:
        cache[fromsite.lang][tosite.lang]={}
    cc=cache[fromsite.lang][tosite.lang]
    if nocache:
        cc={}
    if good:
        try:
            templatelist = template_good[tosite.lang]
            templatelist += template_good['_default']
        except KeyError:
            templatelist = template_good['_default']
    else:
        try:
            templatelist = template[tosite.lang]
            templatelist += template['_default']
        except KeyError:
            templatelist = template['_default']

    findtemplate = '(' + '|'.join(templatelist) + ')'
    re_Link_FA=re.compile(ur"\{\{%s\|%s\}\}" % (findtemplate.replace(u' ', u'[ _]'), fromsite.lang), re.IGNORECASE)
    re_this_iw=re.compile(ur"\[\[%s:[^]]+\]\]" % fromsite.lang)

    arts=featuredArticles(fromsite, good)

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
                        site = wikipedia.getSite()
                        if good:
                            comment = wikipedia.setAction(wikipedia.translate(site, msg_good) % (fromsite.lang, a.title()))
                        else:
                            comment = wikipedia.setAction(wikipedia.translate(site, msg) % (fromsite.lang, a.title()))

                        ### Moving {{Link FA|xx}} to top of interwikis ###
                        if template_on_top == True:
                            # Getting the interwiki
                            iw = wikipedia.getLanguageLinks(text, site)
                            # Removing the interwiki
                            text = wikipedia.removeLanguageLinks(text, site)
                            text += u"\r\n{{%s|%s}}\r\n"%(templatelist[0], fromsite.lang)
                            # Adding the interwiki
                            text = wikipedia.replaceLanguageLinks(text, iw, site)

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
    featuredcount = False
    fromlang=[]
    process_good = False
    all  = False
    part = False
    for arg in wikipedia.handleArgs():
        if arg == '-interactive':
            interactive=1
        elif arg == '-nocache':
            nocache=1
        elif arg.startswith('-fromlang:'):
            fromlang=arg[10:].split(",")
            part = True
        elif arg == '-fromall':
            all = True
        elif arg.startswith('-after:'):
            afterpage=arg[7:]
        elif arg == '-top':
            template_on_top = True
        elif arg == '-count':
            featuredcount = True
        elif arg == '-good':
            process_good = True

    if part:
        try:
            # BUG: range with zh-min-nan (3 "-")
            if len(fromlang)==1 and fromlang[0].index("-")>=0:
                ll1,ll2=fromlang[0].split("--",1)
                if not ll1: ll1=""
                if not ll2: ll2="zzzzzzz"
		if process_good:
                    fromlang=[ll for ll in good_name.keys() if ll>=ll1 and ll<=ll2]
                else:
                    fromlang=[ll for ll in featured_name.keys() if ll>=ll1 and ll<=ll2]
        except:
            pass
			
    if all:
	if process_good:
            fromlang=good_name.keys()
	else:
	    fromlang=featured_name.keys()
			
    if process_good:
        filename="cache/good"
    else:
        filename="cache/featured"
    try:
        cache=pickle.load(file(filename,"rb"))
    except:
        cache={}


    if not fromlang:
        wikipedia.showHelp('featured')
        sys.exit(1)

    fromlang.sort()
    try:
        for ll in fromlang:
            fromsite = wikipedia.getSite(ll)
            if featuredcount:
                featuredArticles(fromsite, process_good)
            elif  fromsite != wikipedia.getSite():
                featuredWithInterwiki(fromsite, wikipedia.getSite(),
                                      template_on_top, process_good)
    except KeyboardInterrupt:
        wikipedia.output('\nQuitting program...')
    finally:
        wikipedia.stopme()
        if not nocache:
            pickle.dump(cache,file(filename,"wb"))

