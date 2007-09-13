# -*- coding: utf-8 -*-
"""
Script to resolve double redirects, and to delete broken redirects.
Requires access to MediaWiki's maintenance pages or to a XML dump file. Delete function requires
adminship.

Syntax:

    python redirect.py action [-argument]

where action can be one of these:

* double - fix redirects which point to other redirects
* broken - delete redirects where targets don\'t exist. Requires adminship.

and argument can be:

* xml         - retrieve information from a local XML dump
                (http://download.wikimedia.org). Argument can also be given as
                "-xml:filename.xml". If this argument isn't given, info will be
                loaded from a special page of the live wiki.

* namespace:n - Namespace to process. Works only with an XML dump. Currently not
                supported!
* restart:n   - Number of redirect to restart with (see progress). Works only
                with an XML dump. Currently not supported!

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
    'en':u'Robot: Fixing double redirect',
    'ar':u'روبوت: تصليح تحويلة مزدوجة',
    'br':u'Kempennet adkas doubl gant robot',
    'de':u'Bot: Korrigiere doppelten Redirect',
    'fr':u'Robot : répare double redirection',
    'he':u'רובוט: מתקן הפניה כפולה',
    'hr':u'Bot: Popravak dvostrukih preusmjeravanja',
    'ia':u'Robot: reparation de duple redirection',
    'is':u'Vélmenni: Lagfæri tvöfalda tilvísun',
    'ka':u'რობოტი: ორმაგი გადამისამართების გასწორება',
    'kk':u'Бот: Шынжырлы айдатуды түзетті',
    'ksh':u'Bot: Dubbel Ömlëijdong fottjemaat',
    'lt':u'robotas: Taisomas dvigubas peradresavimas',
    'nl':u'Robot: Dubbele doorverwijzing gecorrigeerd',
    'no':u'bot: Retter dobbel omdirigering',
    'pl':u'Robot naprawia podwójne przekierowanie',
    'pt':u'Bot: Corrigido duplo redirecionamento',
    'ru':u'Робот: исправление двойного перенаправления',
    'sr':u'Бот: Поправка дуплих преусмерења',
    'tr':u'Bot değişikliği: Yönlendirmeye olan yönlendirme',
    }

# Reason for deleting broken redirects
reason_broken={
    'en':u'Robot: Redirect target doesn\'t exist',
    'de':u'Bot: Weiterleitungsziel existiert nicht',
    'fr':u'Robot : Cible du redirect inexistante',
    'he':u'רובוט: יעד ההפניה אינו קיים',
    'ia':u'Robot: Scopo del redirection non existe',
    'ka':u'რობოტი: გადამისამართებული გვერდი არ არსებობს',
    'kk':u'Бот: Айдату нысанасы жоқ болды',
    'ksh':u'Bot: Dė Ömlëijdong jingk ennet Liiere',
    'lt':u'robotas: Peradresavimas į niekur',
    'nl':u'Robot: Doel doorverwijzing bestaat niet',
    'pl':u'Robot: cel przekierowania nie istnieje',
    'pt':u'Bot: Redirecionamento não existe',
    'ru':u'Робот: перенаправление в никуда',
    'sr':u'Бот: Преусмерење не постоји',
    'tr':u'Bot değişikliği: Var olmayan sayfaya olan yönlendirme',
    }

class RedirectGenerator:
    def __init__(self, xmlFilename = None, namespace = -1, restart = -1):
        self.xmlFilename = xmlFilename
        self.namespace = namespace
        self.restart = restart

    def get_redirects_from_dump(self, alsoGetPageTitles = False):
        '''
        Loads a local XML dump file, looks at all pages which have the redirect flag
        set, and finds out where they're pointing at.
        Returns a dictionary where the redirect names are the keys and the redirect
        targets are the values.
        '''
        xmlFilename = self.xmlFilename
        dict = {}
        # open xml dump and read page titles out of it
        dump = xmlreader.XmlDump(xmlFilename)
        redirR = wikipedia.getSite().redirectRegex()
        readPagesCount = 0
        if alsoGetPageTitles:
            pageTitles = set()
        for entry in dump.parse():
            readPagesCount += 1
            # always print status message after 10000 pages
            if readPagesCount % 10000 == 0:
                wikipedia.output(u'%i pages read...' % readPagesCount)
            # if self.namespace != -1 and self.namespace != entry.namespace:
                # continue
            if alsoGetPageTitles:
                pageTitles.add(entry.title)

            m = redirR.match(entry.text)
            if m:
                target = m.group(1)
                # There might be redirects to another wiki. Ignore these.
                for code in wikipedia.getSite().family.langs.keys():
                    if target.startswith('%s:' % code) or target.startswith(':%s:' % code):
                        wikipedia.output(u'NOTE: Ignoring %s which is a redirect to %s:' % (entry.title, code))
                        target = None
                        break
                # if the redirect does not link to another wiki
                if target:
                    target = target.replace(' ', '_')
                    # remove leading and trailing whitespace
                    target = target.strip()
                    # capitalize the first letter
                    if not wikipedia.getSite().nocapitalize:
                        target = target[0].upper() + target[1:]
                    if '#' in target:
                        target = target[:target.index('#')]
                    if '|' in target:
                        wikipedia.output(u'HINT: %s is a redirect with a pipelink.' % entry.title)
                        target = target[:target.index('|')]
                    dict[entry.title] = target
        if alsoGetPageTitles:
            return dict, pageTitles
        else:
            return dict

    def retrieve_broken_redirects(self):
        if self.xmlFilename == None:
            # retrieve information from the live wiki's maintenance page
            mysite = wikipedia.getSite()
            # broken redirect maintenance page's URL
            path = mysite.broken_redirects_address(default_limit = False)
            print 'Retrieving special page...'
            maintenance_txt = mysite.getUrl(path)

            # regular expression which finds redirects which point to a non-existing page inside the HTML
            Rredir = re.compile('\<li\>\<a href=".+?" title="(.*?)"')

            redir_names = Rredir.findall(maintenance_txt)
            wikipedia.output(u'Retrieved %d redirects from special page.\n' % len(redir_names))
            for redir_name in redir_names:
                yield redir_name
        else:
            # retrieve information from XML dump
            wikipedia.output(u'Getting a list of all redirects and of all page titles...')
            redirs, pageTitles = self.get_redirects_from_dump(alsoGetPageTitles = True)
            for (key, value) in redirs.iteritems():
                if not pagetitles.has_key(value):
                    yield key

    def retrieve_double_redirects(self):
        if self.xmlFilename == None:
            mysite = wikipedia.getSite()
            # retrieve information from the live wiki's maintenance page
            # double redirect maintenance page's URL
            path = mysite.double_redirects_address(default_limit = False)
            wikipedia.output(u'Retrieving special page...')
            maintenance_txt = mysite.getUrl(path)

            # regular expression which finds redirects which point to another redirect inside the HTML
            Rredir = re.compile('\<li\>\<a href=".+?" title="(.*?)">')
            redir_names = Rredir.findall(maintenance_txt)
            wikipedia.output(u'Retrieved %i redirects from special page.\n' % len(redir_names))
            for redir_name in redir_names:
                yield redir_name
        else:
            dict = self.get_redirects_from_dump()
            num = 0
            for (key, value) in dict.iteritems():
                num += 1
                # check if the value - that is, the redirect target - is a
                # redirect as well
                if num > self.restart and dict.has_key(value):
                    yield key
                    wikipedia.output(u'Checking redirect %i of %i...' % (num + 1, len(dict)))

class RedirectRobot:
    def __init__(self, action, generator):
        self.action = action
        self.generator = generator

    def delete_broken_redirects(self):
        # get reason for deletion text
        reason = wikipedia.translate(wikipedia.getSite(), reason_broken)

        for redir_name in self.generator.retrieve_broken_redirects():
            redir_page = wikipedia.Page(wikipedia.getSite(), redir_name)
            # Show the title of the page we're working on.
            # Highlight the title in purple.
            wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" % redir_page.title())
            try:
                target_name = redir_page.getRedirectTarget()
            except wikipedia.IsNotRedirectPage:
                wikipedia.output(u'%s is not a redirect.' % redir_page.title())
            except wikipedia.NoPage:
                wikipedia.output(u'%s doesn\'t exist.' % redir_page.title())
            else:
                try:
                    target_page = wikipedia.Page(wikipedia.getSite(), target_name)
                    target_page.get()
                except wikipedia.NoPage:
                    redir_page.delete(reason, prompt = False)
                except wikipedia.IsRedirectPage:
                    wikipedia.output(u'Redirect target is also a redirect! Won\'t delete anything.')
                else:
                    wikipedia.output(u'Redirect target does exist! Won\'t delete anything.')
                # idle for 1 minute
            wikipedia.output(u'')
            wikipedia.put_throttle()

    def fix_double_redirects(self):
        mysite = wikipedia.getSite()
        for redir_name in self.generator.retrieve_double_redirects():
            redir = wikipedia.Page(mysite, redir_name)
            # Show the title of the page we're working on.
            # Highlight the title in purple.
            wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" % redir.title())
            try:
                target = redir.getRedirectTarget()
            except wikipedia.IsNotRedirectPage:
                wikipedia.output(u'%s is not a redirect.' % redir.aslink())
            except wikipedia.NoPage:
                wikipedia.output(u'%s doesn\'t exist.' % redir.aslink())
            else:
                try:
                    second_redir = wikipedia.Page(mysite, target)
                    second_target = second_redir.getRedirectTarget()
                    anchor = re.search(u'#(.*)$', target)
                    if anchor and not u'#' in second_target:
                        second_target += u'#' + anchor.group(1)
                except wikipedia.SectionError:
                    wikipedia.output(u'Warning: Redirect target section %s doesn\'t exist.' % second_redir.aslink())
                except wikipedia.IsNotRedirectPage:
                    wikipedia.output(u'Redirect target %s is not a redirect.' % second_redir.aslink())
                except wikipedia.NoPage:
                    wikipedia.output(u'Redirect target %s doesn\'t exist.' % second_redir.aslink())
                else:
                    wikipedia.output(u'%s is a redirect to %s, which is a redirect to [[%s]]. Fixing...' % (redir.aslink(), second_redir.aslink(), second_target))
                    # TODO: make this case-insensitive
                    txt = redir.get(get_redirect=True).replace('[['+target,'[['+second_target)
                    try:
                        redir.put(txt)
                    except wikipedia.LockedPage:
                        wikipedia.output(u'%s is locked.' % redir.title())

    def run(self):
        if self.action == 'double':
            # get summary text
            wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg_double))
            self.fix_double_redirects()
        elif self.action == 'broken':
            self.delete_broken_redirects()

def main():
    # read command line parameters
    # what the bot should do (either resolve double redirs, or delete broken redirs)
    action = None
    # where the bot should get his infos from (either None to load the maintenance
    # special page from the live wiki, or the filename of a local XML dump file)
    xmlFilename = None
    # Which namespace should be processed when using a XML dump
    # default to -1 which means all namespaces will be processed
    namespace = -1
    # at which redirect shall we start searching double redirects again (only with dump)
    # default to -1 which means all redirects are checked
    restart = -1
    for arg in wikipedia.handleArgs():
        if arg == 'double':
            action = 'double'
        elif arg == 'broken':
            action = 'broken'
        elif arg.startswith('-xml'):
            if len(arg) == 4:
                xmlFilename = wikipedia.input(u'Please enter the XML dump\'s filename: ')
            else:
                xmlFilename = arg[5:]
        elif arg.startswith('-namespace:'):
            try:
                namespaces.append(int(arg[11:]))
            except ValueError:
                namespaces.append(arg[11:])
        elif arg.startswith('-restart:'):
            restart = int(arg[9:])
        else:
            print 'Unknown argument: %s' % arg

    if not action:
        wikipedia.showHelp('redirect')
    else:
        gen = RedirectGenerator(xmlFilename, namespace, restart)
        bot = RedirectRobot(action, gen)
        bot.run()

try:
    main()
finally:
    wikipedia.stopme()

