# -*- coding: utf-8 -*-

"""
Scripts to manage categories.

Run the bot without arguments for instructions.

See comments below for details.
"""

#
# (C) Rob W.W. Hooft, 2004
# (C) Daniel Herding, 2004
#
# Distribute under the terms of the PSF license.
# 
import re, sys, string
import wikipedia, config, catlib, interwiki


# Summary messages
msg_change={
    'en':u'Robot: Changing [[Category:%s]]',
    'de':u'Bot: Ändere [[Kategorie:%s]]',
    'nl':u'Bot: Wijziging [[Categorie:%s]]',
    }

msg_remove={
    'en':u'Robot: Removing from category %s',
    'de':u'Bot: Entferne aus Kategorie %s',
    'nl':u'Bot: Verwijderd uit Categorie %s',
    }


"""
A robot to mass-add a category to a list of pages.

Just run this robot without any additional arguments.

"""
def add_category(sort_by_last_name = False):
    print "This bot has two modes: you can add a category link to all"
    print "pages mentioned in a List that is now in another wikipedia page"
    print "or you can add a category link to all pages that link to a"
    print "specific page. If you want the second, please give an empty"
    print "answer to the first question."
    listpage = wikipedia.input(u'Wikipedia page with list of pages to change:')
    if listpage:
        try:
            pl = wikipedia.PageLink(wikipedia.mylang, listpage)
        except NoPage:
            print 'The page ' + listpage + ' could not be loaded from the server.'
            sys.exit()
        pagenames = pl.links()
    else:
        refpage = wikipedia.input(u'Wikipedia page that is now linked to:')
        pl = wikipedia.PageLink(wikipedia.mylang, refpage)
        pagenames = wikipedia.getReferences(pl)
    print "  ==> %d pages to process"%len(pagenames)
    print
    newcat = wikipedia.input(u'Category to add (do not give namespace):')
    newcat = newcat[:1].capitalize() + newcat[1:]

    ns = wikipedia.family.category_namespaces(wikipedia.mylang)
    
    cat_namespace = ns[0].encode(wikipedia.myencoding())
    if not sort_by_last_name:
        catpl = wikipedia.PageLink(wikipedia.mylang, cat_namespace + ':' + newcat)
        print "Will add %s"%catpl.aslocallink()

    answer = ''
    for nm in pagenames:
        pl2 = wikipedia.PageLink(wikipedia.mylang, nm)
        if answer != 'a':
            answer = ''
            
        while answer not in ('y','n','a'):
            answer = wikipedia.input(u'%s [y/n/a(ll)]:' % (pl2.aslink()))
            if answer == 'a':
                confirm = ''
		while confirm not in ('y','n'):
	            confirm = wikipedia.input(u'This should be used if and only if you are sure that your links are correct !!! Are you sure ? [y/n]:')
	
	if answer == 'y' or answer == 'a':
            try:
                cats = pl2.categories()
            except wikipedia.NoPage:
                print "%s doesn't exist yet. Ignoring."%(pl2.aslocallink())
                pass
            except wikipedia.IsRedirectPage,arg:
                pl3 = wikipedia.PageLink(wikipedia.mylang,arg.args[0])
                print "WARNING: %s is redirect to [[%s]]. Ignoring."%(pl2.aslocallink(),pl3.aslocallink())
            else:
                print "Current categories: ",cats
                if sort_by_last_name:
                    page_name = pl2.linkname()
                    split_string = page_name.split(' ')
                    if len(split_string) > 1:
                        # pull last part of the name to the beginning, and append the rest after a comma
                        # e.g. "John von Neumann" becomes "Neumann, John von"
                        new_name = split_string[-1] + ', ' + string.join(split_string[:-1], ' ')
                        # give explicit sort key
                        catpl = wikipedia.PageLink(wikipedia.mylang, cat_namespace + ':' + newcat + '|' + new_name)
                    else:
                        catpl = wikipedia.PageLink(wikipedia.mylang, cat_namespace + ':' + newcat)
                if catpl in cats:
                    print "%s already has %s"%(pl2.aslocallink(),catpl.aslocallink())
                else:
                    cats.append(catpl)
                    text = pl2.get()
                    text = wikipedia.replaceCategoryLinks(text, cats)
                    pl2.put(text, comment = catpl.aslocallink().encode(wikipedia.myencoding()))

def rename_category():
    old_cat_title = wikipedia.input(u'Please enter the old name of the category:')
    old_cat = catlib.CatLink(old_cat_title)
    new_cat_title = wikipedia.input(u'Please enter the new name of the category:')
    
    # get edit summary message
    wikipedia.setAction(msg_change[wikipedia.chooselang(wikipedia.mylang,msg_change)] % old_cat_title)
    
    articles = old_cat.articles(recurse = 0)
    if len(articles) == 0:
        print 'There are no articles in category ' + old_cat_title
    else:
        for article in articles:
            catlib.change_category(article, old_cat_title, new_cat_title)
    
    subcategories = old_cat.subcategories(recurse = 0)
    if len(subcategories) == 0:
        print 'There are no subcategories in category ' + old_cat_title
    else:
        for subcategory in subcategories:
            catlib.change_category(subcategory, old_cat_title, new_cat_title)

# asks for a category, and removes the category tag from all pages 
# in that category, without prompting.
def remove_category():
    old_cat_title = wikipedia.input(u'Please enter the name of the category that should be removed:')
    old_cat = catlib.CatLink(old_cat_title)
    # get edit summary message
    wikipedia.setAction(msg_remove[wikipedia.chooselang(wikipedia.mylang,msg_remove)] % old_cat_title)
    
    articles = old_cat.articles(recurse = 0)
    if len(articles) == 0:
        print 'There are no articles in category ' + old_cat_title
    else:
        for article in articles:
            catlib.change_category(article, old_cat_title, None)
    
    subcategories = old_cat.subcategories(recurse = 0)
    if len(subcategories) == 0:
        print 'There are no subcategories in category ' + old_cat_title
    else:
        for subcategory in subcategories:
            catlib.change_category(subcategory, old_cat_title, None)


"""
Script to help a human to tidy up a category by moving its articles into
subcategories

Specify the category name on the command line. The program will
pick up the page, and look for all subcategories, and show them with
a number adjacent to them. It will then automatically loop over all pages
in the category. It will ask you to type the number of the appropriate
replacement, and perform the change robotically.

If you don't want to move the article to a subcategory, but to another
category, you can use the 'j' (jump) command.

Typing 's' will leave the complete page unchanged.

Important:
 * this bot is written to work with the MonoBook skin, so make sure your bot
   account uses this skin
"""

def tidy_category():
    # This is a temporary knowledge base (dictionary data type) for all known
    # supercategory-subcategory relationships, so that category pages don't need to
    # be loaded over and over again

    # This is a purely interactive robot. We set the delays lower.
    wikipedia.get_throttle.setDelay(5)
    wikipedia.put_throttle.setDelay(10)

    subclassDB={}
    # for a given supercategory, return a list of all its subcategories.
    # save this list in a temporary database so that it won't be loaded from the
    # server next time it's required.
    def get_subcats(supercat):
        # if we already know which subcategories exist here
        if subclassDB.has_key(supercat):
            return subclassDB[supercat]
        else:
            subcatlist = supercat.subcategories()
            # add to dictionary
            subclassDB[supercat] = subcatlist
            return subcatlist

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
            print 'u%d - Move up to %s' % (i, supercatlist[i].linkname())
        for i in range(len(subcatlist)):
            # layout: we don't expect a cat to have more than 100 subcats
            print '%2d - Move down to %s' % (i, subcatlist[i].linkname())
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
                    print 'No changes necessarry.'
                else:
                    catlib.change_category(article, original_cat.catname(), current_cat.catname())
                flag = True
            elif choice == 'j':
                new_cat_title = wikipedia.input(u'Please enter the category the article should be moved to:')
                new_cat = catlib.CatLink(new_cat_title)
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
                        wikipedia.output('* %s' % cat.linkname()) 
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
    cat_title = wikipedia.input(u'Which category do you want to tidy up?')
    catlink = catlib.CatLink(cat_title)
    
    # get edit summary message
    wikipedia.setAction(msg_change[wikipedia.chooselang(wikipedia.mylang,msg_change)] % cat_title)
    
    
    articles = catlink.articles(recurse = 0)
    if len(articles) == 0:
        print 'There are no articles in category ' + cat_title
    else:
        for article in articles:
            print
            print '==================================================================='
            move_to_category(article, catlink, catlink)



if __name__ == "__main__":
    action = None
    sort_by_last_name = False
    for arg in sys.argv[1:]:
        if wikipedia.argHandler(arg):
            pass
        elif arg == 'add':
            action = 'add'
        elif arg == 'remove':
            action = 'remove'
        elif arg == 'rename':
            action = 'rename'
        elif arg == 'tidy':
            action = 'tidy'
        elif arg == '-person':
            sort_by_last_name = True
    if action == 'add':
        add_category(sort_by_last_name)
    elif action == 'remove':
        remove_category()
    elif action == 'rename':
        rename_category()
    elif action == 'tidy':
        tidy_category()
    else:
        print
        print 'Syntax: python category.py action [-option]'
        print 'where action can be one of these:'
        print ' * add  - mass-add a category to a list of pages'
        print ' * remove - remove category tag from all pages in a category'
        print ' * rename - move all pages in a category to another category'
        print ' * tidy - tidy up a category by moving its articles into subcategories'
        print 'and  option can be one of these:'
        print ' * person - sort persons by their last name'
        print 
        print 'For example, to create a new category from a list of persons, type:'
        print '  python category.py add -person'
        print 'and follow the on-screen instructions.'
       
