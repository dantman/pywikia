# -*- coding: utf-8 -*-
"""
This bot is used to quickly trawl through candidates for speedy deletion in a fast
and semi-automated fashion.  The bot displays the contents of each page one at a
time and provides a prompt for the user to skip or delete the page.  Of course, this
will require a sysop account.

Future upcoming options include the ability to untag a page as not being eligible
for speedy deletion, as well as the option to commute its sentence to Proposed
Deletion (see [[en:WP:PROD]] for more details).  Also, if the article text is long,
to prevent terminal spamming, it might be a good idea to truncate it just to the
first so many bytes.

WARNING: This tool shows the contents of the top revision only.  It is possible that
a vandal has replaced a perfectly good article with nonsense, which has subsequently
been tagged by someone who didn't realize it was previously a good article.  The onus
is on you to avoid making these mistakes.

NOTE: This script currently only works for the Wikipedia project.

Syntax: python speedy-delete.py

Command line options:

    none yet

Examples:

    none needed yet

"""
__version__ = '$Id$'
#
# Distributed under the terms of the MIT license.
#
import wikipedia
import pagegenerators, catlib
import time

class SpeedyRobot:
    """
    This robot will load a list of pages from the category of candidates for speedy
    deletion on the language's wiki and give the user an interactive prompt to decide
    whether each should be deleted or not.
    """

    csd_cat={
        'wikipedia':{
            'als': u'Kategorie:Wikipedia:Schnelllöschen',
            'ar': u'تصنيف:صفحات للحذف السريع',
            'be': u'Катэгорыя:Вікіпэдыя:Кандыдатуры на выдаленьне',
            'cs': u'Kategorie:Stránky ke smazání',
            'de': u'Kategorie:Wikipedia:Schnelllöschen',
            'en': u'Category:Candidates for speedy deletion',
            'es': u'Categoría:Wikipedia:Borrar (definitivo)',
            'fa': u'رده:مقالات نامزد حذف سریع',
            'fi': u'Luokka:Roskaa',
            'he': u'קטגוריה:ויקיפדיה: למחיקה מהירה',
            'hsb': u'Kategorija:Strony k spěšnemu wušmórnjenju',
            'ia': u'Categoria:Wikipedia:Eliminar',
            'it': 'Categoria:Da_cancellare_subito',
            'ja': u'Category:即時削除',
            'ks': u'Category:Candidates for speedy deletion',
            'nah': u'Categoría:Huiquipedia:Borrar (definitivo)',
            'nl': u'Categorie:Wikipedia:Nuweg',
            'no': u'Kategori:Sider som er foreslått raskt slettet',
            'pl': u'Kategoria:Ekspresowe kasowanko',
            'pt': u'Categoria:Páginas para eliminação rápida',
            'ru': u'Категория:Википедия:К быстрому удалению',
            'sv': u'Kategori:Snabba raderingar',
            'uk': u'Категорія:Статті до швидкого вилучення',
            'vi': u'Thể loại:Chờ xoá',
            'zh': u'Category:快速删除候选',
            'zh-yue': u'Category:快速刪除候選',
        },
        'wikinews':{
            'zh': u'Category:快速删除候选',
        },
    }

    # If the site has several templates for speedy deletion, it might be
    # possible to find out the reason for deletion by the template used.
    # _default will be used if no such semantic template was used.
    deletion_messages = {
        'wikipedia':{
            'ar': {
                u'_default': u'حذف مرشح للحذف السريع حسب [[ويكيبيديا:حذف سريع|معايير الحذف السريع]]',
                },
            'de': {
                u'_default': u'Lösche Artikel mit [[Wikipedia:Schnelllöschantrag|Schnelllöschantrag]]',
                },
            'en': {
                u'_default':      u'Deleting candidate for speedy deletion per [[WP:CSD|CSD]]',
                u'Db-author':     u'Deleting page per [[WP:CSD|CSD]] G7: Author requests deletion and is its only editor.',
                u'Db-nonsense':   u'Deleting page per [[WP:CSD|CSD]] G1: Page is patent nonsense or gibberish.',
                u'Db-test':       u'Deleting page per [[WP:CSD|CSD]] G2: Test page.',
                u'Db-nocontext':  u'Deleting page per [[WP:CSD|CSD]] A1: Short article that provides little or no context.',
                u'Db-empty':      u'Deleting page per [[WP:CSD|CSD]] A1: Empty article.',
                u'Db-attack':     u'Deleting page per [[WP:CSD|CSD]] G10: Page that exists solely to attack its subject.',
                u'Db-catempty':   u'Deleting page per [[WP:CSD|CSD]] C1: Empty category.',
                u'Db-band':       u'Deleting page per [[WP:CSD|CSD]] A7: Article about a non-notable band.',
                u'Db-banned':     u'Deleting page per [[WP:CSD|CSD]] G5: Page created by a banned user.',
                u'Db-bio':        u'Deleting page per [[WP:CSD|CSD]] A7: Article about a non-notable person.',
                u'Db-notenglish': u'Deleting page per [[WP:CSD|CSD]] A2: Article isn\'t written in English.',
                u'Db-copyvio':    u'Deleting page per [[WP:CSD|CSD]] G12: Page is a blatant copyright violation.',
                u'Db-repost':     u'Deleting page per [[WP:CSD|CSD]] G4: Recreation of previously deleted material.',
                u'Db-vandalism':  u'Deleting page per [[WP:CSD|CSD]] G3: Blatant vandalism.',
                u'Db-talk':       u'Deleting page per [[WP:CSD|CSD]] G8: Talk page of a deleted or non-existent page.',
                u'Db-spam':       u'Deleting page per [[WP:CSD|CSD]] G11: Blatant advertising.',
                u'Db-disparage':  u'Deleting page per [[WP:CSD|CSD]] T1: Divisive or inflammatory template.',
                u'Db-r1':         u'Deleting page per [[WP:CSD|CSD]] R1: Redirect to a deleted or non-existent page.',
                u'Db-experiment': u'Deleting page per [[WP:CSD|CSD]] G2: Page was created as an experiment.',
                },
            'he': {
                u'_default':      u'מחיקת מועמד למחיקה מהירה לפי [[ויקיפדיה:מדיניות המחיקה|מדיניות המחיקה]]',
                u'גם בוויקישיתוף': u'הקובץ זמין כעת בוויקישיתוף.',
                },
            'ja':{
                u'_default':u'[[WP:CSD|即時削除の方針]]に基づい削除',
                },
            'pt': {
                u'_default':      u'Apagando página por [[Wikipedia:Páginas para eliminar|eliminação rápida]]',
                },
            'pl': {
                u'_default':      u'Usuwanie artykułu zgodnie z zasadami [[Wikipedia:Ekspresowe kasowanko|ekspresowego kasowania]]',
                },
            'it': {
                u'_default':      u'Bot: Cancello pagine taggate come [[Aiuto:Cancella subito|cancella subito]].',
                },
            'zh':{
                u'_default':u'[[WP:CSD]]',
                u'Notchinese':u'[[WP:CSD#G7|CSD G7]]: 非中文條目且長時間未翻譯',
                u'No source':u'[[WP:CSD#I3|CSD I3]]: 沒有來源連結，無法確認來源與版權資訊',
                u'No license':u'[[WP:CSD#I3|CSD I3]]: 沒有版權模板，無法確認版權資訊',
                u'Unknown':u'[[WP:CSD#I3|CSD I3]]: 沒有版權模板，無法確認版權資訊',
                u'TempPage':u'[[WP:CSD]]: 臨時頁面',
                u'NowCommons':u'[[WP:CSD#I7|CSD I7]]: 此圖片已存在於[[:commons:|維基共享資源]]',
                u'Nowcommons':u'[[WP:CSD#I7|CSD I7]]: 此圖片已存在於[[:commons:|維基共享資源]]',
                u'RoughTranslation':u'[[WP:CSD#G7|CSD G7]]: 機器翻譯',
                u'Advert':u'[[WP:CSD#G11|CSD G11]]: [[WP:NOT#維基百科不是宣傳工具|廣告、宣傳頁面]]',
                },
        },
    }

    # Default reason for deleting a talk page.
    talk_deletion_msg={
        'ar':u'صفحة نقاش يتيمة',
        'de':u'Verwaiste Diskussionsseite',
        'en':u'Orphaned talk page',
        'he':u'דף שיחה של ערך שנמחק',
        'it':u'Bot: Cancello pagina discussione di una pagina già cancellata',
        'pl':u'Osierocona strona dyskusji',
        'pt':u'Página de discussão órfã',
        'zh':u'[[WP:CSD#O1|CSD O1 O2 O6]] 沒有在使用的討論頁',
    }

    # A list of often-used reasons for deletion. Shortcuts are keys, and
    # reasons are values. If the user enters a shortcut, the associated reason
    # will be used.
    delete_reasons = {
        'de': {
            'asdf':  u'Tastaturtest',
            'egal':  u'Eindeutig irrelevant',
            'ka':    u'Kein Artikel',
            'mist':  u'Unsinn',
            'move':  u'Redirectlöschung, um Platz für Verschiebung zu schaffen',
            'nde':   u'Nicht in deutscher Sprache verfasst',
            'pfui':  u'Beleidigung',
            'redir': u'Unnötiger Redirect',
            'spam':  u'Spam',
            'web':   u'Nur ein Weblink',
            'wg':    u'Wiedergänger (wurde bereits zuvor gelöscht)',
            },
        'it': {
            'test': u'Bot: Cancello pagina in seguito ad un test.',
            'vandalismo': u'Bot: Cancello pagina vandalica',
            'copyviol': 'Bot: Cancello copyviol',
            'redirect': 'Bot: Cancello redirect rotto o inutile',
            'spam': 'Bot: Cancello pagina piena di spam',
            'promo': 'Bot: Cancello pagina promozionale',
            },
        'ja':{
            'cont':u'[[WP:CSD]] 全般1 意味不明な内容のページ',
            'test':u'[[WP:CSD]] 全般2 テスト投稿',
            'vand':u'[[WP:CSD]] 全般3 荒らしand/orいたずら',
            'ad':u'[[WP:CSD]] 全般4 宣伝',
            'rep':u'[[WP:CSD]] 全般5 削除されたページの改善なき再作成',
            'cp':u'[[WP:CSD]] 全般6 コピペ移動or分割',
            'sh':u'[[WP:CSD]] 記事1 短すぎ',
            'nd':u'[[WP:CSD]] 記事1 定義なし',
            'auth':u'[[WP:CSD]] 記事3 投稿者依頼or初版立項者による白紙化',
            'nr':u'[[WP:CSD]] リダイレクト1 無意味なリダイレクト',
            'nc':u'[[WP:CSD]] リダイレクト2 [[WP:NC]]違反',
            'ren':u'[[WP:CSD]] リダイレクト3 改名提案を経た曖昧回避括弧付きの移動の残骸',
            'commons':u'[[WP:CSD]] マルチメディア7 コモンズの画像ページ',
            'tmp':u'[[WP:CSD]] テンプレート1 初版投稿者依頼',
            'uau':u'[[WP:CSD]] 利用者ページ1 本人希望',
            'nuu':u'[[WP:CSD]] 利用者ページ2 利用者登録されていない利用者ページ',
            'ipu':u'[[WP:CSD]] 利用者ページ3 IPユーザの利用者ページ',
            },
        'zh':{
            'empty':u'[[WP:CSD#G1|CSD G1]]: 沒有實際内容或歷史記錄的文章。',
            'test':u'[[WP:CSD#G2|CSD G2]]: 測試頁',
            'vand':u'[[WP:CSD#G3|CSD G3]]: 純粹破壞',
            'cont':u'[[WP:CSD#G4|CSD G4]]: 非常短，而且沒有定義或內容。',
            'rep':u'[[WP:CSD#G5|CSD G5]]: 重新建立的內容',
            'text':u'[[WP:CSD#G9|CSD G9]]: 只有相關連結、項目的頁面',
            'auth':u'[[WP:CSD#G10|CSD G10]]: 原作者請求',
            'ad':u'[[WP:CSD#G11|CSD G11]]: 廣告、宣傳頁面',
            'bio':u'[[WP:CSD#G12|CSD G12]]: 生者傳記',
            'br':u'[[WP:CSD#R1|CSD R1]]: 損壞的重定向',
            'wr':u'[[WP:CSD#R3|CSD R3]]: 錯誤重定向',
            'repi':u'[[WP:CSD#I1|CSD I1]]: 重複的圖片',
            'lssd':u'[[WP:CSD#I3|CSD I3]]: 沒有版權或來源資訊，無法確認圖片是否符合方針要求',
            'nls':u'[[WP:CSD#I3|CSD I3]]: 沒有版權模板，無法確認版權資訊',
            'ui':u'[[WP:CSD#I6|CSD I6]]: 圖片未使用且不自由',
            'uc':u'[[WP:CSD#O4|CSD O4 O5]]: 空類別',
            'mactra':u'[[WP:CSD#G7|CSD G7]]: 機器翻譯',
            'tmp':u'[[WP:CSD]]: 臨時頁面',
            },
        # There's a template for nearly every possible reason on en:.
        # If the bot can't guess the reason from the template, the user should
        # enter it manually.
        # 'en':
    }

    def __init__(self):
        """
        Arguments:
            none yet
        """
        self.mySite = wikipedia.getSite()
        self.csdCat = catlib.Category(self.mySite, wikipedia.translate(self.mySite, self.csd_cat))
        self.savedProgress = '!'
        self.preloadingGen = None

    def guessReasonForDeletion(self, page):
        reason = None
        # TODO: The following check loads the page 2 times. Find a better way to do it.
        if page.isTalkPage() and (page.toggleTalkPage().isRedirectPage() or not page.toggleTalkPage().exists()):
            # This is probably a talk page that is orphaned because we
            # just deleted the associated article.
            reason = wikipedia.translate(self.mySite, self.talk_deletion_msg)
        else:
            # Try to guess reason by the template used
            templateNames = page.templates()
            reasons = wikipedia.translate(self.mySite, self.deletion_messages)

            for templateName in templateNames:
                if templateName in reasons.keys():
                    reason = reasons[templateName]
                    break
        if not reason:
            # Unsuccessful in guessing the reason. Use a default message.
            reason = reasons[u'_default']
        return reason

    def getReasonForDeletion(self, page):
        suggestedReason = self.guessReasonForDeletion(page)
        wikipedia.output(u'The suggested reason is: \03{lightred}%s\03{default}' % suggestedReason)

        # We don't use wikipedia.translate() here because for some languages the
        # entry is intentionally left out.
        if self.delete_reasons.has_key(page.site().lang):
            localReasons = self.delete_reasons[page.site().lang]
            wikipedia.output(u'')
            for key, reason in localReasons.iteritems():
                wikipedia.output((key + ':').ljust(8) + reason)
            wikipedia.output(u'')
            reason = wikipedia.input(u'Please enter the reason for deletion, choose a default reason, or press enter for the suggested message:')
            if localReasons.has_key(reason.strip()):
                reason = localReasons[reason]
        else:
            reason = wikipedia.input(u'Please enter the reason for deletion, or press enter for the suggested message:')

        if not reason:
            reason = suggestedReason
        return reason

    def run(self):
        """
        Starts the robot's action.
        """

        keepGoing = True
        startFromBeginning = True
        while keepGoing:
            if startFromBeginning:
                self.savedProgress = '!'
            self.refreshGenerator()
            count = 0
            for page in self.preloadingGen:
                try:
                    pageText = page.get(get_redirect = True)
                    count += 1
                except wikipedia.NoPage:
                    wikipedia.output(u'Page %s does not exist or has already been deleted, skipping.' % page.aslink())
                    continue
                # Show the title of the page we're working on.
                # Highlight the title in purple.
                wikipedia.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<" % page.title())
                wikipedia.output(u'-  -  -  -  -  -  -  -  -  ')
                wikipedia.output(pageText)
                wikipedia.output(u'-  -  -  -  -  -  -  -  -  ')
                choice = wikipedia.inputChoice(u'Input action?', ['delete', 'skip', 'update', 'quit'], ['d', 'S', 'u', 'q'], 'S')
                if choice == 'q':
                    keepGoing = False
                    break
                elif choice == 'u':
                    wikipedia.output(u'Updating from CSD category.')
                    self.savedProgress = page.title()
                    startFromBeginning = False
                    break
                elif choice == 'd':
                    reason = self.getReasonForDeletion(page)
                    wikipedia.output(u'The chosen reason is: \03{lightred}%s\03{default}' % reason)
                    page.delete(reason, prompt = False)
                else:
                    wikipedia.output(u'Skipping page %s' % page.title())
                startFromBeginning = True
            if count == 0:
                if startFromBeginning:
                    wikipedia.output(u'There are no pages to delete. Waiting for 30 seconds...')
                    time.sleep(30)
                else:
                    startFromBeginning = True
        wikipedia.output(u'Quitting program.')

    def refreshGenerator(self):
        generator = pagegenerators.CategorizedPageGenerator(self.csdCat, start = self.savedProgress)
        # wrap another generator around it so that we won't produce orphaned talk pages.
        generator2 = pagegenerators.PageWithTalkPageGenerator(generator)
        self.preloadingGen = pagegenerators.PreloadingGenerator(generator2, pageNumber = 20)

def main():
    # read command line parameters
    for arg in wikipedia.handleArgs():
        pass #No args yet

    bot = SpeedyRobot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
