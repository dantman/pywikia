# -*- coding: utf-8 -*-

"""
Scripts to manage categories.

Syntax: python category.py action [-option]

where action can be one of these:
 * add    - mass-add a category to a list of pages
 * remove - remove category tag from all pages in a category
 * rename - move all pages in a category to another category
 * tidy   - tidy up a category by moving its articles into subcategories
 * tree   - show a tree of subcategories of a given category

and  option can be one of these:
 * person  - sort persons by their last name (for action 'add')
 * restore - if the bot didn't finish last time, resume work (for action 'tree') 

For example, to create a new category from a list of persons, type:
    
  python category.py add -person
    
and follow the on-screen instructions.
"""

#
# (C) Rob W.W. Hooft, 2004
# (C) Daniel Herding, 2004
#
# Distribute under the terms of the PSF license.
# 
import re, sys, string, pickle
import wikipedia, config, interwiki

# Summary messages
msg_add={
    'da':u'Robot: Tilføjer [[Kategori:%s]]',
    'de':u'Bot: Ergänze [[Kategorie:%s]]',
    'en':u'Robot: Adding [[Category:%s]]',
    'es':u'Bot: Añadida [[Categoría:%s]]',
    'is':u'Vélmenni: Bæti við [[Flokkur:%s]]',
    'pt':u'Bot: Adicionando [[Categoria:%s]]',
    }

msg_change={
    'da':u'Robot: Ændrer kategori %s',
    'de':u'Bot: Ändere Kategorie %s',
    'en':u'Robot: Changing category %s',
    'es':u'Bot: Cambiada categoría %s',
    'is':u'Vélmenni: Breyti flokknum %s',
    'nl':u'Bot: Wijziging Categorie %s',
    'pt':u'Bot: Modificando [[Categoria:%s]]',
    }

msg_remove={
    'da':u'Robot: Fjerner fra kategori %s',
    'de':u'Bot: Entferne aus Kategorie %s',
    'en':u'Robot: Removing from category %s',
    'es':u'Bot: Eliminada de la categoría %s',
    'is':u'Vélmenni: Breyti flokknum %s',
    'nl':u'Bot: Verwijderd uit Categorie %s',
    'pt':u'Bot: Removendo [[Categoria:%s]]',
    }



catContentDB={}
def get_subcats(supercat):
    '''
    For a given supercategory, return a list of CatLinks for all its
    subcategories.
    Saves this list in a temporary database so that it won't be loaded from the
    server next time it's required.
    '''
    # if we already know which subcategories exist here
    if catContentDB.has_key(supercat):
        return catContentDB[supercat][0]
    else:
        subcatlist = supercat.subcategories()
        articlelist = supercat.articles()
        # add to dictionary
        catContentDB[supercat] = [subcatlist, articlelist]
        return subcatlist

def get_articles(cat):
    '''
    For a given category, return a list of PageLinks for all its articles.
    Saves this list in a temporary database so that it won't be loaded from the
    server next time it's required.
    '''
    # if we already know which articles exist here
    if catContentDB.has_key(cat):
        return catContentDB[cat][1]
    else:
        subcatlist = cat.subcategories()
        articlelist = cat.articles()
        # add to dictionary
        catContentDB[cat] = [subcatlist, articlelist]
        return articlelist

superclassDB={}
# like the above, but for supercategories
def get_supercats(subcat):
    # if we already know which subcategories exist here
    if superclassDB.has_key(subcat):
        return superclassDB[subcat]
    else:
        supercatlist = subcat.supercategories()
        # add to dictionary
        superclassDB[subcat] = supercatlist
        return supercatlist

def dump(filename):
    '''
    Saves the contents of the dictionaries superclassDB and catContentDB to disk.
    '''
    # this is currently only used by print_treeview(). We might want to add it
    # for others like the tidy bot.
    f = open(filename, 'w')
    databases = {
        'catContentDB': catContentDB,
        'superclassDB': superclassDB
    }
    # store dump to disk in binary format
    pickle.dump(databases, f, bin=1)
    f.close()
    
def sorted_by_last_name(catlink, pagelink):
        '''
        given a CatLink, returns a CatLink which has an explicit sort key which
        sorts persons by their last names.
        Trailing words in brackets will be removed.
        Example: If category_name is 'Author' and pl is a PageLink to
        [[Alexandre Dumas (senior)]], this function will return this CatLink:
        [[Category:Author|Dumas, Alexandre]]
        '''
        page_name = pagelink.linkname()
        site = pagelink.site()
        # regular expression that matches a name followed by a space and
        # disambiguation brackets. Group 1 is the name without the rest.
        bracketsR = re.compile('(.*) \(.+?\)')
        match_object = bracketsR.match(page_name)
        if match_object:
            page_name = match_object.group(1)
        split_string = page_name.split(' ')
        if len(split_string) > 1:
            # pull last part of the name to the beginning, and append the rest after a comma
            # e.g. "John von Neumann" becomes "Neumann, John von"
            sorted_key = split_string[-1] + ', ' + string.join(split_string[:-1], ' ')
            # give explicit sort key
            return wikipedia.PageLink(site, catlink.linkname() + '|' + sorted_key)
        else:
            return wikipedia.PageLink(site, catlink.linkname())

def add_category(sort_by_last_name = False):
    '''
    A robot to mass-add a category to a list of pages.
    '''
    print "This bot has two modes: you can add a category link to all"
    print "pages mentioned in a List that is now in another wikipedia page"
    print "or you can add a category link to all pages that link to a"
    print "specific page. If you want the second, please give an empty"
    print "answer to the first question."
    listpage = wikipedia.input(u'Wikipedia page with list of pages to change:')
    if listpage:
        try:
            pl = wikipedia.PageLink(wikipedia.getSite(), listpage)
        except NoPage:
            wikipedia.output(u'The page ' + listpage + ' could not be loaded from the server.')
            sys.exit()
        pagenames = pl.links()
    else:
        refpage = wikipedia.input(u'Wikipedia page that is now linked to:')
        pl = wikipedia.PageLink(wikipedia.getSit(), refpage)
        pagenames = wikipedia.getReferences(pl)
    print "  ==> %d pages to process"%len(pagenames)
    print
    newcat = wikipedia.input(u'Category to add (do not give namespace):')
    newcat = newcat[:1].capitalize() + newcat[1:]

    # get edit summary message
    wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg_add) % newcat)
    
    cat_namespace = wikipedia.getSite().category_namespaces()[0]

    answer = ''
    for nm in pagenames:
        pl2 = wikipedia.PageLink(wikipedia.getSite(), nm)
        if answer != 'a':
            answer = ''
            
        while answer not in ('y','n','a'):
            answer = wikipedia.input(u'%s [y/n/a(ll)]:' % (pl2.aslink()))
            if answer == 'a':
                confirm = ''
		while confirm not in ('y','n'):
	            confirm = wikipedia.input(u'This should be used if and only if you are sure that your links are correct! Are you sure? [y/n]:')
	
	if answer == 'y' or answer == 'a':
            try:
                cats = pl2.categories()
            except wikipedia.NoPage:
                wikipedia.output(u"%s doesn't exist yet. Ignoring."%(pl2.aslocallink()))
                pass
            except wikipedia.IsRedirectPage,arg:
                pl3 = wikipedia.PageLink(wikipedia.getSite(),arg.args[0])
                wikipedia.output(u"WARNING: %s is redirect to [[%s]]. Ignoring."%(pl2.aslocallink(),pl3.aslocallink()))
            else:
                wikipedia.output(u"Current categories:")
                for curpl in cats:
                    wikipedia.output(u"* %s" % cat.aslink())
                catpl = wikipedia.PageLink(wikipedia.getSite(), cat_namespace + ':' + newcat)
                if sort_by_last_name:
                    catpl = sorted_by_last_name(catpl, pl2) 
                if catpl in cats:
                    wikipedia.output(u"%s already has %s"%(pl2.aslocallink(), catpl.aslocallink()))
                else:
                    wikipedia.output(u'Adding %s' % catpl.aslocallink())
                    cats.append(catpl)
                    text = pl2.get()
                    text = wikipedia.replaceCategoryLinks(text, cats)
                    pl2.put(text)

def rename_category(old_cat_title, new_cat_title):
    old_cat = catlib.CatLink(wikipedia.getSite(), old_cat_title)
    
    # get edit summary message
    wikipedia.setAction(wikipedia.translate(wikipedia.getSite(),msg_change) % old_cat_title)
    
    articles = old_cat.articles(recurse = 0)
    if len(articles) == 0:
        wikipedia.output(u'There are no articles in category ' + old_cat_title)
    else:
        for article in articles:
            catlib.change_category(article, old_cat_title, new_cat_title)
    
    subcategories = old_cat.subcategories(recurse = 0)
    if len(subcategories) == 0:
        wikipedia.output(u'There are no subcategories in category ' + old_cat_title)
    else:
        for subcategory in subcategories:
            catlib.change_category(subcategory, old_cat_title, new_cat_title)

def remove_category(cat_title):
    '''
    Asks for a category, and removes the category tag from all pages 
    in that category and from the category pages of all subcategories, without
    prompting.
    Doesn't remove category tags pointing at subcategories. Doesn't delete the
    category page.
    '''
    cat = catlib.CatLink(wikipedia.getSite(), cat_title)
    # get edit summary message
    wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg_remove) % cat_title)
    
    articles = cat.articles(recurse = 0)
    if len(articles) == 0:
        wikipedia.output(u'There are no articles in category ' + cat_title)
    else:
        for article in articles:
            catlib.change_category(article, cat_title, None)
    # Also removes the category tag from subcategories' pages 
    subcategories = cat.subcategories(recurse = 0)
    if len(subcategories) == 0:
        wikipedia.output(u'There are no subcategories in category ' + cat_title)
    else:
        for subcategory in subcategories:
            catlib.change_category(subcategory, cat_title, None)

def tidy_category(cat_title):
    """
    Script to help a human to tidy up a category by moving its articles into
    subcategories
    
    Specify the category name on the command line. The program will pick up the
    page, and look for all subcategories and supercategories, and show them with
    a number adjacent to them. It will then automatically loop over all pages
    in the category. It will ask you to type the number of the appropriate
    replacement, and perform the change robotically.
    
    If you don't want to move the article to a subcategory or supercategory, but to
    another category, you can use the 'j' (jump) command.
    
    Typing 's' will leave the complete page unchanged.
    
    Typing '?' will show you the first few bytes of the current page, helping
    you to find out what the article is about and in which other categories it
    currently is.
    
    Important:
     * this bot is written to work with the MonoBook skin, so make sure your bot
       account uses this skin
    """
    # This is a temporary knowledge base (dictionary data type) for all known
    # supercategory-subcategory relationships, so that category pages don't need to
    # be loaded over and over again

    # This is a purely interactive robot. We set the delays lower.
    wikipedia.get_throttle.setDelay(5)
    wikipedia.put_throttle.setDelay(10)

    # given an article which is in category original_cat, ask the user if it should
    # be moved to one of original_cat's subcategories. Recursively run through
    # subcategories' subcategories.
    # NOTE: current_cat is only used for internal recursion. You should always use
    # current_cat = original_cat.
    def move_to_category(article, original_cat, current_cat):
        print
        wikipedia.output(u'Treating page %s, currently in category %s' % (article.linkname(), current_cat.linkname()))
        subcatlist = get_subcats(current_cat)
        supercatlist = get_supercats(current_cat)
        print
        if len(subcatlist) == 0:
            print 'This category has no subcategories.'
            print
        if len(supercatlist) == 0:
            print 'This category has no supercategories.'
            print
        # show subcategories as possible choices (with numbers)
        for i in range(len(supercatlist)):
            # layout: we don't expect a cat to have more than 10 supercats
            wikipedia.output(u'u%d - Move up to %s' % (i, supercatlist[i].linkname()))
        for i in range(len(subcatlist)):
            # layout: we don't expect a cat to have more than 100 subcats
            wikipedia.output(u'%2d - Move down to %s' % (i, subcatlist[i].linkname()))
        print ' j - Jump to another category'
        print ' n - Skip this article'
        print ' r - Remove this category tag'
        print ' ? - Read the page'
        wikipedia.output(u'Enter - Save category as %s' % current_cat.linkname())

        flag = False
        length = 1000
        while not flag:
            print ''
            choice=wikipedia.input(u'Choice:')
            if choice == 'n':
                flag = True
            elif choice == '':
                wikipedia.output(u'Saving category as %s' % current_cat.linkname())
                if current_cat == original_cat:
                    print 'No changes necessary.'
                else:
                    catlib.change_category(article, original_cat.catname(), current_cat.catname())
                flag = True
            elif choice == 'j':
                new_cat_title = wikipedia.input(u'Please enter the category the article should be moved to:')
                new_cat = catlib.CatLink(wikipedia.getSite(), new_cat_title)
                # recurse into chosen category
                move_to_category(article, original_cat, new_cat)
                flag = True
            elif choice == 'r':
                # remove the category tag
                catlib.change_category(article, original_cat.catname(), None)
                flag = True
            elif choice == '?':
                print ''
                full_text = article.get()
                print ''
                wikipedia.output(full_text[0:length])
                
                # if categories possibly weren't visible, show them additionally
                # (maybe this should always be shown?)
                if len(full_text) > length:
                    print ''
                    print 'Original categories: '
                    for cat in article.categories(): 
                        wikipedia.output(u'* %s' % cat.linkname()) 
                    # show more text if the user uses this function again
                    length = length+500
            elif choice[0] == 'u':
                try:
                    choice=int(choice[1:])
                except ValueError:
                    # user pressed an unknown command. Prompt him again.
                    continue
                move_to_category(article, original_cat, supercatlist[choice])
                flag = True
            else:
                try:
                    choice=int(choice)
                except ValueError:
                    # user pressed an unknown command. Prompt him again.
                    continue
                # recurse into subcategory
                move_to_category(article, original_cat, subcatlist[choice])
                flag = True
    
    # begin main part of tidy_category
    catlink = catlib.CatLink(wikipedia.getSite(), cat_title)
    
    # get edit summary message
    wikipedia.setAction(wikipedia.translate(wikipedia.getSite(), msg_change) % cat_title)
    
    
    articles = catlink.articles(recurse = 0)
    if len(articles) == 0:
        wikipedia.output(u'There are no articles in category ' + cat_title)
    else:
        for article in articles:
            print
            print '==================================================================='
            move_to_category(article, catlink, catlink)

def treeview(cat, max_depth, current_depth = 0, parent = None):
    '''
    Returns a multi-line string which contains a tree view of all subcategories
    of cat, up to level max_depth.
    
    Parameters:
        * cat - a CatLink which will be the tree's root
        * current_depth - the current level in the tree (for recursion)
        * parent - the CatLink of the category we're coming from
        * max_depth - the limit beyond which no subcategories will be listed
    '''
    # Translations to say that the current category is in more categories than
    # the one we're coming from
    also_in_cats = {
        'da': u'(også i %s)',
        'de': u'(auch in %s)',
        'en': u'(also in %s)',
        'is': u'(einnig í %s)',
        }
        
    result = u''
    result += '#' * current_depth
    result += '[[:%s|%s]]' % (cat.linkname(), cat.linkname().split(':', 1)[1])
    result += ' (%d)' % len(get_articles(cat))
    # We will remove an element of this array, but will need the original array
    # later, so we create a shallow copy with [:]
    supercats = get_supercats(cat)[:]
    # Find out which other cats are supercats of the current cat
    try:
        supercats.remove(parent)
    except:
        pass
    if supercats != []:
        supercat_names = []
        for i in range(len(supercats)):
            # create a list of wiki links to the supercategories
            supercat_names.append('[[:%s|%s]]' % (supercats[i].linkname(), supercats[i].linkname().split(':', 1)[1]))
            # print this list, separated with commas, using translations given in also_in_cats
        result += ' ' + wikipedia.translate(wikipedia.getSite(), also_in_cats) % ', '.join(supercat_names)
    result += '\n'
    if current_depth < max_depth:
        for subcat in get_subcats(cat):
            # recurse into subdirectories
            result += treeview(subcat, max_depth, current_depth + 1, parent = cat)
    else:
        if get_subcats(cat) != []:
            # show that there are more categories beyond the depth limit
            result += '#' * (current_depth + 1) + '[...]\n'
    return result

def print_treeview(catname, max_depth = 10):
    """
    Prints the multi-line string generated by treeview or saves it to a file.

    Parameters:
        * catname - the title of the category which will be the tree's root
        * max_depth - the limit beyond which no subcategories will be listed
    """
    # TODO: make max_depth changeable with a parameter or config file entry 
    filename = wikipedia.input(u'Please enter the name of the file where the tree should be saved, or press enter to simply show the tree:')
    cat = catlib.CatLink(wikipedia.getSite(), catname)
    tree = treeview(cat, max_depth, 0)
    if filename:
        wikipedia.output(u'Saving results in %s' % filename)
        import codecs
        f = codecs.open(filename, 'a', 'utf-8')
        f.write(tree)
        f.close()
    else:
        wikipedia.output(tree)

if __name__ == "__main__":
    action = None
    sort_by_last_name = False
    for arg in sys.argv[1:]:
        arg = wikipedia.argHandler(arg)
        if arg:
            if arg == 'add':
                action = 'add'
            elif arg == 'remove':
                action = 'remove'
            elif arg == 'rename':
                action = 'rename'
            elif arg == 'tidy':
                action = 'tidy'
            elif arg == 'tree':
                action = 'tree'
            elif arg == '-person':
                sort_by_last_name = True
            elif arg == '-restore':
                f = open('cattree.dump', 'r')
                databases = pickle.load(f)
                f.close()
                catContentDB = databases['catContentDB'] 
                superclassDB = databases['superclassDB']
                del databases
                
    # catlib needs to be imported at this position because its constructor uses
    # mylang which might have been changed by wikipedia.argHandler().
    import catlib
    if action == 'add':
        add_category(sort_by_last_name)
    elif action == 'remove':
        cat_title = wikipedia.input(u'Please enter the name of the category that should be removed:')
        remove_category(cat_title)
    elif action == 'rename':
        old_cat_title = wikipedia.input(u'Please enter the old name of the category:')
        new_cat_title = wikipedia.input(u'Please enter the new name of the category:')
        rename_category(old_cat_title, new_cat_title)
    elif action == 'tidy':
        cat_title = wikipedia.input(u'Which category do you want to tidy up?')
        tidy_category(cat_title)
    elif action == 'tree':
        cat_title = wikipedia.input(u'For which category do you want to create a tree view?')
        try:
            print_treeview(cat_title)
        except:
            dump('cattree.dump')
            raise
    else:
        # show help
        wikipedia.output(__doc__, 'utf-8')

