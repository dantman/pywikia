# -*- coding: utf-8 -*-
"""
Script to resolve double redirects, and to delete broken redirects. Requires
access to MediaWiki's maintenance pages or to a XML dump file. Delete
function requires adminship.

Syntax:

    python redirect.py action [-argument]

where action can be one of these:

double         Fix redirects which point to other redirects
broken         Delete redirects where targets don\'t exist. Requires adminship.

and argument can be:

-xml           Retrieve information from a local XML dump
               (http://download.wikimedia.org). Argument can also be given as
               "-xml:filename.xml". If this argument isn't given, info will be
               loaded from a special page of the live wiki.

-namespace:n   Namespace to process. Works only with an XML dump.

-offset:n      Number of redirect to restart with (see progress). Works only
               with an XML dump or with -moves.

-moves         Instead of using Special:Doubleredirects, use the page move
               log to find double-redirect candidates (only works with
               action "double", does not work with -xml)

-always        Don't prompt you for each replacement.

"""
#
# (C) Daniel Herding, 2004
#
# Distributed under the terms of the MIT license.
#
#
from __future__ import generators
import wikipedia, config
import xmlreader
import re, sys

__version__='$Id$'

# Summary message for fixing double redirects
msg_double={
    'en': u'Robot: Fixing double redirect',
    'ar': u'روبوت: تصليح تحويلة مزدوجة',
    'br': u'Kempennet adkas doubl gant robot',
    'de': u'Bot: Korrigiere doppelten Redirect',
    'es': u'Robot: Arreglando doble redirección',
    'fa': u'ربات:اصلاح تغییر مسیر دوتایی',
    'fr': u'Robot : répare double redirection',
    'he': u'בוט: מתקן הפניה כפולה',
    'hr': u'Bot: Popravak dvostrukih preusmjeravanja',
    'ia': u'Robot: reparation de duple redirection',
    'is': u'Vélmenni: Lagfæri tvöfalda tilvísun',
    'it': u'Bot: Sistemo i redirect doppi',
    'ja': u'ロボットによる: 二重リダイレクト修正',
    'ka': u'რობოტი: ორმაგი გადამისამართების გასწორება',
    'ko': u'로봇: 이중 넘겨주기 수정',
    'kk': u'Бот: Шынжырлы айдатуды түзетті',
    'ksh':u'Bot: Dubbel Ömlëijdong fottjemaat',
    'lt': u'robotas: Taisomas dvigubas peradresavimas',
    'nl': u'Robot: Dubbele doorverwijzing gecorrigeerd',
    'nn': u'robot: retta dobbel omdirigering',
    'no': u'bot: Retter dobbel omdirigering',
    'pl': u'Robot naprawia podwójne przekierowanie',
    'pt': u'Bot: Corrigido duplo redirecionamento',
    'ru': u'Робот: исправление двойного перенаправления',
    'sr': u'Бот: Поправка дуплих преусмерења',
    'sv': u'Robot: Rättar dubbel omdirigering',
    'th': u'โรบอต: แก้หน้าเปลี่ยนทางซ้ำซ้อน',
    'tr': u'Bot değişikliği: Yönlendirmeye olan yönlendirme',
    'uk': u'Робот: виправлення подвійного перенаправлення',
    'yi': u'באט: פארראכטן פארטאפלטע ווייטערפירונג',
    'zh': u'機器人:修正雙重重定向',
    'zh-yue': u'機械人：拉直連串跳轉 ',
    'zh-classical': u'僕:復修渡口',
}

# Reason for deleting broken redirects
reason_broken={
    'ar': u'روبوت: هدف التحويلة غير موجود',
    'en': u'Robot: Redirect target doesn\'t exist',
    'de': u'Bot: Weiterleitungsziel existiert nicht',
    'es': u'Robot: La página a la que redirige no existe',
    'fa': u'ربات:تغییرمسیر مقصد ندارد',
    'fr': u'Robot : Cible du redirect inexistante',
    'he': u'בוט: יעד ההפניה אינו קיים',
    'it': u'Bot: Il redirect indirizza ad una pagina inesistente',
    'ja': u'ロボットによる:リダイレクトの目標は存在しませんでした',
    'ka': u'რობოტი: გადამისამართებული გვერდი არ არსებობს',
    'ko': u'로봇: 끊긴 넘겨주기',
    'kk': u'Бот: Айдату нысанасы жоқ болды',
    'ksh':u'Bot: Dė Ömlëijdong jingk ennet Liiere',
    'lt': u'robotas: Peradresavimas į niekur',
    'nl': u'Robot: Doel doorverwijzing bestaat niet',
    'nn': u'robot: målet for omdirigeringa eksisterer ikkje',
    'no': u'robot: målet for omdirigeringen eksisterer ikke',
    'pl': u'Robot: cel przekierowania nie istnieje',
    'pt': u'Bot: Redirecionamento não existe',
    'ru': u'Робот: перенаправление в никуда',
    'sr': u'Бот: Преусмерење не постоји',
    'th': u'โรบอต: หน้าเปลี่ยนทางเสีย',
    'tr': u'Bot değişikliği: Var olmayan sayfaya olan yönlendirme',
    'zh': u'機器人:該重定向的目標不存在',
    'zh-yue': u'機械人：跳轉目標唔存在',
}

class RedirectGenerator:
    def __init__(self, xmlFilename=None, namespaces=[], offset=-1,
                 use_move_log=False):
        self.xmlFilename = xmlFilename
        self.namespaces = namespaces
        self.offset = offset
        self.use_move_log = use_move_log

    def get_redirects_from_dump(self, alsoGetPageTitles = False):
        '''
        Load a local XML dump file, look at all pages which have the
        redirect flag set, and find out where they're pointing at. Return
        a dictionary where the redirect names are the keys and the redirect
        targets are the values.
        '''
        xmlFilename = self.xmlFilename
        redict = {}
        # open xml dump and read page titles out of it
        dump = xmlreader.XmlDump(xmlFilename)
        site = wikipedia.getSite()
        redirR = site.redirectRegex()
        readPagesCount = 0
        if alsoGetPageTitles:
            pageTitles = set()
        for entry in dump.parse():
            readPagesCount += 1
            # always print status message after 10000 pages
            if readPagesCount % 10000 == 0:
                wikipedia.output(u'%i pages read...' % readPagesCount)
            if len(self.namespaces) > 0:
                if wikipedia.Page(site, entry.title).namespace() \
                        not in self.namespaces:
                    continue
            if alsoGetPageTitles:
                pageTitles.add(entry.title.replace(' ', '_'))

            m = redirR.match(entry.text)
            if m:
                target = m.group(1)
                # There might be redirects to another wiki. Ignore these.
                for code in site.family.langs.keys():
                    if target.startswith('%s:' % code) \
                            or target.startswith(':%s:' % code):
                        if code == site.language():
                        # link to our wiki, but with the lang prefix
                            target = target[(len(code)+1):]
                            if target.startswith(':'):
                                target = target[1:]
                        else:
                            wikipedia.output(
                                u'NOTE: Ignoring %s which is a redirect to %s:'
                                % (entry.title, code))
                            target = None
                            break
                # if the redirect does not link to another wiki
                if target:
                    source = entry.title.replace(' ', '_')
                    target = target.replace(' ', '_')
                    # remove leading and trailing whitespace
                    target = target.strip('_')
                    # capitalize the first letter
                    if not wikipedia.getSite().nocapitalize:
                        source = source[:1].upper() + source[1:]
                        target = target[:1].upper() + target[1:]
                    if '#' in target:
                        target = target[:target.index('#')].rstrip("_")
                    if '|' in target:
                        wikipedia.output(
                            u'HINT: %s is a redirect with a pipelink.'
                            % entry.title)
                        target = target[:target.index('|')].rstrip("_")
                    if target: # in case preceding steps left nothing
                        redict[source] = target
        if alsoGetPageTitles:
            return redict, pageTitles
        else:
            return redict

    def retrieve_broken_redirects(self):
        if self.xmlFilename == None:
            # retrieve information from the live wiki's maintenance page
            mysite = wikipedia.getSite()
            # broken redirect maintenance page's URL
            path = mysite.broken_redirects_address(default_limit = False)
            wikipedia.output(u'Retrieving special page...')
            maintenance_txt = mysite.getUrl(path)

            # regular expression which finds redirects which point to a
            # non-existing page inside the HTML
            Rredir = re.compile('\<li\>\<a href=".+?" title="(.*?)"')

            redir_names = Rredir.findall(maintenance_txt)
            wikipedia.output(u'Retrieved %d redirects from special page.\n'
                             % len(redir_names))
            for redir_name in redir_names:
                yield redir_name
        else:
            # retrieve information from XML dump
            wikipedia.output(
                u'Getting a list of all redirects and of all page titles...')
            redirs, pageTitles = self.get_redirects_from_dump(
                                            alsoGetPageTitles=True)
            for (key, value) in redirs.iteritems():
                if value not in pageTitles:
                    yield key

    def retrieve_double_redirects(self):
        if self.xmlFilename == None:
            if self.use_move_log:
                for redir_page in self.get_moved_pages_redirects():
                    yield redir_page.title()
                return
            mysite = wikipedia.getSite()
            # retrieve information from the live wiki's maintenance page
            # double redirect maintenance page's URL
            wikipedia.config.special_page_limit = 1000
            path = mysite.double_redirects_address(default_limit = False)
            wikipedia.output(u'Retrieving special page...')
            maintenance_txt = mysite.getUrl(path)

            # regular expression which finds redirects which point to
            # another redirect inside the HTML
            Rredir = re.compile('\<li\>\<a href=".+?" title="(.*?)">')
            redir_names = Rredir.findall(maintenance_txt)
            wikipedia.output(u'Retrieved %i redirects from special page.\n'
                             % len(redir_names))
            for redir_name in redir_names:
                yield redir_name
        else:
            redict = self.get_redirects_from_dump()
            num = 0
            for (key, value) in redict.iteritems():
                num += 1
                # check if the value - that is, the redirect target - is a
                # redirect as well
                if num > self.offset and redict.has_key(value):
                    yield key
                    wikipedia.output(u'\nChecking redirect %i of %i...'
                                     % (num + 1, len(redict)))

    # /wiki/
    wiki = re.escape(wikipedia.getSite().nice_get_address(''))
    # /w/index.php
    index = re.escape(wikipedia.getSite().path())
    move_regex = re.compile(
        r'<li>.*?<a href="' + wiki + r'User:.*?>.*?</a> '
        r'\(<a href="' + wiki + r'User_talk:.*?>Talk</a> \| '
        r'<a href="' + wiki + r'Special:Contributions/.*?>contribs</a>\) '
        r'moved <a href="' + index + r'?title=.*?>(.*?)</a> to '
        r'<a href="' + index + r'.*?>.*?</a>.*?</li>' )

    def get_moved_pages_redirects(self):
        '''generate redirects to recently-moved pages'''
        # this will run forever, until user interrupts it
        import datetime

        offsetpattern = re.compile(
r"""\(<a href="/w/index\.php\?title=Special:Log&amp;offset=(\d+)&amp;limit=500&amp;type=move" title="Special:Log" rel="next">older 500</a>\)""")
        start = datetime.datetime.utcnow() - datetime.timedelta(0, 3600)
        # one hour ago
        offset = start.strftime("%Y%m%d%H%M%S")
        site = wikipedia.getSite()
        while True:
            move_url = \
                site.path() + "?title=Special:Log&limit=500&offset=%s&type=move"\
                       % offset
            try:
                move_list = site.getUrl(move_url)
#                wikipedia.output(u"[%s]" % offset)
            except:
                import traceback
                traceback.print_exc()
                return
            for moved_page in self.move_regex.findall(move_list):
                # moved_page is now a redirect, so any redirects pointing
                # to it need to be changed
                try:
                    for page in wikipedia.Page(site, moved_page
                                ).getReferences(follow_redirects=True,
                                                redirectsOnly=True):
                        yield page
                except wikipedia.NoPage:
                    # original title must have been deleted after move
                    continue
            m = offsetpattern.search(move_list)
            if not m:
                break
            offset = m.group(1)


class RedirectRobot:
    def __init__(self, action, generator, always=False):
        self.action = action
        self.generator = generator
        self.always = always

    def prompt(self, question):
        if not self.always:
            choice = wikipedia.inputChoice(question, ['Yes', 'No', 'All'],
                                           ['y', 'N', 'a'], 'N')
            if choice == 'n':
                return False
            elif choice == 'a':
                self.always = True
        return True

    def delete_broken_redirects(self):
        # get reason for deletion text
        reason = wikipedia.translate(wikipedia.getSite(), reason_broken)

        for redir_name in self.generator.retrieve_broken_redirects():
            redir_page = wikipedia.Page(wikipedia.getSite(), redir_name)
            # Show the title of the page we're working on.
            # Highlight the title in purple.
            wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                             % redir_page.title())
            try:
                targetPage = redir_page.getRedirectTarget()
            except wikipedia.IsNotRedirectPage:
                wikipedia.output(u'%s is not a redirect.' % redir_page.title())
            except wikipedia.NoPage:
                wikipedia.output(u'%s doesn\'t exist.' % redir_page.title())
            else:
                try:
                    targetPage.get()
                except wikipedia.NoPage:
                    if self.prompt(u'Redirect target %s does not exist. Do you want to delete %s?'
                                   % (targetPage.aslink(), redir_page.aslink())):
                        redir_page.delete(reason, prompt = False)
                except wikipedia.IsRedirectPage:
                    wikipedia.output(
            u'Redirect target %s is also a redirect! Won\'t delete anything.' % targetPage.aslink())
                else:
                    #we successfully get the target page, meaning that
                    #it exists and is not a redirect: no reason to touch it.
                    wikipedia.output(
            u'Redirect target %s does exist! Won\'t delete anything.' % targetPage.aslink())
                # idle for 1 minute
            wikipedia.output(u'')
            wikipedia.put_throttle()

    def fix_double_redirects(self):
        mysite = wikipedia.getSite()
        for redir_name in self.generator.retrieve_double_redirects():
            redir = wikipedia.Page(mysite, redir_name)
            # Show the title of the page we're working on.
            # Highlight the title in purple.
            wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                             % redir.title())
            newRedir = redir
            redirList = []  # bookkeeping to detect loops
            while True:
                redirList.append(u'%s:%s' % (newRedir.site().lang,
                                             newRedir.sectionFreeTitle()))
                try:
                    targetPage = newRedir.getRedirectTarget()
                except wikipedia.IsNotRedirectPage:
                    if len(redirList) == 1:
                        wikipedia.output(u'Skipping: Page %s is not a redirect.'
                                         % redir.aslink())
                        break  #do nothing
                    elif len(redirList) == 2:
                        wikipedia.output(
                            u'Skipping: Redirect target %s is not a redirect.'
                            % newRedir.aslink())
                        break  # do nothing
                except wikipedia.SectionError:
                    wikipedia.output(
                        u'Warning: Redirect target section %s doesn\'t exist.'
                          % newRedir.aslink())
                except wikipedia.BadTitle, e:
                    # str(e) is in the format 'BadTitle: [[Foo]]'
                    wikipedia.output(
                        u'Warning: Redirect target %s is not a valid page title.'
                          % str(e)[10:])
                except wikipedia.NoPage:
                    if len(redirList) == 1:
                        wikipedia.output(u'Skipping: Page %s does not exist.'
                                            % redir.aslink())
                        break
                    else:
                        wikipedia.output(
                            u"Warning: Redirect target %s doesn't exist."
                            % newRedir.aslink())
                else:
                    wikipedia.output(
                        u'   Links to: %s.'
                          % targetPage.aslink())
                    if targetPage.site() != mysite:
                        wikipedia.output(
                        u'Warning: redirect target (%s) is on a different site.'
                             % (targetPage.aslink()))
                        if self.always:
                            break  # skip if automatic 
                    # watch out for redirect loops
                    if redirList.count(u'%s:%s' 
                                       % (targetPage.site().lang,
                                          targetPage.sectionFreeTitle())
                                      ) > 0:
                        wikipedia.output(
                           u'Warning: Redirect target %s forms a redirect loop.'
                              % targetPage.aslink())

                        content=targetPage.get(get_redirect=True)
                        if wikipedia.Page(wikipedia.getSite(), u"Template:Db-r1").exists():
                            wikipedia.output(u"Tagging redirect for deletion")
                            # Delete the two redirects
                            targetPage.put("{{db-r1}}\n"+content, "Tagging for speedy deletion")
                            redir.put("{{db-r1}}\n"+content, "Tagging for speedy deletion")
                        else:
                            break # TODO Better implement loop redirect
                    else:
                        newRedir = targetPage
                        continue #
                oldText = redir.get(get_redirect=True)
                text = mysite.redirectRegex().sub(
                        '#%s %s' %
                            (mysite.redirect( True ),
                              targetPage.aslink()),
                              oldText)
                if text == oldText:
                    break
                wikipedia.showDiff(oldText, text)
                if self.prompt(u'Do you want to accept the changes?'):
                    try:
                        redir.put(text)
                    except wikipedia.LockedPage:
                        wikipedia.output(u'%s is locked.' % redir.title())
                    except wikipedia.SpamfilterError, error:
                        wikipedia.output(
u"Saving page [[%s]] prevented by spam filter: %s"
                                % (redir.title(), error.url))
                    except wikipedia.PageNotSaved, error:
                        wikipedia.output(u"Saving page [[%s]] failed: %s"
                            % (redir.title(), error))
                    except wikipedia.NoUsername:
                        wikipedia.output(
u"Page [[%s]] not saved; sysop privileges required."
                                % redir.title())
                    except wikipedia.Error, error:
                        wikipedia.output(
u"Unexpected error occurred trying to save [[%s]]: %s"
                                % (redir.title(), error))
                break

    def run(self):
        if self.action == 'double':
            # get summary text
            wikipedia.setAction(
                wikipedia.translate(wikipedia.getSite(), msg_double))
            self.fix_double_redirects()
        elif self.action == 'broken':
            self.delete_broken_redirects()

def main():
    # read command line parameters
    # what the bot should do (either resolve double redirs, or delete broken
    # redirs)
    action = None
    # where the bot should get his infos from (either None to load the
    # maintenance special page from the live wiki, or the filename of a
    # local XML dump file)
    xmlFilename = None
    # Which namespace should be processed when using a XML dump
    # default to -1 which means all namespaces will be processed
    namespaces = []
    # at which redirect shall we start searching double redirects again
    # (only with dump); default to -1 which means all redirects are checked
    offset = -1
    moved_pages = False
    always = False
    for arg in wikipedia.handleArgs():
        if arg == 'double':
            action = 'double'
        elif arg == 'broken':
            action = 'broken'
        elif arg.startswith('-xml'):
            if len(arg) == 4:
                xmlFilename = wikipedia.input(
                                u'Please enter the XML dump\'s filename: ')
            else:
                xmlFilename = arg[5:]
        elif arg.startswith('-moves'):
            moved_pages = True
        elif arg.startswith('-namespace:'):
            try:
                namespaces.append(int(arg[11:]))
            except ValueError:
                namespaces.append(arg[11:])
        elif arg.startswith('-offset:'):
            offset = int(arg[8:])
        elif arg == '-always':
            always = True
        else:
            wikipedia.output(u'Unknown argument: %s' % arg)

    if not action:
        wikipedia.showHelp('redirect')
    else:
        gen = RedirectGenerator(xmlFilename, namespaces, offset, moved_pages)
        bot = RedirectRobot(action, gen, always)
        bot.run()

if __name__ == '__main__':
    try:
        main()
    finally:
        wikipedia.stopme()

